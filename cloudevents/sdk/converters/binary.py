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

from cloudevents.sdk import exceptions
from cloudevents.sdk.converters import base
from cloudevents.sdk.event import base as event_base
from cloudevents.sdk.event import v02


class BinaryHTTPCloudEventConverter(base.Converter):

    TYPE = "binary"
    SUPPORTED_VERSIONS = [v02.Event]

    def can_read(self, content_type: str) -> bool:
        return True

    def event_supported(self, event: object) -> bool:
        return type(event) in self.SUPPORTED_VERSIONS

    def read(
        self,
        event: event_base.BaseEvent,
        headers: dict,
        body: typing.IO,
        data_unmarshaller: typing.Callable,
    ) -> event_base.BaseEvent:
        if type(event) not in self.SUPPORTED_VERSIONS:
            raise exceptions.UnsupportedEvent(type(event))
        event.UnmarshalBinary(headers, body, data_unmarshaller)
        return event

    def write(
        self, event: event_base.BaseEvent, data_marshaller: typing.Callable
    ) -> (dict, typing.IO):
        return event.MarshalBinary(data_marshaller)


def NewBinaryHTTPCloudEventConverter() -> BinaryHTTPCloudEventConverter:
    return BinaryHTTPCloudEventConverter()
