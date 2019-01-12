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

    def read(self, event: event_base.BaseEvent,
             headers: dict,
             body: typing.IO,
             data_unmarshaller: typing.Callable) -> event_base.BaseEvent:
        # Note: this is fragile for true dictionaries which don't implement
        # case-insensitive header mappings. HTTP/1.1 specifies that headers
        #  are case insensitive, so this usually affects tests.
        if not headers.get("Content-Type", "").startswith("application/cloudevents+json"):
            raise exceptions.UnsupportedEvent(
                "Structured mode must be application/cloudevents+json, not {0}".format(headers.get("content-type")))
        event.UnmarshalJSON(body, data_unmarshaller)
        return event

    def write(self,
              event: event_base.BaseEvent,
              data_marshaller: typing.Callable) -> (dict, typing.IO):
        if not isinstance(data_marshaller, typing.Callable):
            raise exceptions.InvalidDataMarshaller()

        return {}, event.MarshalJSON(data_marshaller)


def NewJSONHTTPCloudEventConverter() -> JSONHTTPCloudEventConverter:
    return JSONHTTPCloudEventConverter()
