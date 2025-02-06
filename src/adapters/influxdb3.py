import logging
from influxdb_client_3 import InfluxDBClient3, Point, InfluxDBError, write_client_options, WriteOptions
from lib.config_manager import ConfigManager

class InfluxDbAdapter3:

    def __init__(self) -> None:
        try:
            self.config = ConfigManager().get()
            self.host = self.config["INFLUXDB_HOST"]
            self.token = self.config["INFLUXDB_TOKEN"]
            self.org = self.config["INFLUXDB_ORG"]
            self.bucket = self.config["INFLUXDB_BUCKET"]
            write_options = WriteOptions(
                batch_size=100,
                flush_interval=10_000,
                jitter_interval=2_000,
                retry_interval=5_000,
                max_retries=5,
                max_retry_delay=30_000,
                exponential_base=2
            )
            callback = self.InfluxDB3WriteCallback()
            write_opt_client = write_client_options(
                success=callback.success,
                error_callback=callback.error,
                retry_callback=callback.retry,
                write_options=write_options
            )
            self.client = InfluxDBClient3(
                host=self.host,
                token=self.token,
                org=self.org,
                database=self.bucket,
                write_options=write_opt_client
            )
        except Exception as e:
            logging.error(e)

    class InfluxDB3WriteCallback(object):
        def __init__(self):
            None
        def success(self, conf, data: str):
            logging.debug(f"Written successfully, data: {data}")
        def error(self, conf, data: str, exception: InfluxDBError):
            logging.debug(f"Cannot write: {conf}, data: {data} due: {exception}")
        def retry(self, conf, data: str, exception: InfluxDBError):
            logging.debug(f"Retryable error occurs: {conf}, data: {data} retry: {exception}")