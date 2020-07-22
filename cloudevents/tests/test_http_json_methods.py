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
import base64
import json

import pytest

from cloudevents.sdk.http import (
    CloudEvent,
    to_json, 
    from_json
)


test_data = json.dumps({"data-key": "val"})
test_attributes = {
    "type": "com.example.string",
    "source": "https://example.com/event-producer",
}


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_to_json(specversion):
    event = CloudEvent(test_attributes, test_data)
    event_json = to_json(event)
    event_dict = json.loads(event_json)
    print(event_dict)
    for key, val in test_attributes.items():
        assert event_dict[key] == val
    
    assert event_dict['data'] == test_data


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_to_json_base64(specversion):
    data = b'test123'

    event = CloudEvent(test_attributes, data)
    event_json = to_json(event)
    event_dict = json.loads(event_json)
    
    for key, val in test_attributes.items():
        assert event_dict[key] == val

    # test data was properly marshalled into data_base64
    data_base64 = event_dict['data_base64'].encode()
    test_data_base64 = base64.b64encode(data)

    assert data_base64 == test_data_base64
