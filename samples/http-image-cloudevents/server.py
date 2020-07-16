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

from flask import Flask, request
from PIL import Image

from cloudevents.sdk.http_events import CloudEvent

app = Flask(__name__)


# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def home():
    # create a CloudEvent
    event = CloudEvent.from_http(request.get_data(), request.headers)
    size = json.loads(event["size"])

    if event["type"] == "com.example.base64":
        image = Image.frombytes("RGB", size, event.data)
    elif event["type"] == "com.example.string":
        image = Image.frombytes("RGB", size, event.data.encode())
    else:
        raise NotImplementedError(
            f"Endpoint does not support event type {event['type']}"
        )

    print(f"Found image {event['id']} with size {image.size}")

    return "", 204


if __name__ == "__main__":
    app.run(port=3000)
