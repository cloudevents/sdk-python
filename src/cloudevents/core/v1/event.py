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

from typing import Any, Optional, Final
from datetime import datetime
import re

REQUIRED_ATTRIBUTES: Final[set[str]] = {"id", "source", "type", "specversion"}
OPTIONAL_ATTRIBUTES: Final[set[str]] = {
    "datacontenttype",
    "dataschema",
    "subject",
    "time",
}


class CloudEvent:
    """
    The CloudEvent Python wrapper contract exposing generically-available
    properties and APIs.

    Implementations might handle fields and have other APIs exposed but are
    obliged to follow this contract.
    """

    def __init__(self, attributes: dict[str, Any], data: Optional[dict] = None) -> None:
        """
        Create a new CloudEvent instance.

        :param attributes: The attributes of the CloudEvent instance.
        :param data: The payload of the CloudEvent instance.

        :raises ValueError: If any of the required attributes are missing or have invalid values.
        :raises TypeError: If any of the attributes have invalid types.
        """
        self._validate_attribute(attributes)
        self._attributes: dict = attributes
        self._data: Optional[dict] = data

    @staticmethod
    def _validate_attribute(attributes: dict) -> None:
        """
        Validates the attributes of the CloudEvent as per the CloudEvents specification.

        See https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md#required-attributes
        """
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

        for extension_attributes in (
            set(attributes.keys()) - REQUIRED_ATTRIBUTES - OPTIONAL_ATTRIBUTES
        ):
            if extension_attributes == "data":
                raise ValueError(
                    "Extension attribute 'data' is reserved and must not be used"
                )

            if not (1 <= len(extension_attributes) <= 20):
                raise ValueError(
                    f"Extension attribute '{extension_attributes}' should be between 1 and 20 characters long"
                )

            if not re.match(r"^[a-z0-9]+$", extension_attributes):
                raise ValueError(
                    f"Extension attribute '{extension_attributes}' should only contain lowercase letters and numbers"
                )

    def get_id(self) -> str:
        """
        Retrieve the ID of the event.

        :return: The ID of the event.
        """
        return self._attributes["id"]

    def get_source(self) -> str:
        """
        Retrieve the source of the event.

        :return: The source of the event.
        """
        return self._attributes["source"]

    def get_type(self) -> str:
        """
        Retrieve the type of the event.

        :return: The type of the event.
        """
        return self._attributes["type"]

    def get_specversion(self) -> str:
        """
        Retrieve the specversion of the event.

        :return: The specversion of the event.
        """
        return self._attributes["specversion"]

    def get_datacontenttype(self) -> Optional[str]:
        """
        Retrieve the datacontenttype of the event.

        :return: The datacontenttype of the event.
        """
        return self._attributes.get("datacontenttype")

    def get_dataschema(self) -> Optional[str]:
        """
        Retrieve the dataschema of the event.

        :return: The dataschema of the event.
        """
        return self._attributes.get("dataschema")

    def get_subject(self) -> Optional[str]:
        """
        Retrieve the subject of the event.

        :return: The subject of the event.
        """
        return self._attributes.get("subject")

    def get_time(self) -> Optional[datetime]:
        """
        Retrieve the time of the event.

        :return: The time of the event.
        """
        return self._attributes.get("time")

    def get_data(self) -> Optional[dict]:
        """
        Retrieve data of the event.

        :return: The data of the event.
        """
        return self._data
