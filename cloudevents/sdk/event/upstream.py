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

from cloudevents.sdk.event import opt
from cloudevents.sdk.event import base


class Event(base.BaseEvent):

    def __init__(self):
        self.ce__specversion = opt.Option("specversion", "0.1", True)
        self.ce__type = opt.Option("type", None, True)
        self.ce__source = opt.Option("source", None, True)
        self.ce__id = opt.Option("id", None, True)
        self.ce__time = opt.Option("time", None, True)
        self.ce__schemaurl = opt.Option("schemaurl", None, False)
        self.ce__contenttype = opt.Option("contenttype", None, False)
        self.ce__data = opt.Option("data", None, False)
        self.ce__extensions = opt.Option("extensions", dict(), False)

    def CloudEventVersion(self) -> str:
        return self.ce__specversion.get()
