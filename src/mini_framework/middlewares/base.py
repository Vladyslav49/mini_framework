from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeAlias

CallNext: TypeAlias = Callable[[dict[str, Any]], Any]
Middleware: TypeAlias = Callable[[CallNext, dict[str, Any]], Any]


class BaseMiddleware(ABC):
    @abstractmethod
    def __call__(self, call_next: CallNext, data: dict[str, Any]) -> Any:
        raise NotImplementedError
