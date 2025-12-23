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

_K_co = typing.TypeVar("_K_co", covariant=True)
_V_co = typing.TypeVar("_V_co", covariant=True)

# Use consistent types for marshal and unmarshal functions across
# both JSON and Binary format.

MarshallerType = typing.Callable[[typing.Any], typing.AnyStr]

UnmarshallerType = typing.Callable[[typing.AnyStr], typing.Any]


class SupportsDuplicateItems(typing.Protocol[_K_co, _V_co]):
    """
    Dict-like objects with an items() method that may produce duplicate keys.
    """

    # This is wider than _typeshed.SupportsItems, which expects items() to
    # return type an AbstractSet. werkzeug's Headers class satisfies this type,
    # but not _typeshed.SupportsItems.

    def items(self) -> typing.Iterable[typing.Tuple[_K_co, _V_co]]:
        pass
