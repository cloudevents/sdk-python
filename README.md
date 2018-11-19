# Python SDK for [CloudEvents](https://github.com/cloudevents/spec)

**NOTE: This SDK is still considered work in progress, things might (and will) break with every update.**

Package **cloudevents** provides primitives to work with CloudEvents specification: https://github.com/cloudevents/spec.

Parsing upstream Event from HTTP Request:
```python
from cloudevents.sdk.event import upstream
from cloudevents.sdk import marshaller

data = "<this is where your CloudEvent comes from>"
m = marshaller.NewDefaultHTTPMarshaller(upstream.Event)
event = m.FromRequest(
    {"Content-Type": "application/cloudevents+json"}, 
    data, 
    lambda x: x.read()
)

```

Creating a minimal CloudEvent in version 0.1:
```python
from cloudevents.sdk.event import v01

event = (
    v01.Event().
    WithContentType("application/json").
    WithData('{"name":"john"}').
    WithEventID("my-id").
    WithSource("from-galaxy-far-far-away").
    WithEventTime("tomorrow").
    WithEventType("cloudevent.greet.you")
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
    WithContentType("application/json").
    WithData('{"name":"john"}').
    WithEventID("my-id").
    WithSource("from-galaxy-far-far-away").
    WithEventTime("tomorrow").
    WithEventType("cloudevent.greet.you")
)
m = marshaller.NewHTTPMarshaller(
    [
        structured.NewJSONHTTPCloudEventConverter(type(event))
    ]
)

headers, body = m.ToRequest(event, converters.TypeStructured, lambda x: x)

```

The goal of this package is to provide support for all released versions of CloudEvents, ideally while maintaining
the same API. It will use semantic versioning with following rules:
* MAJOR version increments when backwards incompatible changes is introduced.
* MINOR version increments when backwards compatible feature is introduced INCLUDING support for new CloudEvents version.
* PATCH version increments when a backwards compatible bug fix is introduced.
