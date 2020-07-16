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

import json

import requests
import typing

from PIL import Image
import base64

from cloudevents.sdk import converters
from cloudevents.sdk.http_events import CloudEvent

def create_byte_image(size: typing.Tuple[int, int]) -> str:
    # Create image
    image = Image.new('RGB', size)

    # Turn image into bytes 
    b = image.tobytes()

    return b

def create_image_event(size: typing.Tuple[int, int], binary=False) -> CloudEvent:
    # This data defines a binary cloudevent


    return CloudEvent(attributes, data)
    

def send_binary_cloud_event(url):
    size = (8,8)
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
        "size": json.dumps(size)
    }
    data = create_byte_image(size).decode()

    event = CloudEvent(attributes, data)
    headers, body = event.to_http(converters.TypeBinary)

    # send and print event
    requests.post(url, data=body, headers=headers)
    print(f"Sent {event['id']} of type {event['type']}")


def send_structured_cloud_event(url):
    size = (8,8)
    attributes = {
        "type": "com.example.base64",
        "source": "https://example.com/event-producer",
        "size": json.dumps(size)
    }
    data = create_byte_image(size)
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
