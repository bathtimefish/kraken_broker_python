from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from lib import kraken_pb2
from lib.broker import Broker


class HeartbeatBroker(Broker):

    RESPONSE_CONTENT_TYPE = "application/json"

    def __init__(self) -> None:
        self.name = "HeartbeatBroker"

    async def on(
        self,
        request: kraken_pb2.KrakenRequest,
        response: kraken_pb2.KrakenResponse,
    ) -> Optional[kraken_pb2.KrakenResponse]:
        logging.debug(
            "HeartbeatBroker processing collector=%s metadata=%s",
            request.collector_name,
            request.metadata,
        )

        metadata = self._parse_metadata(request.metadata)
        heartbeat_payload = self._build_payload(metadata)

        kraken_response = self.build_response_message(
            collector_name=request.collector_name or "heartbeat",
            content_type=self.RESPONSE_CONTENT_TYPE,
            payload=heartbeat_payload,
            metadata=self._build_response_metadata(metadata),
        )

        logging.debug(
            "HeartbeatBroker responding collector=%s timestamp=%s",
            kraken_response.collector_name,
            heartbeat_payload.get("timestamp"),
        )
        return kraken_response

    def _parse_metadata(self, metadata_json: str) -> dict[str, Any]:
        if not metadata_json:
            return {}
        try:
            metadata = json.loads(metadata_json)
            if isinstance(metadata, dict):
                return metadata
        except json.JSONDecodeError as exc:
            logging.warning("Heartbeat metadata JSON decode failed: %s", exc)
        return {}

    @classmethod
    def _build_payload(cls, metadata: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        return {
            "status": "alive",
            "timestamp": now.isoformat(),
            "metadata": metadata,
        }

    @classmethod
    def _build_response_metadata(cls, request_metadata: dict[str, Any]) -> str:
        response_meta: dict[str, Any] = {
            "response_type": "heartbeat",
            "source_broker": cls.__name__,
        }
        if request_metadata:
            response_meta["request_metadata_keys"] = list(request_metadata.keys())
        return json.dumps(response_meta)

