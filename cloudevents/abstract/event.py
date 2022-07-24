import typing
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

    @property
    def attributes(self) -> typing.Dict[str, typing.Any]:
        """
        :return: Attributes of this event.

        You MUST NOT mutate this dict.
        Implementation MAY assume the dict will not be mutated.
        """
        raise NotImplementedError()

    @property
    def data(self) -> typing.Optional[typing.Any]:
        """
        :return: Data value of the  event.
        You MUST NOT mutate this dict.
        Implementation MAY assume the dict will not be mutated.
        """
        raise NotImplementedError()

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, CloudEvent):
            return self.data == other.data and self.attributes == other.attributes
        return False

    def __getitem__(self, key: str) -> typing.Any:
        """
        Data access is handled via `.data` member
        Attribute access is managed via Mapping type
        :param key: The event attribute name.
        :return: The event attribute value.
        """
        return self.attributes[key]

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
        return self.attributes.get(key, default)

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self.attributes)

    def __len__(self) -> int:
        return len(self.attributes)

    def __contains__(self, key: str) -> bool:
        return key in self.attributes

    def __repr__(self) -> str:
        return str({"attributes": self.attributes, "data": self.data})


AnyCloudEvent = TypeVar("AnyCloudEvent", bound=CloudEvent)
