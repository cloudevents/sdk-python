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

from cloudevents.sdk.converters import is_binary as _moved_is_binary
from cloudevents.sdk.converters import is_structured as _moved_is_structured

# THIS MODULE IS DEPRECATED, YOU SHOULD NOT ADD NEW FUNCTIONALLY HERE


@deprecated(
    deprecated_in="1.6.0",
    details="Use cloudevents.sdk.converters.is_binary function instead",
)
def is_binary(headers: typing.Dict[str, str]) -> bool:
    return _moved_is_binary(headers)


@deprecated(
    deprecated_in="1.6.0",
    details="Use cloudevents.sdk.converters.is_structured function instead",
)
def is_structured(headers: typing.Dict[str, str]) -> bool:
    return _moved_is_structured(headers)
