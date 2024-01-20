from __future__ import annotations

import inspect
from http.client import responses
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mini_framework.responses import Response
    from mini_framework.routes.route import Callback


def get_status_code_and_phrase(status_code: int) -> str:
    """Get status code and phrase for a given status code."""
    if status_code not in responses:
        raise ValueError(f"Invalid status code: {status_code}")
    return f"{status_code} {responses[status_code]}"


def prepare_headers(response: Response) -> dict[str, str]:
    """Prepare headers for a given response."""
    headers = {
        "Content-Type": f"{response.media_type}; charset={response.charset}",
        "Content-Length": str(len(response.body)),
    }
    return headers | dict(response.headers)


def prepare_kwargs(
    callback: Callback, kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Prepare kwargs for a given callback."""
    spec = inspect.getfullargspec(callback)
    if spec.varkw is not None:
        return kwargs
    parameters = {*spec.args, *spec.kwonlyargs}
    return {key: kwargs[key] for key in parameters if key in kwargs}
