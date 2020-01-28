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

from cloudevents.sdk.event import v02, v03, v1

contentType = "application/json"
ce_type = "word.found.exclamation"
ce_id = "16fb5f0b-211e-1102-3dfe-ea6e2806f124"
source = "pytest"
eventTime = "2018-10-23T12:28:23.3464579Z"
body = '{"name":"john"}'

headers = {
    v02.Event: {
        "ce-specversion": "0.2",
        "ce-type": ce_type,
        "ce-id": ce_id,
        "ce-time": eventTime,
        "ce-source": source,
        "Content-Type": contentType,
    },
    v03.Event: {
        "ce-specversion": "0.3",
        "ce-type": ce_type,
        "ce-id": ce_id,
        "ce-time": eventTime,
        "ce-source": source,
        "Content-Type": contentType,
    },
    v1.Event: {
        "ce-specversion": "1.0",
        "ce-type": ce_type,
        "ce-id": ce_id,
        "ce-time": eventTime,
        "ce-source": source,
        "Content-Type": contentType,
    },
}

json_ce = {
    v02.Event: {
        "specversion": "0.2",
        "type": ce_type,
        "id": ce_id,
        "time": eventTime,
        "source": source,
        "contenttype": contentType,
    },
    v03.Event: {
        "specversion": "0.3",
        "type": ce_type,
        "id": ce_id,
        "time": eventTime,
        "source": source,
        "datacontenttype": contentType,
    },
    v1.Event: {
        "specversion": "1.0",
        "type": ce_type,
        "id": ce_id,
        "time": eventTime,
        "source": source,
        "datacontenttype": contentType,
    },
}
