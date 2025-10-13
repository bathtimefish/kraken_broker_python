from __future__ import annotations

import json
from abc import ABCMeta, abstractmethod
from typing import Any, Mapping, Optional, Union

from lib import kraken_pb2


class Broker(metaclass=ABCMeta):
    MetadataInput = Union[str, Mapping[str, Any], None]
    PayloadInput = Union[bytes, bytearray, memoryview, str, Mapping[str, Any], None]

    @abstractmethod
    async def on(
        self,
        request: kraken_pb2.KrakenRequest,
        response: kraken_pb2.KrakenResponse,
    ) -> Optional[kraken_pb2.KrakenResponse]:
        """Handle a Kraken request and optionally return a response."""
        raise NotImplementedError

    @classmethod
    def build_response_message(
        cls,
        *,
        collector_name: str,
        content_type: str,
        metadata: MetadataInput = None,
        payload: PayloadInput = None,
    ) -> kraken_pb2.KrakenResponse:
        """Create a gRPC response message with canonical serialization."""

        return kraken_pb2.KrakenResponse(
            collector_name=collector_name,
            content_type=content_type,
            metadata=cls._serialize_metadata(metadata),
            payload=cls._serialize_payload(payload),
        )

    @staticmethod
    def _serialize_metadata(metadata: MetadataInput) -> str:
        if metadata is None:
            return "{}"
        if isinstance(metadata, str):
            return metadata
        return json.dumps(metadata)

    @staticmethod
    def _serialize_payload(payload: PayloadInput) -> bytes:
        if payload is None:
            return b""
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, bytearray):
            return bytes(payload)
        if isinstance(payload, memoryview):
            return payload.tobytes()
        if isinstance(payload, str):
            return payload.encode("utf-8")
        return json.dumps(payload).encode("utf-8")