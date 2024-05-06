#!/bin/sh
export PYTHONDONTWRITEBYTECODE=1
export KRAKENB_DEBUG=1
export KRAKENB_GRPC_HOST=[::]:5051
export KRAKENB_INFLUXDB_HOST=http://localhost:8086
export KRAKENB_INFLUXDB_API_TOKEN=[YOUR_INFLUXDB_API_TOKEN]
export KRAKENB_INFLUXDB_ORG=[YOUR_INFLUXDB_ORG]
export KRAKENB_INFLUXDB_BUCKET=[YOUR_INFLUXDB_BUCKET]
export KRAKENB_REDIS_HOST=localhost
export KRAKENB_REDIS_PORT=6379
export KRAKENB_REDIS_DB=0
export KRAKENB_REIDS_USER=[YOUR_REDIS_USER]
export KRAKENB_REDIS_PASSWORD=[YOUR_REDIS_PASSWORD]
export KRAKENB_MONGODB_HOST=localhost:27017
export KRAKENB_MONGODB_USER=[YOUR_MONGODB_USER]
export KRAKENB_MONGODB_PASSWORD=[YOUR_MONGODB_PASSWORD]
export KRAKENB_MONGODB_DATABASE=[YOUR_MONGODB_DATABASE]
export KRAKENB_WEBSOCKET_URL=[YOUR_WEBSOCKET_URL]
export KRAKENB_SLACK_URL=[YOUR_SLACK_URL]
