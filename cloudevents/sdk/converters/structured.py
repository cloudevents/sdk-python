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

from cloudevents.sdk import types
from cloudevents.sdk.converters import base
from cloudevents.sdk.converters.util import has_binary_headers
from cloudevents.sdk.event import base as event_base


# TODO: Singleton?
class JSONHTTPCloudEventConverter(base.Converter):

    TYPE = "structured"
    MIME_TYPE = "application/cloudevents+json"

    def can_read(
        self, content_type: str, headers: typing.Dict[str, str] = {},
    ) -> bool:
        return (
            isinstance(content_type, str)
            and content_type.startswith(self.MIME_TYPE)
            or not has_binary_headers(headers)
        )

    def event_supported(self, event: object) -> bool:
        # structured format supported by both spec 0.1 and 0.2
        return True

    def read(
        self,
        event: event_base.BaseEvent,
        headers: dict,
        body: typing.IO,
        data_unmarshaller: types.UnmarshallerType,
    ) -> event_base.BaseEvent:
        event.UnmarshalJSON(body, data_unmarshaller)
        return event

    def write(
        self, event: event_base.BaseEvent, data_marshaller: types.MarshallerType
    ) -> (dict, bytes):
        http_headers = {"content-type": self.MIME_TYPE}
        return http_headers, event.MarshalJSON(data_marshaller).encode("utf-8")


def NewJSONHTTPCloudEventConverter() -> JSONHTTPCloudEventConverter:
    return JSONHTTPCloudEventConverter()
