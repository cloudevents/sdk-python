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

from cloudevents.core.bindings.http import (
    to_binary_event,
    to_structured_event,
)
from cloudevents.core.v1.event import CloudEvent


def send_binary_cloud_event(url):
    # This data defines a binary cloudevent
    attributes = {
        "id": "123",
        "specversion": "1.0",
        "type": "com.example.sampletype1",
        "source": "https://example.com/event-producer",
    }
    data = {"message": "Hello World!"}

    event = CloudEvent(attributes, data)
    http_message = to_binary_event(event)

    # send and print event
    requests.post(url, headers=http_message.headers, data=http_message.body)
    print(f"Sent {event.get_id()} from {event.get_source()} with {event.get_data()}")


def send_structured_cloud_event(url):
    # This data defines a structured cloudevent
    attributes = {
        "id": "123",
        "specversion": "1.0",
        "type": "com.example.sampletype2",
        "source": "https://example.com/event-producer",
    }
    data = {"message": "Hello World!"}

    event = CloudEvent(attributes, data)
    http_message = to_structured_event(event)

    # send and print event
    requests.post(url, headers=http_message.headers, data=http_message.body)
    print(f"Sent {event.get_id()} from {event.get_source()} with {event.get_data()}")


if __name__ == "__main__":
    # expects a url from command line.
    # e.g. python client.py http://localhost:3000/
    if len(sys.argv) < 2:
        sys.exit("Usage: python client.py <CloudEvents controller URL>")

    url = sys.argv[1]
    send_binary_cloud_event(url)
    send_structured_cloud_event(url)
