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

"""
RabbitMQ Protocol Binding for CloudEvents.

Implements the RabbitMQ Protocol Binding specification:
https://github.com/knative-extensions/eventing-rabbitmq/blob/main/cloudevents-protocol-spec/spec.md
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final

from dateutil.parser import isoparse

from cloudevents.core.base import BaseCloudEvent, EventFactory
from cloudevents.core.bindings.common import (
    DATACONTENTTYPE_ATTR,
    TIME_ATTR,
    get_event_factory_for_version,
)
from cloudevents.core.formats.base import Format
from cloudevents.core.formats.json import JSONFormat
from cloudevents.core.spec import SPECVERSION_V1_0
from cloudevents.core.v1.event import CloudEvent

CE_PREFIX: Final[str] = "ce-"


@dataclass(frozen=True)
class RabbitMQMessage:
    """
    Represents a RabbitMQ message containing CloudEvent data.

    This dataclass encapsulates RabbitMQ message components for transmitting
    CloudEvents over RabbitMQ (AMQP 0-9-1). It is immutable to prevent accidental
    modifications and works with any RabbitMQ client library (pika, aio-pika, etc.).

    Attributes:
        headers: RabbitMQ message headers as string key-value pairs
        content_type: RabbitMQ BasicProperties content_type field
        body: Message body as bytes
    """

    headers: dict[str, str]
    content_type: str | None
    body: bytes


def to_binary(event: BaseCloudEvent, event_format: Format) -> RabbitMQMessage:
    """
    Convert a CloudEvent to RabbitMQ binary content mode.

    In binary mode, CloudEvent attributes are mapped to RabbitMQ message headers
    with the 'ce-' prefix, except for 'datacontenttype' which maps to the
    RabbitMQ content_type property. The event data is placed directly in the
    message body. All attribute values are encoded as strings.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = to_binary(event, JSONFormat())
        >>> # message.headers = {"ce-type": "com.example.test", ...}
        >>> # message.content_type = "application/json"
        >>> # message.body = b'{"message": "Hello"}'

    :param event: The CloudEvent to convert
    :param event_format: Format implementation for data serialization
    :return: RabbitMQMessage with CloudEvent attributes as headers
    """
    headers: dict[str, str] = {}
    content_type: str | None = None
    attributes = event.get_attributes()

    for attr_name, attr_value in attributes.items():
        if attr_value is None:
            continue

        if attr_name == DATACONTENTTYPE_ATTR:
            content_type = str(attr_value)
        else:
            header_name = f"{CE_PREFIX}{attr_name}"
            if isinstance(attr_value, datetime):
                s = attr_value.isoformat()
                if s.endswith("+00:00"):
                    s = s[:-6] + "Z"
                headers[header_name] = s
            else:
                headers[header_name] = str(attr_value)

    data = event.get_data()
    datacontenttype = attributes.get(DATACONTENTTYPE_ATTR)
    body = event_format.write_data(data, datacontenttype)

    return RabbitMQMessage(headers=headers, content_type=content_type, body=body)


def from_binary(
    message: RabbitMQMessage,
    event_format: Format,
    event_factory: EventFactory | None = None,
) -> BaseCloudEvent:
    """
    Parse a RabbitMQ binary content mode message to a CloudEvent.

    Auto-detects the CloudEvents version from the headers and uses the
    appropriate event factory if not explicitly provided.

    Extracts CloudEvent attributes from ce-prefixed RabbitMQ headers and treats
    the content_type property as the 'datacontenttype' attribute. The message
    body is parsed as event data according to the content type.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> message = RabbitMQMessage(
        ...     headers={
        ...         "ce-type": "com.example.test",
        ...         "ce-source": "/test",
        ...         "ce-id": "123",
        ...         "ce-specversion": "1.0"
        ...     },
        ...     content_type="application/json",
        ...     body=b'{"message": "Hello"}'
        ... )
        >>> event = from_binary(message, JSONFormat(), CloudEvent)

    :param message: RabbitMQMessage to parse
    :param event_format: Format implementation for data deserialization
    :param event_factory: Factory function to create CloudEvent instances
    :return: CloudEvent instance
    """
    attributes: dict[str, Any] = {}

    for header_name, header_value in message.headers.items():
        normalized_name = header_name.lower()

        if normalized_name.startswith(CE_PREFIX):
            attr_name = normalized_name[len(CE_PREFIX) :]
            if attr_name == TIME_ATTR:
                attributes[attr_name] = isoparse(header_value)
            else:
                attributes[attr_name] = header_value
        # Non-prefixed headers are ignored

    if message.content_type is not None:
        attributes[DATACONTENTTYPE_ATTR] = message.content_type

    # Auto-detect version if factory not provided
    if event_factory is None:
        specversion = attributes.get("specversion", SPECVERSION_V1_0)
        event_factory = get_event_factory_for_version(specversion)

    datacontenttype = attributes.get(DATACONTENTTYPE_ATTR)
    data = event_format.read_data(message.body, datacontenttype)

    return event_factory(attributes, data)


def to_structured(event: BaseCloudEvent, event_format: Format) -> RabbitMQMessage:
    """
    Convert a CloudEvent to RabbitMQ structured content mode.

    In structured mode, the entire CloudEvent (attributes and data) is serialized
    into the message body using the specified format. The content_type property is
    set to the format's media type (e.g., "application/cloudevents+json").

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = to_structured(event, JSONFormat())
        >>> # message.content_type = "application/cloudevents+json"
        >>> # message.body = b'{"type": "com.example.test", ...}'

    :param event: The CloudEvent to convert
    :param event_format: Format implementation for serialization
    :return: RabbitMQMessage with structured content in body
    """
    content_type = event_format.get_content_type()
    headers: dict[str, str] = {}
    body = event_format.write(event)

    return RabbitMQMessage(headers=headers, content_type=content_type, body=body)


def from_structured(
    message: RabbitMQMessage,
    event_format: Format,
    event_factory: EventFactory | None = None,
) -> BaseCloudEvent:
    """
    Parse a RabbitMQ structured content mode message to a CloudEvent.

    Deserializes the CloudEvent from the message body using the specified format.
    Any ce-prefixed headers are ignored as the body contains all event metadata.

    If event_factory is not provided, version detection is delegated to the format
    implementation, which will auto-detect based on the 'specversion' field.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> message = RabbitMQMessage(
        ...     headers={},
        ...     content_type="application/cloudevents+json",
        ...     body=b'{"type": "com.example.test", "source": "/test", ...}'
        ... )
        >>> event = from_structured(message, JSONFormat(), CloudEvent)

    :param message: RabbitMQMessage to parse
    :param event_format: Format implementation for deserialization
    :param event_factory: Factory function to create CloudEvent instances.
                         If None, the format will auto-detect the version.
    :return: CloudEvent instance
    """
    return event_format.read(event_factory, message.body)


def from_rabbitmq(
    message: RabbitMQMessage,
    event_format: Format,
    event_factory: EventFactory | None = None,
) -> BaseCloudEvent:
    """
    Parse a RabbitMQ message to a CloudEvent with automatic mode detection.

    Auto-detects CloudEvents version and uses appropriate event factory if not provided.

    Automatically detects whether the message uses binary or structured content mode:
    - If content_type starts with "application/cloudevents" -> structured mode
    - Otherwise -> binary mode

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> # Works with binary mode
        >>> binary_msg = RabbitMQMessage(
        ...     headers={"ce-type": "com.example.test", ...},
        ...     content_type="application/json",
        ...     body=b'...'
        ... )
        >>> event1 = from_rabbitmq(binary_msg, JSONFormat(), CloudEvent)
        >>>
        >>> # Also works with structured mode
        >>> structured_msg = RabbitMQMessage(
        ...     headers={},
        ...     content_type="application/cloudevents+json",
        ...     body=b'{"type": "com.example.test", ...}'
        ... )
        >>> event2 = from_rabbitmq(structured_msg, JSONFormat(), CloudEvent)

    :param message: RabbitMQMessage to parse
    :param event_format: Format implementation for deserialization
    :param event_factory: Factory function to create CloudEvent instances (auto-detected if None)
    :return: CloudEvent instance
    """
    content_type = message.content_type or ""

    if content_type.lower().startswith("application/cloudevents"):
        return from_structured(message, event_format, event_factory)

    return from_binary(message, event_format, event_factory)


def to_binary_event(
    event: BaseCloudEvent,
    event_format: Format | None = None,
) -> RabbitMQMessage:
    """
    Convenience wrapper for to_binary with JSON format as default.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.bindings import rabbitmq
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = rabbitmq.to_binary_event(event)

    :param event: The CloudEvent to convert
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: RabbitMQMessage with CloudEvent attributes as headers
    """
    if event_format is None:
        event_format = JSONFormat()
    return to_binary(event, event_format)


def from_binary_event(
    message: RabbitMQMessage,
    event_format: Format | None = None,
) -> CloudEvent:
    """
    Convenience wrapper for from_binary with JSON format and CloudEvent as defaults.

    Example:
        >>> from cloudevents.core.bindings import rabbitmq
        >>> event = rabbitmq.from_binary_event(message)

    :param message: RabbitMQMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_binary(message, event_format, CloudEvent)


