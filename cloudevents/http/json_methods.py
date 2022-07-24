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

from cloudevents.conversion import from_json as _abstract_from_json
from cloudevents.conversion import to_json
from cloudevents.http.event import CloudEvent
from cloudevents.sdk import types


def from_json(
    data: typing.Union[str, bytes],
    data_unmarshaller: types.UnmarshallerType = None,
) -> CloudEvent:
    """
    Cast json encoded data into an CloudEvent
    :param data: json encoded cloudevent data
    :param data_unmarshaller: Callable function which will cast data to a
        python object
    :type data_unmarshaller: typing.Callable
    :returns: CloudEvent representing given cloudevent json object
    """
    return _abstract_from_json(CloudEvent, data, data_unmarshaller)


# backwards compatibility
to_json = to_json
