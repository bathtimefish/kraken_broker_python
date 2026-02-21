from __future__ import annotations

import json
import logging
from typing import Any, Optional

from lib import kraken_pb2
from lib.broker import Broker
# from adapters.slack import SlackAdapter

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SimpleBroker(Broker):
    """A minimal broker that echoes a simple acknowledgement response."""

    RESPONSE_CONTENT_TYPE = "text/plain"

    def __init__(self) -> None:
        self.name = "SimpleBroker"
        # self.slack = SlackAdapter()

    async def on(
        self,
        request: kraken_pb2.KrakenRequest,
        response: kraken_pb2.KrakenResponse,
    ) -> Optional[kraken_pb2.KrakenResponse]:
        logger.debug(
            "SimpleBroker processing collector=%s payload_bytes=%d metadata=%s",
            request.collector_name,
            len(request.payload),
            request.metadata,
        )
        logger.debug(request.payload)

        metadata: dict[str, Any]
        try:
            metadata = json.loads(request.metadata) if request.metadata else {}
        except json.JSONDecodeError as exc:
            logger.warning("Invalid metadata JSON for collector=%s: %s", request.collector_name, exc)
            return None

        if not request.collector_name:
            logger.warning("Collector name missing; skipping response")
            return None

        # Check if this is a bjig collector request with data
        bjig_meta = metadata.get("bjig")
        if request.collector_name == "bjig" and bjig_meta == "data":
            # Return a test action command for bjig
            test_action = {"action": "test", "command": "status"}
            response_payload = json.dumps(test_action).encode('utf-8')
            response_meta = self._build_response_metadata(metadata)
            logger.info("Sending bjig test action command: %s", test_action)
        else:
            response_payload = bytes([0x00])
            response_meta = self._build_response_metadata(metadata)

        kraken_response = self.build_response_message(
            collector_name=request.collector_name,
            content_type=self.RESPONSE_CONTENT_TYPE,
            metadata=response_meta,
            payload=response_payload,
        )

        logger.debug(
            "SimpleBroker responding collector=%s response_meta=%s payload_bytes=%d",
            kraken_response.collector_name,
            response_meta,
            len(kraken_response.payload),
        )
        return kraken_response

    @classmethod
    def _build_response_metadata(cls, request_metadata: dict[str, Any], response_type: Optional[str] = None) -> str:
        if response_type is None:
            # Check if this is a bjig collector request
            bjig_meta = request_metadata.get("bjig")
            if bjig_meta == "data":
                response_type = "bjig"
            else:
                response_type = "simple"

        combined_meta = {
            "response_type": response_type,
            "source_broker": cls.__name__,
        }
        # Include passthrough metadata keys if needed in the future
        combined_meta.update({k: v for k, v in request_metadata.items() if k.startswith("x-")})
        return json.dumps(combined_meta)

