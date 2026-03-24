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
from abc import abstractmethod
from types import MappingProxyType
from typing import Mapping

AnyCloudEvent = typing.TypeVar("AnyCloudEvent", bound="CloudEvent")


class CloudEvent:
    """
    The CloudEvent Python wrapper contract exposing generically-available
    properties and APIs.

    Implementations might handle fields and have other APIs exposed but are
    obliged to follow this contract.
    """

    @classmethod
    def create(
        cls: typing.Type[AnyCloudEvent],
        attributes: typing.Mapping[str, typing.Any],
        data: typing.Optional[typing.Any],
    ) -> AnyCloudEvent:
        """
        Creates a new instance of the CloudEvent using supplied `attributes`
        and `data`.

        This method should be preferably used over the constructor to create events
        while custom framework-specific implementations may require or assume
        different arguments.

        :param attributes: The attributes of the CloudEvent instance.
        :param data: The payload of the CloudEvent instance.
        :returns: A new instance of the CloudEvent created from the passed arguments.
        """
        raise NotImplementedError()

    def get_attributes(self) -> Mapping[str, typing.Any]:
        """
        Returns a read-only view on the attributes of the event.

        :returns: Read-only view on the attributes of the event.
        """
        return MappingProxyType(self._get_attributes())

    @abstractmethod
    def _get_attributes(self) -> typing.Dict[str, typing.Any]:
        """
        Returns the attributes of the event.

        The implementation MUST assume that the returned value MAY be mutated.

        Having a function over a property simplifies integration for custom
        framework-specific implementations.

        :returns: Attributes of the event.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_data(self) -> typing.Optional[typing.Any]:
        """
        Returns the data of the event.

        The implementation MUST assume that the returned value MAY be mutated.

        Having a function over a property simplifies integration for custom
        framework-specific implementations.

        :returns: Data of the event.
        """
        raise NotImplementedError()

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, CloudEvent):
            same_data = self.get_data() == other.get_data()
            same_attributes = self._get_attributes() == other._get_attributes()
            return same_data and same_attributes
        return False

    def __getitem__(self, key: str) -> typing.Any:
        """
        Returns a value of an attribute of the event denoted by the given `key`.

        The `data` of the event should be accessed by the `.data` accessor rather
        than this mapping.

        :param key: The name of the event attribute to retrieve the value for.
        :returns: The event attribute value.
        """
        return self._get_attributes()[key]

    def get(
        self, key: str, default: typing.Optional[typing.Any] = None
    ) -> typing.Optional[typing.Any]:
        """
        Retrieves an event attribute value for the given `key`.

        Returns the `default` value if the attribute for the given key does not exist.

        The implementation MUST NOT throw an error when the key does not exist, but
        rather should return `None` or the configured `default`.

        :param key: The name of the event attribute to retrieve the value for.
        :param default: The default value to be returned when
            no attribute with the given key exists.
        :returns: The event attribute value if exists, default value or None otherwise.
        """
        return self._get_attributes().get(key, default)

    def __iter__(self) -> typing.Iterator[typing.Any]:
        """
        Returns an iterator over the event attributes.
        """
        return iter(self._get_attributes())

    def __len__(self) -> int:
        """
        Returns the number of the event attributes.
        """
        return len(self._get_attributes())

    def __contains__(self, key: str) -> bool:
        """
        Determines if an attribute with a given `key` is present
        in the event attributes.
        """
        return key in self._get_attributes()

    def __repr__(self) -> str:
        return str({"attributes": self._get_attributes(), "data": self.get_data()})
