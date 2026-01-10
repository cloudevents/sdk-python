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
from datetime import datetime, timezone
from typing import Any, Final

from dateutil.parser import isoparse

from cloudevents.core.base import BaseCloudEvent, EventFactory
from cloudevents.core.formats.base import Format
from cloudevents.core.formats.json import JSONFormat
from cloudevents.core.v1.event import CloudEvent

# AMQP CloudEvents spec allows both cloudEvents_ and cloudEvents: prefixes
# The underscore variant is preferred for JMS 2.0 compatibility
CE_PREFIX_UNDERSCORE: Final[str] = "cloudEvents_"
CE_PREFIX_COLON: Final[str] = "cloudEvents:"
CONTENT_TYPE_PROPERTY: Final[str] = "content-type"


@dataclass(frozen=True)
class AMQPMessage:
    """
    Represents an AMQP 1.0 message containing CloudEvent data.

    This dataclass encapsulates AMQP message properties, application properties,
    and application data for transmitting CloudEvents over AMQP. It is immutable
    to prevent accidental modifications and works with any AMQP 1.0 library
    (e.g., Pika, aio-pika, qpid-proton, azure-servicebus).

    Attributes:
        properties: AMQP message properties as a dictionary
        application_properties: AMQP application properties as a dictionary
        application_data: AMQP application data section as bytes
    """

    properties: dict[str, Any]
    application_properties: dict[str, Any]
    application_data: bytes


def _encode_amqp_value(value: Any) -> Any:
    """
    Encode a CloudEvent attribute value for AMQP application properties.

    Handles special encoding for datetime objects to AMQP timestamp type
    (milliseconds since Unix epoch as int). Per AMQP 1.0 CloudEvents spec,
    senders SHOULD use native AMQP types when efficient.

    :param value: The attribute value to encode
    :return: Encoded value (int for datetime timestamp, original type otherwise)
    """
    if isinstance(value, datetime):
        # AMQP 1.0 timestamp: milliseconds since Unix epoch (UTC)
        timestamp_ms = int(value.timestamp() * 1000)
        return timestamp_ms

    return value


def _decode_amqp_value(attr_name: str, value: Any) -> Any:
    """
    Decode a CloudEvent attribute value from AMQP application properties.

    Handles special parsing for the 'time' attribute. Per AMQP 1.0 CloudEvents spec,
    receivers MUST accept both native AMQP timestamp (int milliseconds since epoch)
    and canonical string form (ISO 8601).

    :param attr_name: The name of the CloudEvent attribute
    :param value: The AMQP property value
    :return: Decoded value (datetime for 'time' attribute, original type otherwise)
    """
    if attr_name == "time":
        if isinstance(value, int):
            # AMQP timestamp: milliseconds since Unix epoch
            return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
        if isinstance(value, str):
            # ISO 8601 string (canonical form, also accepted per spec)
            return isoparse(value)

    return value


def to_binary(event: BaseCloudEvent, event_format: Format) -> AMQPMessage:
    """
    Convert a CloudEvent to AMQP binary content mode.

    In binary mode, CloudEvent attributes are mapped to AMQP application properties
    with the 'cloudEvents_' prefix, except for 'datacontenttype' which maps to the
    AMQP 'content-type' property. The event data is placed directly in the AMQP
    application-data section. Datetime values are encoded as AMQP timestamp type
    (milliseconds since Unix epoch), while boolean and integer values are preserved
    as native types.

    Note: Per AMQP CloudEvents spec, attributes may use 'cloudEvents_' or 'cloudEvents:'
    prefix. This implementation uses 'cloudEvents_' for JMS 2.0 compatibility.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = to_binary(event, JSONFormat())
        >>> # message.application_properties = {"cloudEvents_type": "com.example.test", ...}
        >>> # message.properties = {"content-type": "application/json"}
        >>> # message.application_data = b'{"message": "Hello"}'

    :param event: The CloudEvent to convert
    :param event_format: Format implementation for data serialization
    :return: AMQPMessage with CloudEvent attributes as application properties
    """
    properties: dict[str, Any] = {}
    application_properties: dict[str, Any] = {}
    attributes = event.get_attributes()

    for attr_name, attr_value in attributes.items():
        if attr_name == "datacontenttype":
            properties[CONTENT_TYPE_PROPERTY] = str(attr_value)
        else:
            property_name = f"{CE_PREFIX_UNDERSCORE}{attr_name}"
            # Encode datetime to AMQP timestamp (milliseconds since epoch)
            # Other types (bool, int, str, bytes) use native AMQP types
            application_properties[property_name] = _encode_amqp_value(attr_value)

    data = event.get_data()
    datacontenttype = attributes.get("datacontenttype")
    application_data = event_format.write_data(data, datacontenttype)

    return AMQPMessage(
        properties=properties,
        application_properties=application_properties,
        application_data=application_data,
    )


