import base64
import io
import json

import requests
from PIL import Image

from cloudevents.sdk.http import (
    CloudEvent,
    from_http,
    to_binary_http,
    to_structured_http,
)

resp = requests.get(
    "https://raw.githubusercontent.com/cncf/artwork/master/projects/cloudevents/horizontal/color/cloudevents-horizontal-color.png"
)
image_bytes = resp.content

image_fileobj = io.BytesIO(image_bytes)
image_expected_shape = (1880, 363)


def test_create_binary_image():
    # Create image and turn image into bytes
    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
    }

    # Create CloudEvent
    event = CloudEvent(attributes, image_bytes)

    # Create http headers/body content
    headers, body = to_binary_http(event)

    # Unmarshall CloudEvent and re-create image
    reconstruct_event = from_http(
        body, headers, data_unmarshaller=lambda x: io.BytesIO(x)
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
    headers, body = to_structured_http(event)

    # Structured has cloudevent attributes marshalled inside the body. For this
    # reason we must load the byte object to create the python dict containing
    # the cloudevent attributes
    data = json.loads(body)

    # Test cloudevent extension from http fields and data
    assert isinstance(data, dict)
    assert base64.b64decode(data["data_base64"]) == image_bytes

    # Unmarshall CloudEvent and re-create image
    reconstruct_event = from_http(
        body, headers, data_unmarshaller=lambda x: io.BytesIO(x)
    )

    # reconstruct_event.data is an io.BytesIO object due to data_unmarshaller
    restore_image = Image.open(reconstruct_event.data)
    assert restore_image.size == image_expected_shape


def test_image_content():

    # Get image and check size
    im = Image.open(image_fileobj)
    # size of this image
    assert im.size == (1880, 363)
