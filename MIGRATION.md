# Migrating from CloudEvents SDK v1 to v2

This guide covers the breaking changes and new patterns introduced in v2 of the CloudEvents Python SDK.

## Requirements

| | v1 | v2 |
|---|---|---|
| Python | 3.7+ | **3.10+** |
| Dependencies | varies (optional `pydantic` extra) | `python-dateutil>=2.8.2` only |

## Intermediate Step: `cloudevents.v1` Compatibility Layer

If you are not ready to migrate to the v2 core API, the `cloudevents.v1` package provides a drop-in compatibility layer that preserves the v1 API under a new namespace. This lets you unpin from the old top-level imports without rewriting your event-handling logic.

Swap the old top-level imports for their `cloudevents.v1.*` equivalents:

| Old import | Compat layer import |
|---|---|
| `from cloudevents.http import CloudEvent` | `from cloudevents.v1.http import CloudEvent` |
| `from cloudevents.http import from_http` | `from cloudevents.v1.http import from_http` |
| `from cloudevents.http import from_json` | `from cloudevents.v1.http import from_json` |
| `from cloudevents.http import from_dict` | `from cloudevents.v1.http import from_dict` |
| `from cloudevents.conversion import to_binary` | `from cloudevents.v1.http import to_binary` |
| `from cloudevents.conversion import to_structured` | `from cloudevents.v1.http import to_structured` |
| `from cloudevents.conversion import to_json` | `from cloudevents.v1.http import to_json` |
| `from cloudevents.conversion import to_dict` | `from cloudevents.v1.conversion import to_dict` |
| `from cloudevents.kafka import KafkaMessage` | `from cloudevents.v1.kafka import KafkaMessage` |
| `from cloudevents.kafka import to_binary` | `from cloudevents.v1.kafka import to_binary` |
| `from cloudevents.kafka import from_binary` | `from cloudevents.v1.kafka import from_binary` |
| `from cloudevents.pydantic import CloudEvent` | `from cloudevents.v1.pydantic import CloudEvent` |

The compat layer behaviour is identical to the old v1 SDK: events are dict-like and mutable, marshallers/unmarshallers are accepted as callables, and `is_binary`/`is_structured` helpers are still available. The compat layer does **not** enforce strict mypy and is not under the v2 validation rules.

When you are ready to move fully to v2, follow the rest of this guide.

## Architectural Changes

v2 is a ground-up rewrite with four fundamental shifts:

1. **Protocol-based design** -- `BaseCloudEvent` is a `Protocol`, not a base class. Events expose explicit getter methods instead of dict-like access.
2. **Explicit serialization** -- Implicit JSON handling with marshaller callbacks is replaced by a `Format` protocol. `JSONFormat` is the built-in implementation; you can write your own.
3. **Same auto-generated attributes** -- Like v1, v2 auto-generates `id` (UUID4), `time` (UTC now), and `specversion` (`"1.0"` or `"0.3"`) if omitted. Only `type` and `source` are strictly required.
4. **Strict validation** -- Events are validated at construction time. Extension attribute names must be 1-20 lowercase alphanumeric characters. `time` must be a timezone-aware `datetime`.

## Creating Events

**v1:**

```python
from cloudevents.http import CloudEvent

# id, specversion, and time are auto-generated
event = CloudEvent(
    {"type": "com.example.test", "source": "/myapp"},
    data={"message": "Hello"},
)
```

**v2:**

```python
from cloudevents.core.v1.event import CloudEvent

# id, specversion, and time are auto-generated (just like v1)
event = CloudEvent(
    attributes={"type": "com.example.test", "source": "/myapp"},
    data={"message": "Hello"},
)
```

## Accessing Event Attributes

v1 events were dict-like. v2 events use explicit getter methods and are immutable after construction.

**v1:**

```python
# Dict-like access
source = event["source"]
event["subject"] = "my-subject"
del event["subject"]

# Iteration
for attr_name in event:
    print(attr_name, event[attr_name])

# Membership test
if "subject" in event:
    pass
```

**v2:**

```python
# Explicit getters for required attributes
source = event.get_source()
event_type = event.get_type()
event_id = event.get_id()
specversion = event.get_specversion()

# Explicit getters for optional attributes (return None if absent)
subject = event.get_subject()
time = event.get_time()
datacontenttype = event.get_datacontenttype()
dataschema = event.get_dataschema()

# Extension attributes
custom_value = event.get_extension("myextension")

# All attributes as a dict
attrs = event.get_attributes()

# Data
data = event.get_data()
```

