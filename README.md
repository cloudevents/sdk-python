# Python SDK for [CloudEvents](https://github.com/cloudevents/spec)

**NOTE: This SDK is still considered work in progress, things might (and will) break with every update.**

Package **cloudevents** provides primitives to work with CloudEvents specification: https://github.com/cloudevents/spec.

Parsing upstream Event from HTTP Request:
```python
import io

from cloudevents.sdk.event import v02
from cloudevents.sdk import marshaller

m = marshaller.NewDefaultHTTPMarshaller()
event = m.FromRequest(
    v02.Event(),
    {
        "content-type": "application/cloudevents+json",
        "ce-specversion": "0.2",
        "ce-time": "2018-10-23T12:28:22.4579346Z",
        "ce-id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "ce-source": "<source-url>",
        "ce-type": "word.found.name",
    },
    io.BytesIO(b"this is where your CloudEvent data"), 
    lambda x: x.read()
)

```

Creating a minimal CloudEvent in version 0.1:
```python
from cloudevents.sdk.event import v01

event = (
    v01.Event().
    SetContentType("application/json").
    SetData('{"name":"john"}').
    SetEventID("my-id").
    SetSource("from-galaxy-far-far-away").
    SetEventTime("tomorrow").
    SetEventType("cloudevent.greet.you")
)

```

Creating HTTP request from CloudEvent:
```python
from cloudevents.sdk import converters
from cloudevents.sdk import marshaller
from cloudevents.sdk.converters import structured
from cloudevents.sdk.event import v01

event = (
    v01.Event().
    SetContentType("application/json").
    SetData('{"name":"john"}').
    SetEventID("my-id").
    SetSource("from-galaxy-far-far-away").
    SetEventTime("tomorrow").
    SetEventType("cloudevent.greet.you")
)
m = marshaller.NewHTTPMarshaller(
    [
        structured.NewJSONHTTPCloudEventConverter()
    ]
)

headers, body = m.ToRequest(event, converters.TypeStructured, lambda x: x)

```

The goal of this package is to provide support for all released versions of CloudEvents, ideally while maintaining
the same API. It will use semantic versioning with following rules:
* MAJOR version increments when backwards incompatible changes is introduced.
* MINOR version increments when backwards compatible feature is introduced INCLUDING support for new CloudEvents version.
* PATCH version increments when a backwards compatible bug fix is introduced.
