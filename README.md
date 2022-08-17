# Python SDK for [CloudEvents](https://github.com/cloudevents/spec)

[![PyPI version](https://badge.fury.io/py/cloudevents.svg)](https://badge.fury.io/py/cloudevents)

## Status

This SDK is still considered a work in progress, therefore things might (and
will) break with every update.

This SDK current supports the following versions of CloudEvents:

- v1.0
- v0.3

## Python SDK

Package **cloudevents** provides primitives to work with CloudEvents specification:
https://github.com/cloudevents/spec.

### Installing

The CloudEvents SDK can be installed with pip:

```
pip install cloudevents
```

## Sending CloudEvents

Below we will provide samples on how to send cloudevents using the popular
[`requests`](http://docs.python-requests.org) library.

### Binary HTTP CloudEvent

```python
from cloudevents.http import CloudEvent
from cloudevents.conversion import to_binary
import requests

# Create a CloudEvent
# - The CloudEvent "id" is generated if omitted. "specversion" defaults to "1.0".
attributes = {
    "type": "com.example.sampletype1",
    "source": "https://example.com/event-producer",
}
data = {"message": "Hello World!"}
event = CloudEvent(attributes, data)

# Creates the HTTP request representation of the CloudEvent in binary content mode
headers, body = to_binary(event)

# POST
requests.post("<some-url>", data=body, headers=headers)
```

### Structured HTTP CloudEvent

```python
from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent
import requests

# Create a CloudEvent
# - The CloudEvent "id" is generated if omitted. "specversion" defaults to "1.0".
attributes = {
    "type": "com.example.sampletype2",
    "source": "https://example.com/event-producer",
}
data = {"message": "Hello World!"}
event = CloudEvent(attributes, data)

# Creates the HTTP request representation of the CloudEvent in structured content mode
headers, body = to_structured(event)

# POST
requests.post("<some-url>", data=body, headers=headers)
```

You can find a complete example of turning a CloudEvent into a HTTP request
[in the samples' directory](samples/http-json-cloudevents/client.py).

## Receiving CloudEvents

The code below shows how to consume a cloudevent using the popular python web framework
[flask](https://flask.palletsprojects.com/en/2.2.x/quickstart/):

```python
from flask import Flask, request

from cloudevents.http import from_http

app = Flask(__name__)


# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def home():
    # create a CloudEvent
    event = from_http(request.headers, request.get_data())

    # you can access cloudevent fields as seen below
    print(
        f"Found {event['id']} from {event['source']} with type "
        f"{event['type']} and specversion {event['specversion']}"
    )

    return "", 204


if __name__ == "__main__":
    app.run(port=3000)
```

You can find a complete example of turning a CloudEvent into a HTTP request
[in the samples' directory](samples/http-json-cloudevents/json_sample_server.py).

## SDK versioning

The goal of this package is to provide support for all released versions of CloudEvents,
ideally while maintaining the same API. It will use semantic versioning
with following rules:

- MAJOR version increments when backwards incompatible changes is introduced.
- MINOR version increments when backwards compatible feature is introduced
  INCLUDING support for new CloudEvents version.
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

Each SDK may have its own unique processes, tooling and guidelines, common
governance related material can be found in the
[CloudEvents `docs`](https://github.com/cloudevents/spec/tree/main/docs)
directory. In particular, in there you will find information concerning
how SDK projects are
[managed](https://github.com/cloudevents/spec/blob/main/docs/GOVERNANCE.md),
[guidelines](https://github.com/cloudevents/spec/blob/main/docs/SDK-maintainer-guidelines.md)
for how PR reviews and approval, and our
[Code of Conduct](https://github.com/cloudevents/spec/blob/main/docs/GOVERNANCE.md#additional-information)
information.

## Maintenance

We use [black][black] and [isort][isort] for autoformatting. We set up a [tox][tox]
environment to reformat the codebase.

e.g.

```bash
pip install tox
tox -e reformat
```

For information on releasing version bumps see [RELEASING.md](RELEASING.md)

[black]: https://black.readthedocs.io/
[isort]: https://pycqa.github.io/isort/
[tox]: https://tox.wiki/
