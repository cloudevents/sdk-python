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

import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Final, Optional

from cloudevents.core.v1.exceptions import (
    BaseCloudEventException,
    CloudEventValidationError,
    CustomExtensionAttributeError,
    InvalidAttributeTypeError,
    MissingRequiredAttributeError,
)

REQUIRED_ATTRIBUTES: Final[list[str]] = ["id", "source", "type", "specversion"]
OPTIONAL_ATTRIBUTES: Final[list[str]] = [
    "datacontenttype",
    "dataschema",
    "subject",
    "time",
]


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
        self._attributes: dict[str, Any] = attributes
        self._data: Optional[dict] = data

    @staticmethod
    def _validate_attribute(attributes: dict[str, Any]) -> None:
        """
        Validates the attributes of the CloudEvent as per the CloudEvents specification.

        See https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md#required-attributes
        """
        errors: dict[str, list] = defaultdict(list)
        errors.update(CloudEvent._validate_required_attributes(attributes))
        errors.update(CloudEvent._validate_optional_attributes(attributes))
        errors.update(CloudEvent._validate_extension_attributes(attributes))
        if errors:
            raise CloudEventValidationError(dict(errors))

    @staticmethod
    def _validate_required_attributes(
        attributes: dict[str, Any],
    ) -> dict[str, list[BaseCloudEventException]]:
        """
        Validates the types of the required attributes.

        :param attributes: The attributes of the CloudEvent instance.
        :return: A dictionary of validation error messages.
        """
        errors = defaultdict(list)

        if "id" not in attributes:
            errors["id"].append(MissingRequiredAttributeError(missing="id"))
        if attributes.get("id") is None:
            errors["id"].append(
                InvalidAttributeTypeError("Attribute 'id' must not be None")
            )
        if not isinstance(attributes.get("id"), str):
            errors["id"].append(
                InvalidAttributeTypeError("Attribute 'id' must be a string")
            )

        if "source" not in attributes:
            errors["source"].append(MissingRequiredAttributeError(missing="source"))
        if not isinstance(attributes.get("source"), str):
            errors["source"].append(
                InvalidAttributeTypeError("Attribute 'source' must be a string")
            )

        if "type" not in attributes:
            errors["type"].append(MissingRequiredAttributeError(missing="type"))
        if not isinstance(attributes.get("type"), str):
            errors["type"].append(
                InvalidAttributeTypeError("Attribute 'type' must be a string")
            )

        if "specversion" not in attributes:
            errors["specversion"].append(
                MissingRequiredAttributeError(missing="specversion")
            )
        if not isinstance(attributes.get("specversion"), str):
            errors["specversion"].append(
                InvalidAttributeTypeError("Attribute 'specversion' must be a string")
            )
        if attributes.get("specversion") != "1.0":
            errors["specversion"].append(
                InvalidAttributeTypeError("Attribute 'specversion' must be '1.0'")
            )
        return errors

    @staticmethod
    def _validate_optional_attributes(
        attributes: dict[str, Any],
    ) -> dict[str, list[BaseCloudEventException]]:
        """
        Validates the types and values of the optional attributes.

        :param attributes: The attributes of the CloudEvent instance.
        :return: A dictionary of validation error messages.
        """
        errors = defaultdict(list)

        if "time" in attributes:
            if not isinstance(attributes["time"], datetime):
                errors["time"].append(
                    InvalidAttributeTypeError(
                        "Attribute 'time' must be a datetime object"
                    )
                )
            if hasattr(attributes["time"], "tzinfo") and not attributes["time"].tzinfo:
                errors["time"].append(
                    InvalidAttributeTypeError("Attribute 'time' must be timezone aware")
                )
        if "subject" in attributes:
            if not isinstance(attributes["subject"], str):
                errors["subject"].append(
                    InvalidAttributeTypeError("Attribute 'subject' must be a string")
                )
            if not attributes["subject"]:
                errors["subject"].append(
                    InvalidAttributeTypeError("Attribute 'subject' must not be empty")
                )
        if "datacontenttype" in attributes:
            if not isinstance(attributes["datacontenttype"], str):
                errors["datacontenttype"].append(
                    InvalidAttributeTypeError(
                        "Attribute 'datacontenttype' must be a string"
                    )
                )
            if not attributes["datacontenttype"]:
                errors["datacontenttype"].append(
                    InvalidAttributeTypeError(
                        "Attribute 'datacontenttype' must not be empty"
                    )
                )
        if "dataschema" in attributes:
            if not isinstance(attributes["dataschema"], str):
                errors["dataschema"].append(
                    InvalidAttributeTypeError("Attribute 'dataschema' must be a string")
                )
            if not attributes["dataschema"]:
                errors["dataschema"].append(
                    InvalidAttributeTypeError(
                        "Attribute 'dataschema' must not be empty"
                    )
                )
        return errors

    @staticmethod
    def _validate_extension_attributes(
        attributes: dict[str, Any],
    ) -> dict[str, list[BaseCloudEventException]]:
        """
        Validates the extension attributes.

        :param attributes: The attributes of the CloudEvent instance.
        :return: A dictionary of validation error messages.
        """
        errors = defaultdict(list)
        extension_attributes = [
            key
            for key in attributes.keys()
            if key not in REQUIRED_ATTRIBUTES and key not in OPTIONAL_ATTRIBUTES
        ]
        for extension_attribute in extension_attributes:
            if extension_attribute == "data":
                errors[extension_attribute].append(
                    CustomExtensionAttributeError(
                        "Extension attribute 'data' is reserved and must not be used"
                    )
                )
            if not (1 <= len(extension_attribute) <= 20):
                errors[extension_attribute].append(
                    CustomExtensionAttributeError(
                        f"Extension attribute '{extension_attribute}' should be between 1 and 20 characters long"
                    )
                )
            if not re.match(r"^[a-z0-9]+$", extension_attribute):
                errors[extension_attribute].append(
                    CustomExtensionAttributeError(
                        f"Extension attribute '{extension_attribute}' should only contain lowercase letters and numbers"
                    )
                )
        return errors

    def get_id(self) -> str:
        """
        Retrieve the ID of the event.

        :return: The ID of the event.
        """
        return self._attributes["id"]  # type: ignore

    def get_source(self) -> str:
        """
        Retrieve the source of the event.

        :return: The source of the event.
        """
        return self._attributes["source"]  # type: ignore

    def get_type(self) -> str:
        """
        Retrieve the type of the event.

        :return: The type of the event.
        """
        return self._attributes["type"]  # type: ignore

    def get_specversion(self) -> str:
        """
        Retrieve the specversion of the event.

        :return: The specversion of the event.
        """
        return self._attributes["specversion"]  # type: ignore

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

    def get_extension(self, extension_name: str) -> Any:
        """
        Retrieve an extension attribute of the event.

        :param extension_name: The name of the extension attribute.
        :return: The value of the extension attribute.
        """
        return self._attributes.get(extension_name)

    def get_data(self) -> Optional[dict]:
        """
        Retrieve data of the event.

        :return: The data of the event.
        """
        return self._data