def to_structured_event(
    event: BaseCloudEvent,
    event_format: Format | None = None,
) -> RabbitMQMessage:
    """
    Convenience wrapper for to_structured with JSON format as default.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.bindings import rabbitmq
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = rabbitmq.to_structured_event(event)

    :param event: The CloudEvent to convert
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: RabbitMQMessage with structured content in body
    """
    if event_format is None:
        event_format = JSONFormat()
    return to_structured(event, event_format)


def from_structured_event(
    message: RabbitMQMessage,
    event_format: Format | None = None,
) -> CloudEvent:
    """
    Convenience wrapper for from_structured with JSON format and CloudEvent as defaults.

    Example:
        >>> from cloudevents.core.bindings import rabbitmq
        >>> event = rabbitmq.from_structured_event(message)

    :param message: RabbitMQMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_structured(message, event_format, CloudEvent)


def from_rabbitmq_event(
    message: RabbitMQMessage,
    event_format: Format | None = None,
) -> CloudEvent:
    """
    Convenience wrapper for from_rabbitmq with JSON format and CloudEvent as defaults.
    Auto-detects binary or structured mode.

    Example:
        >>> from cloudevents.core.bindings import rabbitmq
        >>> event = rabbitmq.from_rabbitmq_event(message)

    :param message: RabbitMQMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_rabbitmq(message, event_format, CloudEvent)
