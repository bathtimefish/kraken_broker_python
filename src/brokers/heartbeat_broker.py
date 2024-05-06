import logging
from lib.broker import Broker

class HeartbeatBroker(Broker):

    def __init__(self):
        self.name = "HeartbeatBroker"
    
    async def on(self, kind: str, provider: str, payload: str) -> None:
        logging.info(
            "%s.on: kind=%s, provider=%s, payload=%s" %
            (
                self.name,
                kind,
                provider,
                payload
            )
        )
