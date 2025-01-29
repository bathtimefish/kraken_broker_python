from lib.broker import Broker

#from brokers.simple_broker import SimpleBroker 
#from brokers.heartbeat_broker import HeartbeatBroker
# test for brave jig helper
from brokers.brave_jig_broker import BraveJigBroker

class BrokerManager:

    def __init__(self)->list[Broker]:
        # Add your brokers here
        self.brokers = [
            #SimpleBroker(),
            #HeartbeatBroker(),
            BraveJigBroker()
        ]
