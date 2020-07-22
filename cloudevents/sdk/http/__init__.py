# All Rights Reserved.
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

from cloudevents.sdk import converters, marshaller, types
from cloudevents.sdk.event import v1, v03
from cloudevents.sdk.http.event import (
    EventClass,
    _obj_by_version,
    to_binary_http,
    to_structured_http,
)


class CloudEvent(EventClass):
    def __repr__(self):
        return to_structured_http(self)[1].decode()


def _json_or_string(content: typing.Union[str, bytes]):
    if len(content) == 0:
        return None
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        return content


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
    :param data_unmarshaller: Callable function to map data arg to python object
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


def to_json(
    event: EventClass, data_marshaller: types.MarshallerType = None
) -> typing.Union[str, bytes]:
    """
    Cast an EventClass into a json object
    :param event: EventClass which will be converted into a json object
    :type event: EventClass
    :param data_marshaller: Callable function which will cast event.data
        into a json object
    :type data_marshaller: typing.Callable
    :returns: json object representing the given event
    """
    return to_structured_http(event, data_marshaller=data_marshaller)[1]


def from_json(
    data: typing.Union[str, bytes],
    data_unmarshaller: types.UnmarshallerType = None,
) -> EventClass:
    """
    Cast json encoded data into an EventClass
    :param data: json encoded cloudevent data
    :type event: typing.Union[str, bytes]
    :param data_unmarshaller: Callable function which will cast json encoded 
        data into a python object retrievable from returned EventClass.data
    :type data_marshaller: typing.Callable
    :returns: EventClass representing given cloudevent json object
    """
    return from_http(data=data, headers={}, data_unmarshaller=data_unmarshaller)
