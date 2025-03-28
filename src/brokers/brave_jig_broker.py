import logging
import json
from lib import kraken_pb2
from lib.broker import Broker
import helpers.brave_jig.main as brave_jig

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BraveJigBroker(Broker):

    def __init__(self):
        self.name = "BraveJigBroker"
    
    async def on(self, request: kraken_pb2.KrakenRequest, response: kraken_pb2.KrakenResponse) -> kraken_pb2.KrakenResponse|None:
        meta = json.loads(request.metadata)
        if request.collector_name == "serial" and meta["device_name"] == "brave_jig":
                data = brave_jig.parse(request.payload)
        logger.info("Lux data: %s" % json.dumps(data))
        response_content_type = "text/plain"
        response_meta = {
            "response_type": "simple"
        }
        meta_str = json.dumps(response_meta)

        # !!! Debug: 即時最初のレスポンスを返す File descriptor limit reached 対策試験 !!! 
        #kraken_response =  response(
        #    collector_name=request.collector_name,
        #    content_type=response_content_type,
        #    metadata=meta_str,
        #    payload=bytes([0x00])
        #)
        #return kraken_response
        return None 