import logging
import struct

def parse(data: bytes) -> dict:
    if data:
        # --- Uplink resopnse division ---
        protocol_ver = struct.unpack("B", data[0:1])[0]
        type_field = struct.unpack("B", data[1:2])[0]
        data_length = struct.unpack("<H", data[2:4])[0]
        unix_time = struct.unpack("<I", data[4:8])[0]
        b_sd_id = data[8:16].hex()
        sensor_device_id = "".join(reversed([b_sd_id[i:i+2] for i in range(0, len(b_sd_id), 2)]))
        b_s_id = data[16:18].hex()
        sensor_id = "".join(reversed([b_s_id[i:i+2] for i in range(0, len(b_s_id), 2)]))
        rssi = struct.unpack("b", data[18:19])[0]
        order = struct.unpack("<H", data[19:21])[0]
        # --- Sensor data division ---
        battery_level = struct.unpack("B", data[21:22])[0]
        sampling_interval = struct.unpack("B", data[22:23])[0]
        sampling_time = struct.unpack("<I", data[23:27])[0]
        sampling_num = struct.unpack("<H", data[27:29])[0]
        logging.info(data.hex())
        accel_x = struct.unpack("<f", data[29:33])[0]  # 4byte(Float)
        accel_y = struct.unpack("<f", data[33:37])[0]  # 4byte(Float)
        accel_z = struct.unpack("<f", data[37:41])[0]  # 4byte(Float)

        #logging.info("Protocol version: %d", protocol_ver)
        #logging.info("Type: %d", type_field)
        #logging.info("Data length: %d", data_length)
        #logging.info("Unix time: %d", unix_time)
        #logging.info("Sensor device ID: %s", sensor_device_id)
        #logging.info("Sensor ID: %s", sensor_id)
        #logging.info("RSSI: %d", rssi)
        #logging.info("Order: %d", order)
        #logging.info("Battery level: %d", battery_level)
        #logging.info("Sampling interval: %d", sampling_interval)
        #logging.info("Sampling time: %d", sampling_time)
        #logging.info("Sampling num: %d", sampling_num)
        #logging.info("Accel X: %d", accel_x)
        #logging.info("Accel Y: %d", accel_y)
        #logging.info("Accel Z: %d", accel_z)
        return {
            "protocol_ver": protocol_ver,
            "type": type_field,
            "data_length": data_length,
            "unix_time": unix_time,
            "sensor_device_id": sensor_device_id,
            "sensor_id": sensor_id,
            "rssi": rssi,
            "order": order,
            "battery_level": battery_level,
            "sampling_interval": sampling_interval,
            "sampling_time": sampling_time,
            "sampling_num": sampling_num,
            "accel_x": accel_x,
            "accel_y": accel_y,
            "accel_z": accel_z
        }
    else:
        logging.error("No dataponse received within timeout period.")