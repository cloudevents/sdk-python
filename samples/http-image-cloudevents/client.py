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
import io
import json
import sys
import typing

import requests
from PIL import Image

from cloudevents.sdk import converters
from cloudevents.sdk.http_events import CloudEvent


def create_byte_image(size: typing.Tuple[int, int]) -> str:
    # Create image
    image = Image.new("RGB", size)

    # Turn image into bytes
    b = image.tobytes()

    return b


def send_binary_cloud_event(url: str):
    size = (8, 8)
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
        "size": json.dumps(size),
    }
    data = create_byte_image(size)

    event = CloudEvent(attributes, data)
    headers, body = event.to_http(
        converters.TypeBinary, data_marshaller=lambda x: x.decode()
    )

    # send and print event
    requests.post(url, data=body, headers=headers)
    print(f"Sent {event['id']} of type {event['type']}")


def send_structured_cloud_event(url: str):
    size = (8, 8)
    attributes = {
        "type": "com.example.base64",
        "source": "https://example.com/event-producer",
        "size": json.dumps(size),
    }
    data = create_byte_image(size)

    # passing data as a bytes object will
    event = CloudEvent(attributes, data)
    headers, body = event.to_http()

    # # POST
    requests.post(url, data=body, headers=headers)
    print(f"Sent {event['id']} of type {event['type']}")


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
