from cloudevents.http.util import default_marshaller
from cloudevents.sdk import converters
from cloudevents.sdk.event import v1, v03

_marshaller_by_format = {
    converters.TypeStructured: lambda x: x,
    converters.TypeBinary: default_marshaller,
}

_obj_by_version = {"1.0": v1.Event, "0.3": v03.Event}

_required_by_version = {
    "1.0": v1.Event._ce_required_fields,
    "0.3": v03.Event._ce_required_fields,
}
