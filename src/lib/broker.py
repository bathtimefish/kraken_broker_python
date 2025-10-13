from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Optional

from lib import kraken_pb2


class Broker(metaclass=ABCMeta):
    @abstractmethod
    async def on(
        self,
        request: kraken_pb2.KrakenRequest,
        response: kraken_pb2.KrakenResponse,
    ) -> Optional[kraken_pb2.KrakenResponse]:
        """Handle a Kraken request and optionally return a response."""
        raise NotImplementedError