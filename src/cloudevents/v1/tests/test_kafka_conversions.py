#  Copyright 2018-Present The CloudEvents Authors
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import datetime
import json

import pytest

from cloudevents_v1 import exceptions as cloud_exceptions
from cloudevents_v1.http import CloudEvent
from cloudevents_v1.kafka.conversion import (
    KafkaMessage,
    from_binary,
    from_structured,
    to_binary,
    to_structured,
)
from cloudevents_v1.kafka.exceptions import KeyMapperError
from cloudevents_v1.sdk import types


def simple_serialize(data: dict) -> bytes:
    return bytes(json.dumps(data).encode("utf-8"))


def simple_deserialize(data: bytes) -> dict:
    return json.loads(data.decode())


def failing_func(*args):
    raise Exception("fail")


class KafkaConversionTestBase:
    expected_data = {"name": "test", "amount": 1}
    expected_custom_mapped_key = "custom-key"

    def custom_key_mapper(self, _) -> str:
        return self.expected_custom_mapped_key

    @pytest.fixture
    def source_event(self) -> CloudEvent:
        return CloudEvent.create(
            attributes={
                "specversion": "1.0",
                "id": "1234-1234-1234",
                "source": "pytest",
                "type": "com.pytest.test",
                "time": datetime.datetime(2000, 1, 1, 6, 42, 33).isoformat(),
                "datacontenttype": "foo",
                "partitionkey": "test_key_123",
            },
            data=self.expected_data,
        )

    @pytest.fixture
    def custom_marshaller(self) -> types.MarshallerType:
        return simple_serialize

    @pytest.fixture
    def custom_unmarshaller(self) -> types.UnmarshallerType:
        return simple_deserialize

    def test_custom_marshaller_can_talk_to_itself(
        self, custom_marshaller, custom_unmarshaller
    ):
        data = self.expected_data
        marshalled = custom_marshaller(data)
        unmarshalled = custom_unmarshaller(marshalled)
        for k, v in data.items():
            assert unmarshalled[k] == v


class TestToBinary(KafkaConversionTestBase):
    def test_sets_value_default_marshaller(self, source_event):
        result = to_binary(source_event)
        assert result.value == json.dumps(source_event.data).encode("utf-8")

    def test_sets_value_custom_marshaller(self, source_event, custom_marshaller):
        result = to_binary(source_event, data_marshaller=custom_marshaller)
        assert result.value == custom_marshaller(source_event.data)

    def test_sets_key(self, source_event):
        result = to_binary(source_event)
        assert result.key == source_event["partitionkey"]

    def test_key_mapper(self, source_event):
        result = to_binary(source_event, key_mapper=self.custom_key_mapper)
        assert result.key == self.expected_custom_mapped_key

    def test_key_mapper_error(self, source_event):
        with pytest.raises(KeyMapperError):
            to_binary(source_event, key_mapper=failing_func)

    def test_none_key(self, source_event):
        source_event["partitionkey"] = None
        result = to_binary(source_event)
        assert result.key is None

    def test_no_key(self, source_event):
        del source_event["partitionkey"]
        result = to_binary(source_event)
        assert result.key is None

    def test_sets_headers(self, source_event):
        result = to_binary(source_event)
        assert result.headers["ce_id"] == source_event["id"].encode("utf-8")
        assert result.headers["ce_specversion"] == source_event["specversion"].encode(
            "utf-8"
        )
        assert result.headers["ce_source"] == source_event["source"].encode("utf-8")
        assert result.headers["ce_type"] == source_event["type"].encode("utf-8")
        assert result.headers["ce_time"] == source_event["time"].encode("utf-8")
        assert result.headers["content-type"] == source_event["datacontenttype"].encode(
            "utf-8"
        )
        assert "data" not in result.headers
        assert "partitionkey" not in result.headers

    def test_raise_marshaller_exception(self, source_event):
        with pytest.raises(cloud_exceptions.DataMarshallerError):
            to_binary(source_event, data_marshaller=failing_func)


