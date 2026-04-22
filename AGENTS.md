# AGENTS.md - Kraken Broker Custom Broker Development Guide

This document is a guide for developing custom brokers for Kraken Broker using generative AI.

## Project Overview

Kraken Broker is a data broker application for IoT. It receives data from Kraken Collector via gRPC and executes event-driven processing with custom brokers. It enables you to implement AWS IoT + Lambda-like functionality in a compact on-premises environment.

### Key Components

- **Kraken Collector**: Collects data from edge devices via HTTP/MQTT (Rust implementation)
- **Kraken Broker**: Receives data and executes processing such as transformation, storage, and notifications (Python implementation)
- **Custom Brokers**: Implement business-specific processing logic

## Architecture

```
[IoT Sensors] -> [Kraken Collector] -> gRPC -> [Kraken Broker]
                                                     |
                                     +---------------+---------------+
                                     |               |               |
                               [Broker A]      [Broker B]      [Broker C]
                                     |               |               |
                                [InfluxDB]       [Slack]         [Redis]
```

### Processing Flow

1. Kraken Collector sends `KrakenRequest` via gRPC
2. gRPC server (`main.py:80`) receives the request
3. `BrokerManager` retrieves all registered brokers
4. Each broker's `on()` method is executed **in parallel** (`main.py:44`)
5. Returns the result from the first broker that returns a valid response

### gRPC Message Structure

```protobuf
// proto/kraken.proto
message KrakenRequest {
    string collector_name = 1;  // Collector identifier
    string content_type = 2;    // Content type
    string metadata = 3;        // Metadata (JSON string)
    bytes payload = 4;          // Payload (binary)
}

message KrakenResponse {
    string collector_name = 1;
    string content_type = 2;
    string metadata = 3;
    bytes payload = 4;
}
```

## Scaling and Multiple Broker Operations

### Critical: Stability of Parallel Broker Execution

When running multiple brokers in parallel, **the entire Broker system becomes unstable if each broker does not return responses appropriately**. This is a very important design consideration.

#### Challenges in Parallel Execution

- All brokers are executed in parallel via the `on()` method (`main.py:44`)
- If any broker returns an inappropriate response (or `None`), it affects the entire gRPC communication
- As the number of brokers increases, the importance of error handling in each broker increases
- Delays or exceptions in one broker can affect the processing of other brokers

#### Not Recommended Architecture

**Running a large number of brokers in a single broker_manager is NOT recommended.**

```python
# ❌ Not Recommended: Registering many brokers in one BrokerManager
class BrokerManager:
    def __init__(self):
        self._brokers: list[Broker] = [
            Broker1(),
            Broker2(),
            Broker3(),
            # ... 10+ brokers
            Broker15(),
        ]
```

**Reasons**:
- Response management for each broker becomes complex
- Errors in one broker easily affect the entire system
- Debugging becomes difficult
- Performance prediction becomes difficult
- Limited scalability

#### Recommended Architecture: Multiple Broker Instances

When you need a large number of brokers, it is recommended to **launch multiple kraken_broker instances and deploy a small number of brokers to each**.

```
[IoT Sensors] -> [Kraken Collector] -> Load Balancer
                                            |
                       +--------------------+--------------------+
                       |                    |                    |
                [Broker Instance 1]  [Broker Instance 2]  [Broker Instance 3]
                       |                    |                    |
                 [Broker A,B,C]       [Broker D,E,F]       [Broker G,H,I]
```

**Implementation Example**:

```python
# Instance 1: broker_manager.py
class BrokerManager:
    def __init__(self):
        self._brokers: list[Broker] = [
            SensorBroker(),
            InfluxDBBroker(),
            SlackNotificationBroker(),
        ]

# Instance 2: broker_manager.py (separate server or process)
class BrokerManager:
    def __init__(self):
        self._brokers: list[Broker] = [
            CameraBroker(),
            ImageProcessingBroker(),
            S3UploadBroker(),
        ]

# Instance 3: broker_manager.py (separate server or process)
class BrokerManager:
    def __init__(self):
        self._brokers: list[Broker] = [
            AlertBroker(),
            MonitoringBroker(),
            LoggingBroker(),
        ]
```

