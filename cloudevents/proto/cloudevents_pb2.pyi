from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CloudEvent(_message.Message):
    __slots__ = ["attributes", "binary_data", "id", "proto_data", "source", "spec_version", "text_data", "type"]
    class AttributesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: CloudEvent.CloudEventAttributeValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[CloudEvent.CloudEventAttributeValue, _Mapping]] = ...) -> None: ...
    class CloudEventAttributeValue(_message.Message):
        __slots__ = ["ce_boolean", "ce_bytes", "ce_integer", "ce_string", "ce_timestamp", "ce_uri", "ce_uri_ref"]
        CE_BOOLEAN_FIELD_NUMBER: _ClassVar[int]
        CE_BYTES_FIELD_NUMBER: _ClassVar[int]
        CE_INTEGER_FIELD_NUMBER: _ClassVar[int]
        CE_STRING_FIELD_NUMBER: _ClassVar[int]
        CE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        CE_URI_FIELD_NUMBER: _ClassVar[int]
        CE_URI_REF_FIELD_NUMBER: _ClassVar[int]
        ce_boolean: bool
        ce_bytes: bytes
        ce_integer: int
        ce_string: str
        ce_timestamp: _timestamp_pb2.Timestamp
        ce_uri: str
        ce_uri_ref: str
        def __init__(self, ce_boolean: bool = ..., ce_integer: _Optional[int] = ..., ce_string: _Optional[str] = ..., ce_bytes: _Optional[bytes] = ..., ce_uri: _Optional[str] = ..., ce_uri_ref: _Optional[str] = ..., ce_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    BINARY_DATA_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PROTO_DATA_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SPEC_VERSION_FIELD_NUMBER: _ClassVar[int]
    TEXT_DATA_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    attributes: _containers.MessageMap[str, CloudEvent.CloudEventAttributeValue]
    binary_data: bytes
    id: str
    proto_data: _any_pb2.Any
    source: str
    spec_version: str
    text_data: str
    type: str
    def __init__(self, id: _Optional[str] = ..., source: _Optional[str] = ..., spec_version: _Optional[str] = ..., type: _Optional[str] = ..., attributes: _Optional[_Mapping[str, CloudEvent.CloudEventAttributeValue]] = ..., binary_data: _Optional[bytes] = ..., text_data: _Optional[str] = ..., proto_data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class CloudEventBatch(_message.Message):
    __slots__ = ["events"]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[CloudEvent]
    def __init__(self, events: _Optional[_Iterable[_Union[CloudEvent, _Mapping]]] = ...) -> None: ...
