from __future__ import annotations

import json
import logging
from typing import Any, Optional

import helpers.brave_jig.main as brave_jig
from influxdb_client_3 import (  # type: ignore
    InfluxDBClient3,
    InfluxDBError,
    Point,
    WriteOptions,
    write_client_options,
)

from lib import kraken_pb2
from lib.broker import Broker

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


class InfluxDB3WriteCallback:
    def success(self, conf, data: str) -> None:
        logger.debug("Written successfully, data: %s", data)

    def error(self, conf, data: str, exception: InfluxDBError) -> None:
        logger.debug("Cannot write: %s, data: %s due: %s", conf, data, exception)

    def retry(self, conf, data: str, exception: InfluxDBError) -> None:
        logger.debug("Retryable error occurs: %s, data: %s retry: %s", conf, data, exception)


class BraveJigBroker(Broker):
    RESPONSE_CONTENT_TYPE = "application/json"

    def __init__(self) -> None:
        self.name = "BraveJigBroker"

    async def on(
        self,
        request: kraken_pb2.KrakenRequest,
        response: kraken_pb2.KrakenResponse,
    ) -> Optional[kraken_pb2.KrakenResponse]:
        logger.debug(
            "BraveJigBroker processing collector=%s payload_bytes=%d metadata=%s",
            request.collector_name,
            len(request.payload),
            request.metadata,
        )

        if request.collector_name != "serial":
            logger.debug("Unsupported collector: %s", request.collector_name)
            return None

        metadata = self._parse_metadata(request.metadata)
        if metadata is None or metadata.get("device_name") != "brave_jig":
            logger.debug("Skipping non-brave_jig device metadata=%s", metadata)
            return None

        sensor_data = self._parse_sensor_payload(request.payload)
        if sensor_data is None:
            return None

        self._write_sensor_data(sensor_data)

        response_meta = self._build_response_metadata(sensor_data)
        kraken_response = self.build_response_message(
            collector_name=request.collector_name,
            content_type=self.RESPONSE_CONTENT_TYPE,
            metadata=response_meta,
            payload={"status": "ok"},
        )

        logger.debug(
            "BraveJigBroker responding collector=%s sensor_id=%s",
            kraken_response.collector_name,
            sensor_data.get("sensor_id"),
        )
        return kraken_response

    def _parse_metadata(self, metadata_json: str) -> Optional[dict[str, Any]]:
        if not metadata_json:
            logger.warning("Metadata missing for brave jig request")
            return None
        try:
            metadata: dict[str, Any] = json.loads(metadata_json)
            return metadata
        except json.JSONDecodeError as exc:
            logger.warning("Invalid metadata JSON: %s", exc)
            return None

    def _parse_sensor_payload(self, payload: bytes) -> Optional[dict[str, Any]]:
        try:
            sensor_json = brave_jig.parse(payload)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to parse sensor payload: %s", exc)
            return None
        logger.info("BraveJig sensor data: %s", sensor_json)
        return sensor_json

    def _write_sensor_data(self, sensor_json: dict[str, Any]) -> None:
        point = self._build_sensor_point(sensor_json)
        if point is None:
            logger.debug("No timeseries point generated for sensor_id=%s", sensor_json.get("sensor_id"))
            return

        try:
            write_options = WriteOptions(
                batch_size=100,
                flush_interval=10_000,
                jitter_interval=2_000,
                retry_interval=5_000,
                max_retries=5,
                max_retry_delay=30_000,
                exponential_base=2,
            )
            callback = InfluxDB3WriteCallback()
            write_opt = write_client_options(
                success=callback.success,
                error_callback=callback.error,
                retry_callback=callback.retry,
                write_options=write_options,
            )
            client = InfluxDBClient3(
                host="[HOST_URL]",
                token="[TOKEN]",
                org="default",
                database="brave_jig",
                write_client_options=write_opt,
            )
            try:
                client.write(point)
                logger.debug("Wrote point to InfluxDB sensor_id=%s", sensor_json.get("sensor_id"))
            finally:
                client.close()
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Failed to write sensor data to InfluxDB: %s", exc)

    def _build_sensor_point(self, sensor_json: dict[str, Any]) -> Optional[Point]:
        sensor_id = sensor_json.get("sensor_id")
        if sensor_id == "0121":
            point = (
                Point("illum_sensor")
                .field("lux", sensor_json.get("lux"))
                .field("rssi", sensor_json.get("rssi"))
                .field("battery_level", sensor_json.get("battery_level"))
            )
        elif sensor_id == "0122":
            point = (
                Point("accel_sensor")
                .field("x", sensor_json.get("accel_x"))
                .field("y", sensor_json.get("accel_y"))
                .field("z", sensor_json.get("accel_z"))
                .field("rssi", sensor_json.get("rssi"))
                .field("battery_level", sensor_json.get("battery_level"))
            )
        elif sensor_id == "0123":
            point = (
                Point("thermo_sensor")
                .field("temp", sensor_json.get("temp"))
                .field("hum", sensor_json.get("hum"))
                .field("rssi", sensor_json.get("rssi"))
                .field("battery_level", sensor_json.get("battery_level"))
            )
        elif sensor_id == "0124":
            point = (
                Point("baro_pressure_sensor")
                .field("hpa", sensor_json.get("pressure"))
                .field("rssi", sensor_json.get("rssi"))
                .field("battery_level", sensor_json.get("battery_level"))
            )
        elif sensor_id == "0125":
            point = (
                Point("distance_sensor")
                .field("mm", sensor_json.get("distance"))
                .field("rssi", sensor_json.get("rssi"))
                .field("battery_level", sensor_json.get("battery_level"))
            )
        else:
            logger.debug("Unsupported sensor_id=%s", sensor_id)
            return None

        point = point.tag("sensor_device_id", sensor_json.get("sensor_device_id"))
        point = point.tag("sensor_id", sensor_id)
        return point

    @classmethod
    def _build_response_metadata(cls, sensor_json: dict[str, Any]) -> str:
        return json.dumps(
            {
                "response_type": "simple",
                "source_broker": cls.__name__,
                "sensor_id": sensor_json.get("sensor_id"),
            }
        )
