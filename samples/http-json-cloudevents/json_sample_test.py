import pytest
from json_sample_server import app

from cloudevents.http import CloudEvent, to_binary_http, to_structured_http


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_binary_request(client):
    # This data defines a binary cloudevent
    attributes = {
        "type": "com.example.sampletype1",
        "source": "https://example.com/event-producer",
    }
    data = {"message": "Hello World!"}

    event = CloudEvent(attributes, data)
    headers, body = to_binary_http(event)

    r = client.post("/", headers=headers, data=body)
    assert r.status_code == 204


def test_structured_request(client):
    # This data defines a binary cloudevent
    attributes = {
        "type": "com.example.sampletype2",
        "source": "https://example.com/event-producer",
    }
    data = {"message": "Hello World!"}

    event = CloudEvent(attributes, data)
    headers, body = to_structured_http(event)

    r = client.post("/", headers=headers, data=body)
    assert r.status_code == 204
