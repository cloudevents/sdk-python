import json
import typing

from cloudevents.http.event import CloudEvent
from cloudevents.http.mappings import _marshaller_by_format, _obj_by_version
from cloudevents.http.util import _json_or_string
from cloudevents.sdk import converters, marshaller, types


def from_http(
    data: typing.Union[str, bytes],
    headers: typing.Dict[str, str],
    data_unmarshaller: types.UnmarshallerType = None,
):
    """
    Unwrap a CloudEvent (binary or structured) from an HTTP request.
    :param data: the HTTP request body
    :type data: typing.IO
    :param headers: the HTTP headers
    :type headers: typing.Dict[str, str]
    :param data_unmarshaller: Callable function to map data to a python object
        e.g. lambda x: x or lambda x: json.loads(x)
    :type data_unmarshaller: types.UnmarshallerType
    """
    if data_unmarshaller is None:
        data_unmarshaller = _json_or_string

    marshall = marshaller.NewDefaultHTTPMarshaller()

    if converters.is_binary(headers):
        specversion = headers.get("ce-specversion", None)
    else:
        raw_ce = json.loads(data)
        specversion = raw_ce.get("specversion", None)

    if specversion is None:
        raise ValueError("could not find specversion in HTTP request")

    event_handler = _obj_by_version.get(specversion, None)

    if event_handler is None:
        raise ValueError(f"found invalid specversion {specversion}")

    event = marshall.FromRequest(
        event_handler(), headers, data, data_unmarshaller=data_unmarshaller
    )
    attrs = event.Properties()
    attrs.pop("data", None)
    attrs.pop("extensions", None)
    attrs.update(**event.extensions)

    return CloudEvent(attrs, event.data)


def _to_http(
    event: CloudEvent,
    format: str = converters.TypeStructured,
    data_marshaller: types.MarshallerType = None,
) -> (dict, typing.Union[bytes, str]):
    """
    Returns a tuple of HTTP headers/body dicts representing this cloudevent

    :param format: constant specifying an encoding format
    :type format: str
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes
    :type data_marshaller: types.MarshallerType
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    if data_marshaller is None:
        data_marshaller = _marshaller_by_format[format]

    if event._attributes["specversion"] not in _obj_by_version:
        raise ValueError(
            f"Unsupported specversion: {event._attributes['specversion']}"
        )

    event_handler = _obj_by_version[event._attributes["specversion"]]()
    for k, v in event._attributes.items():
        event_handler.Set(k, v)
    event_handler.data = event.data

    return marshaller.NewDefaultHTTPMarshaller().ToRequest(
        event_handler, format, data_marshaller=data_marshaller
    )


def to_structured_http(
    event: CloudEvent, data_marshaller: types.MarshallerType = None,
) -> (dict, typing.Union[bytes, str]):
    """
    Returns a tuple of HTTP headers/body dicts representing this cloudevent

    :param event: CloudEvent to cast into http data
    :type event: CloudEvent
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes
    :type data_marshaller: types.MarshallerType
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    return _to_http(event=event, data_marshaller=data_marshaller)


def to_binary_http(
    event: CloudEvent, data_marshaller: types.MarshallerType = None,
) -> (dict, typing.Union[bytes, str]):
    """
    Returns a tuple of HTTP headers/body dicts representing this cloudevent

    :param event: CloudEvent to cast into http data
    :type event: CloudEvent
    :param data_marshaller: Callable function to cast event.data into
        either a string or bytes
    :type data_marshaller: types.UnmarshallerType
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    return _to_http(
        event=event,
        format=converters.TypeBinary,
        data_marshaller=data_marshaller,
    )