**Advantages**:
- **Isolated failures**: Problems in one instance do not affect other instances
- **Scalability**: Can increase or decrease the number of instances according to load
- **Ease of debugging**: Easy to identify problematic broker groups
- **Performance**: Fewer parallel processes per instance, more predictable
- **Maintainability**: Clear responsibilities for each instance

### Instructions for AI Agents

When responding to user design requests, generative AI must check the following points:

1. **Check broker count**: If the user requests a large number (5+) of brokers, suggest splitting into multiple instances
2. **Explain risks**: Clearly explain the risks of registering many brokers in one BrokerManager
3. **Propose alternatives**: Suggest architectures using multiple kraken_broker instances
4. **Emphasize response management**: Stress the importance of each broker reliably returning responses

**Dialogue Example**:

```
User: "I want to add 10 brokers"

AI Recommended Response:
"It is possible to register 10 brokers in one broker_manager, but it is not recommended for the following reasons:
- If each broker does not return responses appropriately, the entire system becomes unstable
- Debugging and maintenance become difficult
- Performance prediction becomes difficult

Instead, I recommend the following architecture:
1. Group brokers by function (e.g., sensor-related, image processing, notifications)
2. Launch each group as a separate kraken_broker instance
3. Deploy about 2-4 brokers per instance

This design enables more stable operations. Would you like me to propose a detailed design?"
```

### Guidelines for Number of Brokers per BrokerManager

**Recommended**: 2-5 brokers
**Acceptable**: 6-8 brokers (if sufficient error handling is implemented)
**Not Recommended**: 9+ brokers

These guidelines are criteria that only advanced users who fully understand Kraken Broker's performance can appropriately judge.

### Broker Division Design Guidelines

#### Design Flexibility

**Important**: Kraken Broker has no clear recommended criteria for how custom brokers should be divided functionally. Design is entirely left to use cases and developer judgment.

Both of the following approaches are valid:

#### Approach 1: Single Large Broker

An approach that processes requests from all `collector_name`s in one large broker.

```python
class UnifiedBroker(Broker):
    """Unified broker that processes all data sources"""

    def __init__(self):
        self.influx = InfluxDbAdapter()
        self.slack = SlackAdapter()
        self.redis = RedisAdapter()

    async def on(self, request, response):
        # Branch by collector_name or metadata
        if request.collector_name == "webhook":
            return await self._handle_temperature(request)
        elif request.collector_name == "camera":
            return await self._handle_camera(request)
        elif request.collector_name == "mqtt":
            return await self._handle_heartbeat(request)
        else:
            return self.build_response_message(
                collector_name=request.collector_name,
                content_type="text/plain",
                metadata="{}",
                payload=bytes([0x00])
            )

    async def _handle_temperature(self, request):
        # Process temperature sensor data
        pass

    async def _handle_camera(self, request):
        # Process camera data
        pass

    async def _handle_heartbeat(self, request):
        # Process health check
        pass
```

**Advantages**:
- Centralized code management
- Easy to reuse common logic
- Simple deployment

**Use Cases**:
- Simple IoT systems
- When there is a lot of common processing logic
- Small number of data sources

#### Approach 2: Multiple Small Brokers

An approach that creates multiple dedicated brokers according to `collector_name` or metadata content.

