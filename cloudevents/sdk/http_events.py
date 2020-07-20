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

import datetime
import json
import typing
import uuid

from cloudevents.sdk import converters, marshaller, types
from cloudevents.sdk.converters import binary, structured
from cloudevents.sdk.event import v1, v03
from cloudevents.sdk.marshaller import HTTPMarshaller

_marshaller_by_format = {
    converters.TypeStructured: lambda x: x,
    converters.TypeBinary: json.dumps,
}
_required_by_version = {
    "1.0": v1.Event._ce_required_fields,
    "0.3": v03.Event._ce_required_fields,
}
_obj_by_version = {"1.0": v1.Event, "0.3": v03.Event}


def _json_or_string(content: typing.Union[str, bytes]):
    if len(content) == 0:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return content


def is_binary(
    headers: typing.Dict[str, str]
) -> bool:
    """Uses internal marshallers to determine whether this event is binary
    :param headers: the HTTP headers
    :type headers: typing.Dict[str, str]
    :returns bool: returns a bool indicating whether the headers indicate a binary event type
    """
    headers = {key.lower(): value for key, value in headers.items()}
    content_type = headers.get("content-type", "")
    binary_parser = binary.BinaryHTTPCloudEventConverter()
    return binary_parser.can_read(content_type=content_type, headers=headers)

    
class CloudEvent:
    """
    Python-friendly cloudevent class supporting v1 events
    Supports both binary and structured mode CloudEvents
    """

    @classmethod
    def from_http(
        cls,
        data: typing.Union[str, bytes],
        headers: typing.Dict[str, str],
        data_unmarshaller: types.UnmarshallerType = None,
    ):
        """Unwrap a CloudEvent (binary or structured) from an HTTP request.
        :param data: the HTTP request body
        :type data: typing.IO
        :param headers: the HTTP headers
        :type headers: typing.Dict[str, str]
        :param data_unmarshaller: Function to decode data into a python object.
        :type data_unmarshaller: types.UnmarshallerType
        """
        if data_unmarshaller is None:
            data_unmarshaller = _json_or_string

        marshall = marshaller.NewDefaultHTTPMarshaller()

        if is_binary(headers):
            specversion = headers.get("ce-specversion", None)
        else:
            raw_ce = json.loads(data)
            specversion = raw_ce.get("specversion", None)

        if specversion is None:
            raise ValueError("could not find specversion in HTTP request")

        event_handler = _obj_by_version.get(specversion, None)

        if event_handler is None:
            raise ValueError(f"found invalid specversion {specversion}")

        event = marshall.FromRequest(
            event_handler(), headers, data, data_unmarshaller
        )
        attrs = event.Properties()
        attrs.pop("data", None)
        attrs.pop("extensions", None)
        attrs.update(**event.extensions)

        return cls(attrs, event.data)

    def __init__(
        self, attributes: typing.Dict[str, str], data: typing.Any = None
    ):
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
        :type attributes: typing.Dict[str, str]
        :param data: The payload of the event, as a python object
        :type data: typing.Any
        """
        self._attributes = {k.lower(): v for k, v in attributes.items()}
        self.data = data
        if "specversion" not in self._attributes:
            self._attributes["specversion"] = "1.0"
        if "id" not in self._attributes:
            self._attributes["id"] = str(uuid.uuid4())
        if "time" not in self._attributes:
            self._attributes["time"] = datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat()

        if self._attributes["specversion"] not in _required_by_version:
            raise ValueError(
                f"Invalid specversion: {self._attributes['specversion']}"
            )
        # There is no good way to default 'source' and 'type', so this
        # checks for those (or any new required attributes).
        required_set = _required_by_version[self._attributes["specversion"]]
        if not required_set <= self._attributes.keys():
            raise ValueError(
                f"Missing required keys: {required_set - attributes.keys()}"
            )

    def to_http(
        self,
        format: str = converters.TypeStructured,
        data_marshaller: types.MarshallerType = None,
    ) -> (dict, typing.Union[bytes, str]):
        """
        Returns a tuple of HTTP headers/body dicts representing this cloudevent

        :param format: constant specifying an encoding format
        :type format: str
        :param data_unmarshaller: Function used to read the data to string.
        :type data_unmarshaller: types.UnmarshallerType
        :returns: (http_headers: dict, http_body: bytes or str)
        """
        if data_marshaller is None:
            data_marshaller = _marshaller_by_format[format]
        if self._attributes["specversion"] not in _obj_by_version:
            raise ValueError(
                f"Unsupported specversion: {self._attributes['specversion']}"
            )

        event = _obj_by_version[self._attributes["specversion"]]()
        for k, v in self._attributes.items():
            event.Set(k, v)
        event.data = self.data

        return marshaller.NewDefaultHTTPMarshaller().ToRequest(
            event, format, data_marshaller
        )

    # Data access is handled via `.data` member
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
        return self.to_http()[1].decode()
