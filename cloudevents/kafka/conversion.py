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
import base64
import json
import typing

from cloudevents import exceptions as cloud_exceptions
from cloudevents import http
from cloudevents.abstract import AnyCloudEvent
from cloudevents.sdk import types

DEFAULT_MARSHALLER = json.dumps
DEFAULT_UNMARSHALLER = json.loads
DEFAULT_EMBEDDED_DATA_MARSHALLER = lambda x: x


class ProtocolMessage(typing.NamedTuple):
    """
    A raw kafka-protocol message.
    """

    headers: typing.Dict[str, bytes]
    key: typing.Union[bytes, str]
    value: typing.Union[bytes, str]


def to_binary(
    event: AnyCloudEvent, data_marshaller: types.MarshallerType = None
) -> ProtocolMessage:
    """
    Returns a Kafka ProtocolMessage in binary format representing this Cloud Event.

    :param event: The event to be converted.
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes.
    :returns: ProtocolMessage
    """
    data_marshaller = data_marshaller or DEFAULT_MARSHALLER
    headers = {}
    if event["content-type"]:
        headers["content-type"] = event["content-type"].encode("utf-8")
    for attr, value in event.get_attributes().items():
        if attr not in ["data", "key", "content-type"]:
            if value is not None:
                headers["ce_{0}".format(attr)] = value.encode("utf-8")

    try:
        data = data_marshaller(event.data)
    except Exception as e:
        raise cloud_exceptions.DataMarshallerError(
            f"Failed to marshall data with error: {type(e).__name__}('{e}')"
        )
    if isinstance(data, str):  # Convenience method for json.dumps
        data = data.encode("utf-8")

    return ProtocolMessage(headers, event.get("key"), data)


def from_binary(
    message: ProtocolMessage,
    event_type: typing.Type[AnyCloudEvent] = None,
    data_unmarshaller: types.MarshallerType = None,
) -> AnyCloudEvent:
    """
    Returns a CloudEvent from a Kafka ProtocolMessage in binary format.

    :param message: The ProtocolMessage to be converted.
    :param event_type:  The type of CloudEvent to create.  Defaults to http.CloudEvent.
    :param data_unmarshaller: Callable function to map data to a python object
    :returns: CloudEvent
    """

    data_unmarshaller = data_unmarshaller or DEFAULT_UNMARSHALLER
    event_type = event_type or http.CloudEvent

    attributes = {}

    for header, value in message.headers.items():
        header = header.lower()
        if header == "content-type":
            attributes["content-type"] = value.decode()
        elif header.startswith("ce_"):
            attributes[header[3:]] = value.decode()

    if message.key is not None:
        attributes["key"] = message.key

    try:
        data = data_unmarshaller(message.value)
    except Exception as e:
        raise cloud_exceptions.DataUnmarshallerError(
            f"Failed to unmarshall data with error: {type(e).__name__}('{e}')"
        )

    return event_type(attributes, data)


def to_structured(
    event: AnyCloudEvent,
    data_marshaller: types.MarshallerType = None,
    envelope_marshaller: types.MarshallerType = None,
) -> ProtocolMessage:
    """
    Returns a Kafka ProtocolMessage in structured format representing this Cloud Event.

    :param event: The event to be converted.
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes.
    :param envelope_marshaller: Callable function to cast event envelope into
        either a string or bytes.
    :returns: ProtocolMessage
    """
    data_marshaller = data_marshaller or DEFAULT_EMBEDDED_DATA_MARSHALLER
    envelope_marshaller = envelope_marshaller or DEFAULT_MARSHALLER

    attrs = event.get_attributes().copy()

    try:
        data = data_marshaller(event.data)
    except Exception as e:
        raise cloud_exceptions.DataMarshallerError(
            f"Failed to marshall data with error: {type(e).__name__}('{e}')"
        )
    if isinstance(data, (bytes, bytes, memoryview)):
        attrs["data_base64"] = base64.b64encode(data).decode("ascii")
    else:
        attrs["data"] = data

    headers = {}
    if "content-type" in attrs:
        headers["content-type"] = attrs.pop("content-type").encode("utf-8")

    if "key" in attrs:
        key = attrs.pop("key")
    else:
        key = None

    value = envelope_marshaller(attrs)

    return ProtocolMessage(headers, key, value)


def from_structured(
    message: ProtocolMessage,
    event_type: typing.Type[AnyCloudEvent] = None,
    data_unmarshaller: types.MarshallerType = None,
    envelope_unmarshaller: types.MarshallerType = None,
) -> AnyCloudEvent:
    """
    Returns a CloudEvent from a Kafka ProtocolMessage in structured format.

    :param message: The ProtocolMessage to be converted.
    :param event_type:  The type of CloudEvent to create.  Defaults to http.CloudEvent.
    :param data_unmarshaller: Callable function to map data to a python object
    :param envelope_unmarshaller: Callable function to map the event envelope to a python object
    :returns: CloudEvent
    """

    data_unmarshaller = data_unmarshaller or DEFAULT_EMBEDDED_DATA_MARSHALLER
    envelope_unmarshaller = envelope_unmarshaller or DEFAULT_UNMARSHALLER
    event_type = event_type or http.CloudEvent

    structure = envelope_unmarshaller(message.value)

    attributes = {"key": message.key}

    for name, value in structure.items():
        decoder = lambda x: x
        if name == "data":
            decoder = lambda v: data_unmarshaller(v)
        if name == "data_base64":
            decoder = lambda v: data_unmarshaller(base64.b64decode(v))
            name = "data"

        try:
            decoded_value = decoder(value)
        except Exception as e:
            raise cloud_exceptions.DataUnmarshallerError(
                "Failed to unmarshall data with error: " f"{type(e).__name__}('{e}')"
            )
        if name == "data":
            data = decoded_value
        else:
            attributes[name] = decoded_value

    for header, val in message.headers.items():
        attributes[header.lower()] = val.decode()

    return event_type(attributes, data)
