import abc
import typing


class AbstractCloudEvent(abc.ABC):
    @property
    def _attributes_read_model(self) -> typing.Dict[str, typing.Any]:
        raise NotImplementedError()

    @property
    def data(self) -> typing.Optional[typing.Any]:
        raise NotImplementedError()

    @data.setter
    def data(self, value: typing.Optional[typing.Any]) -> None:
        raise NotImplementedError()

    def __setitem__(self, key: str, value: typing.Any) -> None:
        raise NotImplementedError()

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError()

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, AbstractCloudEvent):
            return (
                self.data == other.data
                and self._attributes_read_model == other._attributes_read_model
            )
        return False

    # Data access is handled via `.data` member
    # Attribute access is managed via Mapping type
    def __getitem__(self, key: str) -> typing.Any:
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
        return str({"attributes": self._attributes_read_model, "data": self.data})
