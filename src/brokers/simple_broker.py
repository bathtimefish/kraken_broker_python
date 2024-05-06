import logging
from lib.broker import Broker
from adapters.slack import SlackAdapter

class SimpleBroker(Broker):

    def __init__(self):
        self.name = "SimpleBroker"
        self.slack = SlackAdapter()
    
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
        slack_payload_interface = self.slack.get_interface()
        slack_payload = slack_payload_interface("random", "KrakenBroker", f"kind={kind}, provider={provider}, payload={payload}")
        self.slack.send(slack_payload)