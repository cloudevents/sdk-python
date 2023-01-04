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
import datetime
import enum
import json
import typing

from cloudevents import exceptions as cloud_exceptions
from cloudevents.abstract import AnyCloudEvent
from cloudevents.sdk import converters, marshaller, types
from cloudevents.sdk.converters import is_binary
from cloudevents.sdk.event import v1, v03


def _best_effort_serialize_to_json(  # type: ignore[no-untyped-def]
    value: typing.Any, *args, **kwargs
) -> typing.Optional[typing.Union[bytes, str, typing.Any]]:
    """
    Serializes the given value into a JSON-encoded string.

    Given a None value returns None as is.
    Given a non-JSON-serializable value returns the value as is.

    :param value:  The value to be serialized into a JSON string.
    :returns: JSON string of the given value OR None OR given value.
    """
    if value is None:
        return None
    try:
        return json.dumps(value, *args, **kwargs)
    except TypeError:
        return value


_default_marshaller_by_format: typing.Dict[str, types.MarshallerType] = {
    converters.TypeStructured: lambda x: x,
    converters.TypeBinary: _best_effort_serialize_to_json,
}

_obj_by_version = {"1.0": v1.Event, "0.3": v03.Event}


def to_json(
    event: AnyCloudEvent,
    data_marshaller: typing.Optional[types.MarshallerType] = None,
) -> bytes:
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
    data_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
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
    headers: typing.Mapping[str, str],
    data: typing.Optional[typing.Union[str, bytes]],
    data_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
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
                "The following can not be parsed as json: {!r}".format(data)
            )
        if hasattr(raw_ce, "get"):
            specversion = raw_ce.get("specversion", None)
        else:
            raise cloud_exceptions.MissingRequiredFields(
                "Failed to read specversion from both headers and data. "
                "The following deserialized data has no 'get' method: {}".format(raw_ce)
            )

    if specversion is None:
        raise cloud_exceptions.MissingRequiredFields(
            "Failed to find specversion in HTTP request"
        )

    event_handler = _obj_by_version.get(specversion, None)

    if event_handler is None:
        raise cloud_exceptions.InvalidRequiredFields(
            "Found invalid specversion {}".format(specversion)
        )

    event = marshall.FromRequest(
        event_handler(), headers, data, data_unmarshaller=data_unmarshaller
    )
    attrs = event.Properties()
    attrs.pop("data", None)
    attrs.pop("extensions", None)
    attrs.update(**event.extensions)

    result_data: typing.Optional[typing.Any] = event.data
    if event.data == "" or event.data == b"":
        # TODO: Check binary unmarshallers to debug why setting data to ""
        #  returns an event with data set to None, but structured will return ""
        result_data = None
    return event_type.create(attrs, result_data)


def _to_http(
    event: AnyCloudEvent,
    format: str = converters.TypeStructured,
    data_marshaller: typing.Optional[types.MarshallerType] = None,
) -> typing.Tuple[typing.Dict[str, str], bytes]:
    """
    Returns a tuple of HTTP headers/body dicts representing this Cloud Event.

    :param format: The encoding format of the event.
    :param data_marshaller: Callable function that casts event.data into
        either a string or bytes.
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    if data_marshaller is None:
        data_marshaller = _default_marshaller_by_format[format]

    if event["specversion"] not in _obj_by_version:
        raise cloud_exceptions.InvalidRequiredFields(
            f"Unsupported specversion: {event['specversion']}"
        )

    event_handler = _obj_by_version[event["specversion"]]()
    for attribute_name in event:
        event_handler.Set(attribute_name, event[attribute_name])
    event_handler.data = event.get_data()

    return marshaller.NewDefaultHTTPMarshaller().ToRequest(
        event_handler, format, data_marshaller=data_marshaller
    )


def to_structured(
    event: AnyCloudEvent,
    data_marshaller: typing.Optional[types.MarshallerType] = None,
) -> typing.Tuple[typing.Dict[str, str], bytes]:
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
    event: AnyCloudEvent, data_marshaller: typing.Optional[types.MarshallerType] = None
) -> typing.Tuple[typing.Dict[str, str], bytes]:
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


def best_effort_encode_attribute_value(value: typing.Any) -> typing.Any:
    """
    SHOULD convert any value into a JSON serialization friendly format.

    This function acts in a best-effort manner and MAY not actually encode the value
    if it does not know how to do that, or the value is already JSON-friendly.

    :param value: Value which MAY or MAY NOT be JSON serializable.
    :return: Possibly encoded value.
    """
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, datetime.datetime):
        return value.isoformat()

    return value


def from_dict(
    event_type: typing.Type[AnyCloudEvent],
    event: typing.Dict[str, typing.Any],
) -> AnyCloudEvent:
    """
    Constructs an Event object of a given `event_type` from
    a dict `event` representation.

    :param event: The event represented as a  dict.
    :param event_type: The type of the event to be constructed from the dict.
    :returns: The event of the specified type backed by the given dict.
    """
    attributes = {
        attr_name: best_effort_encode_attribute_value(attr_value)
        for attr_name, attr_value in event.items()
        if attr_name != "data"
    }
    return event_type.create(attributes=attributes, data=event.get("data"))


def to_dict(event: AnyCloudEvent) -> typing.Dict[str, typing.Any]:
    """
    Converts given `event` to its canonical dictionary representation.

    :param event: The event to be converted into a dict.
    :returns: The canonical dict representation of the event.
    """
    result = {attribute_name: event.get(attribute_name) for attribute_name in event}
    result["data"] = event.get_data()
    return result


def _json_or_string(
    content: typing.Optional[typing.Union[str, bytes]],
) -> typing.Any:
    """
    Returns a JSON-decoded dictionary or a list of dictionaries if
    a valid JSON string is provided.

    Returns the same `content` in case of an error or `None` when no content provided.
    """
    if content is None:
        return None
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
        return content
