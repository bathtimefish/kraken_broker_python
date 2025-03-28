import logging
import json
from lib import kraken_pb2
from lib.broker import Broker
from adapters.slack import SlackAdapter

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SimpleBroker(Broker):

    def __init__(self):
        self.name = "SimpleBroker"
        self.slack = SlackAdapter()
    
    async def on(self, request: kraken_pb2.KrakenRequest, response: kraken_pb2.KrakenResponse) -> kraken_pb2.KrakenResponse|None:
        logger.debug("=== SimpleBroker: Processing request ===")
        logger.debug(request)
        response_content_type = "text/plain"
        response_meta = {
            "response_type": "simple"
        }
        meta_str = json.dumps(response_meta)
        kraken_response =  response(
            collector_name=request.collector_name,
            content_type=response_content_type,
            metadata=meta_str,
            payload=bytes([0x00])
        )
        logger.debug("=== SimpleBroker: Sending response ===")
        logger.debug(kraken_response)
        return kraken_response