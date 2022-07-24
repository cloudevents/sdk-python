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

from deprecation import deprecated

from cloudevents.conversion import from_http as _abstract_from_http
from cloudevents.conversion import to_binary, to_structured
from cloudevents.http.event import CloudEvent
from cloudevents.sdk import types


def from_http(
    headers: typing.Dict[str, str],
    data: typing.Union[str, bytes, None],
    data_unmarshaller: types.UnmarshallerType = None,
) -> CloudEvent:
    """
    Unwrap a CloudEvent (binary or structured) from an HTTP request.
    :param headers: the HTTP headers
    :type headers: typing.Dict[str, str]
    :param data: the HTTP request body. If set to None, "" or b'', the returned
        event's data field will be set to None
    :type data: typing.IO
    :param data_unmarshaller: Callable function to map data to a python object
        e.g. lambda x: x or lambda x: json.loads(x)
    :type data_unmarshaller: types.UnmarshallerType
    """
    return _abstract_from_http(CloudEvent, headers, data, data_unmarshaller)


# backwards compatibility
to_binary = to_binary
# backwards compatibility
to_structured = to_structured


@deprecated(deprecated_in="1.0.2", details="Use to_binary function instead")
def to_binary_http(
    event: CloudEvent, data_marshaller: types.MarshallerType = None
) -> typing.Tuple[dict, typing.Union[bytes, str]]:
    return to_binary(event, data_marshaller)


@deprecated(deprecated_in="1.0.2", details="Use to_structured function instead")
def to_structured_http(
    event: CloudEvent, data_marshaller: types.MarshallerType = None
) -> typing.Tuple[dict, typing.Union[bytes, str]]:
    return to_structured(event, data_marshaller)
