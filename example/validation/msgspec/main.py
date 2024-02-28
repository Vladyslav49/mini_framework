# pyright: reportAttributeAccessIssue=none

from typing import Annotated, Any

import msgspec
from msgspec import Struct, ValidationError

from mini_framework import Application
from mini_framework.params import Query
from mini_framework.responses import Response
from mini_framework.validators.base import Validator
from mini_framework.exceptions import (
    RequestValidationError,
    ResponseValidationError,
)


class MsgspecValidator(Validator):
    def validate_request(self, params: dict[str, Any], model: type, /) -> Any:
        try:
            return msgspec.convert(params, model, strict=False)
        except ValidationError as e:
            raise RequestValidationError(
                str(e), params=params, expected_type=model
            )

    def validate_response(self, obj: Any, return_type: type, /) -> Any:
        if return_type is Any:
            return obj

        if isinstance(obj, Response):
            content = obj.content
        else:
            content = obj

        try:
            return msgspec.convert(content, return_type, strict=False)
        except ValidationError as e:
            raise ResponseValidationError(
                str(e), value=obj, expected_type=return_type
            )

    def serialize_response(self, obj: Any, return_type: type, /) -> Any:
        return msgspec.to_builtins(obj)


app = Application(validator=MsgspecValidator())


class User(Struct, frozen=True):  # pyright: ignore[reportCallIssue, reportGeneralTypeIssues]
    name: str
    age: int


@app.get("/")
def index(name: Annotated[str, Query()], age: Annotated[int, Query()]) -> User:
    return User(name=name, age=age)
