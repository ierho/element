class UnknownEvent(Exception):
    """Raised when an invalid event is used"""
    pass


class EmptyMessage(Exception):
    """Raised when an empty message is trying to be sent"""
    pass
