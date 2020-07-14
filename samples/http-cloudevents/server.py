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
from flask import Flask, request

from cloudevents.sdk.http import from_http

app = Flask(__name__)


# create an endpoint at http://localhost:/3000/
@app.route("/", methods=["POST"])
def home():
    # convert headers to dict
    print(request.get_data())
    print(request.headers)
    # create a CloudEvent
    event = from_http(request.get_data(), request.headers)

    # print the received CloudEvent
    print(f"Received CloudEvent {event}")
    return "", 204


if __name__ == "__main__":
    app.run(port=3000)
