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

from typing import Any, Optional
from datetime import datetime

REQUIRED_ATTRIBUTES = {"id", "source", "type", "specversion"}
OPTIONAL_ATTRIBUTES = {"datacontenttype", "dataschema", "subject", "time"}


class CloudEvent:
    def __init__(self, attributes: dict, data: Optional[dict] = None) -> 'CloudEvent':
        """
        Create a new CloudEvent instance.

        :param attributes: The attributes of the CloudEvent instance.
        :type attributes: dict
        :param data: The payload of the CloudEvent instance.
        :type data: Optional[dict]

        :raises ValueError: If any of the required attributes are missing or have invalid values.
        :raises TypeError: If any of the attributes have invalid types.
        """
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

    def get_attribute(self, attribute: str) -> Optional[Any]:
        """
        Retrieve a value of an attribute of the event denoted by the given `attribute`.
        
        :param attribute: The name of the event attribute to retrieve the value for.
        :type attribute: str
        
        :return: The event attribute value.
        :rtype: Optional[Any]
        """
        return self._attributes[attribute]

    def get_data(self) -> Optional[dict]:
        """
        Retrieve data of the event.

        :return: The data of the event.
        :rtype: Optional[dict]
        """
        return self._data
