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
from datetime import datetime
from typing import Any, Final
from urllib.parse import quote, unquote

from dateutil.parser import isoparse

from cloudevents.core.base import BaseCloudEvent, EventFactory
from cloudevents.core.bindings.common import (
    CONTENT_TYPE_HEADER,
    DATACONTENTTYPE_ATTR,
    TIME_ATTR,
    get_event_factory_for_version,
)
from cloudevents.core.formats.base import Format
from cloudevents.core.formats.json import JSONFormat
from cloudevents.core.spec import SPECVERSION_V1_0

# Per CloudEvents HTTP binding spec (section 3.1.3.2), all printable ASCII
# characters (U+0021-U+007E) are safe EXCEPT space, double-quote, and percent.
_CE_SAFE_CHARS: Final[str] = "".join(
    c for c in map(chr, range(0x21, 0x7F)) if c not in (" ", '"', "%")
)


def _encode_header_value(value: Any) -> str:
    """
    Encode a CloudEvent attribute value for use in an HTTP header.

    Handles datetime objects (ISO 8601 with 'Z' suffix for UTC) and applies
    percent-encoding per the CloudEvents HTTP binding spec (section 3.1.3.2).

    :param value: The attribute value to encode
    :return: Percent-encoded string suitable for HTTP headers
    """
    if isinstance(value, datetime):
        str_value = value.isoformat()
        if str_value.endswith("+00:00"):
            str_value = str_value[:-6] + "Z"
        return quote(str_value, safe=_CE_SAFE_CHARS)
    return quote(str(value), safe=_CE_SAFE_CHARS)


def _decode_header_value(attr_name: str, value: str) -> Any:
    """
    Decode a CloudEvent attribute value from an HTTP header.

    Applies percent-decoding and parses the 'time' attribute as datetime.

    :param attr_name: The name of the CloudEvent attribute
    :param value: The percent-encoded header value
    :return: Decoded value (datetime for 'time' attribute, string otherwise)
    """
    decoded = unquote(value)
    if attr_name == TIME_ATTR:
        return isoparse(decoded)
    return decoded


CE_PREFIX: Final[str] = "ce-"


@dataclass(frozen=True)
class HTTPMessage:
    """
    Represents an HTTP message (request or response) containing CloudEvent data.

    This dataclass encapsulates HTTP headers and body for transmitting CloudEvents
    over HTTP. It is immutable to prevent accidental modifications and works with
    any HTTP framework or library.

    Attributes:
        headers: HTTP headers as a dictionary with string keys and values
        body: HTTP body as bytes
    """

    headers: dict[str, str]
    body: bytes


def to_binary(event: BaseCloudEvent, event_format: Format) -> HTTPMessage:
    """
    Convert a CloudEvent to HTTP binary content mode.

    In binary mode, CloudEvent attributes are mapped to HTTP headers with the 'ce-' prefix,
    except for 'datacontenttype' which maps to the 'Content-Type' header. The event data
    is placed directly in the HTTP body.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = to_binary(event, JSONFormat())
        >>> # message.headers = {"ce-type": "com.example.test", "ce-source": "/test", ...}
        >>> # message.body = b'{"message": "Hello"}'

    :param event: The CloudEvent to convert
    :param event_format: Format implementation for data serialization
    :return: HTTPMessage with ce-prefixed headers and event data as body
    """
    headers: dict[str, str] = {}
    attributes = event.get_attributes()

    for attr_name, attr_value in attributes.items():
        if attr_value is None:
            continue

        if attr_name == DATACONTENTTYPE_ATTR:
            headers[CONTENT_TYPE_HEADER] = str(attr_value)
        else:
            header_name = f"{CE_PREFIX}{attr_name}"
            headers[header_name] = _encode_header_value(attr_value)

    data = event.get_data()
    datacontenttype = attributes.get(DATACONTENTTYPE_ATTR)
    body = event_format.write_data(data, datacontenttype)

    return HTTPMessage(headers=headers, body=body)


