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

import pytest

from cloudevents.sdk import converters, exceptions, marshaller
from cloudevents.sdk.converters import binary, structured
from cloudevents.sdk.event import v1


@pytest.fixture
def headers():
    return {
        "ce-specversion": "1.0",
        "ce-source": "1.0",
        "ce-type": "com.marshaller.test",
        "ce-id": "1234-1234-1234",
    }


def test_from_request_wrong_unmarshaller():
    with pytest.raises(exceptions.InvalidDataUnmarshaller):
        m = marshaller.NewDefaultHTTPMarshaller()
        _ = m.FromRequest(v1.Event(), {}, "", None)


def test_to_request_wrong_marshaller():
    with pytest.raises(exceptions.InvalidDataMarshaller):
        m = marshaller.NewDefaultHTTPMarshaller()
        _ = m.ToRequest(v1.Event(), data_marshaller="")


def test_from_request_cannot_read(headers):
    with pytest.raises(exceptions.UnsupportedEventConverter):
        m = marshaller.HTTPMarshaller(
            [binary.NewBinaryHTTPCloudEventConverter(),]
        )
        m.FromRequest(v1.Event(), {}, "")

    with pytest.raises(exceptions.UnsupportedEventConverter):
        m = marshaller.HTTPMarshaller(
            [structured.NewJSONHTTPCloudEventConverter()]
        )
        m.FromRequest(v1.Event(), headers, "")


def test_to_request_invalid_converter():
    with pytest.raises(exceptions.NoSuchConverter):
        m = marshaller.HTTPMarshaller(
            [structured.NewJSONHTTPCloudEventConverter()]
        )
        m.ToRequest(v1.Event(), "")
