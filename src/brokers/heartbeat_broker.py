import logging
from lib import kraken_pb2
from lib.broker import Broker

class HeartbeatBroker(Broker):

    def __init__(self):
        self.name = "HeartbeatBroker"
    
    async def on(self, kind: str, provider: str, payload: str) -> kraken_pb2.KrakenResponse|None:
        logging.info(
            "%s.on: kind=%s, provider=%s, payload=%s" %
            (
                self.name,
                kind,
                provider,
                payload
            )
        )
        return None
