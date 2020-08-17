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

from cloudevents.sdk.converters import binary, structured
from cloudevents.sdk import converters, marshaller, exceptions
from cloudevents.sdk.event import v1

import pytest


def test_raise_invalid_data_unmarshaller():
    with pytest.raises(exceptions.InvalidDataUnmarshaller):
        m = marshaller.NewDefaultHTTPMarshaller()
        _ = m.FromRequest(
            v1.Event(),
            {},
            "",
            None
        )

def test():
    with pytest.raises(exceptions.UnsupportedEventConverter):
        m = marshaller.HTTPMarshaller(
            [
                binary.NewBinaryHTTPCloudEventConverter(),
            ]
        )
        m.FromRequest(
            v1.Event(),
            {},
            ""
        )
