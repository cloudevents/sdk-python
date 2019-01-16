# All Rights Reserved.
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

from cloudevents.sdk import marshaller
from cloudevents.sdk import converters
from cloudevents.sdk.event import v02

from sanic import Sanic
from sanic import response

from cloudevents.tests import data as test_data


m = marshaller.NewDefaultHTTPMarshaller()
app = Sanic(__name__)


@app.route("/is-ok", ["POST"])
async def is_ok(request):
    m.FromRequest(
        v02.Event(),
        dict(request.headers),
        request.body,
        lambda x: x
    )
    return response.text("OK")


@app.route("/echo", ["POST"])
async def echo(request):
    event = m.FromRequest(
        v02.Event(),
        dict(request.headers),
        request.body,
        lambda x: x
    )
    hs, body = m.ToRequest(event, converters.TypeBinary, lambda x: x)
    return response.text(body, headers=hs)


def test_reusable_marshaller():
    for i in range(10):
        _, r = app.test_client.post(
            "/is-ok", headers=test_data.headers, data=test_data.body
        )
        assert r.status == 200


def test_web_app_integration():
    _, r = app.test_client.post(
        "/is-ok", headers=test_data.headers, data=test_data.body
    )
    assert r.status == 200


def test_web_app_echo():
    _, r = app.test_client.post("/echo", headers=test_data.headers, data=test_data.body)
    assert r.status == 200
    event = m.FromRequest(v02.Event(), dict(r.headers), r.body, lambda x: x)
    assert event is not None
    props = event.Properties()
    for key in test_data.headers.keys():
        if key == "Content-Type":
            assert "contenttype" in props
        else:
            assert key.lstrip("ce-") in props
