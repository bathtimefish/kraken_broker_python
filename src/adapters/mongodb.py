import logging
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from lib.config_manager import ConfigManager

class MongoDbAdapter:

    def __init__(self) -> MongoClient:
        try:
            self.config = ConfigManager().get()
            self.uri = self.config["MONGODB_URI"]
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            return self.client
        except Exception as e:
            logging.error(e)
