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


class JSONHTTPCloudEventConverter(base.Converter):

    TYPE = "structured"

    def __init__(self, event_class: event_base.BaseEvent,
                 supported_media_types: typing.Mapping[str, bool]):
        super().__init__(event_class, supported_media_types)

    def read(self, headers: dict,
             body: typing.IO,
             data_unmarshaller: typing.Callable) -> event_base.BaseEvent:
        # we ignore headers, since the whole CE is in request body
        event = self.event
        event.UnmarshalJSON(body, data_unmarshaller)
        return event

    def write(self,
              event: event_base.BaseEvent,
              data_marshaller: typing.Callable) -> (dict, typing.IO):
        if not isinstance(data_marshaller, typing.Callable):
            raise exceptions.InvalidDataMarshaller()

        return {}, event.MarshalJSON(data_marshaller)


def NewJSONHTTPCloudEventConverter(
        event_class: event_base.BaseEvent) -> JSONHTTPCloudEventConverter:
    media_types = {
        "application/cloudevents+json": True,
    }

    return JSONHTTPCloudEventConverter(event_class, media_types)
