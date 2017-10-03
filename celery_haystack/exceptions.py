import six


class CeleryHaystackException(Exception):
    pass


@six.python_2_unicode_compatible
class IndexOperationException(CeleryHaystackException):
    def __init__(self, index, reason):
        self.index = index
        self.reason = reason

    def __str__(self):
        return "Failed to update index %s. %s" % (self.index, self.reason)


@six.python_2_unicode_compatible
class InstanceNotFoundException(CeleryHaystackException):
    def __init__(self, model_class, pk, reason):
        self.model_class = model_class
        self.pk = pk
        self.reason = reason

    def __str__(self):
        return "Unable to load instance %s with pk=%s. %s" % (self.model_class, self.pk, self.reason)


@six.python_2_unicode_compatible
class UnrecognizedActionException(CeleryHaystackException):
    def __init__(self, action):
        self.action = action

    def __str__(self):
        return "Unrecognized action '%s'" % self.action
