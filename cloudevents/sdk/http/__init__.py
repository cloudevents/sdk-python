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
import json
import typing

from cloudevents.sdk import converters, marshaller, types
from cloudevents.sdk.event import v1, v03
from cloudevents.sdk.http import binary as binary
from cloudevents.sdk.http import structured as structured
from cloudevents.sdk.http.event import CloudEvent


def _json_or_string(content: typing.Union[str, bytes]):
    if len(content) == 0:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return content


def from_http(
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

    event = marshaller.NewDefaultHTTPMarshaller().FromRequest(
        v1.Event(), headers, data, data_unmarshaller
    )
    attrs = event.Properties()
    attrs.pop("data", None)
    attrs.pop("extensions", None)
    attrs.update(**event.extensions)

    return CloudEvent(attrs, event.data)


def from_json():
    raise NotImplementedError
