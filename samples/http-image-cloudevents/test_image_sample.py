import base64
import io
import json
import typing

import requests
from PIL import Image

from cloudevents.sdk import converters
from cloudevents.sdk.http import (
    CloudEvent,
    from_http,
    to_binary_http,
    to_structured_http,
)


def test_create_binary_image():
    # Create image and turn image into bytes
    size = (8, 8)
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
        "size": json.dumps(size),
    }
    image = Image.new("RGB", size)

    data = image.tobytes()

    # Create CloudEvent
    event = CloudEvent(attributes, data)

    # Test size extension was marshalled properly
    event_image_size = json.loads(event["size"])
    assert event_image_size[0] == size[0] and event_image_size[1] == size[1]

    # Test we can create an image from the marshalled data
    restore_image = Image.frombytes("RGB", event_image_size, event.data)
    assert restore_image.size[0] == size[0], restore_image.size[1] == size[1]

    # Create http headers/body content
    headers, body = to_binary_http(event, data_marshaller=lambda x: x)

    # Test cloudevent extension from http fields and data
    assert headers["ce-size"] == attributes["size"]
    assert isinstance(body, bytes)
    assert isinstance(data, bytes)
    assert body == data


def test_create_structured_image():
    # Create image and turn image into bytes
    size = (8, 8)
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
        "size": json.dumps(size),
    }
    image = Image.new("RGB", size)

    bytesarr = image.tobytes()

    # Create CloudEvent
    event = CloudEvent(attributes, bytesarr)

    # Test size extension was marshalled properly
    event_image_size = json.loads(event["size"])
    assert event_image_size[0] == size[0] and event_image_size[1] == size[1]

    # Test we can create an image from the marshalled data
    restore_image = Image.frombytes("RGB", event_image_size, event.data)
    assert restore_image.size[0] == size[0], restore_image.size[1] == size[1]

    # Create http headers/body content
    headers, body = to_structured_http(event)
    data = json.loads(body.decode())

    # TODO: Extensions need to be top level in structured request

    # Test extension size and marshalled data to original
    assert data["extensions"]["size"] == attributes["size"]
    assert base64.b64decode(data["data_base64"]) == bytesarr

    restored_event = from_http(body, headers)
    assert restored_event.data == bytesarr


def test_image_content():
    # Get image and check size
    resp = requests.get(
        "https://raw.githubusercontent.com/cncf/artwork/master/projects/cloudevents/horizontal/color/cloudevents-horizontal-color.png"
    )
    image_bytes_fileobj = io.BytesIO(resp.content)
    im = Image.open(image_bytes_fileobj)
    # size of this image
    assert im.size == (1880, 363)