def from_binary(
    message: HTTPMessage,
    event_format: Format,
    event_factory: EventFactory | None = None,
) -> BaseCloudEvent:
    """
    Parse an HTTP binary content mode message to a CloudEvent.

    Auto-detects the CloudEvents version from the 'ce-specversion' header
    and uses the appropriate event factory if not explicitly provided.

    Extracts CloudEvent attributes from ce-prefixed HTTP headers and treats the
    'Content-Type' header as the 'datacontenttype' attribute. The HTTP body is
    parsed as event data according to the content type.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> message = HTTPMessage(
        ...     headers={"ce-type": "com.example.test", "ce-source": "/test",
        ...              "ce-id": "123", "ce-specversion": "1.0"},
        ...     body=b'{"message": "Hello"}'
        ... )
        >>> event = from_binary(message, JSONFormat(), CloudEvent)

    :param message: HTTPMessage to parse
    :param event_format: Format implementation for data deserialization
    :param event_factory: Factory function to create CloudEvent instances (auto-detected if None)
    :return: CloudEvent instance
    """
    attributes: dict[str, Any] = {}

    for header_name, header_value in message.headers.items():
        normalized_name = header_name.lower()

        if normalized_name.startswith(CE_PREFIX):
            attr_name = normalized_name[len(CE_PREFIX) :]
            attributes[attr_name] = _decode_header_value(attr_name, header_value)
        elif normalized_name == CONTENT_TYPE_HEADER:
            attributes[DATACONTENTTYPE_ATTR] = header_value

    # Auto-detect version if factory not provided
    if event_factory is None:
        specversion = attributes.get("specversion", SPECVERSION_V1_0)
        event_factory = get_event_factory_for_version(specversion)

    datacontenttype = attributes.get(DATACONTENTTYPE_ATTR)
    data = event_format.read_data(message.body, datacontenttype)

    return event_factory(attributes, data)


def to_structured(event: BaseCloudEvent, event_format: Format) -> HTTPMessage:
    """
    Convert a CloudEvent to HTTP structured content mode.

    In structured mode, the entire CloudEvent (attributes and data) is serialized
    into the HTTP body using the specified format. The Content-Type header is set
    to the format's media type.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = to_structured(event, JSONFormat())
        >>> # message.headers = {"content-type": "application/cloudevents+json"}
        >>> # message.body = b'{"type": "com.example.test", "source": "/test", ...}'

    :param event: The CloudEvent to convert
    :param event_format: Format implementation for serialization
    :return: HTTPMessage with structured content in body
    """
    content_type = event_format.get_content_type()

    headers = {CONTENT_TYPE_HEADER: content_type}

    body = event_format.write(event)

    return HTTPMessage(headers=headers, body=body)


def from_structured(
    message: HTTPMessage,
    event_format: Format,
    event_factory: EventFactory | None = None,
) -> BaseCloudEvent:
    """
    Parse an HTTP structured content mode message to a CloudEvent.

    Deserializes the CloudEvent from the HTTP body using the specified format.
    Any ce-prefixed headers are ignored as the body contains all event metadata.

    If event_factory is not provided, version detection is delegated to the format
    implementation, which will auto-detect based on the 'specversion' field.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> # Explicit factory (recommended for performance)
        >>> message = HTTPMessage(
        ...     headers={"content-type": "application/cloudevents+json"},
        ...     body=b'{"type": "com.example.test", "source": "/test", ...}'
        ... )
        >>> event = from_structured(message, JSONFormat(), CloudEvent)
        >>>
        >>> # Auto-detect version (convenient)
        >>> event = from_structured(message, JSONFormat())

    :param message: HTTPMessage to parse
    :param event_format: Format implementation for deserialization
    :param event_factory: Factory function to create CloudEvent instances.
                         If None, the format will auto-detect the version.
    :return: CloudEvent instance
    """
    # Delegate version detection to format layer
    return event_format.read(event_factory, message.body)


