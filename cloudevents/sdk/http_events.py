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
import datetime
import json
import io
import typing
import uuid

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller
from cloudevents.sdk import types
from cloudevents.sdk.converters import binary
from cloudevents.sdk.converters import structured

from cloudevents.sdk.event import v03, v1


class CloudEvent():
    """
    Python-friendly cloudevent class supporting v1 events
    Supports both binary and structured mode CloudEvents
    """

    @classmethod
    def FromHttp(
        cls,
        data: typing.Union[str, bytes],
        headers: dict = {},
        data_unmarshaller: types.UnmarshallerType = None
    ):
        """Unwrap a CloudEvent (binary or structured) from an HTTP request.
        :param data: the HTTP request body
        :type data: typing.IO
        :param headers: the HTTP headers
        :type headers: dict
        :param data_unmarshaller: A function to decode data into a python object.
        :type data_unmarshaller: types.UnmarshallerType
        """
        def json_or_string(content: typing.Union[str, bytes]):
            if len(content) == 0:
                return None
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
        if data_unmarshaller is None:
            data_unmarshaller = json_or_string

        event = marshaller.NewDefaultHTTPMarshaller().FromRequest(
            v1.Event(), headers, data, data_unmarshaller)
        attrs = event.Properties()
        attrs.pop('data', None)
        attrs.pop('extensions', None)
        attrs.update(**event.extensions)

        return cls(attrs, event.data)

    def __init__(self, attributes: dict = {}, data: typing.Any = None):
        """
        Event Constructor
        :param attributes: a dict with HTTP headers
            e.g. {
                "content-type": "application/cloudevents+json",
                "id": "16fb5f0b-211e-1102-3dfe-ea6e2806f124",
                "source": "<event-source>",
                "type": "cloudevent.event.type",
                "specversion": "0.2"
            }
        :type headers: dict
        :param data: The payload of the event, as a python object
        :type data: typing.Any
        """
        self._attributes = {k.lower(): v for k, v in attributes.items()}
        self.data = data
        required_by_version = {
            "1.0": v1.Event._ce_required_fields, "0.3": v03.Event._ce_required_fields}
        if 'specversion' not in self._attributes:
            self._attributes['specversion'] = "1.0"
        if 'id' not in self._attributes:
            self._attributes['id'] = str(uuid.uuid4())
        if 'time' not in self._attributes:
            self._attributes['time'] = datetime.datetime.now(
                datetime.timezone.utc).isoformat()

        if self._attributes['specversion'] not in required_by_version:
            raise ValueError(
                f"Invalid specversion: {self._attributes['specversion']}")
        required_set = required_by_version[self._attributes['specversion']]
        # There is no good way to default 'source' and 'type', so this checks for those.
        # required_set = required_by_version.get(attributes.get("specversion"))
        if not required_set <= self._attributes.keys():
            raise ValueError(
                f"Missing required keys: {required_set - attributes.keys()}")

    def to_http(
        self,
        format: str = converters.TypeStructured,
        data_marshaller: types.MarshallerType = None
    ) -> (dict, typing.Union[bytes, str]):
        """
        Returns a tuple of HTTP headers/body dicts representing this cloudevent

        :param format: constant specifying an encoding format
        :type format: str
        :param data_unmarshaller: callable function used to read the data io object
        :type data_unmarshaller: types.UnmarshallerType
        :returns: (http_headers: dict, http_body: bytes or str)
        """
        marshaller_by_format = {converters.TypeStructured: lambda x: x,
                                converters.TypeBinary: json.dumps}
        if data_marshaller is None:
            data_marshaller = marshaller_by_format[format]
        obj_by_type = {"1.0": v1.Event, "0.3": v03.Event}
        if self._attributes["specversion"] not in obj_by_type:
            raise ValueError(
                "Unsupported specversion: {self._attributes['specversion']}")

        event = obj_by_type[self._attributes["specversion"]]()
        for k, v in self._attributes.items():
            event.Set(k, v)
        event.data = self.data

        return marshaller.NewDefaultHTTPMarshaller().ToRequest(event, format, data_marshaller)

    # Attribute access is managed via Mapping type
    def __getitem__(self, key):
        return self._attributes[key]

    def __setitem__(self, key, value):
        self._attributes[key] = value

    def __delitem__(self, key):
        del self._attributes[key]

    def __iter__(self):
        return iter(self._attributes)

    def __len__(self):
        return len(self._attributes)

    def __contains__(self, key):
        return key in self._attributes

    def __repr__(self):
        return self.to_http()[1]
