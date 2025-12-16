#  Copyright 2018-Present The CloudEvents Authors
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from dataclasses import dataclass
from typing import Any, Callable, Final

from cloudevents.core.base import BaseCloudEvent
from cloudevents.core.bindings.common import (
    CONTENT_TYPE_HEADER,
    DATACONTENTTYPE_ATTR,
    decode_header_value,
    encode_header_value,
)
from cloudevents.core.formats.base import Format
from cloudevents.core.formats.json import JSONFormat
from cloudevents.core.v1.event import CloudEvent

CE_PREFIX: Final[str] = "ce_"
PARTITIONKEY_ATTR: Final[str] = "partitionkey"

KeyMapper = Callable[[BaseCloudEvent], str | bytes | None]


@dataclass(frozen=True)
class KafkaMessage:
    """
    Represents a Kafka message containing CloudEvent data.

    This dataclass encapsulates Kafka message components for transmitting CloudEvents
    over Kafka. It is immutable to prevent accidental modifications and works with
    any Kafka client library (kafka-python, confluent-kafka, etc.).

    Attributes:
        headers: Kafka message headers as bytes (per Kafka protocol requirement)
        key: Optional Kafka message key for partitioning
        value: Kafka message value/payload as bytes
    """

    headers: dict[str, bytes]
    key: str | bytes | None
    value: bytes


def _default_key_mapper(event: BaseCloudEvent) -> str | bytes | None:
    """
    Default key mapper that extracts the partitionkey extension attribute.

    :param event: The CloudEvent to extract key from
    :return: The partitionkey extension attribute value, or None if not present
    """
    value = event.get_extension(PARTITIONKEY_ATTR)
    # Type narrowing: get_extension returns Any, but we know partitionkey should be str/bytes/None
    return value if value is None or isinstance(value, (str, bytes)) else str(value)


def to_binary(
    event: BaseCloudEvent,
    event_format: Format,
    key_mapper: KeyMapper | None = None,
) -> KafkaMessage:
    """
    Convert a CloudEvent to Kafka binary content mode.

    In binary mode, CloudEvent attributes are mapped to Kafka headers with the 'ce_' prefix,
    except for 'datacontenttype' which maps to the 'content-type' header. The event data
    is placed in the Kafka message value. The message key is derived from the partitionkey
    extension attribute or a custom key_mapper function.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = to_binary(event, JSONFormat())
        >>> # message.headers = {"ce_type": b"com.example.test", "ce_source": b"/test", ...}
        >>> # message.value = b'{"message": "Hello"}'
        >>> # message.key = None

    :param event: The CloudEvent to convert
    :param event_format: Format implementation for data serialization
    :param key_mapper: Optional function to extract message key from event (defaults to partitionkey attribute)
    :return: KafkaMessage with ce_-prefixed headers and event data as value
    """
    headers: dict[str, bytes] = {}
    attributes = event.get_attributes()

    # Apply key mapper
    if key_mapper is None:
        key_mapper = _default_key_mapper
    message_key = key_mapper(event)

    for attr_name, attr_value in attributes.items():
        if attr_value is None:
            continue

        # Skip partitionkey - it goes in the message key, not headers
        if attr_name == PARTITIONKEY_ATTR:
            continue

        if attr_name == DATACONTENTTYPE_ATTR:
            headers[CONTENT_TYPE_HEADER] = str(attr_value).encode("utf-8")
        else:
            header_name = f"{CE_PREFIX}{attr_name}"
            headers[header_name] = encode_header_value(attr_value).encode("utf-8")

    data = event.get_data()
    datacontenttype = attributes.get(DATACONTENTTYPE_ATTR)
    value = event_format.write_data(data, datacontenttype)

    return KafkaMessage(headers=headers, key=message_key, value=value)


