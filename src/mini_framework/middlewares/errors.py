from __future__ import annotations

from typing import Any, TYPE_CHECKING

from mini_framework.middlewares.base import BaseMiddleware, CallNext
from mini_framework.routes.manager import SkipRoute, UNHANDLED

if TYPE_CHECKING:
    from mini_framework import Application, Response


class ErrorsMiddleware(BaseMiddleware):
    def __init__(self, app: Application) -> None:
        self._app = app

    def __call__(self, call_next: CallNext, data: dict[str, Any]) -> Any:
        try:
            return call_next(data)
        except SkipRoute:
            raise
        except Exception as exception:
            response: Response = self._app.propagate_error(exception, data)
            if response is not UNHANDLED:
                return response
            raise