class TestFromBinary(KafkaConversionTestBase):
    @pytest.fixture
    def source_binary_json_message(self) -> KafkaMessage:
        return KafkaMessage(
            headers={
                "ce_specversion": "1.0".encode("utf-8"),
                "ce_id": "1234-1234-1234".encode("utf-8"),
                "ce_source": "pytest".encode("utf-8"),
                "ce_type": "com.pytest.test".encode("utf-8"),
                "ce_time": datetime.datetime(2000, 1, 1, 6, 42, 33)
                .isoformat()
                .encode("utf-8"),
                "content-type": "foo".encode("utf-8"),
            },
            value=json.dumps(self.expected_data).encode("utf-8"),
            key="test_key_123",
        )

    @pytest.fixture
    def source_binary_bytes_message(self) -> KafkaMessage:
        return KafkaMessage(
            headers={
                "ce_specversion": "1.0".encode("utf-8"),
                "ce_id": "1234-1234-1234".encode("utf-8"),
                "ce_source": "pytest".encode("utf-8"),
                "ce_type": "com.pytest.test".encode("utf-8"),
                "ce_time": datetime.datetime(2000, 1, 1, 6, 42, 33)
                .isoformat()
                .encode("utf-8"),
                "datacontenttype": "foo".encode("utf-8"),
            },
            value=simple_serialize(self.expected_data),
            key="test_key_123",
        )

    def test_default_marshaller(self, source_binary_json_message):
        result = from_binary(source_binary_json_message)
        assert result.data == json.loads(source_binary_json_message.value.decode())

    def test_custom_marshaller(self, source_binary_bytes_message, custom_unmarshaller):
        result = from_binary(
            source_binary_bytes_message, data_unmarshaller=custom_unmarshaller
        )
        assert result.data == custom_unmarshaller(source_binary_bytes_message.value)

    def test_sets_key(self, source_binary_json_message):
        result = from_binary(source_binary_json_message)
        assert result["partitionkey"] == source_binary_json_message.key

    def test_no_key(self, source_binary_json_message):
        keyless_message = KafkaMessage(
            headers=source_binary_json_message.headers,
            key=None,
            value=source_binary_json_message.value,
        )
        result = from_binary(keyless_message)
        assert "partitionkey" not in result.get_attributes()

    def test_sets_attrs_from_headers(self, source_binary_json_message):
        result = from_binary(source_binary_json_message)
        assert result["id"] == source_binary_json_message.headers["ce_id"].decode()
        assert (
            result["specversion"]
            == source_binary_json_message.headers["ce_specversion"].decode()
        )
        assert (
            result["source"] == source_binary_json_message.headers["ce_source"].decode()
        )
        assert result["type"] == source_binary_json_message.headers["ce_type"].decode()
        assert result["time"] == source_binary_json_message.headers["ce_time"].decode()
        assert (
            result["datacontenttype"]
            == source_binary_json_message.headers["content-type"].decode()
        )

    def test_unmarshaller_exception(self, source_binary_json_message):
        with pytest.raises(cloud_exceptions.DataUnmarshallerError):
            from_binary(source_binary_json_message, data_unmarshaller=failing_func)


class TestToFromBinary(KafkaConversionTestBase):
    def test_can_talk_to_itself(self, source_event):
        message = to_binary(source_event)
        event = from_binary(message)
        for key, val in source_event.get_attributes().items():
            assert event[key] == val
        for key, val in source_event.data.items():
            assert event.data[key] == val

    def test_can_talk_to_itself_custom_marshaller(
        self, source_event, custom_marshaller, custom_unmarshaller
    ):
        message = to_binary(source_event, data_marshaller=custom_marshaller)
        event = from_binary(message, data_unmarshaller=custom_unmarshaller)
        for key, val in source_event.get_attributes().items():
            assert event[key] == val
        for key, val in source_event.data.items():
            assert event.data[key] == val


