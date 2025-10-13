from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from typing import cast

import grpc  # type: ignore
from grpc.aio import ServerInterceptor  # type: ignore

from broker_manager import BrokerManager
from lib import kraken_pb2
from lib import kraken_pb2_grpc
from lib.broker import Broker
from lib.config_manager import ConfigManager

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

active_rpc_count = 0

class CountingInterceptor(ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        global active_rpc_count
        active_rpc_count += 1
        logger.debug(f"RPC Started: Active RPC = {active_rpc_count}")
        try:
            response = await continuation(handler_call_details)
            return response
        finally:
            active_rpc_count -= 1
            logger.debug(f"RPC Finished: Active RPC = {active_rpc_count}")

class KrakenServiceServicer(kraken_pb2_grpc.KrakenServiceServicer):
    def __init__(self, brokers: Sequence[Broker]):
        self.brokers = brokers

    async def ProcessKrakenRequest(
        self,
        request: kraken_pb2.KrakenRequest,
        context: grpc.aio.ServicerContext,
    ) -> kraken_pb2.KrakenResponse:
        response = kraken_pb2.KrakenResponse()
        tasks = [asyncio.create_task(broker.on(request, response)) for broker in self.brokers]
        results: list[kraken_pb2.KrakenResponse | None] = []
        try:
            gathered: list[kraken_pb2.KrakenResponse | None | BaseException] = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0,
            )
            # Filter out exceptions while logging them; abort if any broker fails
            for broker, result in zip(self.brokers, gathered):
                if isinstance(result, Exception):
                    logger.error("Broker %s failed to handle request", broker.__class__.__name__, exc_info=result)
                    await context.abort(grpc.StatusCode.INTERNAL, f"Broker error: {result}")
                    raise RuntimeError("context.abort returned unexpectedly")
            filtered = [result for result in gathered if not isinstance(result, Exception)]
            results = cast(list[kraken_pb2.KrakenResponse | None], filtered)
        except asyncio.TimeoutError:
            for task in tasks:
                task.cancel()
            await context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Broker processing timed out")
            raise RuntimeError("context.abort returned unexpectedly")
        except Exception as e:  # pragma: no cover - defensive logging
            for task in tasks:
                task.cancel()
            await context.abort(grpc.StatusCode.INTERNAL, f"Error processing request: {e}")
            raise RuntimeError("context.abort returned unexpectedly")
        finally:
            for task in tasks:
                if task.done():
                    continue
                task.cancel()

        valid_response = next((result for result in results if result is not None), None)
        if valid_response is None:
            await context.abort(grpc.StatusCode.INTERNAL, "No valid response from broker.on")
            raise RuntimeError("context.abort returned unexpectedly")
    
        return valid_response

async def serve():
    try:
        config = ConfigManager().get()
        servicer = KrakenServiceServicer(brokers=BrokerManager().brokers)
        # grpc server options
        server_options = [
            ('grpc.max_concurrent_streams', 1000),
            ('grpc.max_connection_idle_ms', 30000),  # 30sec
            ('grpc.max_connection_age_ms', 300000),  # 5min
            ('grpc.keepalive_time_ms', 60000),       # 1min
            ('grpc.keepalive_timeout_ms', 20000),    # 20sec
            ('grpc.max_receive_message_length', 16 * 1024 * 1024),  # 16MB
            ('grpc.max_send_message_length', 16 * 1024 * 1024),     # 16MB
        ]
        server = grpc.aio.server(options=server_options, maximum_concurrent_rpcs=1000, interceptors=[CountingInterceptor()]) 
        kraken_pb2_grpc.add_KrakenServiceServicer_to_server(servicer, server)
        # rise the server on port 5051
        grpc_host = config["KRAKENB_GRPC_HOST"] 
        server.add_insecure_port(grpc_host)
        logger.info('KRAKEN BROKER - Highlevel IoT data router was started.')
        logger.info("gRPC server was started on `%s`" % grpc_host)
        if (int(config["KRAKENB_DEBUG"]) > 0):
            logger.info("KRAKEN BROKER is running as debug mode.")
        await server.start()
        await server.wait_for_termination()
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    asyncio.run(serve())
