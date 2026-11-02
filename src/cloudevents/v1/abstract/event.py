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

    A CloudEvent describes event data in a common, vendor-neutral way, as
    defined by the CloudEvents specification
    (https://github.com/cloudevents/spec). Every event is made of two
    distinct parts:

    - Attributes (also called context attributes): metadata describing the
      event. The CloudEvents v1.0 specification defines the required
      attributes `id`, `source`, `type` and `specversion`, together with the
      optional attributes `datacontenttype`, `dataschema`, `subject` and
      `time`. Concrete implementations may also carry user-defined extension
      attributes.
    - Data: the optional event payload. The payload is not an attribute and is
      kept separate from the attribute mapping.

    This class only defines the read-only contract shared by every concrete
    implementation (for example `cloudevents.v1.http.CloudEvent` or the
    Pydantic variants). It is abstract and cannot be instantiated directly;
    use a concrete subclass or its `create` factory instead.

    Attributes can be read through a read-only, mapping-like interface
    (`__getitem__`, `get`, `__iter__`, `__len__` and `__contains__`). That
    interface exposes the attributes only: the event `data` is never part of
    it and must be read through the `.data` accessor (or `get_data`). This is
    why `event["data"]` raises a `KeyError` and `event.get("data")` returns the
    default instead of the payload.

    Example:
        >>> from cloudevents.v1.http import CloudEvent
        >>> event = CloudEvent(
        ...     {
        ...         "type": "com.example.sampletype1",
        ...         "source": "https://example.com/event-producer",
        ...     },
        ...     {"message": "Hello World!"},
        ... )
        >>> event["type"]
        'com.example.sampletype1'
        >>> event.data
        {'message': 'Hello World!'}
        >>> "data" in event  # `data` is the payload, not an attribute
        False

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

        This mapping-style accessor exposes the event's context attributes
        only. The event `data` (its payload) is not an attribute and is
        deliberately not reachable this way; it must be read through the
        `.data` accessor (or `get_data`). Requesting `event["data"]` therefore
        raises a `KeyError` rather than returning the payload.

        :param key: The name of the event attribute to retrieve the value for.
        :returns: The event attribute value.
        :raises KeyError: If no attribute with the given `key` exists.
        """
        return self._get_attributes()[key]

    def get(
        self, key: str, default: typing.Optional[typing.Any] = None
    ) -> typing.Optional[typing.Any]:
        """
        Retrieves an event attribute value for the given `key`.

        Like `__getitem__`, this operates over the event's context attributes
        only and never over the event `data`; `event.get("data")` returns the
        `default` rather than the payload, which must be read through the
        `.data` accessor (or `get_data`).

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
