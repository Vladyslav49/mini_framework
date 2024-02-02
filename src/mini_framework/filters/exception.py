from http.client import responses

from mini_framework.exceptions import HTTPException
from mini_framework.filters import BaseFilter


class ExceptionTypeFilter(BaseFilter):
    def __init__(self, *exceptions: type[Exception]) -> None:
        if not exceptions:
            raise ValueError("At least one exception type is required")
        for exception in exceptions:
            if not issubclass(exception, Exception):
                raise TypeError(
                    f"exception should be subclass of Exception not '{exception.__name__}'"  # noqa: E501
                )
        self._exceptions = exceptions

    def __call__(self, exception: Exception) -> bool:
        return isinstance(exception, self._exceptions)


class HTTPExceptionStatusCodeFilter(BaseFilter):
    def __init__(self, *status_codes: int) -> None:
        if not status_codes:
            raise ValueError("At least one status code is required")
        for status_code in status_codes:
            if status_code not in responses:
                raise ValueError(f"Invalid status code: {status_code}")
        self._status_codes = status_codes

    def __call__(self, exception: Exception) -> bool:
        if isinstance(exception, HTTPException):
            return exception.status_code in self._status_codes
        return False