```python
# Temperature sensor dedicated broker
class TemperatureBroker(Broker):
    def __init__(self):
        self.influx = InfluxDbAdapter()

    async def on(self, request, response):
        if request.collector_name != "webhook":
            # Return Simple Response for non-target data
            return self.build_response_message(
                collector_name=request.collector_name,
                content_type="text/plain",
                metadata="{}",
                payload=bytes([0x00])
            )

        # Process temperature data
        data = json.loads(request.payload.decode('utf-8'))
        # ... Save to InfluxDB
        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="application/json",
            metadata=json.dumps({"saved": True}),
            payload=b""
        )

# Camera data dedicated broker
class CameraBroker(Broker):
    def __init__(self):
        self.s3 = S3Adapter()

    async def on(self, request, response):
        if request.collector_name != "camera":
            return self.build_response_message(
                collector_name=request.collector_name,
                content_type="text/plain",
                metadata="{}",
                payload=bytes([0x00])
            )

        # Process image data and upload to S3
        # ...
        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="application/json",
            metadata=json.dumps({"uploaded": True}),
            payload=b""
        )

# Alert notification dedicated broker
class AlertBroker(Broker):
    def __init__(self):
        self.slack = SlackAdapter()

    async def on(self, request, response):
        # Monitor all requests and notify based on conditions
        metadata = json.loads(request.metadata)
        if metadata.get("alert_level") == "critical":
            self.slack.send(SlackPayload(
                channel="#critical-alerts",
                username="Kraken Alert",
                text=f"Critical alert from {request.collector_name}"
            ))

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="text/plain",
            metadata="{}",
            payload=bytes([0x00])
        )
```

**Advantages**:
- **Strength of asynchronous/parallel processing**: Each broker executes independently in parallel
- **Data-driven design**: Specialized processing according to data type and content
- **Loose coupling**: Brokers are independent, limiting the scope of impact of changes
- **Clear responsibilities**: Each broker's role is clear
- **Individual testing**: Independent testing possible for each broker

**Use Cases**:
- When there are multiple data sources
- When processing logic differs significantly for each data source
- When you want to leverage data-driven parallel processing
- Design with scale-out in mind

#### Leveraging Data-Driven and Asynchronous Execution Strengths

Kraken Broker's greatest feature is that **multiple brokers operate asynchronously in a data-driven manner**. Generative AI should propose implementations that leverage this strength to users.

**Usage Example**:

```python
# Multiple brokers process the same request in parallel

# 1. Data storage broker
class DataStorageBroker(Broker):
    async def on(self, request, response):
        # Save to InfluxDB
        await self._save_to_influxdb(request)
        return self.build_response_message(...)

# 2. Statistics processing broker
class StatisticsBroker(Broker):
    async def on(self, request, response):
        # Update real-time statistics
        await self._update_statistics(request)
        return self.build_response_message(...)

# 3. Alert monitoring broker
class MonitoringBroker(Broker):
    async def on(self, request, response):
        # Check thresholds and alert
        await self._check_thresholds(request)
        return self.build_response_message(...)

# These 3 brokers execute in parallel for the same request
# Each broker operates independently without affecting each other
```

#### AI Agent Proposal Guidelines

For user requirements, propose optimal designs from the following perspectives:

1. **Number of data sources**: Unified broker if few, split if many
2. **Processing complexity**: Unified if simple, split if complex
3. **Scalability**: Consider splitting with future scale in mind
4. **Maintainability**: Splitting is advantageous for team development
5. **Leveraging parallel processing**: Recommend splitting if data-driven processing is needed

**Dialogue Example**:

```
User: "I want to process 3 data sources: temperature sensor, humidity sensor, and camera"

AI Recommended Response:
"For 3 data sources, two approaches are possible:

Approach 1: Unified Broker (Simple)
- Process all data sources in one broker
- Code is consolidated in one place, easy to reuse common logic
- Suitable for small-scale systems

Approach 2: Dedicated Brokers (Data-Driven - Recommended)
- Create dedicated brokers for each data source (TemperatureBroker, HumidityBroker, CameraBroker)
- Each broker executes in parallel, enabling data-driven processing
- Easy to handle future scaling and feature additions
- Maximally leverages Kraken Broker's asynchronous/parallel processing strengths

Based on your requirements, I recommend Approach 2. Reasons:
- Camera data requires image processing, which differs significantly from other sensors
- Parallel execution of each data source's processing improves overall throughput
- When adding new sensors in the future, minimal impact on existing code

Would you like me to propose detailed implementation examples?"
```

### Summary: Design Freedom

- **No clear criteria**: Broker division method is completely free
- **Both approaches are valid**: Both unified and split are appropriate depending on use case
- **Leverage strengths**: Recommend designs that leverage asynchronous and data-driven processing
- **AI's role**: Propose optimal designs according to user requirements and present multiple options

