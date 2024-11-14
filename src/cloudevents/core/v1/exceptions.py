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
class BaseCloudEventException(Exception):
    """A CloudEvent generic exception."""

    pass


class CloudEventValidationError(BaseCloudEventException):
    """
    Holds validation errors aggregated during a CloudEvent creation.
    """

    def __init__(self, errors: dict[str, list[BaseCloudEventException]]) -> None:
        """
        :param errors: The errors gathered during the CloudEvent creation where key
            is the name of the attribute and value is a list of errors related to that attribute.
        """
        super().__init__("Failed to create CloudEvent due to the validation errors:")
        self.errors: dict[str, list[BaseCloudEventException]] = errors

    def __str__(self) -> str:
        error_messages = [
            f"{key}: {', '.join(str(value))}" for key, value in self.errors.items()
        ]
        return f"{super().__str__()}: {', '.join(error_messages)}"


class MissingRequiredAttributeError(BaseCloudEventException, ValueError):
    """
    Raised for attributes that are required to be present by the specification.
    """

    def __init__(self, attribute_name: str) -> None:
        super().__init__(f"Missing required attribute: '{attribute_name}'")


class CustomExtensionAttributeError(BaseCloudEventException, ValueError):
    """
    Raised when a custom extension attribute violates naming conventions.
    """

    def __init__(self, extension_attribute: str, msg: str) -> None:
        self.extension_attribute = extension_attribute
        super().__init__(msg)


class InvalidAttributeTypeError(BaseCloudEventException, TypeError):
    """
    Raised when an attribute has an unsupported type.
    """

    def __init__(self, attribute_name: str, expected_type: type) -> None:
        self.attribute_name = attribute_name
        super().__init__(f"Attribute '{attribute_name}' must be a {expected_type}")


class InvalidAttributeValueError(BaseCloudEventException, ValueError):
    """
    Raised when an attribute has an invalid value.
    """

    def __init__(self, attribute_name: str, msg: str) -> None:
        self.attribute_name = attribute_name
        super().__init__(msg)
