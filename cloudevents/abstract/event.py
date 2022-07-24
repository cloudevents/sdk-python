import abc
import typing
from typing import TypeVar


class CloudEvent(abc.ABC):
    """
    Used internally for multi-framework event type integration
    """

    @classmethod
    @abc.abstractmethod
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
        pass

    @property
    @abc.abstractmethod
    def _attributes_read_model(self) -> typing.Dict[str, typing.Any]:
        """
        :return: attributes of this event

        you MUST NOT mutate this dict
        implementation MAY assume the dic will not be mutated
        """
        pass

    @property
    @abc.abstractmethod
    def _data_read_model(self) -> typing.Optional[typing.Any]:
        """
        :return: data value of the  event
        you MUST NOT mutate this value
        implementation MAY assume the value will not be mutated
        """
        pass

    def __setitem__(self, key: str, value: typing.Any) -> None:
        raise NotImplementedError()

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError()

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, CloudEvent):
            return (
                self._data_read_model == other._data_read_model
                and self._attributes_read_model == other._attributes_read_model
            )
        return False

    def __getitem__(self, key: str) -> typing.Any:
        """
        Data access is handled via `.data` member
        Attribute access is managed via Mapping type
        :param key: The event attribute name.
        :return: The event attribute value.
        """
        return self._attributes_read_model[key]

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
        return self._attributes_read_model.get(key, default)

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self._attributes_read_model)

    def __len__(self) -> int:
        return len(self._attributes_read_model)

    def __contains__(self, key: str) -> bool:
        return key in self._attributes_read_model

    def __repr__(self) -> str:
        return str(
            {"attributes": self._attributes_read_model, "data": self._data_read_model}
        )


AnyCloudEvent = TypeVar("AnyCloudEvent", bound=CloudEvent)
