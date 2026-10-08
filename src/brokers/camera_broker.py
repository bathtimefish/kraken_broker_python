from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Optional

from lib import kraken_pb2
from lib.broker import Broker
# from adapters.slack import SlackAdapter

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CameraBroker(Broker):

    RESPONSE_CONTENT_TYPE = "text/plain"

    def __init__(self) -> None:
        self.name = "CameraBroker"
    # self.slack = SlackAdapter()

    async def on(
        self,
        request: kraken_pb2.KrakenRequest,
        response: kraken_pb2.KrakenResponse,
    ) -> Optional[kraken_pb2.KrakenResponse]:
        logger.debug(
            "CameraBroker processing collector=%s payload_bytes=%d metadata=%s",
            request.collector_name,
            len(request.payload),
            request.metadata,
        )

        if not request.collector_name:
            logger.warning("Collector name missing; aborting camera processing")
            return None

        metadata = self._parse_metadata(request.metadata)
        if metadata is None:
            return None

        saved_path = self.save_img(request.payload, metadata)
        if not saved_path:
            logger.warning("Image save failed for collector=%s", request.collector_name)
            return None

        response_meta = self._build_response_metadata(saved_path)
        kraken_response = self.build_response_message(
            collector_name=request.collector_name,
            content_type=self.RESPONSE_CONTENT_TYPE,
            metadata=response_meta,
            payload=bytes([0x00]),
        )

        logger.debug(
            "CameraBroker responding collector=%s saved_image=%s",
            kraken_response.collector_name,
            saved_path,
        )
        return kraken_response

    def _parse_metadata(self, metadata_json: str) -> Optional[dict[str, Any]]:
        if not metadata_json:
            logger.warning("Metadata missing for camera request")
            return None
        try:
            metadata: dict[str, Any] = json.loads(metadata_json)
        except json.JSONDecodeError as exc:
            logger.warning("Invalid metadata JSON: %s", exc)
            return None

        if "width" not in metadata or "height" not in metadata:
            logger.warning("Metadata lacks resolution information: %s", metadata)
            return None
        return metadata

    # JPEG の先頭（SOI マーカー）と末尾（EOI マーカー）
    JPEG_START = b"\xff\xd8\xff"
    JPEG_END = b"\xff\xd9"

    def save_img(self, payload, metadata, output_dir="images"):
        """
        受信した JPEG をそのままファイルとして保存する
        （kraken_collector 3.0.0 以降、camera の payload は JPEG。2.x までは無圧縮の RGB24 だった）

        Args:
            payload (bytes): JPEG のバイト列
            metadata (dict): メタデータ（camera_name, width, height）
            output_dir (str): 保存先ディレクトリ

        Returns:
            str: 保存されたファイルのパス（JPEG でなければ None）
        """
        try:
            width = metadata.get('width')
            height = metadata.get('height')
            camera_name = metadata.get('camera_name', 'unknown')

            logger.info(f"Processing image from {camera_name}: {width}x{height}")

            if not payload.startswith(self.JPEG_START):
                logger.error(
                    "The camera payload is not JPEG; kraken_collector 3.0.0 or later sends JPEG "
                    f"({len(payload)} bytes)"
                )
                return None
            if not payload.rstrip(b"\x00").endswith(self.JPEG_END):
                logger.warning("The JPEG may be cut off (no end marker)")

            # 出力ディレクトリの作成
            os.makedirs(output_dir, exist_ok=True)

            # Unixtimestampを使用してファイル名生成
            timestamp = int(time.time())
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "wb") as f:
                f.write(payload)

            logger.info(f"Image saved: {filepath} ({width}x{height}, {len(payload)} bytes)")
            return filepath

        except Exception as e:
            logger.error(f"Error saving image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    @classmethod
    def _build_response_metadata(cls, saved_path: str) -> str:
        return json.dumps(
            {
                "response_type": "simple",
                "saved_image": saved_path,
                "source_broker": cls.__name__,
            }
        )

