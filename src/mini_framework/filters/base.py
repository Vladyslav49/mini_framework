from typing import Callable, Protocol, runtime_checkable, TYPE_CHECKING


@runtime_checkable
class BaseFilter(Protocol):
    if TYPE_CHECKING:
        __call__: Callable[[], bool]
    else:

        def __call__(self) -> bool:
            ...
