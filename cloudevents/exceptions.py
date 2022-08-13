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


class GenericException(Exception):
    pass


class MissingRequiredFields(GenericException):
    pass


class InvalidRequiredFields(GenericException):
    pass


class InvalidStructuredJSON(GenericException):
    pass


class InvalidHeadersFormat(GenericException):
    pass


class DataMarshallerError(GenericException):
    pass


class DataUnmarshallerError(GenericException):
    pass


class IncompatibleArgumentsError(GenericException):
    """
    Raised when a user tries to call a function with arguments which are incompatible
    with each other.
    """


class PydanticFeatureNotInstalled(GenericException):
    """
    Raised when a user tries to use the pydantic feature but did not install it.
    """