## Directory Structure

```
kraken_broker_python/
├── src/
│   ├── main.py                 # gRPC server entry point
│   ├── broker_manager.py       # Broker management class
│   │
│   ├── lib/
│   │   ├── broker.py           # Broker base class (must inherit)
│   │   ├── config_manager.py   # Environment variable management
│   │   ├── kraken_pb2.py       # gRPC auto-generated code
│   │   └── kraken_pb2_grpc.py
│   │
│   ├── brokers/                # Custom broker directory
│   │   ├── simple_broker.py    # Basic example
│   │   ├── heartbeat_broker.py # Health check example
│   │   └── camera_broker.py    # Image processing example
│   │
│   ├── adapters/               # External service integration adapters
│   │   ├── slack.py            # Slack notifications
│   │   ├── influxdb.py         # InfluxDB write
│   │   ├── redis.py            # Redis operations
│   │   ├── mongodb.py          # MongoDB operations
│   │   └── websocket.py        # WebSocket communication
│   │
│   └── helpers/                # Custom helper functions
│
├── proto/
│   └── kraken.proto            # gRPC definition file
│
└── requirements.txt
```

## Custom Broker Development Steps

### Step 1: Create Broker Class

Create a new file in `src/brokers/`.

```python
# src/brokers/my_custom_broker.py
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from lib import kraken_pb2
from lib.broker import Broker

logger = logging.getLogger(__name__)

class MyCustomBroker(Broker):
    """Custom broker description"""

    RESPONSE_CONTENT_TYPE = "application/json"  # or "text/plain"

    def __init__(self) -> None:
        self.name = "MyCustomBroker"
        # Initialize adapters as needed
        # self.slack = SlackAdapter()

    async def on(
        self,
        request: kraken_pb2.KrakenRequest,
        response: kraken_pb2.KrakenResponse,
    ) -> kraken_pb2.KrakenResponse:
        """
        Process request and return response

        Args:
            request: Request from Collector
            response: Response object (often unused)

        Returns:
            KrakenResponse (always return. Avoid None)
        """
        logger.debug(
            "MyCustomBroker processing collector=%s metadata=%s",
            request.collector_name,
            request.metadata,
        )

        # Parse metadata
        metadata = self._parse_metadata(request.metadata)
        if metadata is None:
            # Return Simple Response even on error (recommended)
            return self.build_response_message(
                collector_name=request.collector_name or "unknown",
                content_type="text/plain",
                metadata="{}",
                payload=bytes([0x00])
            )

        # Process payload
        # request.payload is bytes type

        # Execute business logic
        result = self._process_data(request.payload, metadata)

        # Build response
        kraken_response = self.build_response_message(
            collector_name=request.collector_name or "unknown",
            content_type=self.RESPONSE_CONTENT_TYPE,
            metadata=self._build_response_metadata(metadata),
            payload=result,
        )

        return kraken_response

    def _parse_metadata(self, metadata_json: str) -> Optional[dict[str, Any]]:
        """Parse and validate metadata"""
        if not metadata_json:
            return {}
        try:
            return json.loads(metadata_json)
        except json.JSONDecodeError as exc:
            logger.warning("Invalid metadata JSON: %s", exc)
            return None

    def _process_data(self, payload: bytes, metadata: dict[str, Any]) -> bytes:
        """Data processing logic"""
        # Implement your custom processing here
        return b""

    @classmethod
    def _build_response_metadata(cls, request_metadata: dict[str, Any]) -> str:
        """Build response metadata"""
        response_meta = {
            "response_type": "custom",
            "source_broker": cls.__name__,
        }
        return json.dumps(response_meta)
```

### Step 2: Register with BrokerManager

Edit `src/broker_manager.py` to register the broker.

```python
# src/broker_manager.py
from brokers.my_custom_broker import MyCustomBroker

class BrokerManager:
    def __init__(self) -> None:
        self._brokers: list[Broker] = [
            SimpleBroker(),
            MyCustomBroker(),  # Add
            # ...
        ]
```

