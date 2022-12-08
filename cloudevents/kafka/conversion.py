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
from cloudevents.kafka.exceptions import KeyMapperError
from cloudevents.sdk import types

DEFAULT_MARSHALLER: types.MarshallerType = json.dumps
DEFAULT_UNMARSHALLER: types.MarshallerType = json.loads
DEFAULT_EMBEDDED_DATA_MARSHALLER: types.MarshallerType = lambda x: x


class KafkaMessage(typing.NamedTuple):
    """
    Represents the elements of a message sent or received through the Kafka protocol.
    Callers can map their client-specific message representation to and from this
    type in order to use the cloudevents.kafka conversion functions.
    """

    headers: typing.Dict[str, bytes]
    """
    The dictionary of message headers key/values.
    """

    key: typing.Optional[typing.Union[str, bytes]]
    """
    The message key.
    """

    value: typing.Union[str, bytes]
    """
    The message value.
    """


KeyMapper = typing.Callable[[AnyCloudEvent], typing.AnyStr]
"""
A callable function that creates a Kafka message key, given a CloudEvent instance.
"""

DEFAULT_KEY_MAPPER: KeyMapper = lambda event: event.get("partitionkey")
"""
The default KeyMapper which maps the user provided `partitionkey` attribute value
    to the `key` of the Kafka message as-is, if present.
"""


def to_binary(
    event: AnyCloudEvent,
    data_marshaller: typing.Optional[types.MarshallerType] = None,
    key_mapper: typing.Optional[KeyMapper] = None,
) -> KafkaMessage:
    """
    Returns a KafkaMessage in binary format representing this Cloud Event.

    :param event: The event to be converted. To specify the Kafka messaage Key, set
        the `partitionkey` attribute of the event, or provide a KeyMapper.
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes.
    :param key_mapper: Callable function to get the Kafka message key.
    :returns: KafkaMessage
    """
    data_marshaller = data_marshaller or DEFAULT_MARSHALLER
    key_mapper = key_mapper or DEFAULT_KEY_MAPPER

    try:
        message_key = key_mapper(event)
    except Exception as e:
        raise KeyMapperError(
            f"Failed to map message key with error: {type(e).__name__}('{e}')"
        )

    headers = {}
    if event["content-type"]:
        headers["content-type"] = event["content-type"].encode("utf-8")
    for attr, value in event.get_attributes().items():
        if attr not in ["data", "partitionkey", "content-type"]:
            if value is not None:
                headers["ce_{0}".format(attr)] = value.encode("utf-8")

    try:
        data = data_marshaller(event.get_data())
    except Exception as e:
        raise cloud_exceptions.DataMarshallerError(
            f"Failed to marshall data with error: {type(e).__name__}('{e}')"
        )
    if isinstance(data, str):
        data = data.encode("utf-8")

    return KafkaMessage(headers, message_key, data)


def from_binary(
    message: KafkaMessage,
    event_type: typing.Optional[typing.Type[AnyCloudEvent]] = None,
    data_unmarshaller: typing.Optional[types.MarshallerType] = None,
) -> AnyCloudEvent:
    """
    Returns a CloudEvent from a KafkaMessage in binary format.

    :param message: The KafkaMessage to be converted.
    :param event_type: The type of CloudEvent to create.  Defaults to http.CloudEvent.
    :param data_unmarshaller: Callable function to map data to a python object
    :returns: CloudEvent
    """

    data_unmarshaller = data_unmarshaller or DEFAULT_UNMARSHALLER
    attributes: typing.Dict[str, typing.Any] = {}

    for header, value in message.headers.items():
        header = header.lower()
        if header == "content-type":
            attributes["content-type"] = value.decode()
        elif header.startswith("ce_"):
            attributes[header[3:]] = value.decode()

    if message.key is not None:
        attributes["partitionkey"] = message.key

    try:
        data = data_unmarshaller(message.value)
    except Exception as e:
        raise cloud_exceptions.DataUnmarshallerError(
            f"Failed to unmarshall data with error: {type(e).__name__}('{e}')"
        )
    if event_type:
        result = event_type.create(attributes, data)
    else:
        result = http.CloudEvent.create(attributes, data)  # type: ignore
    return result


def to_structured(
    event: AnyCloudEvent,
    data_marshaller: typing.Optional[types.MarshallerType] = None,
    envelope_marshaller: typing.Optional[types.MarshallerType] = None,
    key_mapper: typing.Optional[KeyMapper] = None,
) -> KafkaMessage:
    """
    Returns a KafkaMessage in structured format representing this Cloud Event.

    :param event: The event to be converted. To specify the Kafka message KEY, set
        the `partitionkey` attribute of the event.
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes.
    :param envelope_marshaller: Callable function to cast event envelope into
        either a string or bytes.
    :param key_mapper: Callable function to get the Kafka message key.
    :returns: KafkaMessage
    """
    data_marshaller = data_marshaller or DEFAULT_EMBEDDED_DATA_MARSHALLER
    envelope_marshaller = envelope_marshaller or DEFAULT_MARSHALLER
    key_mapper = key_mapper or DEFAULT_KEY_MAPPER

    try:
        message_key = key_mapper(event)
    except Exception as e:
        raise KeyMapperError(
            f"Failed to map message key with error: {type(e).__name__}('{e}')"
        )

    attrs: typing.Dict[str, typing.Any] = dict(event.get_attributes())

    try:
        data = data_marshaller(event.get_data())
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

    try:
        value = envelope_marshaller(attrs)
    except Exception as e:
        raise cloud_exceptions.DataMarshallerError(
            f"Failed to marshall event with error: {type(e).__name__}('{e}')"
        )

    if isinstance(value, str):
        value = value.encode("utf-8")

    return KafkaMessage(headers, message_key, value)


def from_structured(
    message: KafkaMessage,
    event_type: typing.Optional[typing.Type[AnyCloudEvent]] = None,
    data_unmarshaller: typing.Optional[types.MarshallerType] = None,
    envelope_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
) -> AnyCloudEvent:
    """
    Returns a CloudEvent from a KafkaMessage in structured format.

    :param message: The KafkaMessage to be converted.
    :param event_type: The type of CloudEvent to create. Defaults to http.CloudEvent.
    :param data_unmarshaller: Callable function to map the data to a python object.
    :param envelope_unmarshaller: Callable function to map the envelope to a python
        object.
    :returns: CloudEvent
    """

    data_unmarshaller = data_unmarshaller or DEFAULT_EMBEDDED_DATA_MARSHALLER
    envelope_unmarshaller = envelope_unmarshaller or DEFAULT_UNMARSHALLER
    try:
        structure = envelope_unmarshaller(message.value)
    except Exception as e:
        raise cloud_exceptions.DataUnmarshallerError(
            "Failed to unmarshall message with error: " f"{type(e).__name__}('{e}')"
        )

    attributes: typing.Dict[str, typing.Any] = {}
    if message.key is not None:
        attributes["partitionkey"] = message.key

    data: typing.Optional[typing.Any] = None
    for name, value in structure.items():
        try:
            if name == "data":
                decoded_value = data_unmarshaller(value)
            elif name == "data_base64":
                decoded_value = data_unmarshaller(base64.b64decode(value))
                name = "data"
            else:
                decoded_value = value
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
    if event_type:
        result = event_type.create(attributes, data)
    else:
        result = http.CloudEvent.create(attributes, data)  # type: ignore
    return result
