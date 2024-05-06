import logging
import requests
from dataclasses import dataclass, asdict
from lib.config_manager import ConfigManager


@dataclass
class SlackPayload:
    channel: str
    username: str
    text: str


class SlackAdapter:

    def __init__(self) -> None:
        try:
            self.config = ConfigManager().get()
            self.url = self.config["KRAKENB_SLACK_URL"]
        except Exception as e:
            logging.error(e)

    def send(self, payload: SlackPayload) -> None:
        try:
            json_data = asdict(payload)
            logging.info("URL: %s" % self.url)
            logging.info(f"SlackAdapter.send: {json_data}")
            res = requests.post(
                self.url,
                headers={"Content-Type": "application/json"},
                json=json_data
            )
            logging.info(f"SlackAdapter.send: {res.text}")
        except Exception as e:
            logging.error(e)

    def get_interface(self) -> SlackPayload:
        return SlackPayload
