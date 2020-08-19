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
import typing
import uuid

import cloudevents.exceptions as cloud_exceptions
from cloudevents.http.mappings import _required_by_version


class CloudEvent:
    """
    Python-friendly cloudevent class supporting v1 events
    Supports both binary and structured mode CloudEvents
    """

    def __init__(
        self, attributes: typing.Dict[str, str], data: typing.Any = None
    ):
        """
        Event Constructor
        :param attributes: a dict with cloudevent attributes. Minimally
            expects the attributes 'type' and 'source'. If not given the
            attributes 'specversion', 'id' or 'time', this will create
            those attributes with default values.
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
            raise cloud_exceptions.MissingRequiredFields(
                f"Invalid specversion: {self._attributes['specversion']}"
            )
        # There is no good way to default 'source' and 'type', so this
        # checks for those (or any new required attributes).
        required_set = _required_by_version[self._attributes["specversion"]]
        if not required_set <= self._attributes.keys():
            raise cloud_exceptions.MissingRequiredFields(
                f"Missing required keys: {required_set - self._attributes.keys()}"
            )

    def __eq__(self, other):
        return self.data == other.data and self._attributes == other._attributes

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
        return str({"attributes": self._attributes, "data": self.data})
