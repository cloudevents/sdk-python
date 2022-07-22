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

from cloudevents.abstract import AnyCloudEvent
from cloudevents.sdk import types
from cloudevents.abstract.http_methods import to_structured, from_http


def to_json(
    event: AnyCloudEvent,
    data_marshaller: types.MarshallerType = None,
) -> typing.Union[str, bytes]:
    """
    Cast an CloudEvent into a json object
    :param event: CloudEvent which will be converted into a json object
    :type event: CloudEvent
    :param data_marshaller: Callable function which will cast event.data
        into a json object
    :type data_marshaller: typing.Callable
    :returns: json object representing the given event
    """
    return to_structured(event, data_marshaller=data_marshaller)[1]


def from_json(
    event_type: typing.Type[AnyCloudEvent],
    data: typing.Union[str, bytes],
    data_unmarshaller: types.UnmarshallerType = None,
) -> AnyCloudEvent:
    """
    Cast json encoded data into an CloudEvent
    :param event_type: Concrete event type to which deserialize the json event
    :param data: json encoded cloudevent data
    :param data_unmarshaller: Callable function which will cast data to a
        python object
    :type data_unmarshaller: typing.Callable
    :returns: CloudEvent representing given cloudevent json object
    """
    return from_http(
        event_type, headers={}, data=data, data_unmarshaller=data_unmarshaller
    )