def from_binary(
    message: AMQPMessage,
    event_format: Format,
    event_factory: EventFactory,
) -> BaseCloudEvent:
    """
    Parse an AMQP binary content mode message to a CloudEvent.

    Extracts CloudEvent attributes from AMQP application properties with either
    'cloudEvents_' or 'cloudEvents:' prefix (per AMQP CloudEvents spec), and treats
    the AMQP 'content-type' property as the 'datacontenttype' attribute. The
    application-data section is parsed as event data according to the content type.
    The 'time' attribute accepts both AMQP timestamp (int milliseconds) and ISO 8601
    string, while other native AMQP types (boolean, integer) are preserved.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> message = AMQPMessage(
        ...     properties={"content-type": "application/json"},
        ...     application_properties={
        ...         "cloudEvents_type": "com.example.test",
        ...         "cloudEvents_source": "/test",
        ...         "cloudEvents_id": "123",
        ...         "cloudEvents_specversion": "1.0"
        ...     },
        ...     application_data=b'{"message": "Hello"}'
        ... )
        >>> event = from_binary(message, JSONFormat(), CloudEvent)

    :param message: AMQPMessage to parse
    :param event_format: Format implementation for data deserialization
    :param event_factory: Factory function to create CloudEvent instances
    :return: CloudEvent instance
    """
    attributes: dict[str, Any] = {}

    for prop_name, prop_value in message.application_properties.items():
        # Check for both cloudEvents_ and cloudEvents: prefixes
        attr_name = None

        if prop_name.startswith(CE_PREFIX_UNDERSCORE):
            attr_name = prop_name[len(CE_PREFIX_UNDERSCORE) :]
        elif prop_name.startswith(CE_PREFIX_COLON):
            attr_name = prop_name[len(CE_PREFIX_COLON) :]

        if attr_name:
            # Decode timestamp (int or ISO 8601 string) to datetime, preserve other native types
            attributes[attr_name] = _decode_amqp_value(attr_name, prop_value)

    if CONTENT_TYPE_PROPERTY in message.properties:
        attributes["datacontenttype"] = message.properties[CONTENT_TYPE_PROPERTY]

    datacontenttype = attributes.get("datacontenttype")
    data = event_format.read_data(message.application_data, datacontenttype)

    return event_factory(attributes, data)


def to_structured(event: BaseCloudEvent, event_format: Format) -> AMQPMessage:
    """
    Convert a CloudEvent to AMQP structured content mode.

    In structured mode, the entire CloudEvent (attributes and data) is serialized
    into the AMQP application-data section using the specified format. The
    content-type property is set to the format's media type (e.g.,
    "application/cloudevents+json").

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = to_structured(event, JSONFormat())
        >>> # message.properties = {"content-type": "application/cloudevents+json"}
        >>> # message.application_data = b'{"type": "com.example.test", ...}'

    :param event: The CloudEvent to convert
    :param event_format: Format implementation for serialization
    :return: AMQPMessage with structured content in application-data
    """
    content_type = event_format.get_content_type()

    properties = {CONTENT_TYPE_PROPERTY: content_type}
    application_properties: dict[str, Any] = {}

    application_data = event_format.write(event)

    return AMQPMessage(
        properties=properties,
        application_properties=application_properties,
        application_data=application_data,
    )


