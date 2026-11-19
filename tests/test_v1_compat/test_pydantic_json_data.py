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
"""JSON serialization of Pydantic CloudEvent ``data`` (issue #213)."""

import datetime
import json
import uuid
from decimal import Decimal
from typing import Any, Optional

import pytest
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from pydantic.v1 import BaseModel as V1BaseModel
from pydantic.v1 import Field as V1Field

from cloudevents.v1.pydantic import CloudEvent as PublicCloudEvent
from cloudevents.v1.pydantic.v1.event import CloudEvent as PydanticV1CloudEvent
from cloudevents.v1.pydantic.v2.event import CloudEvent as PydanticV2CloudEvent

_SOURCE = "my.source"
_TYPE = "com.my.type"
_EVENT_ID = "event-id"
_AWARE = datetime.datetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=datetime.timezone.utc)
_NAIVE = datetime.datetime(2024, 1, 2, 3, 4, 5)
_OFFSET = datetime.datetime(
    2024, 1, 2, 3, 4, 5, tzinfo=datetime.timezone(datetime.timedelta(hours=8))
)
_DATE = datetime.date(2024, 5, 6)
_TIME = datetime.time(7, 8, 9)
_UUID = uuid.UUID("12345678-1234-5678-1234-567812345678")
_DECIMAL = Decimal("1.50")

_pydantic_implementation = {
    "v1": {"event": PydanticV1CloudEvent, "pydantic_version": "v1"},
    "v2": {"event": PydanticV2CloudEvent, "pydantic_version": "v2"},
}


class _V2Inner(BaseModel):
    when: datetime.datetime
    label: str
    note: Optional[str] = None
    n: int = 1