## HTTP Binding

### Serializing Events

**v1:**

```python
from cloudevents.conversion import to_binary, to_structured

# Returns a (headers, body) tuple
headers, body = to_binary(event)
headers, body = to_structured(event)
```

**v2:**

```python
from cloudevents.core.bindings.http import to_binary_event, to_structured_event

# Returns an HTTPMessage dataclass with .headers and .body
message = to_binary_event(event)
message = to_structured_event(event)

# Use in HTTP requests
requests.post(url, headers=message.headers, data=message.body)
```

If you need to pass a custom `Format`, use the lower-level functions:

```python
from cloudevents.core.bindings.http import to_binary, to_structured
from cloudevents.core.formats.json import JSONFormat

message = to_binary(event, event_format=JSONFormat())
message = to_structured(event, event_format=JSONFormat())
```

### Deserializing Events

**v1:**

```python
from cloudevents.http import from_http

# Auto-detects binary vs structured from headers
event = from_http(headers, body)
```

**v2:**

```python
from cloudevents.core.bindings.http import from_http_event, HTTPMessage

# Wrap raw headers/body into an HTTPMessage first
message = HTTPMessage(headers=headers, body=body)

# Auto-detects binary vs structured and spec version (v1.0 / v0.3)
event = from_http_event(message)
```

Or explicitly choose the content mode:

```python
from cloudevents.core.bindings.http import from_binary_event, from_structured_event

event = from_binary_event(message)
event = from_structured_event(message)
```

## Kafka Binding

### Serializing

**v1:**

```python
from cloudevents.kafka import to_binary, KafkaMessage

kafka_msg = to_binary(event)
# kafka_msg is a NamedTuple: .headers, .key, .value
```

**v2:**

```python
from cloudevents.core.bindings.kafka import to_binary_event, KafkaMessage

kafka_msg = to_binary_event(event)
# kafka_msg is a frozen dataclass: .headers, .key, .value

# Custom key mapping
kafka_msg = to_binary_event(
    event,
    key_mapper=lambda e: e.get_extension("partitionkey"),
)
```

### Deserializing

**v1:**

```python
from cloudevents.kafka import from_binary, KafkaMessage

msg = KafkaMessage(headers=headers, key=key, value=value)
event = from_binary(msg)
```

**v2:**

```python
from cloudevents.core.bindings.kafka import from_kafka_event, KafkaMessage

msg = KafkaMessage(headers=headers, key=key, value=value)

# Auto-detects binary vs structured and spec version
event = from_kafka_event(msg)
```

## AMQP Binding (New in v2)

v2 adds native AMQP 1.0 protocol binding support.

```python
from cloudevents.core.v1.event import CloudEvent
from cloudevents.core.bindings.amqp import (
    AMQPMessage,
    to_binary_event,
    from_amqp_event,
)

# Serialize: attributes go to application_properties with cloudEvents_ prefix
amqp_msg = to_binary_event(event)
# amqp_msg.properties              - AMQP message properties (e.g. content-type)
# amqp_msg.application_properties  - CloudEvent attributes
# amqp_msg.application_data        - event data as bytes

# Deserialize: auto-detects binary vs structured
event = from_amqp_event(amqp_msg)
```

## Custom Serialization Formats

**v1** used marshaller/unmarshaller callbacks:

```python
# v1: pass callbacks directly
headers, body = to_binary(event, data_marshaller=yaml.dump)
event = from_http(headers, body, data_unmarshaller=yaml.safe_load)
```

**v2** uses the `Format` protocol. Implement it to support non-JSON formats:

```python
from cloudevents.core.formats.base import Format
from cloudevents.core.base import BaseCloudEvent, EventFactory

class YAMLFormat:
    """Example custom format -- implement the Format protocol."""

    def read(
        self,
        event_factory: EventFactory | None,
        data: str | bytes,
    ) -> BaseCloudEvent:
        ...  # Parse YAML into attributes dict, call event_factory(attributes, data)

    def write(self, event: BaseCloudEvent) -> bytes:
        ...  # Serialize entire event to YAML bytes

    def write_data(
        self,
        data: dict | str | bytes | None,
        datacontenttype: str | None,
    ) -> bytes:
        ...  # Serialize just the data payload

    def read_data(
        self,
        body: bytes,
        datacontenttype: str | None,
    ) -> dict | str | bytes | None:
        ...  # Deserialize just the data payload

    def get_content_type(self) -> str:
        return "application/cloudevents+yaml"
```

