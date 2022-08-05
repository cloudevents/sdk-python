import typing
from abc import abstractmethod
from typing import TypeVar


class CloudEvent:
    """
    The CloudEvent Python wrapper contract exposing generically-available
    properties and APIs.

    Implementations might handle fields and have other APIs exposed but are
    obliged to follow this contract.
    """

    @classmethod
    def create(
        cls,
        attributes: typing.Dict[str, typing.Any],
        data: typing.Optional[typing.Any],
    ) -> "AnyCloudEvent":
        """
        Factory function.
        We SHOULD NOT use the __init__ function as the factory because
        we MUST NOT assume how the __init__ function looks across different python
        frameworks
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_attributes(self) -> typing.Dict[str, typing.Any]:
        """
        :return: Attributes of this event.

        Implementation MUST assume the returned value MAY be mutated.

        The reason this function is not a property is to prevent possible issues
        with different frameworks that assumes behaviours for properties
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_data(self) -> typing.Optional[typing.Any]:
        """
        :return: Data value of the  event.

        Implementation MUST assume the returned value MAY be mutated.

        The reason this function is not a property is to prevent possible issues
        with different frameworks that assumes behaviours for properties
        """
        raise NotImplementedError()

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, CloudEvent):
            same_data = self._get_data() == other._get_data()
            same_attributes = self._get_attributes() == other._get_attributes()
            return same_data and same_attributes
        return False

    def __getitem__(self, key: str) -> typing.Any:
        """
        Data access is handled via `.data` member
        Attribute access is managed via Mapping type
        :param key: The event attribute name.
        :return: The event attribute value.
        """
        return self._get_attributes()[key]

    def get(
        self, key: str, default: typing.Optional[typing.Any] = None
    ) -> typing.Optional[typing.Any]:
        """
        Retrieves an event attribute value for the given key.
        Returns the default value if not attribute for the given key exists.

        MUST NOT throw an exception when the key does not exist.

        :param key: The event attribute name.
        :param default: The default value to be returned when
            no attribute with the given key exists.
        :returns: The event attribute value if exists, default value otherwise.
        """
        return self._get_attributes().get(key, default)

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self._get_attributes())

    def __len__(self) -> int:
        return len(self._get_attributes())

    def __contains__(self, key: str) -> bool:
        return key in self._get_attributes()

    def __repr__(self) -> str:
        return str({"attributes": self._get_attributes(), "data": self._get_data()})


AnyCloudEvent = TypeVar("AnyCloudEvent", bound=CloudEvent)
