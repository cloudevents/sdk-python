# All Rights Reserved.
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

import typing

from cloudevents.sdk.converters import binary, structured

TypeBinary = binary.BinaryHTTPCloudEventConverter.TYPE
TypeStructured = structured.JSONHTTPCloudEventConverter.TYPE


def is_binary(headers: typing.Dict[str, str]) -> bool:
    """Uses internal marshallers to determine whether this event is binary
    :param headers: the HTTP headers
    :type headers: typing.Dict[str, str]
    :returns bool: returns a bool indicating whether the headers indicate a binary event type
    """
    headers = {key.lower(): value for key, value in headers.items()}
    content_type = headers.get("content-type", "")
    binary_parser = binary.BinaryHTTPCloudEventConverter()
    return binary_parser.can_read(content_type=content_type, headers=headers)


def is_structured(headers: typing.Dict[str, str]) -> bool:
    """Uses internal marshallers to determine whether this event is structured
    :param headers: the HTTP headers
    :type headers: typing.Dict[str, str]
    :returns bool: returns a bool indicating whether the headers indicate a structured event type
    """
    headers = {key.lower(): value for key, value in headers.items()}
    content_type = headers.get("content-type", "")
    structured_parser = structured.JSONHTTPCloudEventConverter()
    return structured_parser.can_read(
        content_type=content_type, headers=headers
    )