def from_structured(
    message: AMQPMessage,
    event_format: Format,
    event_factory: EventFactory,
) -> BaseCloudEvent:
    """
    Parse an AMQP structured content mode message to a CloudEvent.

    Deserializes the CloudEvent from the AMQP application-data section using the
    specified format. Any cloudEvents_-prefixed application properties are ignored
    as the application-data contains all event metadata.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> message = AMQPMessage(
        ...     properties={"content-type": "application/cloudevents+json"},
        ...     application_properties={},
        ...     application_data=b'{"type": "com.example.test", "source": "/test", ...}'
        ... )
        >>> event = from_structured(message, JSONFormat(), CloudEvent)

    :param message: AMQPMessage to parse
    :param event_format: Format implementation for deserialization
    :param event_factory: Factory function to create CloudEvent instances
    :return: CloudEvent instance
    """
    return event_format.read(event_factory, message.application_data)


def from_amqp(
    message: AMQPMessage,
    event_format: Format,
    event_factory: EventFactory,
) -> BaseCloudEvent:
    """
    Parse an AMQP message to a CloudEvent with automatic mode detection.

    Automatically detects whether the message uses binary or structured content mode:
    - If content-type starts with "application/cloudevents" → structured mode
    - Otherwise → binary mode

    This function provides a convenient way to handle both content modes without
    requiring the caller to determine the mode beforehand.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> # Works with binary mode
        >>> binary_msg = AMQPMessage(
        ...     properties={"content-type": "application/json"},
        ...     application_properties={"cloudEvents_type": "com.example.test", ...},
        ...     application_data=b'...'
        ... )
        >>> event1 = from_amqp(binary_msg, JSONFormat(), CloudEvent)
        >>>
        >>> # Also works with structured mode
        >>> structured_msg = AMQPMessage(
        ...     properties={"content-type": "application/cloudevents+json"},
        ...     application_properties={},
        ...     application_data=b'{"type": "com.example.test", ...}'
        ... )
        >>> event2 = from_amqp(structured_msg, JSONFormat(), CloudEvent)

    :param message: AMQPMessage to parse
    :param event_format: Format implementation for deserialization
    :param event_factory: Factory function to create CloudEvent instances
    :return: CloudEvent instance
    """
    content_type = message.properties.get(CONTENT_TYPE_PROPERTY, "")

    if isinstance(content_type, str) and content_type.lower().startswith(
        "application/cloudevents"
    ):
        return from_structured(message, event_format, event_factory)

    return from_binary(message, event_format, event_factory)


def to_binary_event(
    event: BaseCloudEvent,
    event_format: Format | None = None,
) -> AMQPMessage:
    """
    Convenience wrapper for to_binary with JSON format as default.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.bindings import amqp
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = amqp.to_binary_event(event)

    :param event: The CloudEvent to convert
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: AMQPMessage with CloudEvent attributes as application properties
    """
    if event_format is None:
        event_format = JSONFormat()
    return to_binary(event, event_format)


def from_binary_event(
    message: AMQPMessage,
    event_format: Format | None = None,
) -> CloudEvent:
    """
    Convenience wrapper for from_binary with JSON format and CloudEvent as defaults.

    Example:
        >>> from cloudevents.core.bindings import amqp
        >>> event = amqp.from_binary_event(message)

    :param message: AMQPMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_binary(message, event_format, CloudEvent)


def to_structured_event(
    event: BaseCloudEvent,
    event_format: Format | None = None,
) -> AMQPMessage:
    """
    Convenience wrapper for to_structured with JSON format as default.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.bindings import amqp
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = amqp.to_structured_event(event)

    :param event: The CloudEvent to convert
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: AMQPMessage with structured content in application-data
    """
    if event_format is None:
        event_format = JSONFormat()
    return to_structured(event, event_format)


def from_structured_event(
    message: AMQPMessage,
    event_format: Format | None = None,
) -> CloudEvent:
    """
    Convenience wrapper for from_structured with JSON format and CloudEvent as defaults.

    Example:
        >>> from cloudevents.core.bindings import amqp
        >>> event = amqp.from_structured_event(message)

    :param message: AMQPMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_structured(message, event_format, CloudEvent)


def from_amqp_event(
    message: AMQPMessage,
    event_format: Format | None = None,
) -> CloudEvent:
    """
    Convenience wrapper for from_amqp with JSON format and CloudEvent as defaults.
    Auto-detects binary or structured mode.

    Example:
        >>> from cloudevents.core.bindings import amqp
        >>> event = amqp.from_amqp_event(message)

    :param message: AMQPMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_amqp(message, event_format, CloudEvent)