class TestToStructured(KafkaConversionTestBase):
    def test_sets_value_default_marshallers(self, source_event):
        result = to_structured(source_event)
        assert result.value == json.dumps(
            {
                "specversion": source_event["specversion"],
                "id": source_event["id"],
                "source": source_event["source"],
                "type": source_event["type"],
                "time": source_event["time"],
                "partitionkey": source_event["partitionkey"],
                "data": self.expected_data,
            }
        ).encode("utf-8")

    def test_sets_value_custom_data_marshaller_default_envelope(
        self, source_event, custom_marshaller
    ):
        result = to_structured(source_event, data_marshaller=custom_marshaller)
        assert result.value == json.dumps(
            {
                "specversion": source_event["specversion"],
                "id": source_event["id"],
                "source": source_event["source"],
                "type": source_event["type"],
                "time": source_event["time"],
                "partitionkey": source_event["partitionkey"],
                "data_base64": base64.b64encode(
                    custom_marshaller(self.expected_data)
                ).decode("ascii"),
            }
        ).encode("utf-8")

    def test_sets_value_custom_envelope_marshaller(
        self, source_event, custom_marshaller
    ):
        result = to_structured(source_event, envelope_marshaller=custom_marshaller)
        assert result.value == custom_marshaller(
            {
                "specversion": source_event["specversion"],
                "id": source_event["id"],
                "source": source_event["source"],
                "type": source_event["type"],
                "time": source_event["time"],
                "partitionkey": source_event["partitionkey"],
                "data": self.expected_data,
            }
        )

    def test_sets_value_custom_marshallers(self, source_event, custom_marshaller):
        result = to_structured(
            source_event,
            data_marshaller=custom_marshaller,
            envelope_marshaller=custom_marshaller,
        )
        assert result.value == custom_marshaller(
            {
                "specversion": source_event["specversion"],
                "id": source_event["id"],
                "source": source_event["source"],
                "type": source_event["type"],
                "time": source_event["time"],
                "partitionkey": source_event["partitionkey"],
                "data_base64": base64.b64encode(
                    custom_marshaller(self.expected_data)
                ).decode("ascii"),
            }
        )

    def test_sets_key(self, source_event):
        result = to_structured(source_event)
        assert result.key == source_event["partitionkey"]

    def test_key_mapper(self, source_event):
        result = to_structured(source_event, key_mapper=self.custom_key_mapper)
        assert result.key == self.expected_custom_mapped_key

    def test_key_mapper_error(self, source_event):
        with pytest.raises(KeyMapperError):
            to_structured(source_event, key_mapper=failing_func)

    def test_none_key(self, source_event):
        source_event["partitionkey"] = None
        result = to_structured(source_event)
        assert result.key is None

    def test_no_key(self, source_event):
        del source_event["partitionkey"]
        result = to_structured(source_event)
        assert result.key is None

    def test_sets_headers(self, source_event):
        result = to_structured(source_event)
        assert len(result.headers) == 1
        assert result.headers["content-type"] == source_event["datacontenttype"].encode(
            "utf-8"
        )

    def test_datamarshaller_exception(self, source_event):
        with pytest.raises(cloud_exceptions.DataMarshallerError):
            to_structured(source_event, data_marshaller=failing_func)

    def test_envelope_datamarshaller_exception(self, source_event):
        with pytest.raises(cloud_exceptions.DataMarshallerError):
            to_structured(source_event, envelope_marshaller=failing_func)


class TestToFromStructured(KafkaConversionTestBase):
    def test_can_talk_to_itself(self, source_event):
        message = to_structured(source_event)
        event = from_structured(message)
        for key, val in source_event.get_attributes().items():
            assert event[key] == val
        for key, val in source_event.data.items():
            assert event.data[key] == val


