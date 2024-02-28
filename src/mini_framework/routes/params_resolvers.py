from __future__ import annotations

from typing import Any, get_args, TYPE_CHECKING

from mini_framework.datastructures import UploadFile
from mini_framework.request import Request

if TYPE_CHECKING:
    from mini_framework.routes.route import Route


def resolve_params(route: Route, request: Request) -> dict[str, Any]:
    params = {}

    resolve_path_params(route, request, params=params)
    resolve_query_params(route, request, params=params)
    resolve_body_params(route, request, params=params)
    resolve_body_model_params(route, request, params=params)
    resolve_field_params(route, request, params=params)
    resolve_file_params(route, request, params=params)
    resolve_upload_file_params(route, request, params=params)
    resolve_header_params(route, request, params=params)
    resolve_cookie_params(route, request, params=params)

    return params


def resolve_path_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.path_params:
        params.update(request.path_params)


def resolve_query_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.query_params:
        params.update(request.query_params)


def resolve_body_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.bodies:
        body = request.json()
        params.update(body)


def resolve_body_model_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.body_models:
        body = request.json()

        for param, annotation in route.body_models.items():
            model, model_param = get_args(annotation)

            params[param] = {}

            is_single_model = (len(route.body_models) + len(route.bodies)) == 1

            if is_single_model and not model_param.embed:
                embed = False
            else:
                embed = True

            for name in model.__annotations__:
                try:
                    if embed:
                        params[param][name] = body[param][name]
                    else:
                        params[param][name] = body[name]
                except KeyError:
                    pass


def resolve_field_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.fields:
        form = request.form()

        if not form.fields:
            return

        for param in route.fields:
            for field in form.fields:
                if field.field_name.decode() == param:
                    params[param] = field.value.decode()


def resolve_file_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.files:
        form = request.form()

        if not form.files:
            return

        for param in route.files:
            for file in form.files:
                if (
                    file.field_name is not None
                    and file.field_name.decode() == param
                ):
                    file.file_object.seek(0)
                    params[param] = file.file_object.read()


def resolve_upload_file_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.upload_files or route.upload_files_param is not None:
        try:
            form = request.form()
        except ValueError as e:
            if str(e) == "No Content-Type header given!":
                return
            else:
                raise

        if not form.files:
            return

        upload_files: list[UploadFile] = []

        for file in form.files:
            file.file_object.seek(0)
            upload_files.append(
                UploadFile(
                    file.file_object,
                    size=file.size,
                    filename=file.file_name,
                ),
            )

        for param in route.upload_files:
            try:
                params[param] = upload_files.pop(0)
            except IndexError:
                return

        if route.upload_files_param is not None:
            params[route.upload_files_param] = upload_files


def resolve_header_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.headers:
        for key, value in request.headers.items():
            params[key.lower()] = value


def resolve_cookie_params(
    route: Route,
    request: Request,
    *,
    params: dict[str, Any],
) -> None:
    if route.cookies:
        params.update(request.cookies)
