from typing import Optional
from datetime import datetime

REQUIRED_ATTRIBUTES = {"id", "source", "type", "specversion"}
OPTIONAL_ATTRIBUTES = {"datacontenttype", "dataschema", "subject", "time"}


class CloudEvent:
    def __init__(self, attributes: dict, data: Optional[dict] = None):
        self.__validate_attribute(attributes)
        self._attributes = attributes
        self._data = data

    def __validate_attribute(self, attributes: dict):
        missing_attributes = [
            attr for attr in REQUIRED_ATTRIBUTES if attr not in attributes
        ]
        if missing_attributes:
            raise ValueError(
                f"Missing required attribute(s): {', '.join(missing_attributes)}"
            )

        if attributes["id"] is None:
            raise ValueError("Attribute 'id' must not be None")
        if not isinstance(attributes["id"], str):
            raise TypeError("Attribute 'id' must be a string")

        if not isinstance(attributes["source"], str):
            raise TypeError("Attribute 'source' must be a string")

        if not isinstance(attributes["type"], str):
            raise TypeError("Attribute 'type' must be a string")

        if not isinstance(attributes["specversion"], str):
            raise TypeError("Attribute 'specversion' must be a string")
        if attributes["specversion"] != "1.0":
            raise ValueError("Attribute 'specversion' must be '1.0'")

        if "time" in attributes:
            if not isinstance(attributes["time"], datetime):
                raise TypeError("Attribute 'time' must be a datetime object")

            if not attributes["time"].tzinfo:
                raise ValueError("Attribute 'time' must be timezone aware")

        if "subject" in attributes:
            if not isinstance(attributes["subject"], str):
                raise TypeError("Attribute 'subject' must be a string")

            if not attributes["subject"]:
                raise ValueError("Attribute 'subject' must not be empty")

        if "datacontenttype" in attributes:
            if not isinstance(attributes["datacontenttype"], str):
                raise TypeError("Attribute 'datacontenttype' must be a string")

            if not attributes["datacontenttype"]:
                raise ValueError("Attribute 'datacontenttype' must not be empty")

        if "dataschema" in attributes:
            if not isinstance(attributes["dataschema"], str):
                raise TypeError("Attribute 'dataschema' must be a string")

            if not attributes["dataschema"]:
                raise ValueError("Attribute 'dataschema' must not be empty")

    def get_attribute(self, attribute: str):
        return self._attributes[attribute]

    def get_data(self):
        return self._data
