from __future__ import annotations

from collections.abc import Sequence

from lib.broker import Broker

from brokers.simple_broker import SimpleBroker
# from brokers.teltonika_fmt887_broker import TeltonikaFTM887Broker
# from brokers.heartbeat_broker import HeartbeatBroker
# from brokers.bjig_broker import BraveJigBroker
# from brokers.camera_broker import CameraBroker


class BrokerManager:
    def __init__(self) -> None:
        """Instantiate and register available brokers."""
        self._brokers: list[Broker] = [
            SimpleBroker(),
            # TeltonikaFTM887Broker(),
            # CameraBroker(),
            # HeartbeatBroker(),
            # BraveJigBroker(),
        ]

    @property
    def brokers(self) -> Sequence[Broker]:
        """Return the registered brokers as an immutable sequence."""
        return tuple(self._brokers)