class _V2Aliased(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    foo_bar: int = Field(alias="fooBar")
    when: datetime.datetime
    note: Optional[str] = None
    n: int = 1


class _V2DataOracle(BaseModel):
    """Plain Pydantic model used as the JSON oracle for ``data``."""

    data: Any = None


class _V1Inner(V1BaseModel):
    when: datetime.datetime
    label: str
    note: Optional[str] = None
    n: int = 1


class _V1Aliased(V1BaseModel):
    class Config:
        allow_population_by_field_name = True

    foo_bar: int = V1Field(alias="fooBar")
    when: datetime.datetime
    note: Optional[str] = None
    n: int = 1


class _V1DataOracle(V1BaseModel):
    data: Any = None


@pytest.fixture(params=["v1", "v2"])
def cloudevents_implementation(request):
    return _pydantic_implementation[request.param]


def _attributes(specversion="1.0"):
    return {
        "source": _SOURCE,
        "type": _TYPE,
        "id": _EVENT_ID,
        "specversion": specversion,
        "time": _AWARE,
    }


def _event_json(implementation, event, **kwargs):
    if implementation["pydantic_version"] == "v2":
        return event.model_dump_json(**kwargs)
    return event.json(**kwargs)


def _expected_data(implementation, data, **kwargs):
    if implementation["pydantic_version"] == "v2":
        encoded = _V2DataOracle(data=data).model_dump_json(**kwargs)
    else:
        encoded = _V1DataOracle(data=data).json(**kwargs)
    return json.loads(encoded)["data"]


def _rich_payload(implementation):
    inner_type = _V2Inner if implementation["pydantic_version"] == "v2" else _V1Inner
    return {
        "dt": _AWARE,
        "naive": _NAIVE,
        "off": _OFFSET,
        "d": _DATE,
        "t": _TIME,
        "u": _UUID,
        "dec": _DECIMAL,
        "inner": inner_type(when=_AWARE, label="nested"),
        "nested": [{"u": _UUID, "d": _DATE}, _NAIVE],
        "items": [_AWARE, _DATE, _UUID],
        "flag": False,
        "zero": 0,
        "empty": "",
        "none": None,
        "text": "café",
        "blob": b"hi",
    }


def test_issue_213_json_serializes_datetime_now(cloudevents_implementation):
    """The reported repro: ``data={'dt': datetime.now()}`` then ``.json()``."""
    moment = datetime.datetime.now()
    event = cloudevents_implementation["event"](
        attributes={"source": _SOURCE, "type": _TYPE},
        data={"dt": moment},
    )

    body = json.loads(event.json())

    assert body["source"] == _SOURCE
    assert body["type"] == _TYPE
    assert body["specversion"] == "1.0"
    assert set(body) >= {"source", "type", "specversion", "id", "time", "data"}
    assert "attributes" not in body
    assert body["data"] == _expected_data(cloudevents_implementation, {"dt": moment})
    if cloudevents_implementation["pydantic_version"] == "v2":
        assert json.loads(event.model_dump_json()) == body


def test_public_pydantic_facade_serializes_datetime_now():
    moment = datetime.datetime.now(datetime.timezone.utc)
    event = PublicCloudEvent(
        attributes={"source": _SOURCE, "type": _TYPE},
        data={"dt": moment},
    )

    body = json.loads(event.json())
    assert body["data"]["dt"] == TypeAdapter(Any).dump_python(moment, mode="json")
    assert json.loads(event.model_dump_json())["data"] == body["data"]


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_timezone_aware_datetime_matches_pydantic(
    cloudevents_implementation, specversion
):
    data = {"utc": _AWARE, "offset": _OFFSET, "naive": _NAIVE}
    event = cloudevents_implementation["event"](_attributes(specversion), data)

    body = json.loads(_event_json(cloudevents_implementation, event))

    assert body["specversion"] == specversion
    assert body["id"] == _EVENT_ID
    assert body["source"] == _SOURCE
    assert body["type"] == _TYPE
    # Attribute ``time`` stays on the SDK RFC3339 path (isoformat, ``+00:00``).
    assert body["time"] == _AWARE.isoformat()
    assert body["data"] == _expected_data(cloudevents_implementation, data)
    assert (
        body["data"]["utc"]
        == {
            "v1": "2024-01-02T03:04:05.123456+00:00",
            "v2": "2024-01-02T03:04:05.123456Z",
        }[cloudevents_implementation["pydantic_version"]]
    )
    assert body["data"]["offset"] == "2024-01-02T03:04:05+08:00"
    assert "data_base64" not in body


def test_nested_json_values_match_pydantic(cloudevents_implementation):
    data = _rich_payload(cloudevents_implementation)
    event = cloudevents_implementation["event"](_attributes(), data)

    body = json.loads(_event_json(cloudevents_implementation, event))

    assert body["data"] == _expected_data(cloudevents_implementation, data)
    version = cloudevents_implementation["pydantic_version"]
    assert body["data"]["d"] == "2024-05-06"
    assert body["data"]["t"] == "07:08:09"
    assert body["data"]["u"] == str(_UUID)
    assert body["data"]["dec"] == ("1.50" if version == "v2" else 1.5)
    assert body["data"]["inner"]["label"] == "nested"
    assert body["data"]["flag"] is False
    assert body["data"]["zero"] == 0
    assert body["data"]["empty"] == ""
    assert body["data"]["none"] is None
    assert body["data"]["blob"] == "hi"
    assert body["data"]["items"][1] == "2024-05-06"


def test_top_level_datetime_date_and_model_data(cloudevents_implementation):
    version = cloudevents_implementation["pydantic_version"]
    inner_type = _V2Inner if version == "v2" else _V1Inner
    samples = (
        _AWARE,
        _DATE,
        _TIME,
        _UUID,
        _DECIMAL,
        inner_type(when=_AWARE, label="root"),
        [_AWARE, {"on": _DATE}],
    )
    for sample in samples:
        event = cloudevents_implementation["event"](_attributes(), sample)
        body = json.loads(_event_json(cloudevents_implementation, event))
        assert body["data"] == _expected_data(cloudevents_implementation, sample)
        assert body["time"] == _AWARE.isoformat()


def test_bytes_payload_stays_data_base64(cloudevents_implementation):
    payload = b"\x00\x00\x11Hello World"
    event = cloudevents_implementation["event"](
        {
            "source": _SOURCE,
            "type": _TYPE,
            "id": _EVENT_ID,
            "time": _AWARE,
            "datacontenttype": "application/octet-stream",
        },
        payload,
    )

    body = json.loads(_event_json(cloudevents_implementation, event))

    assert body["data_base64"] == "AAARSGVsbG8gV29ybGQ="
    assert "data" not in body
    assert body["time"] == _AWARE.isoformat()
    assert body["datacontenttype"] == "application/octet-stream"


@pytest.mark.parametrize(
    "data, present",
    [
        (None, False),
        ("hello", True),
        ('{"hello": "world"}', True),
        (0, True),
        (False, True),
        ("", True),
        ([], True),
        ({}, True),
        (1.5, True),
    ],
)
def test_scalar_and_empty_data_round_trip(cloudevents_implementation, data, present):
    event = cloudevents_implementation["event"](_attributes(), data)
    body = json.loads(_event_json(cloudevents_implementation, event))
    assert ("data" in body) is present
    if present:
        assert body["data"] == data
    assert "data_base64" not in body


def test_extensions_stay_at_top_level(cloudevents_implementation):
    attributes = _attributes()
    attributes["comexample"] = "extension-value"
    event = cloudevents_implementation["event"](attributes, {"dt": _AWARE, "n": 1})

    body = json.loads(_event_json(cloudevents_implementation, event))

    assert body["comexample"] == "extension-value"
    assert body["data"] == _expected_data(
        cloudevents_implementation, {"dt": _AWARE, "n": 1}
    )


def test_python_dump_keeps_datetime_objects(cloudevents_implementation):
    event = cloudevents_implementation["event"](
        _attributes(), {"dt": _AWARE, "d": _DATE}
    )
    if cloudevents_implementation["pydantic_version"] == "v2":
        dumped = event.model_dump()
    else:
        dumped = event.dict()
    assert dumped["data"]["dt"] == _AWARE
    assert dumped["data"]["d"] == _DATE
    assert dumped["time"] == _AWARE


def test_serialization_kwargs_apply_to_data_and_document(
    cloudevents_implementation,
):
    version = cloudevents_implementation["pydantic_version"]
    aliased = (
        _V2Aliased(fooBar=3, when=_AWARE)
        if version == "v2"
        else _V1Aliased(fooBar=3, when=_AWARE)
    )
    data = {"item": aliased, "label": "café"}
    event = cloudevents_implementation["event"](_attributes(), data)

    aliased_body = json.loads(
        _event_json(cloudevents_implementation, event, by_alias=True)
    )
    named_body = json.loads(
        _event_json(cloudevents_implementation, event, by_alias=False)
    )
    assert aliased_body["data"] == _expected_data(
        cloudevents_implementation, data, by_alias=True
    )
    assert named_body["data"] == _expected_data(
        cloudevents_implementation, data, by_alias=False
    )
    assert aliased_body["data"]["item"]["fooBar"] == 3
    assert "foo_bar" not in aliased_body["data"]["item"]
    assert named_body["data"]["item"]["foo_bar"] == 3
    assert aliased_body["source"] == _SOURCE
    assert aliased_body["time"] == _AWARE.isoformat()

    unset_body = json.loads(
        _event_json(cloudevents_implementation, event, exclude_unset=True)
    )
    assert unset_body["data"] == _expected_data(
        cloudevents_implementation, data, exclude_unset=True
    )
    assert "note" not in unset_body["data"]["item"]
    assert "n" not in unset_body["data"]["item"]
    # Required CloudEvent attributes stay on the structured envelope.
    assert unset_body["specversion"] == "1.0"
    assert unset_body["id"] == _EVENT_ID
    assert unset_body["source"] == _SOURCE
    assert unset_body["type"] == _TYPE
    assert unset_body["time"] == _AWARE.isoformat()

    none_body = json.loads(
        _event_json(cloudevents_implementation, event, exclude_none=True)
    )
    assert none_body["data"] == _expected_data(
        cloudevents_implementation, data, exclude_none=True
    )
    assert "note" not in none_body["data"]["item"]

    if version == "v2":
        indented = event.model_dump_json(indent=2)
        escaped = event.model_dump_json(ensure_ascii=True)
        raw = event.model_dump_json(ensure_ascii=False)
    else:
        indented = event.json(indent=2)
        escaped = event.json(ensure_ascii=True)
        raw = event.json(ensure_ascii=False)
    assert "\n" in indented
    assert json.loads(indented)["data"]["item"]["foo_bar"] == 3
    assert "\\u00e9" in escaped
    assert "café" in raw
