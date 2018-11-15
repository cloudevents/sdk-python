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

import io
import ujson
import typing


class BaseEvent(object):

    def Properties(self) -> dict:
        props = dict()
        for name, value in self.__dict__.items():
            if str(name).startswith("ce__"):
                props.update(
                    {
                        str(name).replace("ce__", ""): value.get()
                    }
                )

        return props

    def Extensions(self) -> dict:
        props = self.Properties()
        return props.get("extensions")

    def Get(self, key: str) -> (object, bool):
        formatted_key = "ce__{0}".format(key.lower())
        ok = hasattr(self, formatted_key)
        value = getattr(self, formatted_key, None)
        if not ok:
            exts = self.Extensions()
            return exts.get(key), key in exts

        return value.get(), ok

    def Set(self, key: str, value: object):
        formatted_key = "ce__{0}".format(key)
        key_exists = hasattr(self, formatted_key)
        if key_exists:
            attr = getattr(self, formatted_key)
            attr.set(value)
            setattr(self, formatted_key, attr)
            return

        exts = self.Extensions()
        exts.update({key: value})
        self.Set("extensions", exts)

    def MarshalJSON(self) -> typing.IO:
        return io.StringIO(ujson.dumps(self.Properties()))

    def UnmarshalJSON(self, b: typing.IO):
        raw_ce = ujson.load(b)
        for name, value in raw_ce.items():
            self.Set(name, value)

    def UnmarshalBinary(self, headers: dict, body: typing.IO):
        props = self.Properties()
        for key in props:
            self.Set(key, headers.get("ce-{0}".format(key)))

        data = None
        if body:
            data = body.read()

        self.Set("data", data)

    def MarshalBinary(self) -> (dict, object):
        headers = {}
        props = self.Properties()
        for key, value in props.items():
            if key not in ["data", "extensions"]:
                headers["ce-{0}".format(key)] = value

        exts = props.get("extensions")
        headers.update(**exts)
        data, _ = self.Get("data")
        return headers, data