### Step 3: Configure Environment Variables (if needed)

If new environment variables are needed, add them to `src/lib/config_manager.py`.

```python
# src/lib/config_manager.py
self.param_names = [
    # ...
    "KRAKENB_MYCUSTOM_API_KEY",  # Add
]
```

### Step 4: Test and Launch

```bash
# Set environment variables
export PYTHONDONTWRITEBYTECODE=1
export KRAKENB_DEBUG=1
export KRAKENB_GRPC_HOST=[::]:50051
export KRAKENB_MYCUSTOM_API_KEY=your_api_key

# Launch broker
python ./src/main.py
```

## Implementation Patterns and Best Practices

### Pattern 1: Simple Logging Broker

```python
# src/brokers/simple_broker.py:14
class SimpleBroker(Broker):
    async def on(self, request, response):
        logger.debug("Received: %s", request.payload)

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="text/plain",
            metadata="{}",
            payload=bytes([0x00]),
        )
```

### Pattern 2: External Service Integration Broker

```python
from adapters.slack import SlackAdapter, SlackPayload

class NotificationBroker(Broker):
    def __init__(self):
        self.slack = SlackAdapter()

    async def on(self, request, response):
        metadata = json.loads(request.metadata)

        # Slack notification
        self.slack.send(SlackPayload(
            channel="#iot-alerts",
            username="Kraken Broker",
            text=f"Data received from {request.collector_name}"
        ))

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="text/plain",
            metadata=json.dumps({"notified": True}),
            payload=b"",
        )
```

### Pattern 3: Database Storage Broker

```python
from adapters.influxdb import InfluxDbAdapter

class InfluxBroker(Broker):
    def __init__(self):
        self.influx = InfluxDbAdapter()

    async def on(self, request, response):
        data = json.loads(request.payload.decode('utf-8'))

        # Write to InfluxDB
        point = {
            "measurement": request.collector_name,
            "tags": {"location": data.get("location")},
            "fields": {"temperature": float(data.get("temp"))}
        }
        # write_api = self.influx.client.write_api()
        # write_api.write(bucket=self.influx.bucket, record=point)

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="application/json",
            metadata=json.dumps({"saved": True}),
            payload=b"",
        )
```

### Pattern 4: Conditional Branch Broker

```python
class ConditionalBroker(Broker):
    async def on(self, request, response):
        # Process specific collector only (return Simple Response for others)
        if request.collector_name != "webhook":
            # Recommended: Return Simple Response instead of None
            return self.build_response_message(
                collector_name=request.collector_name,
                content_type="text/plain",
                metadata="{}",
                payload=bytes([0x00])
            )

        metadata = json.loads(request.metadata)
        data = json.loads(request.payload.decode('utf-8'))
        temp = float(data.get("temp", 0))

        # Threshold check
        if temp > 30.0:
            # Alert processing
            logger.warning("High temperature detected: %s", temp)

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="application/json",
            metadata=json.dumps({"checked": True}),
            payload=b"",
        )
```

### Pattern 5: Binary Data Processing (Images, etc.)

```python
# src/brokers/camera_broker.py:19
import numpy as np
from PIL import Image

class CameraBroker(Broker):
    async def on(self, request, response):
        metadata = json.loads(request.metadata)
        width = metadata.get('width', 640)
        height = metadata.get('height', 480)

        # Convert RGB binary data to numpy array
        rgb_array = np.frombuffer(request.payload, dtype=np.uint8)
        rgb_array = rgb_array.reshape((height, width, 3))

        # Save as PIL Image
        image = Image.fromarray(rgb_array, 'RGB')
        image.save("output.jpg", 'JPEG', quality=85)

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="text/plain",
            metadata=json.dumps({"saved_image": "output.jpg"}),
            payload=bytes([0x00]),
        )
```

## Adapter Usage

### Existing Adapters

#### SlackAdapter (src/adapters/slack.py)

```python
from adapters.slack import SlackAdapter, SlackPayload

slack = SlackAdapter()
slack.send(SlackPayload(
    channel="#alerts",
    username="Bot",
    text="Message"
))
```

