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

import typing

from cloudevents.conversion import from_dict as _abstract_from_dict
from cloudevents.conversion import from_http as _abstract_from_http
from cloudevents.conversion import from_json as _abstract_from_json
from cloudevents.http.event import CloudEvent
from cloudevents.sdk import types


def from_json(
    data: typing.Union[str, bytes],
    data_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
) -> CloudEvent:
    """
    Parses JSON string `data` into a CloudEvent.

    :param data: JSON string representation of a CloudEvent.
    :param data_unmarshaller: Callable function that casts `data` to a
        Python object.
    :returns: A CloudEvent parsed from the given JSON representation.
    """
    return _abstract_from_json(CloudEvent, data, data_unmarshaller)


def from_http(
    headers: typing.Dict[str, str],
    data: typing.Optional[typing.Union[str, bytes]],
    data_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
) -> CloudEvent:
    """
    Parses CloudEvent `data` and `headers` into a CloudEvent`.

    The method supports both binary and structured representations.

    :param headers: The HTTP request headers.
    :param data: The HTTP request body. If set to None, "" or b'', the returned
        event's `data` field will be set to None.
    :param data_unmarshaller: Callable function to map data to a python object
        e.g. lambda x: x or lambda x: json.loads(x)
    :returns: A CloudEvent instance parsed from the passed HTTP parameters of
        the specified type.
    """
    return _abstract_from_http(CloudEvent, headers, data, data_unmarshaller)


def from_dict(
    event: typing.Dict[str, typing.Any],
) -> CloudEvent:
    """
    Constructs a CloudEvent from a dict `event` representation.

    :param event: The event represented as a dict.
    :returns: The event of the specified type backed by the given dict.
    """
    return _abstract_from_dict(CloudEvent, event)
