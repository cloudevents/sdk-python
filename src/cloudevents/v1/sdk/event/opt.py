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
from typing import Any


class Option:
    """A value holder of CloudEvents extensions."""

    def __init__(self, name: str, value: typing.Optional[Any], is_required: bool):
        self.name: str = name
        """The name of the option."""
        self.value: Any = value
        """The value of the option."""
        self.is_required: bool = is_required
        """Determines if the option value must be present."""

    def set(self, new_value: typing.Optional[Any]) -> None:
        """Sets given new value as the value of this option."""
        is_none = new_value is None
        if self.is_required and is_none:
            raise ValueError(
                "Attribute value error: '{0}', invalid new value.".format(self.name)
            )
        self.value = new_value

    def get(self) -> typing.Optional[Any]:
        """Returns the value of this option."""
        return self.value

    def required(self):
        """Determines if the option value must be present."""
        return self.is_required

    def __eq__(self, obj):
        return (
            isinstance(obj, Option)
            and obj.name == self.name
            and obj.value == self.value
            and obj.is_required == self.is_required
        )
