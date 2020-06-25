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

import json
import typing

from cloudevents.sdk import marshaller

from cloudevents.sdk.event import v03, v1


class CloudEvent():
    """
    Python-friendly cloudevent class supporting v1 events
    Currently only supports binary content mode CloudEvents
    """

    def __init__(
            self,
            headers: dict,
            data: dict,
            data_unmarshaller: typing.Callable = lambda x: x
    ):
        """
        Event HTTP Constructor
        :param headers: a dict with HTTP headers
            e.g. {
                "content-type": "application/cloudevents+json",
                "ce-id": "16fb5f0b-211e-1102-3dfe-ea6e2806f124",
                "ce-source": "<event-source>",
                "ce-type": "cloudevent.event.type",
                "ce-specversion": "0.2"
            }
        :type headers: dict
        :param data: a dict to be stored inside Event
        :type data: dict
        :param binary: a bool indicating binary events
        :type binary: bool
        :param data_unmarshaller: callable function for reading/extracting data
        :type data_unmarshaller: typing.Callable
        """
        headers = {key.lower(): value for key, value in headers.items()}
        data = {key.lower(): value for key, value in data.items()}

        # returns an event class depending on proper version
        event_version = CloudEvent.detect_event_version(headers, data)

        isbinary = CloudEvent.is_binary_cloud_event(event_version, headers)

        # Headers validation for binary events
        for field in event_version._ce_required_fields:

            # prefixes with ce- if this is a binary event
            fieldname = CloudEvent.field_name_modifier(field, isbinary)

            # fields_refs holds a reference to where fields should be
            fields_refs = headers if isbinary else data

            fields_refs_name = 'headers' if isbinary else 'data'

            # Verify field exists else throw TypeError
            if fieldname not in fields_refs:
                raise TypeError(
                    f"parameter {fields_refs_name} has no required "
                    f"attribute {fieldname}."
                )

            if not isinstance(fields_refs[fieldname], str):
                raise TypeError(
                    f"in parameter {fields_refs_name}, {fieldname} "
                    f"expected type str but found type "
                    f"{type(fields_refs[fieldname])}."
                )

        for field in event_version._ce_optional_fields:
            fieldname = CloudEvent.field_name_modifier(field, isbinary)
            if (fieldname in fields_refs) and not \
                    isinstance(fields_refs[fieldname], str):
                raise TypeError(
                    f"in parameter {fields_refs_name}, {fieldname} "
                    f"expected type str but found type "
                    f"{type(fields_refs[fieldname])}."
                )

        # structured data is inside json resp['data']
        self.data = copy.deepcopy(data) if isbinary else \
            copy.deepcopy(data['data'])
        self.headers = copy.deepcopy(headers)

        self.marshall = marshaller.NewDefaultHTTPMarshaller()
        self.event_handler = event_version()

        self.marshall.FromRequest(
            self.event_handler,
            self.headers,
            self.data,
            data_unmarshaller
        )

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
