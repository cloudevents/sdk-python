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

    def read(
        self,
        event,
        headers: dict,
        body: typing.IO,
        data_unmarshaller: typing.Callable,
    ) -> base.BaseEvent:
        raise Exception("not implemented")

    def event_supported(self, event: object) -> bool:
        raise Exception("not implemented")

    def can_read(self, content_type: str) -> bool:
        raise Exception("not implemented")

    def write(
        self, event: base.BaseEvent, data_marshaller: typing.Callable
    ) -> (dict, object):
        raise Exception("not implemented")
