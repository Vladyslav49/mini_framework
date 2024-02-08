from collections.abc import Sequence
from os import PathLike
from typing import Optional

try:
    import jinja2
    from jinja2 import Environment, Template
except ImportError:
    jinja2 = None


class Jinja2Templates:
    __slots__ = ("_env",)

    def __init__(
        self,
        directory: str | PathLike | Sequence[str | PathLike] | None = None,
        env: Optional[
            "Environment"  # pyright: ignore [reportGeneralTypeIssues]
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

    def get_template(self, name: str) -> "Template":  # pyright: ignore [reportGeneralTypeIssues]
        return self._env.get_template(name)
