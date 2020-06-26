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
import copy

import io

import json
import typing

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller

from cloudevents.sdk.event import v03, v1


class CloudEvent():
    """
    Python-friendly cloudevent class supporting v1 events
    Currently only supports binary content mode CloudEvents
    """

    def __init__(
            self,
            data: typing.Union[dict, None],
            headers: dict = {},
            data_unmarshaller: typing.Callable = lambda x: x,
    ):
        """
        Event HTTP Constructor
        :param data: a nullable dict to be stored inside Event.
        :type data: dict or None
        :param headers: a dict with HTTP headers
            e.g. {
                "content-type": "application/cloudevents+json",
                "ce-id": "16fb5f0b-211e-1102-3dfe-ea6e2806f124",
                "ce-source": "<event-source>",
                "ce-type": "cloudevent.event.type",
                "ce-specversion": "0.2"
            }
        :type headers: dict
        :param binary: a bool indicating binary events
        :type binary: bool
        :param data_unmarshaller: callable function for reading/extracting data
        :type data_unmarshaller: typing.Callable
        """
        self.required_attribute_values = {}
        self.optional_attribute_values = {}
        if data is None:
            data = {}

        headers = {key.lower(): value for key, value in headers.items()}
        data = {key.lower(): value for key, value in data.items()}

        # returns an event class depending on proper version
        event_version = CloudEvent.detect_event_version(headers, data)
        self.isbinary = CloudEvent.is_binary_cloud_event(
            event_version,
            headers
        )

        self.marshall = marshaller.NewDefaultHTTPMarshaller()
        self.event_handler = event_version()

        self.__event = self.marshall.FromRequest(
            self.event_handler,
            headers,
            io.BytesIO(json.dumps(data).encode()),
            data_unmarshaller
        )

        # headers validation for binary events
        for field in event_version._ce_required_fields:

            # prefixes with ce- if this is a binary event
            fieldname = CloudEvent.field_name_modifier(field, self.isbinary)

            # fields_refs holds a reference to where fields should be
            fields_refs = headers if self.isbinary else data

            fields_refs_name = 'headers' if self.isbinary else 'data'

            # verify field exists else throw TypeError
            if fieldname not in fields_refs:
                raise TypeError(
                    f"parameter {fields_refs_name} has no required "
                    f"attribute {fieldname}."
                )

            elif not isinstance(fields_refs[fieldname], str):
                raise TypeError(
                    f"in parameter {fields_refs_name}, {fieldname} "
                    f"expected type str but found type "
                    f"{type(fields_refs[fieldname])}."
                )

            else:
                self.required_attribute_values[f"ce-{field}"] = \
                    fields_refs[fieldname]

        for field in event_version._ce_optional_fields:
            fieldname = CloudEvent.field_name_modifier(field, self.isbinary)
            if (fieldname in fields_refs) and not \
                    isinstance(fields_refs[fieldname], str):
                raise TypeError(
                    f"in parameter {fields_refs_name}, {fieldname} "
                    f"expected type str but found type "
                    f"{type(fields_refs[fieldname])}."
                )
            else:
                self.optional_attribute_values[f"ce-{field}"] = field

        # structured data is inside json resp['data']
        self.data = copy.deepcopy(data) if self.isbinary else \
            copy.deepcopy(data.get('data', {}))

        self.headers = {
            **self.required_attribute_values,
            **self.optional_attribute_values
        }

    def to_request(
        self,
        data_unmarshaller: typing.Callable = lambda x: json.loads(
            x.read()
            .decode('utf-8')
        )
    ) -> (dict, dict):
        converter_type = converters.TypeBinary if self.isbinary else \
            converters.TypeStructured

        headers, data = self.marshall.ToRequest(
            self.__event,
            converter_type,
            data_unmarshaller
        )
        return headers, (data if self.isbinary else 
        data_unmarshaller(data)['data'])

    def __getitem__(self, key):
        return self.data if key == 'data' else self.headers[key]

    @staticmethod
    def is_binary_cloud_event(event_handler, headers):
        for field in event_handler._ce_required_fields:
            if f"ce-{field}" not in headers:
                return False
        return True

    @staticmethod
    def detect_event_version(headers, data):
        """
        Returns event handler depending on specversion within
        headers for binary cloudevents or within data for structured
        cloud events
        """
        specversion = headers.get('ce-specversion', data.get('specversion'))
        if specversion == '1.0':
            return v1.Event
        elif specversion == '0.3':
            return v03.Event
        else:
            raise TypeError(f"specversion {specversion} "
                            "currently unsupported")

    @staticmethod
    def field_name_modifier(field, isbinary):
        return f"ce-{field}" if isbinary else field

    def __repr__(self):
        return json.dumps(
            {
                'Event': {
                    'headers': self.headers,
                    'data': self.data
                }
            },
            indent=4
        )
