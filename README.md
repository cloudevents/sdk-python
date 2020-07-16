# Python SDK for [CloudEvents](https://github.com/cloudevents/spec)

## Status

This SDK is still considered a work in progress, therefore things might (and
will) break with every update.

This SDK current supports the following versions of CloudEvents:

- v1.0
- v0.3

## Python SDK

Package **cloudevents** provides primitives to work with CloudEvents specification: https://github.com/cloudevents/spec.

## Sending CloudEvents

Below we will provide samples on how to send cloudevents using the popular
[`requests`](http://docs.python-requests.org) library.

### Binary HTTP CloudEvent

```python
from cloudevents.sdk.http import CloudEvent, to_binary_http
import requests


# This data defines a binary cloudevent
attributes = {
    "type": "com.example.sampletype1",
    "source": "https://example.com/event-producer",
}
data = {"message": "Hello World!"}

event = CloudEvent(attributes, data)
headers, body = to_binary_http(event)

# POST
requests.post("<some-url>", data=body, headers=headers)
```

### Structured HTTP CloudEvent

```python
from cloudevents.sdk.http import CloudEvent, to_structured_http
import requests


# This data defines a structured cloudevent
attributes = {
    "type": "com.example.sampletype2",
    "source": "https://example.com/event-producer",
}
data = {"message": "Hello World!"}
event = CloudEvent(attributes, data)
headers, body = to_structured_http(event)

# POST
requests.post("<some-url>", data=body, headers=headers)
```

You can find a complete example of turning a CloudEvent into a HTTP request [in the samples directory](samples/http-cloudevents/client.py).

#### Request to CloudEvent

The code below shows how to consume a cloudevent using the popular python web framework
[flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/):

```python
from flask import Flask, request

from cloudevents.sdk.http_events import from_http

app = Flask(__name__)

# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def home():
    # create a CloudEvent
    event = from_http(request.get_data(), request.headers)

    # you can access cloudevent fields as seen below
    print(f"Found CloudEvent from {event['source']} with specversion {event['specversion']}")

    if event['type'] == 'com.example.sampletype1':
        print(f"CloudEvent {event['id']} is binary")

    elif event['type'] == 'com.example.sampletype2':
        print(f"CloudEvent {event['id']} is structured")

    return "", 204


if __name__ == "__main__":
    app.run(port=3000)
```

You can find a complete example of turning a CloudEvent into a HTTP request [in the samples directory](samples/http-cloudevents/server.py).

## SDK versioning

The goal of this package is to provide support for all released versions of CloudEvents, ideally while maintaining
the same API. It will use semantic versioning with following rules:

- MAJOR version increments when backwards incompatible changes is introduced.
- MINOR version increments when backwards compatible feature is introduced INCLUDING support for new CloudEvents version.
- PATCH version increments when a backwards compatible bug fix is introduced.

## Community

- There are bi-weekly calls immediately following the [Serverless/CloudEvents
  call](https://github.com/cloudevents/spec#meeting-time) at
  9am PT (US Pacific). Which means they will typically start at 10am PT, but
  if the other call ends early then the SDK call will start early as well.
  See the [CloudEvents meeting minutes](https://docs.google.com/document/d/1OVF68rpuPK5shIHILK9JOqlZBbfe91RNzQ7u_P7YCDE/edit#)
  to determine which week will have the call.
- Slack: #cloudeventssdk channel under
  [CNCF's Slack workspace](https://slack.cncf.io/).
- Email: https://lists.cncf.io/g/cncf-cloudevents-sdk
- Contact for additional information: Denis Makogon (`@denysmakogon` on slack).

## Maintenance

We use black and isort for autoformatting. We setup a tox environment to reformat
the codebase.

e.g.

```python
pip install tox
tox -e reformat
```
