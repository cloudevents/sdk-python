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
from cloudevents.sdk.event import v01


class BinaryHTTPCloudEventConverter(base.Converter):

    TYPE = "binary"

    def __init__(self, event_class: event_base.BaseEvent,
                 supported_media_types: typing.Mapping[str, bool]):
        if event_class == v01.Event:
            raise exceptions.UnsupportedEvent(event_class)

        super().__init__(event_class, supported_media_types)

    def read(self,
             headers: dict, body: typing.IO,
             data_unmarshaller: typing.Callable) -> event_base.BaseEvent:
        # we ignore headers, since the whole CE is in request body
        event = self.event
        event.UnmarshalBinary(headers, body, data_unmarshaller)
        return event

    def write(self, event: event_base.BaseEvent,
              data_marshaller: typing.Callable) -> (dict, typing.IO):
        if not isinstance(data_marshaller, typing.Callable):
            raise exceptions.InvalidDataMarshaller()

        hs, data = event.MarshalBinary()
        return hs, data_marshaller(data)


def NewBinaryHTTPCloudEventConverter(
        event_class: event_base.BaseEvent) -> BinaryHTTPCloudEventConverter:
    media_types = {
        "application/json": True,
        "application/xml": True,
        "application/octet-stream": True,
    }
    return BinaryHTTPCloudEventConverter(event_class, media_types)
