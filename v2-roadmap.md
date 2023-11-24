# V2 implementation proposal

## Why this proposal

The current implementation uses different `CloudEvent` classes for the implementation
of different protocol bindings. This adds complexity the integration of new technologies
like `pydantic`.

The separation of responsibilities in the package is not clear. We have multiple JSON
implementations, while the format specification is the same for all bindings in the
[`CloudEvent` spec](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/formats/json-format.md):

* Pydantic implementation is calling the HTTP implementation for this, adding unnecessary overhead
* the Kafka binding uses its own implementation, creating code duplication and unnecessary maintenance efforts

We should have a single `CloudEvent` class used for all bindings/formats since the event
is the Python representation of the event data, which is the same no matter what binding
is used. (we potentially could receive a HTTP event and forward it as it is using Kafka).

The specific bindings and formats implementations should be separate from the `CloudEvent`
class.

This proposal contains some base rules for the package architecture and how we could implement
the `CloudEvent` spec in this package.

## Requirements

In order to be able to transform a python CloudEvent to/from a specific
protocol binding, this SDK has the following responsibilities:

* Identifying what attributes have to be marshalled/unmarshalled (identifying the cloudevents extensions)
* Validate required fields and generation of defaults
* Marshalling/unmarshalling the cloudevents core and extensions fields
* Marshalling/unmarshalling the `data` field
* Encode/decode the marshalled fields to/from the specific binding format

We want to separate the responsibilities that belong to the event and its implementation
in the user system (data, extensions) from the binding and format specification for
core fields.

## Modules

We should separate the implementation of the requirements so that they can be tested independently and
each component be used for composition.

Ideally we should have these modules (naming TBC):

* `cloudevents.event` - This would contain the `CloudEvent` base class. This class is the same for all bindings/formats.
* `cloudevents.formats` - This would contain the structured formats implementations (JSON, AVRO, Protobuf)
* `cloudevents.bindings` - This would contain the specific binding implementations (kafka, http)

This matches the naming and concepts we have in the `CloudEvent` spec

## Matching requirements and modules

### The `cloudevents.event` module and `CloudEvent` class

The `CloudEvent` class would satisfy the following requirements:

* Validate required fields and generation of default values
* Marshalling/unmarshalling the `data` field
* Identifying what attributes have to be marshalled/unmarshalled

The `data` field depends on the specific event and the `contentdatatype` attribute and
its marshalling/unmarshalling logic should be the same for any binding/format. It seems
a `CloudEvent` class responsibility to take care of this. (We should implement this logic
in overridable methods)

Ideally the end user will be able to extend the `CloudEvent` class for their necessity. Ie:

* adding new extensions fields
* adding fields/methods not meant to be marshalled (internal fields)
* implementing new defaults (ie. creating a `MyEvent` class with `type="myevent"` default)

We also want a DTO that can be accepted by the most common libraries (ie. JSON) to keep the
`CloudEvent` class decoupled from the formats/bindings. Using a dictionary seems a good idea.

We should implement a `to_dict`/`from_dict` functionalities in the `CloudEvent` class.

QUESTION: Can we define a data type for the `data` field after it's been marshalled?
(ie. can we say it will be either `str` or binary data?)

### Formats

Formats do solve a single responsibility:

* Marshalling/unmarshalling the cloudevents core and extensions fields

Their implementation has to be used when other bindings implement their
structured input/output and make sure their implementation is compatible.

Each format accepts the dictionary from the `CloudEvent` as param
and produces an output based on the format itself. Ie.

```python
def to_json(event: dict) -> str: ...
def from_json(event: str) -> dict: ...
```

TODO: Review typing as JSON produces a string but other formats might be different.

### Bindings

Bindings do solve these responsibilities:

* Marshalling/unmarshalling the cloudevents core and extensions fields **(if binary format)**
* Encode/decode the marshalled fields to/from the specific binding format

They also have the responsibility of coordinating the other modules.

This is a **concept** example for `cloudevents.bindings.http` module

```python
from cloudevents.formats.json import to_json, from_json
from cloudevents.event import CloudEvent


# Shared dataclass to help with typing, might be a dictionary or a named tuple (not important)
@dataclass
class HTTPCloudEvent:
    headers: list
    body: Any  # unsure about typing here

    
def to_binary(event: CloudEvent) -> HTTPCloudEvent:
    e = event.to_dict()
    # logic to marshall into http binary output
    return HTTPCloudEvent(headers=[], body=[])


def to_json(event: CloudEvent) -> HTTPCloudEvent:
    e = to_json(event.to_dict())
    # logic to compose the JSON response
    return HTTPCloudEvent(headers=[], body=[])


def from_binary(headers: list, body: dict) -> CloudEvent:
    e = {}
    # specific logic to unmarshall raw headers into a dictionary
    return CloudEvent.from_dict(e)


def from_json(body: str) -> CloudEvent:
    e = from_json(body)
    return CloudEvent.from_dict(e)


def from_http(headers: list, body: dict) -> CloudEvent:
    # identify if structured or binary based on headers / body
    # and use the proper `from_` function
    # We should also handle here batches
    ...
```

Other bindings would behave similarly, where the end user would need only
to use the relevant module in `cloudevents.bindings` namespace.

## CloudEvent subclasses

We'll want SDK users to be able to extend the `CloudEvent` class, so they will
be able to manage marshalling/unmarshalling of the `data` field for different
event types and their python typing.

This could be easily done by introducing a mapping between the `type` field and
`CloudEvent` subclasses as a parameter in the `from_` functions. Ie.

```python
def from_binary(headers: list, body: dict, event_types: Optional[dict[str, type]] = None) -> CloudEvent:
    event_as_dict = {}
    # specific logic to unmarshall raw headers into a dictionary
    if event_types:
        # Use 
        return event_types.get(event_as_dict['type'], CloudEvent).from_dict(e)
    else:    
        return CloudEvent.from_dict(e)
```

## Pydantic support

The current Pydantic implementation is implemented as a possible substitute of
HTTP Event class, by looking at its conversion module and tests, but it's used
by calling the functions in conversion module.

Pydantic offers good support and performance for data validation, defaults and
JSON serialization (some of the requirements we have identified)

We need to make a decision:

* We use pydantic as a base for `CloudEvent` class:
  * PROs
    * No need to implement data validation
    * Performance (pydantic V2 is written in Rust)
    * We can lay down some base logic on `data` field serialization (ie. nested pydantic models)
    * Enable users to use pydantic for automatic documentation functionalities
  * CONs
    * We introduce a new package dependency, and depend on its implementation
    * _minor_ If we use pydantic JSON serialization it is implemented in the model class (slightly different from what proposed but we can use wrapper functions in the JSON format module)
* We remove pydantic support:
  * PROs
    * We have more control over validation and defaults implementation
    * We don't depend on other packages
  * CONs
    * Performance on validation and defaults (we can still use libraries like `orjson` for JSON performance)
    * Additional effort in writing and maintaining data validation and required/default fields
...
