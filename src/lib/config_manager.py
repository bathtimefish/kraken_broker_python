import os

class ConfigManager:

    def __init__(self):
        # define the environment variables for kraken config
        self.param_names = [
            "KRAKENB_DEBUG",
            "KRAKENB_GRPC_HOST",
            "KRAKENB_INFLUXDB_HOST",
            "KRAKENB_INFLUXDB_API_TOKEN",
            "KRAKENB_INFLUXDB_ORG",
            "KRAKENB_INFLUXDB_BUCKET",
            "KRAKENB_REDIS_HOST",
            "KRAKENB_REDIS_PORT",
            "KRAKENB_REDIS_DB",
            "KRAKENB_REIDS_USER",
            "KRAKENB_REDIS_PASSWORD",
            "KRAKENB_MONGODB_HOST",
            "KRAKENB_MONGODB_USER",
            "KRAKENB_MONGODB_PASSWORD",
            "KRAKENB_MONGODB_DATABASE",
            "KRAKENB_WEBSOCKET_URL",
            "KRAKENB_SLACK_URL",
        ]

    def _load_config(self) -> dict:
        config = {}
        for param_name in self.param_names:
            config[param_name] = os.getenv(param_name)
        return config
    
    def get(self) -> dict:
        return self._load_config()
