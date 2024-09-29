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

import io

from cloudevents_v1.http import from_http
from flask import Flask, request
from PIL import Image

app = Flask(__name__)


@app.route("/", methods=["POST"])
def home():
    # Create a CloudEvent.
    # data_unmarshaller will cast event.data into an io.BytesIO object
    event = from_http(
        request.headers,
        request.get_data(),
        data_unmarshaller=lambda x: io.BytesIO(x),
    )

    # Create image from cloudevent data
    image = Image.open(event.data)

    # Print
    print(f"Found event {event['id']} with image of size {image.size}")
    return f"Found image of size {image.size}", 200


if __name__ == "__main__":
    app.run(port=3000)
