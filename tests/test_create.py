from contextlib import AbstractContextManager, nullcontext
from http import HTTPMethod

import pytest

from mini_framework import Router
from mini_framework.routes.route import Route


def test_create_router() -> None:
    Router()


def test_create_router_with_name() -> None:
    router = Router(name="my_router")

    assert router.name == "my_router"


@pytest.mark.parametrize(
    "path, method, contextmanager",
    [
        (
            "/",
            HTTPMethod.GET,
            nullcontext(),
        ),
        (
            "wrong_path/",
            HTTPMethod.GET,
            pytest.raises(
                ValueError, match="Path 'wrong_path/' must start with '/'"
            ),
        ),
        (
            "/wrong_path",
            HTTPMethod.GET,
            pytest.raises(
                ValueError, match="Path '/wrong_path' must end with '/'"
            ),
        ),
        (
            "/",
            "WRONG",
            pytest.raises(
                ValueError, match="Method 'WRONG' is not valid HTTP method"
            ),
        ),
    ],
)
def test_create_route(
    path: str, method: str, contextmanager: AbstractContextManager
) -> None:
    with contextmanager:
        Route(callback=lambda: None, path=path, method=method)
