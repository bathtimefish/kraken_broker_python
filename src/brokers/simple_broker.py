import logging
import json
from lib import kraken_pb2
from lib.broker import Broker
from adapters.slack import SlackAdapter

class SimpleBroker(Broker):

    def __init__(self):
        self.name = "SimpleBroker"
        self.slack = SlackAdapter()
    
    async def on(self, request: kraken_pb2.KrakenRequest, response: kraken_pb2.KrakenResponse) -> None:
        logging.info(request)
        logging.info(response)
        response_content_type = "text/plain"
        response_meta = {
            "response_type": "simple"
        }
        meta_str = json.dumps(response_meta)
        return  response(request.collector_name, response_content_type, meta_str, "0")