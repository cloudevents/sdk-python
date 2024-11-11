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
class CloudEventValidationError(Exception):
    """
    Custom exception for validation errors.
    """

    def __init__(self, errors: dict[str, list[str]]) -> None:
        super().__init__("Validation errors occurred")
        self.errors: dict[str, list[str]] = errors

    def __str__(self) -> str:
        error_messages = [
            f"{key}: {', '.join(value)}" for key, value in self.errors.items()
        ]
        return f"{super().__str__()}: {', '.join(error_messages)}"
