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

from cloudevents.abstract import AnyCloudEvent
from cloudevents.conversion import to_binary as _moved_to_binary
from cloudevents.conversion import to_structured as _moved_to_structured
from cloudevents.http.conversion import from_http as _moved_from_http
from cloudevents.http.event import CloudEvent
from cloudevents.sdk import types

# THIS MODULE IS DEPRECATED, YOU SHOULD NOT ADD NEW FUNCTIONALLY HERE


@deprecated(
    deprecated_in="1.6.0",
    details="Use cloudevents.conversion.to_binary function instead",
)
def to_binary(
    event: AnyCloudEvent, data_marshaller: typing.Optional[types.MarshallerType] = None
) -> typing.Tuple[typing.Dict[str, str], bytes]:
    return _moved_to_binary(event, data_marshaller)


@deprecated(
    deprecated_in="1.6.0",
    details="Use cloudevents.conversion.to_structured function instead",
)
def to_structured(
    event: AnyCloudEvent,
    data_marshaller: typing.Optional[types.MarshallerType] = None,
) -> typing.Tuple[typing.Dict[str, str], bytes]:
    return _moved_to_structured(event, data_marshaller)


@deprecated(
    deprecated_in="1.6.0",
    details="Use cloudevents.http.from_http function instead",
)
def from_http(
    headers: typing.Dict[str, str],
    data: typing.Optional[typing.AnyStr],
    data_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
) -> CloudEvent:
    return _moved_from_http(headers, data, data_unmarshaller)


@deprecated(deprecated_in="1.0.2", details="Use to_binary function instead")
def to_binary_http(
    event: CloudEvent, data_marshaller: typing.Optional[types.MarshallerType] = None
) -> typing.Tuple[typing.Dict[str, str], bytes]:
    return _moved_to_binary(event, data_marshaller)


@deprecated(deprecated_in="1.0.2", details="Use to_structured function instead")
def to_structured_http(
    event: CloudEvent, data_marshaller: typing.Optional[types.MarshallerType] = None
) -> typing.Tuple[typing.Dict[str, str], bytes]:
    return _moved_to_structured(event, data_marshaller)
