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

import datetime
import typing
import uuid

import cloudevents.exceptions as cloud_exceptions
from cloudevents import abstract
from cloudevents.sdk.event import v1, v03

_required_by_version = {
    "1.0": v1.Event._ce_required_fields,
    "0.3": v03.Event._ce_required_fields,
}


class CloudEvent(abstract.CloudEvent):
    """
    Python-friendly cloudevent class supporting v1 events
    Supports both binary and structured mode CloudEvents
    """

    @classmethod
    def create(
        cls, attributes: typing.Dict[str, typing.Any], data: typing.Optional[typing.Any]
    ) -> "CloudEvent":
        return cls(attributes, data)

    def __init__(self, attributes: typing.Dict[str, str], data: typing.Any = None):
        """
        Event Constructor
        :param attributes: a dict with cloudevent attributes. Minimally
            expects the attributes 'type' and 'source'. If not given the
            attributes 'specversion', 'id' or 'time', this will create
            those attributes with default values.
            e.g. {
                "specversion": "1.0",
                "type": "com.github.pull_request.opened",
                "source": "https://github.com/cloudevents/spec/pull",
                "id": "A234-1234-1234",
                "time": "2018-04-05T17:31:00Z",
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

    def _get_attributes(self) -> typing.Dict[str, typing.Any]:
        return self._attributes

    def get_data(self) -> typing.Optional[typing.Any]:
        return self.data

    def __setitem__(self, key: str, value: typing.Any) -> None:
        self._attributes[key] = value

    def __delitem__(self, key: str) -> None:
        del self._attributes[key]
