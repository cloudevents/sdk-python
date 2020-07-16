import base64
import json

from PIL import Image

from cloudevents.sdk import converters
from cloudevents.sdk.http_events import CloudEvent


def test_create_binary_image():
    size = (8, 8)

    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
        "size": json.dumps(size),
    }

    image = Image.new("RGB", size)
    bytestr = image.tobytes().decode()

    event = CloudEvent(attributes, bytestr)

    event_image_size = json.loads(event["size"])
    assert event_image_size[0] == size[0] and event_image_size[1] == size[1]

    restore_image = Image.frombytes(
        "RGB", event_image_size, event.data.encode()
    )
    assert restore_image.size[0] == size[0], restore_image.size[1] == size[1]

    headers, body = event.to_http(converters.TypeBinary)
    assert headers["ce-size"] == attributes["size"]
    assert json.loads(body.decode()) == bytestr


def test_create_structured_image():
    size = (8, 8)

    attributes = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
        "size": json.dumps(size),
    }

    image = Image.new("RGB", size)
    bytesarr = image.tobytes()

    event = CloudEvent(attributes, bytesarr)

    event_image_size = json.loads(event["size"])
    assert event_image_size[0] == size[0] and event_image_size[1] == size[1]

    restore_image = Image.frombytes("RGB", event_image_size, event.data)
    assert restore_image.size[0] == size[0], restore_image.size[1] == size[1]

    headers, body = event.to_http()
    data = json.loads(body.decode())

    assert data["extensions"]["size"] == attributes["size"]
    assert base64.b64decode(data["data_base64"]) == bytesarr

    restored_event = CloudEvent.from_http(body, headers)
    assert restored_event.data == bytesarr
