import asyncio
import logging
import grpc
from lib import kraken_pb2
from lib import kraken_pb2_grpc
from lib.broker import Broker
from broker_manager import BrokerManager
from lib.config_manager import ConfigManager

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class KrakenServiceServicer(kraken_pb2_grpc.KrakenServiceServicer):
    def __init__(self, brokers: list[Broker]):
        self.brokers = brokers

    async def ProcessKrakenRequest(
        self,
        request: kraken_pb2.KrakenRequest,
        context: grpc.aio.ServicerContext,
    ) -> kraken_pb2.KrakenResponse|None:
        response = kraken_pb2.KrakenResponse
        tasks = []
        #response_once = None
        for broker in self.brokers:
            task = asyncio.create_task(broker.on(request, response))
            tasks.append(task)
        #results = await asyncio.gather(*tasks)
        #response_once = next((result for result in results if result is not None), None)
        #logging.info(response_once)  # This line is added for debugging
        #return response_once
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=30.0)
        except Exception as e:
            # タイムアウトや他の例外が発生した場合、RPCを中断する
            context.abort(grpc.StatusCode.INTERNAL, f"Error processing request: {e}")
    
        # 有効なレスポンスが得られなかった場合も中断する
        valid_response = next((result for result in results if result is not None), None)
        if valid_response is None:
            context.abort(grpc.StatusCode.INTERNAL, "No valid response from broker.on")
    
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
            ('grpc.keepalive_time_ms', 60000),      # 1min
            ('grpc.keepalive_timeout_ms', 20000)    # 20sec
        ]
        server = grpc.aio.server(options=server_options, maximum_concurrent_rpcs=1000) 
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