def from_binary(
    message: KafkaMessage,
    event_format: Format,
    event_factory: Callable[
        [dict[str, Any], dict[str, Any] | str | bytes | None], BaseCloudEvent
    ],
) -> BaseCloudEvent:
    """
    Parse a Kafka binary content mode message to a CloudEvent.

    Extracts CloudEvent attributes from ce_-prefixed Kafka headers and treats the
    'content-type' header as the 'datacontenttype' attribute. The Kafka message value
    is parsed as event data according to the content type. If the message has a key,
    it is added as the 'partitionkey' extension attribute.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> message = KafkaMessage(
        ...     headers={"ce_type": b"com.example.test", "ce_source": b"/test",
        ...              "ce_id": b"123", "ce_specversion": b"1.0"},
        ...     key=b"partition-key-123",
        ...     value=b'{"message": "Hello"}'
        ... )
        >>> event = from_binary(message, JSONFormat(), CloudEvent)

    :param message: KafkaMessage to parse
    :param event_format: Format implementation for data deserialization
    :param event_factory: Factory function to create CloudEvent instances
    :return: CloudEvent instance
    """
    attributes: dict[str, Any] = {}

    for header_name, header_value_bytes in message.headers.items():
        header_value = header_value_bytes.decode("utf-8")

        normalized_name = header_name.lower()

        if normalized_name.startswith(CE_PREFIX):
            attr_name = normalized_name[len(CE_PREFIX) :]
            attributes[attr_name] = decode_header_value(attr_name, header_value)
        elif normalized_name == CONTENT_TYPE_HEADER:
            attributes[DATACONTENTTYPE_ATTR] = header_value

    # If message has a key, add it as partitionkey extension attribute
    if message.key is not None:
        key_value = (
            message.key.decode("utf-8")
            if isinstance(message.key, bytes)
            else message.key
        )
        attributes[PARTITIONKEY_ATTR] = key_value

    datacontenttype = attributes.get(DATACONTENTTYPE_ATTR)
    data = event_format.read_data(message.value, datacontenttype)

    return event_factory(attributes, data)


def to_structured(
    event: BaseCloudEvent,
    event_format: Format,
    key_mapper: KeyMapper | None = None,
) -> KafkaMessage:
    """
    Convert a CloudEvent to Kafka structured content mode.

    In structured mode, the entire CloudEvent (attributes and data) is serialized
    into the Kafka message value using the specified format. The content-type header
    is set to the format's media type. The message key is derived from the partitionkey
    extension attribute or a custom key_mapper function.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = to_structured(event, JSONFormat())
        >>> # message.headers = {"content-type": b"application/cloudevents+json"}
        >>> # message.value = b'{"type": "com.example.test", "source": "/test", ...}'

    :param event: The CloudEvent to convert
    :param event_format: Format implementation for serialization
    :param key_mapper: Optional function to extract message key from event (defaults to partitionkey attribute)
    :return: KafkaMessage with structured content in value
    """
    content_type = event_format.get_content_type()

    headers = {CONTENT_TYPE_HEADER: content_type.encode("utf-8")}

    value = event_format.write(event)

    if key_mapper is None:
        key_mapper = _default_key_mapper
    message_key = key_mapper(event)

    return KafkaMessage(headers=headers, key=message_key, value=value)


def from_structured(
    message: KafkaMessage,
    event_format: Format,
    event_factory: Callable[
        [dict[str, Any], dict[str, Any] | str | bytes | None], BaseCloudEvent
    ],
) -> BaseCloudEvent:
    """
    Parse a Kafka structured content mode message to a CloudEvent.

    Deserializes the CloudEvent from the Kafka message value using the specified format.
    Any ce_-prefixed headers are ignored as the value contains all event metadata.
    If the message has a key, it is added as the 'partitionkey' extension attribute.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> message = KafkaMessage(
        ...     headers={"content-type": b"application/cloudevents+json"},
        ...     key=b"partition-key-123",
        ...     value=b'{"type": "com.example.test", "source": "/test", ...}'
        ... )
        >>> event = from_structured(message, JSONFormat(), CloudEvent)

    :param message: KafkaMessage to parse
    :param event_format: Format implementation for deserialization
    :param event_factory: Factory function to create CloudEvent instances
    :return: CloudEvent instance
    """
    event = event_format.read(event_factory, message.value)

    # If message has a key, we need to add it as partitionkey extension attribute
    # Since the event is already created, we need to reconstruct it with the additional attribute
    if message.key is not None:
        key_value = (
            message.key.decode("utf-8")
            if isinstance(message.key, bytes)
            else message.key
        )
        attributes = event.get_attributes()
        attributes[PARTITIONKEY_ATTR] = key_value
        data = event.get_data()
        event = event_factory(attributes, data)

    return event


