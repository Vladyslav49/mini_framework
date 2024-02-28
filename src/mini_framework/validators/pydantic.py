import inspect
from dataclasses import is_dataclass
from functools import cache
from typing import Any

from pydantic import TypeAdapter, ValidationError, ConfigDict
from pydantic_core import to_jsonable_python

from mini_framework.responses import Response
from mini_framework.validators.base import Validator
from mini_framework.exceptions import (
    ResponseValidationError,
    RequestValidationError,
)


class PydanticValidator(Validator):
    def validate_request(self, params: dict[str, Any], model: type, /) -> Any:
        adapter = _get_adapter(model)

        try:
            return adapter.validate_python(params)
        except ValidationError as e:
            raise RequestValidationError(
                e.errors(include_url=False),
                params=params,
                expected_type=model,
            )

    def validate_response(self, obj: Any, return_type: type, /) -> Any:
        if inspect.isclass(return_type) and (
            issubclass(return_type, Response) or return_type is Any
        ):
            return obj

        adapter = _get_adapter(return_type)

        try:
            return adapter.validate_python(obj)
        except ValidationError as e:
            raise ResponseValidationError(
                e.errors(),
                value=obj,
                expected_type=return_type,
            )

    def serialize_response(self, obj: Any, return_type: type, /) -> Any:
        if inspect.isclass(return_type) and (
            issubclass(return_type, Response) or return_type is Any
        ):
            if isinstance(obj, Response):
                obj.content = to_jsonable_python(obj.content)
                return obj
            return to_jsonable_python(obj)

        adapter = _get_adapter(return_type)
        return adapter.dump_python(obj, mode="json")


@cache
def _get_adapter(type_: type) -> TypeAdapter:
    if is_dataclass(type_):
        type_.__pydantic_config__ = ConfigDict(  # pyright: ignore[reportAttributeAccessIssue]
            validate_assignment=True,
            arbitrary_types_allowed=True,
            validate_default=True,
        )
    return TypeAdapter(type_)
