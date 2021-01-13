
return_statues = {
    512: "ApiSuccess",
    513: "ApiFailed",
    514: "ApiAccessDenied",
    515: "ApiDmaChannelUnavailable",
    516: "ApiDmaChannelInvalid",
    517: "ApiDmaChannelTypeError",
    518: "ApiDmaInProgress",
    519: "ApiDmaDone",
    520: "ApiDmaPaused",
    521: "ApiDmaNotPaused",
    522: "ApiDmaCommandInvalid",
    523: "ApiDmaManReady",
    524: "ApiDmaManNotReady",
    525: "ApiDmaInvalidChannelPriority",
    526: "ApiDmaManCorrupted",
    527: "ApiDmaInvalidElementIndex",
    528: "ApiDmaNoMoreElements",
    529: "ApiDmaSglInvalid",
    530: "ApiDmaSglQueueFull",
    531: "ApiNullParam",
    532: "ApiInvalidBusIndex",
    533: "ApiUnsupportedFunction",
    534: "ApiInvalidPciSpace",
    535: "ApiInvalidIopSpace",
    536: "ApiInvalidSize",
    537: "ApiInvalidAddress",
    538: "ApiInvalidAccessType",
    539: "ApiInvalidIndex",
    540: "ApiMuNotReady",
    541: "ApiMuFifoEmpty",
    542: "ApiMuFifoFull",
    543: "ApiInvalidRegister",
    544: "ApiDoorbellClearFailed",
    545: "ApiInvalidUserPin",
    546: "ApiInvalidUserState",
    547: "ApiEepromNotPresent",
    548: "ApiEepromTypeNotSupported",
    549: "ApiEepromBlank",
    550: "ApiConfigAccessFailed",
    551: "ApiInvalidDeviceInfo",
    552: "ApiNoActiveDriver",
    553: "ApiInsufficientResources",
    554: "ApiObjectAlreadyAllocated",
    555: "ApiAlreadyInitialized",
    556: "ApiNotInitialized",
    557: "ApiBadConfigRegEndianMode",
    558: "ApiInvalidPowerState",
    559: "ApiPowerDown",
    560: "ApiFlybyNotSupported",
    561: "ApiNotSupportThisChannel",
    562: "ApiNoAction",
    563: "ApiHSNotSupported",
    564: "ApiVPDNotSupported",
    565: "ApiVpdNotEnabled",
    566: "ApiNoMoreCap",
    567: "ApiInvalidOffset",
    568: "ApiBadPinDirection",
    569: "ApiPciTimeout",
    570: "ApiDmaChannelClosed",
    571: "ApiDmaChannelError",
    572: "ApiInvalidHandle",
    573: "ApiBufferNotReady",
    574: "ApiInvalidData",
    575: "ApiDoNothing",
    576: "ApiDmaSglBuildFailed",
    577: "ApiPMNotSupported",
    578: "ApiInvalidDriverVersion",
    579: "ApiWaitTimeout",
    580: "ApiWaitCanceled",
    581: "ApiBufferTooSmall",
    582: "ApiBufferOverflow",
    583: "ApiInvalidBuffer",
    584: "ApiInvalidRecordsPerBuffer",
    585: "ApiDmaPending",
    586: "ApiLockAndProbePagesFailed",
    587: "ApiWaitAbandoned",
    588: "ApiWaitFailed",
    589: "ApiTransferComplete",
    590: "ApiPllNotLocked",
    591: "ApiNotSupportedInDualChannelMode",
}



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

        Args:
            func (fn): the function to execute
            *args, **kwargs: positional and named arguments to pass to the
            wrapped function
        """

        # Try the function a number of times before failing (unless had failed before)
        try:
            ret = func(*args, **kwargs)

            if isinstance(ret, bool):
                return ret

            if not isinstance(ret, int):
                return ret


            if ret in return_statues:
                if return_statues[ret] == "ApiSuccess":
                    return ret
                else:
                    raise self.ExceptionType(self._logger, 'ATS310 Failed: ' + return_statues[ret])

            else:
                raise self.ExceptionType(self._logger, f'Unkown return code {ret}')

        except self.ExceptionType as error:
            self._logger.error(error)
            raise Exception() # FIXME


    def __init__(self, instance, logger, ExceptionType):
        #pylint: disable=invalid-name
        """
        Constructor.
        It implements public methods by wrapping that of 'instance' within
        the _wrap function.

        Args:
            instance (object): an instance of an arbitrary object to wrap public
            methods
            ExceptionType (Exception) the Exception class or tuple of Exception classes
            to catch in the wrapper.
        """

        methods = dir(instance)
        self.ExceptionType = ExceptionType
        self._logger = logger
        self._last_error_str = None

        for __method in methods:
            if callable(getattr(instance, __method)) and __method[0] != '_':
                replacement = lambda *args, __method=__method, **kwargs: self._wrap(
                    getattr(instance, __method), *args, **kwargs)
                setattr(self, __method, replacement)
