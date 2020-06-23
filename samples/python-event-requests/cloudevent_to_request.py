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
import sys
import io
from cloudevents.sdk.http_events import CloudEvent

import requests

if __name__ == "__main__":
    # expects a url from command line. e.g.
    #     python3 sample-server.py http://localhost:3000/event
    if len(sys.argv) < 2:
        sys.exit("Usage: python with_requests.py "
                 "<CloudEvents controller URL>")

    url = sys.argv[1]

    # CloudEvent headers and data
    headers = {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": "1.0"
    }
    data = {"payload-content": "Hello World!"}

    # Create a CloudEvent
    event = CloudEvent(headers=headers, data=data)

    # Print the created CloudEvent then send it to some url we got from
    # command line
    print(f"Sent {event}")
    requests.post(url, headers=event.headers, json=event.data)
