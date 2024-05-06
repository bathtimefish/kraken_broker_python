import asyncio
import logging
import grpc
from lib import kraken_pb2
from lib import kraken_pb2_grpc
from lib.broker import Broker
from broker_manager import BrokerManager
from lib.config_manager import ConfigManager

class KrakenMessanger(kraken_pb2_grpc.KrakenMessageServicer):
    def __init__(self, brokers: list[Broker]):
        self.brokers = brokers

    async def Send(
        self,
        request: kraken_pb2.KrakenMessageRequest,
        context: grpc.aio.ServicerContext,
    ) -> kraken_pb2.KrakenMessageResponse:
        status_code = 1
        #logging.info(
        #    "Received: kind=%s, provider=%s, payload=%s" %
        #    (
        #        request.kind,
        #        request.provider,
        #        request.payload
        #    )
        #)
        loop = asyncio.get_event_loop()
        for broker in self.brokers:
            loop.create_task(broker.on(request.kind, request.provider, request.payload))
        return kraken_pb2.KrakenMessageResponse(status=status_code)


async def serve():
    try:
        config = ConfigManager().get()
        messenger = KrakenMessanger(brokers=BrokerManager().brokers)
        server = grpc.aio.server()
        kraken_pb2_grpc.add_KrakenMessageServicer_to_server(messenger, server)
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
