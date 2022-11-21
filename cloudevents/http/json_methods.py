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
from cloudevents.conversion import to_json as _moved_to_json
from cloudevents.http import CloudEvent
from cloudevents.http.conversion import from_json as _moved_from_json
from cloudevents.sdk import types

# THIS MODULE IS DEPRECATED, YOU SHOULD NOT ADD NEW FUNCTIONALLY HERE


@deprecated(
    deprecated_in="1.6.0",
    details="Use cloudevents.conversion.to_json function instead",
)
def to_json(
    event: AnyCloudEvent,
    data_marshaller: typing.Optional[types.MarshallerType] = None,
) -> bytes:
    return _moved_to_json(event, data_marshaller)


@deprecated(
    deprecated_in="1.6.0",
    details="Use cloudevents.http.from_json function instead",
)
def from_json(
    data: typing.Union[str, bytes],
    data_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
) -> CloudEvent:
    return _moved_from_json(data, data_unmarshaller)
