import asyncio
import logging
import grpc
from lib import kraken_pb2
from lib import kraken_pb2_grpc
from lib.broker import Broker
from broker_manager import BrokerManager
from lib.config_manager import ConfigManager

class KrakenServiceServicer(kraken_pb2_grpc.KrakenServiceServicer):
    def __init__(self, brokers: list[Broker]):
        self.brokers = brokers

    async def ProcessKrakenRequest(
        self,
        request: kraken_pb2.KrakenRequest,
        context: grpc.aio.ServicerContext,
    ) -> kraken_pb2.KrakenResponse:
        response = kraken_pb2.KrakenResponse
        tasks = []
        response_once = None
        for broker in self.brokers:
            task = asyncio.create_task(broker.on(request, response))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        response_once = next((result for result in results if result is not None), None)
        #logging.info(response_once)  # This line is added for debugging
        return response_once


async def serve():
    try:
        config = ConfigManager().get()
        servicer = KrakenServiceServicer(brokers=BrokerManager().brokers)
        server = grpc.aio.server()
        kraken_pb2_grpc.add_KrakenServiceServicer_to_server(servicer, server)
        # rise the server on port 5051
        grpc_host = config["KRAKENB_GRPC_HOST"] 
        server.add_insecure_port(grpc_host)
        logging.info('KRAKEN BROKER - Highlevel IoT data router was started.')
        logging.info("gRPC server was started on `%s`" % grpc_host)
        if (int(config["KRAKENB_DEBUG"]) > 0):
            logging.info("KRAKEN BROKER is running as debug mode.")
        await server.start()
        await server.wait_for_termination()
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
