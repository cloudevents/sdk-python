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


class UnsupportedEvent(Exception):
    def __init__(self, event_class):
        super().__init__("Invalid CloudEvent class: '{0}'".format(event_class))


class InvalidDataUnmarshaller(Exception):
    def __init__(self):
        super().__init__("Invalid data unmarshaller, is not a callable")


class InvalidDataMarshaller(Exception):
    def __init__(self):
        super().__init__("Invalid data marshaller, is not a callable")


class NoSuchConverter(Exception):
    def __init__(self, converter_type):
        super().__init__("No such converter {0}".format(converter_type))


class UnsupportedEventConverter(Exception):
    def __init__(self, content_type):
        super().__init__(
            "Unable to identify valid event converter "
            "for content-type: '{0}'".format(content_type)
        )
