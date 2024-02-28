import inspect
from collections.abc import Callable
from dataclasses import dataclass, field, make_dataclass
from http import HTTPMethod, HTTPStatus
from typing import Any, _AnnotatedAlias, get_origin, get_args, TypeAlias  # pyright: ignore[reportAttributeAccessIssue]
from unittest.mock import sentinel

from mini_framework.routes.params_resolvers import resolve_params
from mini_framework.validators.base import Validator
from mini_framework.datastructures import UploadFile
from mini_framework.params import (
    Path,
    Query,
    Body,
    Field,
    File,
    Header,
    Cookie,
    Param,
    BodyModel,
)
from mini_framework.request import Request
from mini_framework.responses import Response

CallbackType: TypeAlias = Callable[..., Any]

MISSING = sentinel.MISSING


@dataclass(slots=True, kw_only=True)
class CallableObject:
    callback: CallbackType
    params: list[str] = field(init=False)
    varkw: bool = field(init=False)

    def __post_init__(self) -> None:
        callback = inspect.unwrap(self.callback)
        spec = inspect.getfullargspec(callback)
        self.params = [*spec.args, *spec.kwonlyargs]
        self.varkw = spec.varkw is not None

    def _prepare_kwargs(self, kwargs: dict[str, Any], /) -> dict[str, Any]:
        if self.varkw:
            return kwargs
        return {key: kwargs[key] for key in self.params if key in kwargs}

    def call(self, **kwargs: Any) -> Any:
        kwargs = self._prepare_kwargs(kwargs)
        return self.callback(**kwargs)


@dataclass(slots=True, kw_only=True)
class HandlerObject(CallableObject):
    filters: list[CallableObject] = field(default_factory=list)

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


@dataclass(slots=True, kw_only=True)
class Route(HandlerObject):
    path: str
    method: str
    status_code: int = HTTPStatus.OK
    response_class: type[Response] | None = None
    response_model: type | None = None
    model: type = field(init=False)
    return_annotation: Any = field(default=None)
    path_params: set[str] = field(default_factory=set)
    query_params: set[str] = field(default_factory=set)
    bodies: set[str] = field(default_factory=set)
    body_models: dict[str, Any] = field(default_factory=dict)
    fields: set[str] = field(default_factory=set)
    files: set[str] = field(default_factory=set)
    upload_files: list[str] = field(default_factory=list)
    upload_files_param: str | None = field(default=None)
    headers: set[str] = field(default_factory=set)
    cookies: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.path.startswith("/"):
            raise ValueError(f"Path {self.path!r} must start with '/'")
        if not self.path.endswith("/"):
            raise ValueError(f"Path {self.path!r} must end with '/'")
        if self.method not in tuple(HTTPMethod):
            raise ValueError(
                f"Method {self.method!r} is not valid HTTP method"
            )
        super(HandlerObject, self).__post_init__()

        callback = inspect.unwrap(self.callback)
        signature = inspect.signature(callback)

        if signature.return_annotation is inspect.Parameter.empty:
            self.return_annotation = Any
        else:
            self.return_annotation = signature.return_annotation

        names: list[str] = []

        for param in signature.parameters.values():
            if inspect.isclass(param.annotation) and issubclass(
                param.annotation, UploadFile
            ):
                names.append(param.name)
                self.upload_files.append(param.name)
            elif (
                inspect.isclass(get_origin(param.annotation))
                and issubclass(get_origin(param.annotation), list)  # pyright: ignore[reportArgumentType]
                and issubclass(get_args(param.annotation)[0], UploadFile)
            ):
                names.append(param.name)
                self.upload_files_param = param.name
            elif isinstance(param.annotation, _AnnotatedAlias):
                param_type = param.annotation.__metadata__[0]

                if isinstance(param_type, Param):
                    names.append(param.name)

                if isinstance(param_type, Path):
                    self.path_params.add(param.name)
                elif isinstance(param_type, Query):
                    self.query_params.add(param.name)
                elif isinstance(param_type, BodyModel):
                    self.body_models[param.name] = param.annotation
                elif isinstance(param_type, Body):
                    self.bodies.add(param.name)
                elif isinstance(param_type, Field):
                    self.fields.add(param.name)
                elif isinstance(param_type, File):
                    self.files.add(param.name)
                elif isinstance(param_type, Header):
                    self.headers.add(param.name)
                elif isinstance(param_type, Cookie):
                    self.cookies.add(param.name)

        fields: list[tuple[str, type] | tuple[str, type, Any]] = []

        for param in signature.parameters.values():
            if param.name not in names:
                continue

            if param.default is inspect.Parameter.empty:
                fields.append((param.name, param.annotation))
            else:
                fields.append((param.name, param.annotation, param.default))

        self.model = make_dataclass("Model", fields, frozen=True, slots=True)

    def validate_params(
        self, request: Request, validator: Validator
    ) -> dict[str, Any]:
        resolved_params = resolve_params(self, request)

        obj = validator.validate_request(resolved_params, self.model)

        validated_params = {}

        for name in self.model.__annotations__:
            value = getattr(obj, name)
            validated_params[name] = value

        return validated_params

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