#### RedisAdapter (src/adapters/redis.py)

```python
from adapters.redis import RedisAdapter

redis_client = RedisAdapter()
# redis_client.client.set("key", "value")
# redis_client.client.get("key")
```

#### InfluxDbAdapter (src/adapters/influxdb.py)

```python
from adapters.influxdb import InfluxDbAdapter

influx = InfluxDbAdapter()
# write_api = influx.client.write_api()
# write_api.write(bucket=influx.bucket, record=point)
```

### Creating Custom Adapters

```python
# src/adapters/my_service.py
import logging
from lib.config_manager import ConfigManager

class MyServiceAdapter:
    def __init__(self):
        self.config = ConfigManager().get()
        self.api_key = self.config["KRAKENB_MYSERVICE_API_KEY"]
        # Initialize client

    def send_data(self, data: dict) -> None:
        try:
            # API call
            pass
        except Exception as e:
            logging.error("MyService error: %s", e)
```

## Environment Variables

### Standard Environment Variables (src/lib/config_manager.py:7)

| Environment Variable | Purpose |
|---------------------|---------|
| `KRAKENB_DEBUG` | Debug mode (0 or 1) |
| `KRAKENB_GRPC_HOST` | gRPC server address (e.g., `[::]:50051`) |
| `KRAKENB_SLACK_URL` | Slack Webhook URL |
| `KRAKENB_INFLUXDB_HOST` | InfluxDB host URL |
| `KRAKENB_INFLUXDB_API_TOKEN` | InfluxDB API Token |
| `KRAKENB_INFLUXDB_ORG` | InfluxDB Organization |
| `KRAKENB_INFLUXDB_BUCKET` | InfluxDB Bucket |
| `KRAKENB_REDIS_HOST` | Redis host |
| `KRAKENB_REDIS_PORT` | Redis port |
| `KRAKENB_REDIS_DB` | Redis DB number |
| `KRAKENB_REDIS_USER` | Redis username |
| `KRAKENB_REDIS_PASSWORD` | Redis password |
| `KRAKENB_MONGODB_HOST` | MongoDB host URL |
| `KRAKENB_WEBSOCKET_URL` | WebSocket server URL |

### Adding Custom Environment Variables

1. Add to `param_names` list in `src/lib/config_manager.py`
2. Set with `export KRAKENB_YOUR_VARIABLE=value`
3. Retrieve in brokers or adapters with `ConfigManager().get()["KRAKENB_YOUR_VARIABLE"]`

## Debugging and Testing

### Log Output

```python
import logging

logger = logging.getLogger(__name__)

# Debug log
logger.debug("Processing request: %s", request.collector_name)

# Warning
logger.warning("Invalid data format: %s", data)

# Error
logger.error("Failed to process: %s", exc)
```

### Sending Test Data

To test without Kraken Collector, use a gRPC client.

```python
# Refer to src/test_grpc_client.py for testing
```

Or send data to Collector with curl:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"id":"101", "name":"sensor", "temp":"25.6"}' \
  http://localhost:3000/webhook
```

## Common Implementation Scenarios

### Scenario 1: Sensor Data Threshold Monitoring

```python
class ThresholdMonitorBroker(Broker):
    THRESHOLD = 30.0

    def __init__(self):
        # Initialize adapter in __init__ (recommended)
        self.slack = SlackAdapter()

    async def on(self, request, response):
        data = json.loads(request.payload.decode('utf-8'))
        value = float(data.get("value", 0))

        if value > self.THRESHOLD:
            # Send alert
            self.slack.send(SlackPayload(
                channel="#alerts",
                username="Monitor",
                text=f"Threshold exceeded: {value}"
            ))

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="application/json",
            metadata=json.dumps({"threshold_checked": True}),
            payload=b"",
        )