class TestFromStructured(KafkaConversionTestBase):
    @pytest.fixture
    def source_structured_json_message(self) -> KafkaMessage:
        return KafkaMessage(
            headers={
                "content-type": "foo".encode("utf-8"),
            },
            value=json.dumps(
                {
                    "specversion": "1.0",
                    "id": "1234-1234-1234",
                    "source": "pytest",
                    "type": "com.pytest.test",
                    "time": datetime.datetime(2000, 1, 1, 6, 42, 33).isoformat(),
                    "partitionkey": "test_key_123",
                    "data": self.expected_data,
                }
            ).encode("utf-8"),
            key="test_key_123",
        )

    @pytest.fixture
    def source_structured_json_bytes_message(self) -> KafkaMessage:
        return KafkaMessage(
            headers={
                "content-type": "foo".encode("utf-8"),
            },
            value=json.dumps(
                {
                    "specversion": "1.0",
                    "id": "1234-1234-1234",
                    "source": "pytest",
                    "type": "com.pytest.test",
                    "time": datetime.datetime(2000, 1, 1, 6, 42, 33).isoformat(),
                    "partitionkey": "test_key_123",
                    "data_base64": base64.b64encode(
                        simple_serialize(self.expected_data)
                    ).decode("ascii"),
                }
            ).encode("utf-8"),
            key="test_key_123",
        )

    @pytest.fixture
    def source_structured_bytes_bytes_message(self) -> KafkaMessage:
        return KafkaMessage(
            headers={
                "content-type": "foo".encode("utf-8"),
            },
            value=simple_serialize(
                {
                    "specversion": "1.0",
                    "id": "1234-1234-1234",
                    "source": "pytest",
                    "type": "com.pytest.test",
                    "time": datetime.datetime(2000, 1, 1, 6, 42, 33).isoformat(),
                    "partitionkey": "test_key_123",
                    "data_base64": base64.b64encode(
                        simple_serialize(self.expected_data)
                    ).decode("ascii"),
                }
            ),
            key="test_key_123",
        )

    def test_sets_data_default_data_unmarshaller(
        self,
        source_structured_json_message,
    ):
        result = from_structured(source_structured_json_message)
        assert result.data == self.expected_data

    def test_sets_data_custom_data_unmarshaller(
        self, source_structured_json_bytes_message, custom_unmarshaller
    ):
        result = from_structured(
            source_structured_json_bytes_message, data_unmarshaller=custom_unmarshaller
        )
        assert result.data == self.expected_data

    def test_sets_data_custom_unmarshallers(
        self, source_structured_bytes_bytes_message, custom_unmarshaller
    ):
        result = from_structured(
            source_structured_bytes_bytes_message,
            data_unmarshaller=custom_unmarshaller,
            envelope_unmarshaller=custom_unmarshaller,
        )
        assert result.data == self.expected_data

    def test_sets_attrs_default_enveloper_unmarshaller(
        self,
        source_structured_json_message,
    ):
        result = from_structured(source_structured_json_message)
        for key, value in json.loads(
            source_structured_json_message.value.decode()
        ).items():
            if key != "data":
                assert result[key] == value

    def test_sets_attrs_custom_enveloper_unmarshaller(
        self,
        source_structured_bytes_bytes_message,
        custom_unmarshaller,
    ):
        result = from_structured(
            source_structured_bytes_bytes_message,
            data_unmarshaller=custom_unmarshaller,
            envelope_unmarshaller=custom_unmarshaller,
        )
        for key, value in custom_unmarshaller(
            source_structured_bytes_bytes_message.value
        ).items():
            if key not in ["data_base64"]:
                assert result[key] == value

    def test_sets_content_type_default_envelope_unmarshaller(
        self,
        source_structured_json_message,
    ):
        result = from_structured(source_structured_json_message)
        assert (
            result["datacontenttype"]
            == source_structured_json_message.headers["content-type"].decode()
        )

    def test_sets_content_type_custom_envelope_unmarshaller(
        self, source_structured_bytes_bytes_message, custom_unmarshaller
    ):
        result = from_structured(
            source_structured_bytes_bytes_message,
            data_unmarshaller=custom_unmarshaller,
            envelope_unmarshaller=custom_unmarshaller,
        )
        assert (
            result["datacontenttype"]
            == source_structured_bytes_bytes_message.headers["content-type"].decode()
        )

    def test_data_unmarshaller_exception(
        self, source_structured_bytes_bytes_message, custom_unmarshaller
    ):
        with pytest.raises(cloud_exceptions.DataUnmarshallerError):
            from_structured(
                source_structured_bytes_bytes_message,
                data_unmarshaller=failing_func,
                envelope_unmarshaller=custom_unmarshaller,
            )

    def test_envelope_unmarshaller_exception(
        self,
        source_structured_bytes_bytes_message,
    ):
        with pytest.raises(cloud_exceptions.DataUnmarshallerError):
            from_structured(
                source_structured_bytes_bytes_message,
                envelope_unmarshaller=failing_func,
            )