def from_kafka(
    message: KafkaMessage,
    event_format: Format,
    event_factory: Callable[
        [dict[str, Any], dict[str, Any] | str | bytes | None], BaseCloudEvent
    ],
) -> BaseCloudEvent:
    """
    Parse a Kafka message to a CloudEvent with automatic mode detection.

    Automatically detects whether the message uses binary or structured content mode:
    - If any ce_ prefixed headers are present → binary mode
    - Otherwise → structured mode

    This function provides a convenient way to handle both content modes without
    requiring the caller to determine the mode beforehand.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> # Works with binary mode
        >>> binary_msg = KafkaMessage(
        ...     headers={"ce_type": b"com.example.test", ...},
        ...     key=None,
        ...     value=b'...'
        ... )
        >>> event1 = from_kafka(binary_msg, JSONFormat(), CloudEvent)
        >>>
        >>> # Also works with structured mode
        >>> structured_msg = KafkaMessage(
        ...     headers={"content-type": b"application/cloudevents+json"},
        ...     key=None,
        ...     value=b'{"type": "com.example.test", ...}'
        ... )
        >>> event2 = from_kafka(structured_msg, JSONFormat(), CloudEvent)

    :param message: KafkaMessage to parse
    :param event_format: Format implementation for deserialization
    :param event_factory: Factory function to create CloudEvent instances
    :return: CloudEvent instance
    """
    for header_name in message.headers.keys():
        if header_name.lower().startswith(CE_PREFIX):
            return from_binary(message, event_format, event_factory)

    return from_structured(message, event_format, event_factory)


def to_binary_event(
    event: BaseCloudEvent,
    event_format: Format | None = None,
    key_mapper: KeyMapper | None = None,
) -> KafkaMessage:
    """
    Convenience wrapper for to_binary with JSON format and CloudEvent as defaults.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.bindings import kafka
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = kafka.to_binary_event(event)

    :param event: The CloudEvent to convert
    :param event_format: Format implementation (defaults to JSONFormat)
    :param key_mapper: Optional function to extract message key from event
    :return: KafkaMessage with ce_-prefixed headers
    """
    if event_format is None:
        event_format = JSONFormat()
    return to_binary(event, event_format, key_mapper)


def from_binary_event(
    message: KafkaMessage,
    event_format: Format | None = None,
) -> BaseCloudEvent:
    """
    Convenience wrapper for from_binary with JSON format and CloudEvent as defaults.

    Example:
        >>> from cloudevents.core.bindings import kafka
        >>> event = kafka.from_binary_event(message)

    :param message: KafkaMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_binary(message, event_format, CloudEvent)


def to_structured_event(
    event: BaseCloudEvent,
    event_format: Format | None = None,
    key_mapper: KeyMapper | None = None,
) -> KafkaMessage:
    """
    Convenience wrapper for to_structured with JSON format as default.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.bindings import kafka
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = kafka.to_structured_event(event)

    :param event: The CloudEvent to convert
    :param event_format: Format implementation (defaults to JSONFormat)
    :param key_mapper: Optional function to extract message key from event
    :return: KafkaMessage with structured content
    """
    if event_format is None:
        event_format = JSONFormat()
    return to_structured(event, event_format, key_mapper)


def from_structured_event(
    message: KafkaMessage,
    event_format: Format | None = None,
) -> BaseCloudEvent:
    """
    Convenience wrapper for from_structured with JSON format and CloudEvent as defaults.

    Example:
        >>> from cloudevents.core.bindings import kafka
        >>> event = kafka.from_structured_event(message)

    :param message: KafkaMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_structured(message, event_format, CloudEvent)


def from_kafka_event(
    message: KafkaMessage,
    event_format: Format | None = None,
) -> BaseCloudEvent:
    """
    Convenience wrapper for from_kafka with JSON format and CloudEvent as defaults.
    Auto-detects binary or structured mode.

    Example:
        >>> from cloudevents.core.bindings import kafka
        >>> event = kafka.from_kafka_event(message)

    :param message: KafkaMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_kafka(message, event_format, CloudEvent)
