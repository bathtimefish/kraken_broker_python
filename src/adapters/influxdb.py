import logging
import influxdb_client
from influxdb_client import InfluxDBClient
from lib.config_manager import ConfigManager

class InfluxDbAdapter:

    def __init__(self) -> InfluxDBClient:
        try:
            self.config = ConfigManager().get()
            self.host = self.config["INFLUXDB_HOST"]
            self.token = self.config["INFLUXDB_TOKEN"]
            self.org = self.config["INFLUXDB_ORG"]
            self.bucket = self.config["INFLUXDB_BUCKET"]
            self.client = influxdb_client.InfluxDBClient(
                url=self.host,
                token=self.token,
                org=self.org
            )
        except Exception as e:
            logging.error(e)
