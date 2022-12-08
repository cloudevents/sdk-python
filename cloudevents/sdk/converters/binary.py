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

import typing

from cloudevents.sdk import exceptions, types
from cloudevents.sdk.converters import base
from cloudevents.sdk.converters.util import has_binary_headers
from cloudevents.sdk.event import base as event_base
from cloudevents.sdk.event import v1, v03


class BinaryHTTPCloudEventConverter(base.Converter):
    TYPE: str = "binary"
    SUPPORTED_VERSIONS = [v03.Event, v1.Event]

    def can_read(
        self,
        content_type: typing.Optional[str] = None,
        headers: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> bool:

        if headers is None:
            headers = {"ce-specversion": ""}
        return has_binary_headers(headers)

    def event_supported(self, event: object) -> bool:
        return type(event) in self.SUPPORTED_VERSIONS

    def read(
        self,
        event: event_base.BaseEvent,
        headers: typing.Mapping[str, str],
        body: typing.Union[str, bytes],
        data_unmarshaller: types.UnmarshallerType,
    ) -> event_base.BaseEvent:
        if type(event) not in self.SUPPORTED_VERSIONS:
            raise exceptions.UnsupportedEvent(type(event))
        event.UnmarshalBinary(headers, body, data_unmarshaller)
        return event

    def write(
        self,
        event: event_base.BaseEvent,
        data_marshaller: typing.Optional[types.MarshallerType],
    ) -> typing.Tuple[typing.Dict[str, str], bytes]:
        return event.MarshalBinary(data_marshaller)


def NewBinaryHTTPCloudEventConverter() -> BinaryHTTPCloudEventConverter:
    return BinaryHTTPCloudEventConverter()


def is_binary(headers: typing.Mapping[str, str]) -> bool:
    """
    Determines whether an event with the supplied `headers` is in binary format.

    :param headers: The HTTP headers of a potential event.
    :returns: Returns a bool indicating whether the headers indicate
        a binary event type.
    """
    headers = {key.lower(): value for key, value in headers.items()}
    content_type = headers.get("content-type", "")
    binary_parser = BinaryHTTPCloudEventConverter()
    return binary_parser.can_read(content_type=content_type, headers=headers)