```

### Scenario 2: Data Aggregation and Batch Processing

```python
class BatchProcessingBroker(Broker):
    def __init__(self):
        self.buffer = []
        self.batch_size = 10

    async def on(self, request, response):
        data = json.loads(request.payload.decode('utf-8'))
        self.buffer.append(data)

        if len(self.buffer) >= self.batch_size:
            # Execute batch processing
            self._process_batch(self.buffer)
            self.buffer = []

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="text/plain",
            metadata=json.dumps({"buffered": True}),
            payload=b"",
        )

    def _process_batch(self, batch):
        logger.info("Processing batch of %d items", len(batch))
        # Batch processing logic
```

### Scenario 3: Data Transformation and Forwarding

```python
class DataTransformBroker(Broker):
    async def on(self, request, response):
        # Parse input data
        raw_data = json.loads(request.payload.decode('utf-8'))

        # Transform data
        transformed = {
            "timestamp": raw_data.get("ts"),
            "sensor_id": raw_data.get("id"),
            "measurements": {
                "temperature": float(raw_data.get("temp")),
                "humidity": float(raw_data.get("hum"))
            }
        }

        # Forward to other services
        # api.send(transformed)

        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="application/json",
            metadata=json.dumps({"transformed": True}),
            payload=json.dumps(transformed).encode('utf-8'),
        )
```

## Troubleshooting

### Broker Not Executing

1. Check if correctly registered in `broker_manager.py`
2. Check logs for errors in `__init__`
3. Check for import errors

### No Response Returned

1. Verify `on()` method always returns `KrakenResponse` (avoid `None`)
2. Check correct usage of `build_response_message()`
3. Verify collector_name is not empty (src/brokers/simple_broker.py:43)
4. Check Simple Response is returned even on errors

### Adapter Not Working

1. Verify environment variables are correctly set
2. Check if `ConfigManager().get()` returns None
3. Check network connection and credentials

## Best Practices

### Critical Principles

1. **Initialize Adapters**: Custom brokers must initialize adapters and external libraries in `__init__()`
   ```python
   def __init__(self):
       self.slack = SlackAdapter()  # Initialize here
       self.redis = RedisAdapter()
   ```

2. **Always Return KrakenResponse**: The `on()` method should return `KrakenResponse` unless there's a special reason (not `None`)
   - Reason: To ensure Kraken Collector (gRPC client) can reliably receive responses
   - Even when skipping processing, returning Simple Response is recommended

3. **Recommend Simple Response**: When there are no special needs, returning Simple Response is recommended
   ```python
   return self.build_response_message(
       collector_name=request.collector_name,
       content_type="text/plain",
       metadata="{}",
       payload=bytes([0x00])
   )
   ```

4. **Control via KrakenResponse**: `KrakenResponse`'s `payload` and `metadata` can control Kraken Collector's behavior in some cases
   - Set appropriate values when custom control is needed
   - Simple Response is sufficient when not needed

### Other Recommendations

5. **Error Handling**: Catch exceptions, log them, and return Simple Response
6. **Type Hints**: Add type hints to function arguments and return values
7. **Log Output**: Record start, success, and failure of processing
8. **Metadata Validation**: Handle JSON parse errors in _parse_metadata()
9. **Asynchronous Processing**: Always define on() method with `async def`
10. **Helper Methods**: Split complex processing into private methods with _ prefix
11. **Constant Definition**: Define constants like RESPONSE_CONTENT_TYPE as class variables

## Distinguishing KrakenResponse and None

### Basic Principle

The return type of the `on()` method is `Optional[KrakenResponse]`, but **unless there is a special reason, you should always return `KrakenResponse`**.

### Why Return KrakenResponse?

- Kraken Collector (gRPC client) always expects a response to requests
- Returning `None` can make gRPC communication unstable
- Returning Simple Response ensures safe and predictable operation

### Recommended Pattern

```python
# ✅ Recommended: Return Simple Response even on errors
async def on(self, request, response):
    try:
        # Processing
        if not self._validate(request):
            # Return response even on validation failure
            return self.build_response_message(
                collector_name=request.collector_name,
                content_type="text/plain",
                metadata="{}",
                payload=bytes([0x00])
            )

        # Normal processing
        result = self._process(request)
        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="application/json",
            metadata=json.dumps({"status": "success"}),
            payload=result
        )
    except Exception as e:
        logger.error("Processing failed: %s", e)
        # Return Simple Response even on exceptions
        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="text/plain",
            metadata="{}",
            payload=bytes([0x00])
        )

