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
Common utilities for CloudEvents protocol bindings.

This module provides shared functionality for protocol bindings (HTTP, Kafka, etc.)
to handle CloudEvent attribute encoding and decoding per the CloudEvents specification.
"""

from datetime import datetime
from typing import Any, Final
from urllib.parse import quote, unquote

from dateutil.parser import isoparse

from cloudevents.core import SPECVERSION_V0_3
from cloudevents.core.base import EventFactory
from cloudevents.core.v03.event import CloudEvent as CloudEventV03
from cloudevents.core.v1.event import CloudEvent

TIME_ATTR: Final[str] = "time"
CONTENT_TYPE_HEADER: Final[str] = "content-type"
DATACONTENTTYPE_ATTR: Final[str] = "datacontenttype"


def encode_header_value(value: Any) -> str:
    """
    Encode a CloudEvent attribute value for use in a protocol header.

    Handles special encoding for datetime objects (ISO 8601 with 'Z' suffix for UTC)
    and applies percent-encoding for non-ASCII and special characters per RFC 3986.

    :param value: The attribute value to encode
    :return: Percent-encoded string suitable for protocol headers
    """
    if isinstance(value, datetime):
        str_value = value.isoformat()
        if str_value.endswith("+00:00"):
            str_value = str_value[:-6] + "Z"
        return quote(str_value, safe="")

    return quote(str(value), safe="")


def decode_header_value(attr_name: str, value: str) -> Any:
    """
    Decode a CloudEvent attribute value from a protocol header.

    Applies percent-decoding and special parsing for the 'time' attribute
    (converts to datetime object using RFC 3339 parsing).

    :param attr_name: The name of the CloudEvent attribute
    :param value: The percent-encoded header value
    :return: Decoded value (datetime for 'time' attribute, string otherwise)
    """
    decoded = unquote(value)

    if attr_name == TIME_ATTR:
        return isoparse(decoded)

    return decoded


def get_event_factory_for_version(specversion: str) -> EventFactory:
    """
    Get the appropriate event factory based on the CloudEvents specification version.

    This function returns the CloudEvent class implementation for the specified
    version. Used by protocol bindings for automatic version detection.

    :param specversion: The CloudEvents specification version (e.g., "0.3" or "1.0")
    :return: EventFactory for the specified version (defaults to v1.0 for unknown versions)
    """
    if specversion == SPECVERSION_V0_3:
        return CloudEventV03
    # Default to v1.0 for unknown versions
    return CloudEvent
