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
        super().__init__("Validation errors occurred")
        self.errors: dict[str, list[BaseCloudEventException]] = errors

    def __str__(self) -> str:
        error_messages = [
            f"{key}: {', '.join(str(value))}" for key, value in self.errors.items()
        ]
        return f"{super().__str__()}: {', '.join(error_messages)}"


class MissingRequiredAttributeError(BaseCloudEventException):
    """
    Exception for missing required attribute.
    """

    def __init__(self, missing: str) -> None:
        super().__init__(f"Missing required attribute: '{missing}'")


class CustomExtensionAttributeError(BaseCloudEventException):
    """
    Exception for invalid custom extension names.
    """


class InvalidAttributeTypeError(BaseCloudEventException):
    """
    Exception for invalid attribute type.
    """
