from contextlib import nullcontext, AbstractContextManager

import pytest

from mini_framework import Application, Router, Response
from mini_framework.responses import PlainTextResponse, JSONResponse


def test_create_router_with_name() -> None:
    router = Router(name="my_router")

    assert router.name == "my_router"


@pytest.mark.parametrize(
    "prefix, contextmanager",
    [
        ("", nullcontext()),
        (
            "prefix",
            pytest.raises(
                ValueError, match="Prefix 'prefix' must start with '/'"
            ),
        ),
        (
            "/prefix/",
            pytest.raises(
                ValueError, match="Prefix '/prefix/' must not end with '/'"
            ),
        ),
    ],
)
def test_create_router_with_prefix(
    prefix: str, contextmanager: AbstractContextManager
) -> None:
    with contextmanager:
        Router(prefix=prefix)


def test_include_router(app: Application) -> None:
    router = Router()

    app.include_router(router)

    assert router.parent_router is app


def test_include_application_to_router(app: Application) -> None:
    router = Router()

    with pytest.raises(
        RuntimeError,
        match="Application can not be attached to another Router",
    ):
        router.include_router(app)


def test_include_router_self_reference() -> None:
    router = Router()

    with pytest.raises(
        RuntimeError, match="Self-referencing routers is not allowed"
    ):
        router.include_router(router)


def test_include_router_circular_reference() -> None:
    router1 = Router()
    router2 = Router()

    router1.include_router(router2)

    with pytest.raises(
        RuntimeError, match="Circular referencing of Router is not allowed"
    ):
        router2.include_router(router1)


def test_router_is_already_attached(app: Application) -> None:
    router1 = Router()
    router2 = Router()

    router1.include_router(router2)

    with pytest.raises(
        RuntimeError, match=f"Router is already attached to {router1!r}"
    ):
        app.include_router(router2)


def test_include_router_not_router(app: Application) -> None:
    with pytest.raises(
        ValueError, match="router should be instance of Router not 'str'"
    ):
        app.include_router("some")  # type: ignore[arg-type]


def test_set_parent_router_not_router() -> None:
    router = Router()

    with pytest.raises(
        ValueError, match="router should be instance of Router not 'str'"
    ):
        router.parent_router = "some"  # type: ignore[reportAttributeAccessIssue]


def test_router_chain_head() -> None:
    router1 = Router()
    router2 = Router()
    router3 = Router()

    router1.include_router(router2)
    router2.include_router(router3)

    assert list(router3.chain_head) == [router3, router2, router1]


def test_router_chain_tail() -> None:
    router1 = Router()
    router2 = Router()
    router3 = Router()
    router4 = Router()

    router1.include_router(router2)
    router2.include_router(router3)
    router2.include_router(router4)

    assert list(router1.chain_tail) == [router1, router2, router3, router4]


def test_include_router_with_prefix(app: Application) -> None:
    router = Router()

    app.include_router(router, prefix="/prefix")

    assert router.prefix == "/prefix"


@pytest.mark.parametrize(
    "prefix, contextmanager",
    [
        (
            "prefix",
            pytest.raises(
                ValueError, match="Prefix 'prefix' must start with '/'"
            ),
        ),
        (
            "/prefix/",
            pytest.raises(
                ValueError, match="Prefix '/prefix/' must not end with '/'"
            ),
        ),
    ],
)
def test_include_router_with_prefix_invalid_prefix(
    app: Application, prefix: str, contextmanager: AbstractContextManager
) -> None:
    router = Router()

    with contextmanager:
        app.include_router(router, prefix=prefix)

    assert router.prefix == ""


@pytest.mark.parametrize(
    "default_response_class, expected_default_response_class",
    [
        (None, JSONResponse),
        (PlainTextResponse, PlainTextResponse),
    ],
)
def test_include_router_with_default_response_class(
    app: Application,
    default_response_class: type[Response] | None,
    expected_default_response_class: type[Response],
) -> None:
    router = Router()

    app.include_router(router, default_response_class=default_response_class)

    assert router.default_response_class == expected_default_response_class
