# Kraken Broker
Data Collection/Broker Application for IoT

![logo](./assets/kraken-logo-300.png)

# Introduction
Kraken Collector was developed as a data collection application for IoT. It can be used in combination with [Kraken Broker](https://github.com/bathtimefish/kraken_broker_python/).

Using Kraken Collector/Broker, you can receive data sent from edge IoT sensors via HTTP or MQTT in cloud or on-premise environments. This setup enables data-driven processing, such as data transformation, database storage, and user notifications, tailored to specific business needs.

If we compare what Kraken can achieve to existing services, it resembles a simplified combination of AWS IoT and Lambda. Kraken Collector/Broker allows for a compact, open-source implementation of these capabilities.

# Why Kraken?
Having worked on IoT systems for clients for many years, I have observed that while many projects are well-suited to the robust features offered by cloud services like AWS IoT and Azure IoT Hub, some are not.

Certain projects prioritize operational costs or control over scalability and stability, with requirements like "minimizing subscription costs," "distrusting cloud services," or "keeping all resources managed within the worksite." These needs are especially prevalent in certain industries where introducing sensing technology and data storage can be highly beneficial, but cloud solutions become overly complex and costly.

Kraken was developed to address these needs, allowing IoT systems to start small. Kraken Collector/Broker can implement IoT solutions, typically achievable through AWS IoT and Lambda, on on-premise, low-resource computers like Raspberry Pi.

The features of Kraken were selected from the most frequently used functions and experiences in IoT system development. The focus is on providing only the essential functions needed for quickly building IoT background systems rather than offering extensive features.

I hope Kraken can deliver its benefits to areas where IoT has yet to reach.

# Kraken Broker
Kraken Broker functions as a data broker that receives data from [Kraken Collector](https://github.com/bathtimefish/kraken_collector) and executes custom processing such as data transformation and database storage.

You can describe your business-specific data processing by customizing brokers in the [brokers](https://github.com/bathtimefish/kraken_broker_python/tree/main/src/brokers) directory or by creating entirely new brokers. Multiple brokers can be launched in an event-driven manner and execute asynchronous tasks according to the type of data.

Kraken Broker is currently available in Python, with versions in other languages planned for future release.

# Getting Started
This tutorial guides you through setting up Kraken Collector/Broker, starting them, and receiving your first data.

## Setup Broker
Clone the broker:
```bash
git clone https://github.com/bathtimefish/kraken_broker_python
cd kraken_broker_python
```

Set environment variables to launch the broker as a Slack broker:
```bash
export PYTHONDONTWRITEBYTECODE=1
export KRAKENB_DEBUG=1
export KRAKENB_GRPC_HOST=[::]:50051
export KRAKENB_SLACK_URL=[YOUR_SLACK_WEBHOOK_URL]
```

Start the broker:
```bash
python ./src/main.py
```

If you see the following log, the startup was successful:
```plaintext
INFO:root:gRPC server was started on `[::]:50051`
INFO:root:KRAKEN BROKER is running as debug mode.
```

## Setup Collector
Build the collector:
```bash
git clone https://github.com/bathtimefish/kraken_collector
cd kraken_collector
cargo build
```

Set environment variables to launch the collector as a webhook receiver:
```bash
export KRKNC_BROKER_HOST=http://[::1]:50051
export KRKNC_WEBHOOK_PATH=webhook
export KRKNC_WEBHOOK_PORT=3000
```

Start the collector:
```bash
RUST_LOG=error,main=debug cargo run --bin main
```

If you see the following log, the startup was successful:
```plaintext
[2024-01-01T00:00:00Z INFO  main] KRAKEN Collector -- The Highlevel Data Collector -- boot sequence start.
[2024-01-01T00:00:00Z DEBUG main::service] starting webhook collector service...
[2024-01-01T00:00:00Z DEBUG main::service] collector service started.
[2024-01-01T00:00:00Z DEBUG main::collectors::webhook] Webhook server was started and is listening on http://0.0.0.0:3000
```

## Send Data to Collector
Send data to the collector:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"id":"101", "name":"env-sensor", "temp":"25.6", "hum":"52.4"}' http://localhost:3000/webhook
```

If you receive a message like the following on Slack, Kraken Collector/Broker is working correctly:
```plaintext
kind=collector, provider=webhook, payload={"id":"101", "name":"env-sensor", "temp":"25.6", "hum":"52.4"}
```

# Broker Settings
The functionality of the broker is configured through environment variables. Currently, the following environment variables are defined:

- `KRAKENB_GRPC_HOST`
- `KRAKENB_INFLUXDB_HOST`
- `KRAKENB_INFLUXDB_API_TOKEN`
- `KRAKENB_INFLUXDB_ORG`
- `KRAKENB_INFLUXDB_BUCKET`
- `KRAKENB_REDIS_HOST`
- `KRAKENB_REDIS_PORT`
- `KRAKENB_REDIS_DB`
- `KRAKENB_REDIS_USER`
- `KRAKENB_REDIS_PASSWORD`
- `KRAKENB_MONGODB_HOST`
- `KRAKENB_WEBSOCKET_URL`
- `KRAKENB_SLACK_URL`

## for Collector
### KRAKENB_GRPC_HOST
Specify the gRPC Server URL. In most cases, the following setting should be sufficient:
```bash
KRAKENB_GRPC_HOST=[::]:50051
```

## InfluxDB
The [InfluxDB adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/influxdb.py) can be used by setting `KRAKENB_INFLUXDB_HOST`, `KRAKENB_INFLUXDB_API_TOKEN`, `KRAKENB_INFLUXDB_ORG`, and `KRAKENB_INFLUXDB_BUCKET`.
### KRAKENB_INFLUXDB_HOST
Set the InfluxDB host URL.
### KRAKENB_INFLUXDB_API_TOKEN
Set the InfluxDB API Token.
### KRAKENB_INFLUXDB_ORG
Set the InfluxDB Organization.
### KRAKENB_INFLUXDB_BUCKET
Set the InfluxDB Bucket.

## Redis
The [Redis adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/redis.py) can be used by setting `KRAKENB_REDIS_HOST`, `KRAKENB_REDIS_PORT`, `KRAKENB_REDIS_DB`, `KRAKENB_REDIS_USER`, and `KRAKENB_REDIS_PASSWORD`.
### KRAKENB_REDIS_HOST
Set the Redis host URL.
### KRAKENB_REDIS_PORT
Set the Redis port number.
### KRAKENB_REDIS_DB
Set the Redis DB number.
### KRAKENB_REDIS_USER
Set the Redis username.
### KRAKENB_REDIS_PASSWORD
Set the Redis password.

## MongoDB
The [MongoDB adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/mongodb.py) can be used by setting `KRAKENB_MONGODB_HOST`.
### KRAKENB_MONGODB_HOST
Set the MongoDB host URL.

## Websocket
The [Websocket adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/websocket.py) can be used by setting `KRAKENB_WEBSOCKET_URL`. The Websocket adapter provides Websocket client functionality to the Broker.
### KRAKENB_WEBSOCKET_URL
Set the Websocket Server URL.

## Slack
The [Slack adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/slack.py) can be used by setting `KRAKENB_SLACK_URL`. The Slack adapter provides Slack incoming webhooks client functionality to the Broker.
### KRAKENB_SLACK_URL
Set the Slack incoming webhooks URL.

# Customizing Broker
WIP