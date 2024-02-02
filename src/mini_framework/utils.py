from __future__ import annotations

import inspect
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from mini_framework.routes.route import Callback


def prepare_kwargs(
    callback: Callback, kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Prepare kwargs for a given callback."""
    spec = inspect.getfullargspec(callback)
    if spec.varkw is not None:
        return kwargs
    parameters = {*spec.args, *spec.kwonlyargs}
    return {key: kwargs[key] for key in parameters if key in kwargs}


def prepare_path(path: str) -> str:
    if path[-1] == "/":
        return path
    return path + "/"