def from_http(
    message: HTTPMessage,
    event_format: Format,
    event_factory: EventFactory | None = None,
) -> BaseCloudEvent:
    """
    Parse an HTTP message to a CloudEvent with automatic mode detection.

    Auto-detects CloudEvents version and uses appropriate event factory if not provided.

    Automatically detects whether the message uses binary or structured content mode:
    - If any ce- prefixed headers are present → binary mode
    - Otherwise → structured mode

    This function provides a convenient way to handle both content modes without
    requiring the caller to determine the mode beforehand.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.formats.json import JSONFormat
        >>>
        >>> # Works with binary mode
        >>> binary_msg = HTTPMessage(
        ...     headers={"ce-type": "com.example.test", ...},
        ...     body=b'...'
        ... )
        >>> event1 = from_http(binary_msg, JSONFormat(), CloudEvent)
        >>>
        >>> # Also works with structured mode
        >>> structured_msg = HTTPMessage(
        ...     headers={"content-type": "application/cloudevents+json"},
        ...     body=b'{"type": "com.example.test", ...}'
        ... )
        >>> event2 = from_http(structured_msg, JSONFormat(), CloudEvent)

    :param message: HTTPMessage to parse
    :param event_format: Format implementation for deserialization
    :param event_factory: Factory function to create CloudEvent instances (auto-detected if None)
    :return: CloudEvent instance
    """
    if any(key.lower().startswith(CE_PREFIX) for key in message.headers.keys()):
        return from_binary(message, event_format, event_factory)

    return from_structured(message, event_format, event_factory)


def to_binary_event(
    event: BaseCloudEvent,
    event_format: Format | None = None,
) -> HTTPMessage:
    """
    Convenience wrapper for to_binary with JSON format as default.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.bindings import http
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = http.to_binary_event(event)

    :param event: The CloudEvent to convert
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: HTTPMessage with ce-prefixed headers
    """
    if event_format is None:
        event_format = JSONFormat()
    return to_binary(event, event_format)


def from_binary_event(
    message: HTTPMessage,
    event_format: Format | None = None,
) -> BaseCloudEvent:
    """
    Convenience wrapper for from_binary with JSON format and auto-detection.

    Auto-detects CloudEvents version (v0.3 or v1.0) from headers.

    Example:
        >>> from cloudevents.core.bindings import http
        >>> event = http.from_binary_event(message)

    :param message: HTTPMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance (v0.3 or v1.0 based on specversion)
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_binary(message, event_format, None)


def to_structured_event(
    event: BaseCloudEvent,
    event_format: Format | None = None,
) -> HTTPMessage:
    """
    Convenience wrapper for to_structured with JSON format as default.

    Example:
        >>> from cloudevents.core.v1.event import CloudEvent
        >>> from cloudevents.core.bindings import http
        >>>
        >>> event = CloudEvent(
        ...     attributes={"type": "com.example.test", "source": "/test"},
        ...     data={"message": "Hello"}
        ... )
        >>> message = http.to_structured_event(event)

    :param event: The CloudEvent to convert
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: HTTPMessage with structured content
    """
    if event_format is None:
        event_format = JSONFormat()
    return to_structured(event, event_format)


def from_structured_event(
    message: HTTPMessage,
    event_format: Format | None = None,
) -> BaseCloudEvent:
    """
    Convenience wrapper for from_structured with JSON format and auto-detection.

    Auto-detects CloudEvents version (v0.3 or v1.0) from body.

    Example:
        >>> from cloudevents.core.bindings import http
        >>> event = http.from_structured_event(message)

    :param message: HTTPMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance (v0.3 or v1.0 based on specversion)
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_structured(message, event_format, None)


def from_http_event(
    message: HTTPMessage,
    event_format: Format | None = None,
) -> BaseCloudEvent:
    """
    Convenience wrapper for from_http with JSON format and auto-detection.
    Auto-detects binary or structured mode, and CloudEvents version.

    Example:
        >>> from cloudevents.core.bindings import http
        >>> event = http.from_http_event(message)

    :param message: HTTPMessage to parse
    :param event_format: Format implementation (defaults to JSONFormat)
    :return: CloudEvent instance (v0.3 or v1.0 based on specversion)
    """
    if event_format is None:
        event_format = JSONFormat()
    return from_http(message, event_format, None)
