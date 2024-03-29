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

from cloudevents.sdk.event import v1, v03

content_type = "application/json"
ce_type = "word.found.exclamation"
ce_id = "16fb5f0b-211e-1102-3dfe-ea6e2806f124"
source = "pytest"
event_time = "2018-10-23T12:28:23.3464579Z"
body = '{"name":"john"}'

headers = {
    v03.Event: {
        "ce-specversion": "1.0",
        "ce-type": ce_type,
        "ce-id": ce_id,
        "ce-time": event_time,
        "ce-source": source,
        "Content-Type": content_type,
    },
    v1.Event: {
        "ce-specversion": "1.0",
        "ce-type": ce_type,
        "ce-id": ce_id,
        "ce-time": event_time,
        "ce-source": source,
        "Content-Type": content_type,
    },
}

json_ce = {
    v03.Event: {
        "specversion": "1.0",
        "type": ce_type,
        "id": ce_id,
        "time": event_time,
        "source": source,
        "datacontenttype": content_type,
    },
    v1.Event: {
        "specversion": "1.0",
        "type": ce_type,
        "id": ce_id,
        "time": event_time,
        "source": source,
        "datacontenttype": content_type,
    },
}
