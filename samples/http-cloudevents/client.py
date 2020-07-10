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
import io
import sys

import requests

from cloudevents.sdk import converters
from cloudevents.sdk.http_events import CloudEvent


def send_binary_cloud_event(url):
    # This data defines a binary cloudevent
    attributes = {
        "Content-Type": "application/json",
        "type": "com.readme.binary",
        "id": "A234-1234-1234",
        "source": "/client.py",
    }
    data = {"message": "Hello World!"}

    event = CloudEvent(attributes, data)
    headers, body = event.to_http(converters.TypeBinary)

    # send and print event
    requests.post(url, data=body, headers=headers)
    print(f"Sent {event['id']} from {event['source']} with " f"{event.data}")


def send_structured_cloud_event(url):
    # This data defines a structured cloudevent
    attributes = {
        "type": "com.readme.structured",
        "id": "B234-1234-1234",
        "source": "/client.py",
        # Time will be filled in automatically if not set
        "time": "2018-10-23T12:28:23.3464579Z",
    }
    data = {"message": "Hello World!"}
    event = CloudEvent(attributes, data)
    headers, body = event.to_http()

    # POST
    requests.post(url, data=body, headers=headers)
    print(f"Sent {event['id']} from {event['source']} with " f"{event.data}")


if __name__ == "__main__":
    # expects a url from command line.
    # e.g. python3 client.py http://localhost:3000/
    if len(sys.argv) < 2:
        sys.exit(
            "Usage: python with_requests.py " "<CloudEvents controller URL>"
        )

    url = sys.argv[1]
    send_binary_cloud_event(url)
    send_structured_cloud_event(url)
