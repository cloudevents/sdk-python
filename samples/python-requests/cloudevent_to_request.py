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

import json
import requests
import sys

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller

from cloudevents.sdk.event import v02


def run_binary(event, url):
    binary_headers, binary_data = http_marshaller.ToRequest(
        event, converters.TypeBinary, json.dumps)

    print("binary CloudEvent")
    for k, v in binary_headers.items():
        print("{0}: {1}\r\n".format(k, v))
    print(binary_data)
    response = requests.post(
        url, headers=binary_headers, data=binary_data)
    response.raise_for_status()


def run_structured(event, url):
    structured_headers, structured_data = http_marshaller.ToRequest(
        event, converters.TypeStructured, json.dumps
    )
    print("structured CloudEvent")
    print(structured_data.getvalue())

    response = requests.post(url,
                             headers=structured_headers,
                             data=structured_data.getvalue())
    response.raise_for_status()


if __name__ == "__main__":

    if len(sys.argv) < 3:
        sys.exit("Usage: python with_requests.py "
                 "[binary | structured] "
                 "<CloudEvents controller URL>")

    fmt = sys.argv[1]
    url = sys.argv[2]

    http_marshaller = marshaller.NewDefaultHTTPMarshaller()
    event = (
        v02.Event().
        SetContentType("application/json").
        SetData({"name": "denis"}).
        SetEventID("my-id").
        SetSource("<event-source").
        SetEventType("cloudevent.event.type")
    )
    if "structured" == fmt:
        run_structured(event, url)
    elif "binary" == fmt:
        run_binary(event, url)
    else:
        sys.exit("unknown format: {0}".format(fmt))
