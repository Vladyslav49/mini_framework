from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TYPE_CHECKING


class BaseFilter(ABC):
    if TYPE_CHECKING:
        __call__: Callable[..., dict[str, Any] | bool]
    else:  # pragma: no cover

        @abstractmethod
        def __call__(self, **kwargs: Any) -> dict[str, Any] | bool:
            raise NotImplementedError
