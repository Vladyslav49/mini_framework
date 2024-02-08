import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from http import HTTPMethod
from typing import Any, TypeAlias

from mini_framework.request import Request

CallbackType: TypeAlias = Callable[..., Any]


@dataclass(slots=True, kw_only=True)
class CallableObject:
    callback: CallbackType
    params: set[str] = field(init=False)
    varkw: bool = field(init=False)

    def __post_init__(self) -> None:
        callback = inspect.unwrap(self.callback)
        spec = inspect.getfullargspec(callback)
        self.params = {*spec.args, *spec.kwonlyargs}
        self.varkw = spec.varkw is not None

    def _prepare_kwargs(self, kwargs: dict[str, Any], /) -> dict[str, Any]:
        if self.varkw:
            return kwargs
        return {key: kwargs[key] for key in self.params if key in kwargs}

    def call(self, **kwargs: Any) -> Any:
        kwargs = self._prepare_kwargs(kwargs)
        return self.callback(**kwargs)


@dataclass(slots=True, kw_only=True)
class Route(CallableObject):
    path: str
    method: str
    filters: list[CallableObject] = field(default_factory=list)
    path_params: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.path.startswith("/"):
            raise ValueError(f"Path {self.path!r} must start with '/'")
        if not self.path.endswith("/"):
            raise ValueError(f"Path {self.path!r} must end with '/'")
        if self.method not in tuple(HTTPMethod):
            raise ValueError(
                f"Method {self.method!r} is not valid HTTP method"
            )
        super(Route, self).__post_init__()

    def match(self, request: Request) -> bool:
        if request.method != self.method:
            return False
        if not request.path_params:
            return self.path == request.path
        try:
            return request.path == self.path.format_map(request.path_params)
        except KeyError:  # occurs when path_params do not match
            return False

    def check(self, **kwargs: Any) -> tuple[bool, dict[str, Any]]:
        if not self.filters:
            return True, kwargs
        for filter in self.filters:
            check = filter.call(**kwargs)
            if not check:
                return False, kwargs
            if isinstance(check, dict):
                kwargs.update(check)
        return True, kwargs
