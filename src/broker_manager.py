from lib.broker import Broker

from brokers.simple_broker import SimpleBroker 
#from brokers.heartbeat_broker import HeartbeatBroker
#from brokers.brave_jig_broker import BraveJigBroker
#from brokers.test_jig_broker import TestJigBroker
from brokers.camera_broker import CameraBroker 

class BrokerManager:

    def __init__(self)->list[Broker]:
        # Add your brokers here
        self.brokers = [
            #SimpleBroker(),
            CameraBroker(),
            #HeartbeatBroker(),
            #BraveJigBroker(),
            #TestJigBroker(),
        ]
