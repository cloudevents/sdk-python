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

from cloudevents.sdk.event import base


class Converter(object):

    TYPE = None

    def __init__(
            self, event_class: base.BaseEvent,
            supported_media_types: typing.Mapping[str, bool]):
        self.event = event_class()
        self.supported_media_types = supported_media_types

    def can_read(self, media_type: str) -> bool:
        return media_type in self.supported_media_types

    def read(self, headers: dict, body: typing.IO,
             data_unmarshaller: typing.Callable) -> base.BaseEvent:
        raise Exception("not implemented")

    def write(self, event: base.BaseEvent,
              data_marshaller: typing.Callable) -> (dict, typing.IO):
        raise Exception("not implemented")
