import logging
import json
from lib.broker import Broker
import helpers.brave_jig.main as brave_jig

class BraveJigBroker(Broker):

    def __init__(self):
        self.name = "SimpleBroker"
    
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
        payload_json = json.loads(payload)
        if provider == "serial":
            if payload_json["device_name"] == "brave_jig":
                data = brave_jig.parse(payload_json["hex_string"])
        logging.info(data)