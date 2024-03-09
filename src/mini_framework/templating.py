from collections.abc import Sequence
from os import PathLike
from typing import Optional, Any

from mini_framework import Request

try:
    import jinja2
    from jinja2 import Environment, Template, pass_context
except ImportError:
    jinja2 = None


class Jinja2Templates:
    __slots__ = ("_env",)

    def __init__(
        self,
        directory: str | PathLike | Sequence[str | PathLike] | None = None,
        env: Optional[
            "Environment"  # pyright: ignore[reportGeneralTypeIssues]
        ] = None,
    ) -> None:
        assert jinja2 is not None, "jinja2 must be installed"
        if directory is not None and env is not None:
            raise ValueError("Cannot specify both 'directory' and 'env'")
        if directory is None and env is None:
            raise ValueError("Must specify either 'directory' or 'env'")
        if directory is not None:
            self._env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(directory)
            )
        elif env is not None:
            self._env = env

        self._env.globals.setdefault("url_for", _url_for)

    def render(
        self,
        request: Request,
        /,
        *,
        name: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        if context is None:
            context = {}
        template = self.get_template(name)
        content = template.render(request=request, **context)
        return content

    def get_template(self, name: str) -> "Template":  # pyright: ignore[reportGeneralTypeIssues]
        return self._env.get_template(name)


@pass_context  # pyright: ignore[reportPossiblyUnboundVariable]
def _url_for(
    context: dict[str, Any],
    name: str,
    /,
    **path_params: Any,
) -> str:
    request: Request = context["request"]
    return request.url_for(name, **path_params)
