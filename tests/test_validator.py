from dataclasses import dataclass
from typing import Annotated, Any
from unittest.mock import Mock

import pytest

from mini_framework import Application
from mini_framework.datastructures import FormData
from mini_framework.exceptions import ResponseValidationError
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


@pytest.mark.parametrize(
    "param, param_type",
    [
        (Path(), "path_params"),
        (Query(), "query_params"),
        (Body(), "bodies"),
        (Field(), "fields"),
        (File(), "files"),
        (Header(), "headers"),
        (Cookie(), "cookies"),
    ],
)
def test_missing_params(
    app: Application,
    mock_request: Mock,
    param: Param,
    param_type: str,
) -> None:
    setattr(mock_request, param_type, {})
    mock_request.json.return_value = {}
    mock_request.form.return_value = FormData(fields=[], files=[])

    def index(name: Annotated[Any, param]):
        assert False  # noqa: B011

    app.get("/")(index)

    response = app.propagate(mock_request)

    assert len(response.content["detail"]) == 1
    assert (
        response.content["detail"][0].items()
        >= {
            "loc": ("name",),
            "msg": "Field required",
            "type": "missing",
        }.items()
    )


def test_missing_body_model_param(
    app: Application, mock_request: Mock
) -> None:
    mock_request.body_models = {}
    mock_request.json.return_value = {}

    @dataclass(frozen=True, slots=True, kw_only=True)
    class Model:
        name: str
        age: int

    def index(model: Annotated[Model, BodyModel()]):
        assert False  # noqa: B011

    app.get("/")(index)

    response = app.propagate(mock_request)

    assert len(response.content["detail"]) == 2
    assert (
        response.content["detail"][0].items()
        >= {
            "loc": ("model", "name"),
            "msg": "Field required",
            "type": "missing",
        }.items()
    )
    assert (
        response.content["detail"][1].items()
        >= {
            "loc": ("model", "age"),
            "msg": "Field required",
            "type": "missing",
        }.items()
    )


def test_missing_fields_and_files_params(
    app: Application, mock_request: Mock
) -> None:
    field = Mock()
    field.field_name.decode.return_value = "nonexistent_field"
    file = Mock()
    file.field_name.decode.return_value = "nonexistent_file"
    mock_request.form.return_value = FormData(fields=[field], files=[file])

    def index(field: Annotated[str, Field()], file: Annotated[bytes, File()]):
        assert False  # noqa: B011

    app.get("/")(index)

    response = app.propagate(mock_request)

    assert len(response.content["detail"]) == 2
    assert (
        response.content["detail"][0].items()
        >= {
            "loc": ("field",),
            "msg": "Field required",
            "type": "missing",
        }.items()
    )
    assert (
        response.content["detail"][1].items()
        >= {
            "loc": ("file",),
            "msg": "Field required",
            "type": "missing",
        }.items()
    )


def test_validation_error(app: Application, mock_request: Mock) -> None:
    @app.get("/")
    def index() -> int:
        return "World"  # type: ignore[return-value]

    with pytest.raises(ResponseValidationError) as exc_info:
        app.propagate(mock_request)

    assert exc_info.value.value == "World"
    assert exc_info.value.expected_type is int
