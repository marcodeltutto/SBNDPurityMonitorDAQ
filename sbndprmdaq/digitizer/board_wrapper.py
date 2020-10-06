
try:
    from . import atsapi as ats
except:
    import atsapi as ats


class BoardWrapper:
    #pylint: disable=too-few-public-methods
    """
    The BoardWrapper class.
    It has only the constructor, but it will automagically generate all
    other methods starting from the public methods of the provided class.
    extra arguments:
    """

    def _wrap(self, func, *args, **kwargs):
        """
        Wrapper function. This implements the try-catch statement
        arguments:
        - func:          the function to execute
        *args, **kwargs: positional and named arguments to pass to the
                         wrapped function
        """

        # Try the function a number of times before failing (unless had failed before)
        try:
            ret = func(*args, **kwargs)

            if ret == ats.ApiSuccess:
                pass
            elif ret == ats.ApiFailed:
                pass
            elif ret == ats.ApiAccessDenied:
                pass
            elif ret == ats.ApiDmaChannelUnavailable:
                pass
            else:
                pass

            return ret
        except self.ExceptionType as error:
            logging.error(self._last_error_str)


    def __init__(self, instance, ExceptionType):
        #pylint: disable=invalid-name
        """
        Constructor.
        It implements public methods by wrapping that of 'instance' within
        the _wrap function.
        arguments:
        - instance:      an instance of an arbitrary object to wrap public
                         methods
        - ExceptionType: the Exception class or tuple of Exception classes
                         to catch in the wrapper.
        """

        methods = dir(instance)
        self.ExceptionType = ExceptionType
        self._last_error_str = None

        for __method in methods:
            if callable(getattr(instance, __method)) and __method[0] != '_':
                replacement = lambda *args, __method=__method, **kwargs: self._wrap(
                    getattr(instance, __method), *args, **kwargs)
                setattr(self, __method, replacement)
