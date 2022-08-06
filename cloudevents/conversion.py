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
import json
import typing

from cloudevents import exceptions as cloud_exceptions
from cloudevents.abstract import AnyCloudEvent
from cloudevents.http import is_binary
from cloudevents.http.mappings import _marshaller_by_format, _obj_by_version
from cloudevents.http.util import _json_or_string
from cloudevents.sdk import converters, marshaller, types


def to_json(
    event: AnyCloudEvent,
    data_marshaller: types.MarshallerType = None,
) -> typing.Union[str, bytes]:
    """
    Converts given `event` to a JSON string.

    :param event: A CloudEvent to be converted into a JSON string.
    :param data_marshaller: Callable function which will cast `event.data`
        into a JSON string.
    :returns: A JSON string representing the given event.
    """
    return to_structured(event, data_marshaller=data_marshaller)[1]


def from_json(
    event_type: typing.Type[AnyCloudEvent],
    data: typing.Union[str, bytes],
    data_unmarshaller: types.UnmarshallerType = None,
) -> AnyCloudEvent:
    """
    Parses JSON string `data` into a CloudEvent.

    :param data: JSON string representation of a CloudEvent.
    :param data_unmarshaller: Callable function that casts `data` to a
        Python object.
    :param event_type: A concrete type of the event into which the data is
        deserialized.
    :returns: A CloudEvent parsed from the given JSON representation.
    """
    return from_http(
        headers={},
        data=data,
        data_unmarshaller=data_unmarshaller,
        event_type=event_type,
    )


def from_http(
    event_type: typing.Type[AnyCloudEvent],
    headers: typing.Dict[str, str],
    data: typing.Union[str, bytes, None],
    data_unmarshaller: types.UnmarshallerType = None,
) -> AnyCloudEvent:
    """
    Parses CloudEvent `data` and `headers` into an instance of a given `event_type`.

    The method supports both binary and structured representations.

    :param headers: The HTTP request headers.
    :param data: The HTTP request body. If set to None, "" or b'', the returned
        event's `data` field will be set to None.
    :param data_unmarshaller: Callable function to map data to a python object
        e.g. lambda x: x or lambda x: json.loads(x)
    :param event_type: The actual type of CloudEvent to deserialize the event to.
    :returns: A CloudEvent instance parsed from the passed HTTP parameters of
        the specified type.
    """
    if data is None or data == b"":
        # Empty string will cause data to be marshalled into None
        data = ""

    if not isinstance(data, (str, bytes, bytearray)):
        raise cloud_exceptions.InvalidStructuredJSON(
            "Expected json of type (str, bytes, bytearray), "
            f"but instead found type {type(data)}"
        )

    headers = {key.lower(): value for key, value in headers.items()}
    if data_unmarshaller is None:
        data_unmarshaller = _json_or_string

    marshall = marshaller.NewDefaultHTTPMarshaller()

    if is_binary(headers):
        specversion = headers.get("ce-specversion", None)
    else:
        try:
            raw_ce = json.loads(data)
        except json.decoder.JSONDecodeError:
            raise cloud_exceptions.MissingRequiredFields(
                "Failed to read specversion from both headers and data. "
                f"The following can not be parsed as json: {data}"
            )
        if hasattr(raw_ce, "get"):
            specversion = raw_ce.get("specversion", None)
        else:
            raise cloud_exceptions.MissingRequiredFields(
                "Failed to read specversion from both headers and data. "
                f"The following deserialized data has no 'get' method: {raw_ce}"
            )

    if specversion is None:
        raise cloud_exceptions.MissingRequiredFields(
            "Failed to find specversion in HTTP request"
        )

    event_handler = _obj_by_version.get(specversion, None)

    if event_handler is None:
        raise cloud_exceptions.InvalidRequiredFields(
            f"Found invalid specversion {specversion}"
        )

    event = marshall.FromRequest(
        event_handler(), headers, data, data_unmarshaller=data_unmarshaller
    )
    attrs = event.Properties()
    attrs.pop("data", None)
    attrs.pop("extensions", None)
    attrs.update(**event.extensions)

    if event.data == "" or event.data == b"":
        # TODO: Check binary unmarshallers to debug why setting data to ""
        # returns an event with data set to None, but structured will return ""
        data = None
    else:
        data = event.data
    return event_type.create(attrs, data)


def _to_http(
    event: AnyCloudEvent,
    format: str = converters.TypeStructured,
    data_marshaller: types.MarshallerType = None,
) -> typing.Tuple[dict, typing.Union[bytes, str]]:
    """
    Returns a tuple of HTTP headers/body dicts representing this Cloud Event.

    :param format: The encoding format of the event.
    :param data_marshaller: Callable function that casts event.data into
        either a string or bytes.
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    if data_marshaller is None:
        data_marshaller = _marshaller_by_format[format]

    if event["specversion"] not in _obj_by_version:
        raise cloud_exceptions.InvalidRequiredFields(
            f"Unsupported specversion: {event['specversion']}"
        )

    event_handler = _obj_by_version[event["specversion"]]()
    for attribute_name in event:
        event_handler.Set(attribute_name, event[attribute_name])
    event_handler.data = event.data

    return marshaller.NewDefaultHTTPMarshaller().ToRequest(
        event_handler, format, data_marshaller=data_marshaller
    )


def to_structured(
    event: AnyCloudEvent,
    data_marshaller: types.MarshallerType = None,
) -> typing.Tuple[dict, typing.Union[bytes, str]]:
    """
    Returns a tuple of HTTP headers/body dicts representing this Cloud Event.

    If event.data is a byte object, body will have a `data_base64` field instead of
    `data`.

    :param event: The event to be converted.
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    return _to_http(event=event, data_marshaller=data_marshaller)


def to_binary(
    event: AnyCloudEvent, data_marshaller: types.MarshallerType = None
) -> typing.Tuple[dict, typing.Union[bytes, str]]:
    """
    Returns a tuple of HTTP headers/body dicts representing this Cloud Event.

    Uses Binary conversion format.

    :param event: The event to be converted.
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes.
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    return _to_http(
        event=event,
        format=converters.TypeBinary,
        data_marshaller=data_marshaller,
    )
