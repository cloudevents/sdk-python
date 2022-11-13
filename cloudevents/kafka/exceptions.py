from cloudevents import exceptions as cloud_exceptions


class KeyMapperError(cloud_exceptions.GenericException):
    """
    Raised when a KeyMapper fails.
    """
