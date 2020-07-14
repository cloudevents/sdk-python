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
from cloudevents.sdk.event import v1, v03

_marshaller_by_format = {
    converters.TypeStructured: lambda x: x,
    converters.TypeBinary: json.dumps,
}

_obj_by_version = {"1.0": v1.Event, "0.3": v03.Event}

_required_by_version = {
    "1.0": v1.Event._ce_required_fields,
    "0.3": v03.Event._ce_required_fields,
}


class EventClass:
    """
    Python-friendly cloudevent class supporting v1 events
    Supports both binary and structured mode CloudEvents
    """

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



def _to_http(
    event: EventClass,
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
    if event._attributes["specversion"] not in _obj_by_version:
        raise ValueError(
            f"Unsupported specversion: {event._attributes['specversion']}"
        )

    event_handler = _obj_by_version[event._attributes["specversion"]]()
    for k, v in event._attributes.items():
        event_handler.Set(k, v)
    event_handler.data = event.data

    return marshaller.NewDefaultHTTPMarshaller().ToRequest(
        event_handler, format, data_marshaller
    )


def to_structured_http(
    event: EventClass, data_marshaller: types.MarshallerType = None,
) -> (dict, typing.Union[bytes, str]):
    """
    Returns a tuple of HTTP headers/body dicts representing this cloudevent

    :param event: CloudEvent to cast into http data
    :type event: CloudEvent
    :param data_unmarshaller: Function used to read the data to string.
    :type data_unmarshaller: types.UnmarshallerType
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    return _to_http(event=event, data_marshaller=data_marshaller)


def to_binary_http(
    event: EventClass, data_marshaller: types.MarshallerType = None,
) -> (dict, typing.Union[bytes, str]):
    """
    Returns a tuple of HTTP headers/body dicts representing this cloudevent

    :param event: CloudEvent to cast into http data
    :type event: CloudEvent
    :param data_unmarshaller: Function used to read the data to string.
    :type data_unmarshaller: types.UnmarshallerType
    :returns: (http_headers: dict, http_body: bytes or str)
    """
    return _to_http(
        event=event,
        format=converters.TypeBinary,
        data_marshaller=data_marshaller,
    )


def to_json():
    raise NotImplementedError