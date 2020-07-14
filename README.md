# Python SDK for [CloudEvents](https://github.com/cloudevents/spec)

## Status

This SDK is still considered a work in progress, therefore things might (and
will) break with every update.

This SDK current supports the following versions of CloudEvents:

- v1.0
- v0.3

## Python SDK

Package **cloudevents** provides primitives to work with CloudEvents specification: https://github.com/cloudevents/spec.

Sending CloudEvents:

### Binary HTTP CloudEvent

```python
from cloudevents.sdk import converters
from cloudevents.sdk.http import CloudEvent, to_binary_http
import requests


# This data defines a binary cloudevent
attributes = {
    "Content-Type": "application/json",
    "type": "README.sample.binary",
    "id": "binary-event",
    "source": "README",
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
    "type": "README.sample.structured",
    "id": "structured-event",
    "source": "README",
}
data = {"message": "Hello World!"}
event = CloudEvent(attributes, data)
headers, body = to_structured_http(event)

# POST
requests.post("<some-url>", data=body, headers=headers)
```

### Event base classes usage

Parsing upstream structured Event from HTTP request:

```python
import io

from cloudevents.sdk.event import v1
from cloudevents.sdk import marshaller

m = marshaller.NewDefaultHTTPMarshaller()

event = m.FromRequest(
    v1.Event(),
    {"content-type": "application/cloudevents+json"},
    """
    {
        "specversion": "1.0",
        "datacontenttype": "application/json",
        "type": "word.found.name",
        "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "time": "2018-10-23T12:28:22.4579346Z",
        "source": "<source-url>"
    }
    """,
)
```

Parsing upstream binary Event from HTTP request:

```python
import io

from cloudevents.sdk.event import v1
from cloudevents.sdk import marshaller

m = marshaller.NewDefaultHTTPMarshaller()

event = m.FromRequest(
    v1.Event(),
    {
        "ce-specversion": "1.0",
        "content-type": "application/octet-stream",
        "ce-type": "word.found.name",
        "ce-id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "ce-time": "2018-10-23T12:28:22.4579346Z",
        "ce-source": "<source-url>",
    },
    b"this is where your CloudEvent data is, including image/jpeg",
    lambda x: x,  # Do not decode body as JSON
)
```

Creating HTTP request from CloudEvent:

```python
from cloudevents.sdk import converters
from cloudevents.sdk import marshaller
from cloudevents.sdk.converters import structured
from cloudevents.sdk.event import v1

event = (
    v1.Event()
    .SetContentType("application/json")
    .SetData('{"name":"john"}')
    .SetEventID("my-id")
    .SetSource("from-galaxy-far-far-away")
    .SetEventTime("tomorrow")
    .SetEventType("cloudevent.greet.you")
)

m = marshaller.NewDefaultHTTPMarshaller()

headers, body = m.ToRequest(event, converters.TypeStructured, lambda x: x)
```

## HOWTOs with various Python HTTP frameworks

In this topic you'd find various example how to integrate an SDK with various HTTP frameworks.

### Python requests

One of popular framework is [`requests`](http://docs.python-requests.org/en/master/).

#### CloudEvent to request

The code below shows how integrate both libraries in order to convert a CloudEvent into an HTTP request:

```python
from cloudevents.sdk.http import CloudEvent, to_binary_http, to_structured_http
from cloudevents.sdk.types import converters

def run_binary(event: CloudEvent, url):
    # If event.data is a custom type, set data_marshaller as well
    headers, data = to_binary_http(event)

    print("binary CloudEvent")
    for k, v in headers.items():
        print("{0}: {1}\r\n".format(k, v))
    print(data)
    response = requests.post(url,
                             headers=headers,
                             data=data)
    response.raise_for_status()


def run_structured(event: CloudEvent, url):
    # If event.data is a custom type, set data_marshaller as well
    headers, data = to_structured_http(event)

    print("structured CloudEvent")
    print(data)

    response = requests.post(url,
                             headers=headers,
                             data=data)
    response.raise_for_status()

```

Complete example of turning a CloudEvent into a request you can find [here](samples/python-requests/cloudevent_to_request.py).

#### Request to CloudEvent

The code below shows how integrate both libraries in order to create a CloudEvent from an HTTP response:

```python
    response = requests.get(url)
    response.raise_for_status()

    event = CloudEvent.from_http(response.content, response.headers)
```

Complete example of turning a CloudEvent into a request you can find [here](samples/python-requests/request_to_cloudevent.py).

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
