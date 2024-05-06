import logging
import redis
from lib.config_manager import ConfigManager

class RedisAdapter:

    def __init__(self) -> redis.Redis:
        try:
            self.config = ConfigManager().get()
            self.host = self.config["KRAKENB_REDIS_HOST"]
            self.port = self.config["KRAKENB_REDIS_PORT"]
            self.db = self.config["KRAKENB_REDIS_DB"]
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db
            )
        except Exception as e:
            logging.error(e)
