from typing import Any

from mini_framework.exceptions import HTTPException
from mini_framework.filters import BaseFilter


class ExceptionTypeFilter(BaseFilter):
    def __init__(self, *exceptions: type[Exception]) -> None:
        if not exceptions:
            raise ValueError("At least one exception type is required")
        self._exceptions = exceptions

    def __call__(self, exception: Exception) -> dict[str, Any] | bool:
        return isinstance(exception, self._exceptions)


class HTTPExceptionStatusCodeFilter(BaseFilter):
    def __init__(self, status_code: int) -> None:
        self._status_code = status_code

    def __call__(self, exception: Exception) -> dict[str, Any] | bool:
        if isinstance(exception, HTTPException):
            return self._status_code == exception.status_code
        return False
