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

from cloudevents.sdk import types
from cloudevents.sdk.http import CloudEvent, _to_http


def to_json() -> str:
    raise NotImplementedError


def to_http(
    event: CloudEvent, data_marshaller: types.MarshallerType = None,
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
