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

import base64
import io
import json

import pytest
from client import image_bytes
from image_sample_server import app
from PIL import Image

from cloudevents.conversion import to_binary, to_structured
from cloudevents.http import CloudEvent, from_http

image_fileobj = io.BytesIO(image_bytes)
image_expected_shape = (1880, 363)


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_create_binary_image():
    # Create image and turn image into bytes
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
    }

    # Create CloudEvent
    event = CloudEvent(attributes, image_bytes)

    # Create http headers/body content
    headers, body = to_binary(event)

    # Unmarshall CloudEvent and re-create image
    reconstruct_event = from_http(
        headers, body, data_unmarshaller=lambda x: io.BytesIO(x)
    )

    # reconstruct_event.data is an io.BytesIO object due to data_unmarshaller
    restore_image = Image.open(reconstruct_event.data)
    assert restore_image.size == image_expected_shape

    # # Test cloudevent extension from http fields and data
    assert isinstance(body, bytes)
    assert body == image_bytes


def test_create_structured_image():
    # Create image and turn image into bytes
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
    }

    # Create CloudEvent
    event = CloudEvent(attributes, image_bytes)

    # Create http headers/body content
    headers, body = to_structured(event)

    # Structured has cloudevent attributes marshalled inside the body. For this
    # reason we must load the byte object to create the python dict containing
    # the cloudevent attributes
    data = json.loads(body)

    # Test cloudevent extension from http fields and data
    assert isinstance(data, dict)
    assert base64.b64decode(data["data_base64"]) == image_bytes

    # Unmarshall CloudEvent and re-create image
    reconstruct_event = from_http(
        headers, body, data_unmarshaller=lambda x: io.BytesIO(x)
    )

    # reconstruct_event.data is an io.BytesIO object due to data_unmarshaller
    restore_image = Image.open(reconstruct_event.data)
    assert restore_image.size == image_expected_shape


def test_server_structured(client):
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
    r = client.post("/", headers=headers, data=body)
    assert r.status_code == 200
    assert r.data.decode() == f"Found image of size {image_expected_shape}"


def test_server_binary(client):
    # Create cloudevent
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
    }

    event = CloudEvent(attributes, image_bytes)

    # Create cloudevent HTTP headers and content
    headers, body = to_binary(event)

    # Send cloudevent
    r = client.post("/", headers=headers, data=body)
    assert r.status_code == 200
    assert r.data.decode() == f"Found image of size {image_expected_shape}"


def test_image_content():
    # Get image and check size
    im = Image.open(image_fileobj)
    # size of this image
    assert im.size == (1880, 363)
