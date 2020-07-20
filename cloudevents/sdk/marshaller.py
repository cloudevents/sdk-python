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

import json
import typing

from cloudevents.sdk import exceptions, types
from cloudevents.sdk.converters import base, binary, structured
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
        self.http_converters = [c for c in converters]
        self.http_converters_by_type = {c.TYPE: c for c in converters}

    def FromRequest(
        self,
        event: event_base.BaseEvent,
        headers: dict,
        body: typing.Union[str, bytes],
        data_unmarshaller: types.UnmarshallerType = json.loads,
    ) -> event_base.BaseEvent:
        """
        Reads a CloudEvent from an HTTP headers and request body
        :param event: CloudEvent placeholder
        :type event: cloudevents.sdk.event.base.BaseEvent
        :param headers: a dict-like HTTP headers
        :type headers: dict
        :param body: an HTTP request body as a string or bytes
        :type body: typing.Union[str, bytes]
        :param data_unmarshaller: a callable-like
                                  unmarshaller the CloudEvent data
        :return: a CloudEvent
        :rtype: event_base.BaseEvent
        """
        if not isinstance(data_unmarshaller, typing.Callable):
            raise exceptions.InvalidDataUnmarshaller()

        # Lower all header keys
        headers = {key.lower(): value for key, value in headers.items()}
        content_type = headers.get("content-type", None)

        for cnvrtr in self.http_converters:
            if cnvrtr.can_read(
                content_type, headers=headers
            ) and cnvrtr.event_supported(event):
                return cnvrtr.read(event, headers, body, data_unmarshaller)

        raise exceptions.UnsupportedEventConverter(
            "No registered marshaller for {0} in {1}".format(
                content_type, self.http_converters
            )
        )

    def ToRequest(
        self,
        event: event_base.BaseEvent,
        converter_type: str = None,
        data_marshaller: types.MarshallerType = None,
    ) -> (dict, bytes):
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
        if data_marshaller is not None and not isinstance(
            data_marshaller, typing.Callable
        ):
            raise exceptions.InvalidDataMarshaller()

        if converter_type is None:
            converter_type = self.http_converters[0].TYPE

        if converter_type in self.http_converters_by_type:
            cnvrtr = self.http_converters_by_type[converter_type]
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
    converters: typing.List[base.Converter],
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