# ❌ Not Recommended: Return None
async def on(self, request, response):
    if not self._validate(request):
        return None  # Should be avoided
    # ...
```

### What is Simple Response?

Simple Response is a response with minimal information:

```python
self.build_response_message(
    collector_name=request.collector_name,
    content_type="text/plain",
    metadata="{}",           # Empty JSON object
    payload=bytes([0x00])    # Single null byte
)
```

### When to Use Simple Response

- When an error occurs
- When validation fails
- When you want to skip processing (non-target data in conditional branching)
- When there is no specific information to return to Collector

### Cases Where Returning None is Acceptable (Exceptional)

Consider returning `None` only in the following special cases:

#### 1. When Multiple Brokers Execute in Parallel and Only Specific Brokers Return Responses

When multiple brokers execute in parallel and only specific brokers are designed to return responses.

#### 2. For Debug/Test Purposes to Intentionally Generate Collector Error Logs (Important)

By returning `None`, you can **intentionally generate an error in the Collector's log stating "response to request was not returned properly"**. This is an irregular usage useful for debugging and testing.

```python
# For debugging: Intentionally return None to check Collector's error log
async def on(self, request, response):
    try:
        result = self._critical_process(request)
        return self.build_response_message(
            collector_name=request.collector_name,
            content_type="application/json",
            metadata=json.dumps({"status": "success"}),
            payload=result
        )
    except CriticalError as e:
        logger.error("Critical error occurred: %s", e)
        # For debugging: Return None to check error log on Collector side
        # Return Simple Response in production
        return None  # Explicit error is logged in Collector
```

**Use Cases**:
- When you want to track problems in Collector-side logs when errors occur in broker processing
- When you want to test gRPC communication error handling in development/test environments
- When you want to verify error propagation under specific conditions

**Important**: In production environments, returning Simple Response is recommended whenever possible. `return None` is an irregular means only for debugging/testing purposes.

## Reference Links

- **README**: [README-ja.md](./README-ja.md) - Project overview
- **Kraken Collector**: https://github.com/bathtimefish/kraken_collector
- **Key Files**:
  - Broker base class: `src/lib/broker.py:10`
  - BrokerManager: `src/broker_manager.py:14`
  - gRPC server: `src/main.py:80`
  - ConfigManager: `src/lib/config_manager.py:27`
- **Implementation Examples**:
  - SimpleBroker: `src/brokers/simple_broker.py:14`
  - HeartbeatBroker: `src/brokers/heartbeat_broker.py:12`
  - CameraBroker: `src/brokers/camera_broker.py:19`

## Summary

By following this guide, you can develop custom brokers for Kraken Broker using generative AI.

### Basic Development Steps

1. Create a new file in `src/brokers/`
2. Inherit from `Broker` class
3. Initialize adapters and external libraries in `__init__()`
4. Implement `async def on()` method (always return `KrakenResponse`)
5. Register in `broker_manager.py`
6. Add environment variables as needed
7. Test and launch

### 3 Critical Principles to Follow

1. **Initialize adapters in `__init__()`**
2. **`on()` method must always return `KrakenResponse` (avoid `None`)**
3. **Unless there's a special reason, return Simple Response (`metadata="{}"`, `payload=bytes([0x00])`)**

Following these principles ensures stable communication between Kraken Collector and Broker and achieves predictable operation.

### Critical Considerations When Scaling

**Do not register a large number of brokers in one BrokerManager**

- Recommended: 2-5 brokers/instance
- Acceptable: 6-8 brokers (if sufficient error handling exists)
- Not Recommended: 9+ brokers

When many brokers are needed, **launch multiple kraken_broker instances for distributed operation**. Registering many brokers in one instance risks system-wide instability.

### AI Agent Responsibilities

When users request large numbers of brokers, always explain the risks and suggest multi-instance operations. Refer to the "Scaling and Multiple Broker Operations" section for details.

For questions or additional features, refer to existing implementation examples.