Then use it with any binding:

```python
from cloudevents.core.bindings.http import to_binary

message = to_binary(event, event_format=YAMLFormat())
```

## Error Handling

v2 replaces v1's exception hierarchy with more granular, typed exceptions.

**v1:**

```python
from cloudevents.exceptions import (
    GenericException,
    MissingRequiredFields,
    InvalidRequiredFields,
    DataMarshallerError,
    DataUnmarshallerError,
)
```

**v2:**

```python
from cloudevents.core.exceptions import (
    BaseCloudEventException,          # Base for all CloudEvent errors
    CloudEventValidationError,        # Aggregated validation errors (raised on construction)
    MissingRequiredAttributeError,    # Missing required attribute (also a ValueError)
    InvalidAttributeTypeError,        # Wrong attribute type (also a TypeError)
    InvalidAttributeValueError,       # Invalid attribute value (also a ValueError)
    CustomExtensionAttributeError,    # Invalid extension name (also a ValueError)
)
```

`CloudEventValidationError` contains all validation failures at once:

```python
try:
    event = CloudEvent(attributes={"source": "/test"})  # missing type
except CloudEventValidationError as e:
    # e.errors is a dict[str, list[BaseCloudEventException]]
    for attr_name, errors in e.errors.items():
        print(f"{attr_name}: {errors}")
```

## Removed Features

| Feature | v1 | v2 Alternative |
|---|---|---|
| Pydantic integration | `from cloudevents.pydantic import CloudEvent` | Removed -- use the core `CloudEvent` directly |
| Dict-like event access | `event["source"]`, `event["x"] = y` | `event.get_source()`, `event.get_extension("x")` |
| `from_dict()` | `from cloudevents.http import from_dict` | Construct `CloudEvent(attributes=d)` directly |
| `to_dict()` | `from cloudevents.conversion import to_dict` | `event.get_attributes()` + `event.get_data()` |
| `from_json()` | `from cloudevents.http import from_json` | `JSONFormat().read(None, json_bytes)` |
| `to_json()` | `from cloudevents.conversion import to_json` | `JSONFormat().write(event)` |
| Custom marshallers | `data_marshaller=fn` / `data_unmarshaller=fn` | Implement the `Format` protocol |
| `is_binary()` / `is_structured()` | `from cloudevents.http import is_binary` | Mode is handled internally by `from_http_event()` |
| Deprecated helpers | `to_binary_http()`, `to_structured_http()` | `to_binary_event()`, `to_structured_event()` |

## Quick Reference: Import Mapping

| v1 Import | v2 Import |
|---|---|
| `cloudevents.http.CloudEvent` | `cloudevents.core.v1.event.CloudEvent` |
| `cloudevents.http.from_http` | `cloudevents.core.bindings.http.from_http_event` |
| `cloudevents.http.from_json` | `cloudevents.core.formats.json.JSONFormat().read` |
| `cloudevents.http.from_dict` | `cloudevents.core.v1.event.CloudEvent(attributes=...)` |
| `cloudevents.conversion.to_binary` | `cloudevents.core.bindings.http.to_binary_event` |
| `cloudevents.conversion.to_structured` | `cloudevents.core.bindings.http.to_structured_event` |
| `cloudevents.conversion.to_json` | `cloudevents.core.formats.json.JSONFormat().write` |
| `cloudevents.conversion.to_dict` | `event.get_attributes()` |
| `cloudevents.kafka.KafkaMessage` | `cloudevents.core.bindings.kafka.KafkaMessage` |
| `cloudevents.kafka.to_binary` | `cloudevents.core.bindings.kafka.to_binary_event` |
| `cloudevents.kafka.from_binary` | `cloudevents.core.bindings.kafka.from_binary_event` |
| `cloudevents.pydantic.CloudEvent` | Removed |
| `cloudevents.abstract.AnyCloudEvent` | `cloudevents.core.base.BaseCloudEvent` |

## CloudEvents Spec v0.3

Both v1 and v2 support CloudEvents spec v0.3. In v2, use the dedicated class:

```python
from cloudevents.core.v03.event import CloudEvent

event = CloudEvent(
    attributes={
        "type": "com.example.test",
        "source": "/myapp",
        "id": "123",
        "specversion": "0.3",
        "schemaurl": "https://example.com/schema",  # v0.3-specific (renamed to dataschema in v1.0)
    },
)
```

Binding functions auto-detect the spec version when deserializing, so no special handling is needed on the receiving side.
