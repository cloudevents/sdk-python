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

from cloudevents_v1.conversion import (
    _best_effort_serialize_to_json as _moved_default_marshaller,
)
from deprecation import deprecated

# THIS MODULE IS DEPRECATED, YOU SHOULD NOT ADD NEW FUNCTIONALLY HERE


@deprecated(
    deprecated_in="1.6.0",
    details="You SHOULD NOT use the default marshaller",
)
def default_marshaller(
    content: typing.Any,
) -> typing.Optional[typing.Union[bytes, str, typing.Any]]:
    return _moved_default_marshaller(content)
