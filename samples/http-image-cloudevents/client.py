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

import sys

import requests

from cloudevents.conversion import to_binary, to_structured
from cloudevents.http import CloudEvent

resp = requests.get(
    "https://raw.githubusercontent.com/cncf/artwork/master/projects/cloudevents/horizontal/color/cloudevents-horizontal-color.png"  # noqa
)
image_bytes = resp.content


def send_binary_cloud_event(url: str) -> None:
    # Create cloudevent
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
    }

    event = CloudEvent(attributes, image_bytes)

    # Create cloudevent HTTP headers and content
    headers, body = to_binary(event)

    # Send cloudevent
    requests.post(url, headers=headers, data=body)
    print(f"Sent {event['id']} of type {event['type']}")


def send_structured_cloud_event(url: str) -> None:
    # Create cloudevent
    attributes = {
        "type": "com.example.base64",
        "source": "https://example.com/event-producer",
    }

    event = CloudEvent(attributes, image_bytes)

    # Create cloudevent HTTP headers and content
    # Note that to_structured will create a data_base64 data field in
    # specversion 1.0 (default specversion) if given
    # an event whose data field is of type bytes.
    headers, body = to_structured(event)

    # Send cloudevent
    requests.post(url, headers=headers, data=body)
    print(f"Sent {event['id']} of type {event['type']}")


if __name__ == "__main__":
    # Run client.py via: 'python3 client.py http://localhost:3000/'
    if len(sys.argv) < 2:
        sys.exit("Usage: python with_requests.py <CloudEvents controller URL>")

    url = sys.argv[1]
    send_binary_cloud_event(url)
    send_structured_cloud_event(url)
