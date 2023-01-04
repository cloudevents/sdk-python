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

    def __init__(self, converters: typing.Sequence[base.Converter]):
        """
        CloudEvent HTTP marshaller constructor
        :param converters: a list of HTTP-to-CloudEvent-to-HTTP constructors
        """
        self.http_converters: typing.List[base.Converter] = [c for c in converters]
        self.http_converters_by_type: typing.Dict[str, base.Converter] = {
            c.TYPE: c for c in converters
        }

    def FromRequest(
        self,
        event: event_base.BaseEvent,
        headers: typing.Mapping[str, str],
        body: typing.Union[str, bytes],
        data_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
    ) -> event_base.BaseEvent:
        """
        Reads a CloudEvent from an HTTP headers and request body
        :param event: CloudEvent placeholder
        :param headers: a dict-like HTTP headers
        :param body: an HTTP request body as a string or bytes
        :param data_unmarshaller: a callable-like unmarshaller the CloudEvent data
        :return: a CloudEvent
        """
        if not data_unmarshaller:
            data_unmarshaller = json.loads
        if not callable(data_unmarshaller):
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
        converter_type: typing.Optional[str] = None,
        data_marshaller: typing.Optional[types.MarshallerType] = None,
    ) -> typing.Tuple[typing.Dict[str, str], bytes]:
        """
        Writes a CloudEvent into a HTTP-ready form of headers and request body
        :param event: CloudEvent
        :param converter_type: a type of CloudEvent-to-HTTP converter
        :param data_marshaller: a callable-like marshaller CloudEvent data
        :return: dict of HTTP headers and stream of HTTP request body
        """
        if data_marshaller is not None and not callable(data_marshaller):
            raise exceptions.InvalidDataMarshaller()

        if converter_type is None:
            converter_type = self.http_converters[0].TYPE

        if converter_type in self.http_converters_by_type:
            cnvrtr = self.http_converters_by_type[converter_type]
            return cnvrtr.write(event, data_marshaller)

        raise exceptions.NoSuchConverter(converter_type)


def NewDefaultHTTPMarshaller() -> HTTPMarshaller:
    """
    Creates the default HTTP marshaller with both structured and binary converters.

    :return: an instance of HTTP marshaller
    """
    return HTTPMarshaller(
        [
            structured.NewJSONHTTPCloudEventConverter(),
            binary.NewBinaryHTTPCloudEventConverter(),
        ]
    )


def NewHTTPMarshaller(
    converters: typing.Sequence[base.Converter],
) -> HTTPMarshaller:
    """
    Creates the default HTTP marshaller with both structured and binary converters.

    :param converters: a list of CloudEvent-to-HTTP-to-CloudEvent converters

    :return: an instance of HTTP marshaller
    """
    return HTTPMarshaller(converters)
