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
import io
import requests
import sys

from cloudevents.sdk import marshaller

from cloudevents.sdk.event import v02


if __name__ == "__main__":

    if len(sys.argv) < 2:
        sys.exit("Usage: python with_requests.py "
                 "<CloudEvent source URL>")

    url = sys.argv[1]
    response = requests.get(url)
    response.raise_for_status()
    headers = response.headers
    data = io.BytesIO(response.content)
    event = v02.Event()
    http_marshaller = marshaller.NewDefaultHTTPMarshaller()
    event = http_marshaller.FromRequest(
        event, headers, data, json.load)

    print(json.dumps(event.Properties()))
