import logging
from websockets.sync.client import connect
from lib.config_manager import ConfigManager

class WebSocketAdapter:

    def __init__(self) -> None:
        try:
            self.config = ConfigManager().get()
            self.url = self.config["KRAKENB_WEBSOCKET_URL"]
        except Exception as e:
            logging.error(e)

    def send(self, payload: str) -> None:
        try:
            with connect(self.url) as websocket:
                websocket.send(payload)
        except Exception as e:
            logging.error(e)
