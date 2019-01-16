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
    """
    HTTP Marshaller class.
    API of this class designed to work with CloudEvent (upstream and v0.1)
    """

    def __init__(self, converters: typing.List[base.Converter]):
        """
        CloudEvent HTTP marshaller constructor
        :param converters: a list of HTTP-to-CloudEvent-to-HTTP constructors
        :type converters: typing.List[base.Converter]
        """
        self.__converters = [c for c in converters]
        self.__converters_by_type = {c.TYPE: c for c in converters}

    def FromRequest(
        self,
        event: event_base.BaseEvent,
        headers: dict,
        body: typing.IO,
        data_unmarshaller: typing.Callable,
    ) -> event_base.BaseEvent:
        """
        Reads a CloudEvent from an HTTP headers and request body
        :param event: CloudEvent placeholder
        :type event: cloudevents.sdk.event.base.BaseEvent
        :param headers: a dict-like HTTP headers
        :type headers: dict
        :param body: a stream-like HTTP request body
        :type body: typing.IO
        :param data_unmarshaller: a callable-like
                                  unmarshaller the CloudEvent data
        :return: a CloudEvent
        :rtype: event_base.BaseEvent
        """
        if not isinstance(data_unmarshaller, typing.Callable):
            raise exceptions.InvalidDataUnmarshaller()

        content_type = headers.get("content-type", headers.get("Content-Type"))

        for cnvrtr in self.__converters:
            if cnvrtr.can_read(content_type) and cnvrtr.event_supported(event):
                return cnvrtr.read(event, headers, body, data_unmarshaller)

        raise exceptions.UnsupportedEventConverter(
            "No registered marshaller for {0} in {1}".format(
                content_type, self.__converters
            )
        )

    def ToRequest(
        self,
        event: event_base.BaseEvent,
        converter_type: str,
        data_marshaller: typing.Callable,
    ) -> (dict, typing.IO):
        """
        Writes a CloudEvent into a HTTP-ready form of headers and request body
        :param event: CloudEvent
        :type event: event_base.BaseEvent
        :param converter_type: a type of CloudEvent-to-HTTP converter
        :type converter_type: str
        :param data_marshaller: a callable-like marshaller CloudEvent data
        :type data_marshaller: typing.Callable
        :return: dict of HTTP headers and stream of HTTP request body
        :rtype: tuple
        """
        if not isinstance(data_marshaller, typing.Callable):
            raise exceptions.InvalidDataMarshaller()

        if converter_type in self.__converters_by_type:
            cnvrtr = self.__converters_by_type[converter_type]
            return cnvrtr.write(event, data_marshaller)

        raise exceptions.NoSuchConverter(converter_type)


def NewDefaultHTTPMarshaller() -> HTTPMarshaller:
    """
    Creates the default HTTP marshaller with both structured
        and binary converters
    :return: an instance of HTTP marshaller
    :rtype: cloudevents.sdk.marshaller.HTTPMarshaller
    """
    return HTTPMarshaller(
        [
            structured.NewJSONHTTPCloudEventConverter(),
            binary.NewBinaryHTTPCloudEventConverter(),
        ]
    )


def NewHTTPMarshaller(
        converters: typing.List[base.Converter]
) -> HTTPMarshaller:
    """
    Creates the default HTTP marshaller with both
        structured and binary converters
    :param converters: a list of CloudEvent-to-HTTP-to-CloudEvent converters
    :type converters: typing.List[base.Converter]
    :return: an instance of HTTP marshaller
    :rtype: cloudevents.sdk.marshaller.HTTPMarshaller
    """
    return HTTPMarshaller(converters)
