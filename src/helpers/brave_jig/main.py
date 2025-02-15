"""
Broker helper for Brave Jig
"""

import logging
import helpers.brave_jig.lux as lux

def get_sensor_id(data: bytes) -> str:
    """
    Get sensor id from data
    """
    b_s_id = data[16:18].hex()
    sensor_id = "".join(reversed([b_s_id[i:i+2] for i in range(0, len(b_s_id), 2)]))
    return sensor_id

def parse_sensor_data(data: bytes) -> dict:
    """
    Dispatch data to the correct handler
    """
    sensor_id = get_sensor_id(data)
    logging.info("Brave Jig: Sensor ID: %s" % sensor_id)
    if sensor_id == "0121":   # lux sensor
        logging.info("Brave Jig: Found lux sensor")
        return lux.parse(data)
    else:
        logging.error("Brave Jig: Unknown sensor")

def parse(hex_str: str) -> dict:
    """
    Parse data from Brave Jig
    """
    result = {}
    try:
        data = bytes.fromhex(hex_str)
        logging.info(data)
        if data[1] == 0x00:
            result = parse_sensor_data(data)
        elif data[1] == 0xFF:
            logging.info("Brave Jig: Found error data")
        else:
            logging.error("Brave Jig: Unknown data")
        return result
    except Exception as e:
        logging.error(e)
        return {}