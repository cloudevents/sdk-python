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
from cloudevents.sdk.http_events import CloudEvent
from flask import Flask, request
app = Flask(__name__)


# Create an endpoint at http://localhost:/3000/event
@app.route('/event', methods=['POST'])
def hello():
    # Convert headers to dict
    headers = dict(request.headers)

    # Create a CloudEvent
    event = CloudEvent(headers=headers, data=request.json)

    # Print the received CloudEvent
    print(f"Received {event}")
    return '', 204


if __name__ == '__main__':
    app.run(port=3000)
