from abc import ABC, abstractmethod
from typing import Any, Callable, TYPE_CHECKING


class BaseFilter(ABC):
    if TYPE_CHECKING:
        __call__: Callable[..., dict[str, Any] | bool]
    else:

        @abstractmethod
        def __call__(self, **kwargs: Any) -> dict[str, Any] | bool:
            raise NotImplementedError
