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

import typing

from cloudevents.sdk.event import base


class Converter(object):
    TYPE: str = ""

    def read(
        self,
        event: typing.Any,
        headers: typing.Mapping[str, str],
        body: typing.Union[str, bytes],
        data_unmarshaller: typing.Callable,
    ) -> base.BaseEvent:
        raise Exception("not implemented")

    def event_supported(self, event: object) -> bool:
        raise Exception("not implemented")

    def can_read(
        self,
        content_type: typing.Optional[str],
        headers: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> bool:
        raise Exception("not implemented")

    def write(
        self, event: base.BaseEvent, data_marshaller: typing.Optional[typing.Callable]
    ) -> typing.Tuple[typing.Dict[str, str], bytes]:
        raise Exception("not implemented")
