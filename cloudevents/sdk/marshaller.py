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
from cloudevents.sdk.converters import binary
from cloudevents.sdk.converters import structured

from cloudevents.sdk.event import base as event_base


class HTTPMarshaller(object):

    def __init__(self, converters: typing.List[base.Converter]):
        self.__converters = converters

    def FromRequest(self, headers: dict, body: typing.IO):
        mimeType = headers.get("Content-Type")
        for cnvrtr in self.__converters:
            if cnvrtr.can_read(mimeType):
                return cnvrtr.read(headers, body)

        raise exceptions.InvalidMimeType(mimeType)

    def ToRequest(self, event: event_base.BaseEvent,
                  converter_type: str,
                  data_marshaller: typing.Callable) -> (dict, typing.IO):
        for cnvrtv in self.__converters:
            if converter_type == cnvrtv.TYPE:
                return cnvrtv.write(event, data_marshaller)


def NewDefaultHTTPMarshaller(
        event_class: event_base.BaseEvent) -> HTTPMarshaller:
    return HTTPMarshaller([
        structured.NewJSONHTTPCloudEventConverter(event_class),
        binary.NewBinaryHTTPCloudEventConverter(event_class),
    ])


def NewHTTPMarshaller(
        converters: typing.List[base.Converter]) -> HTTPMarshaller:
    return HTTPMarshaller(converters)
