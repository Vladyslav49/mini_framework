import importlib
import sys
from contextlib import AbstractContextManager, nullcontext
from unittest.mock import patch

import pytest
from jinja2 import Environment, Template, DictLoader

import mini_framework.templating
from mini_framework import Application, Request
from mini_framework.templating import Jinja2Templates


@pytest.mark.parametrize(
    "directory, env, contextmanager",
    [
        (
            "templates",
            None,
            nullcontext(),
        ),
        (
            "templates",
            Environment(),
            pytest.raises(
                ValueError, match="Cannot specify both 'directory' and 'env'"
            ),
        ),
        (
            None,
            Environment(),
            nullcontext(),
        ),
        (
            None,
            None,
            pytest.raises(
                ValueError, match="Must specify either 'directory' or 'env'"
            ),
        ),
    ],
)
def test_create_jinja2_templates(
    directory: str | None,
    env: Environment | None,
    contextmanager: AbstractContextManager,
) -> None:
    with contextmanager:
        Jinja2Templates(directory=directory, env=env)


def test_create_jinja2_templates_when_jinja2_is_not_installed() -> None:
    with patch.dict(sys.modules, {"jinja2": None}):
        importlib.reload(mini_framework.templating)
        with pytest.raises(AssertionError, match="jinja2 must be installed"):
            Jinja2Templates(directory="templates")

    importlib.reload(mini_framework.templating)


def test_get_template() -> None:
    mocked_template = Template("")

    with patch.object(
        Environment, "get_template", autospec=Environment.get_template
    ) as mocked_get_template:
        mocked_get_template.return_value = mocked_template

        env = Environment()
        templates = Jinja2Templates(env=env)
        template = templates.get_template("index.html")

    assert template == mocked_template
    mocked_get_template.assert_called_once_with(env, "index.html")


def test_url_for(app: Application) -> None:
    @app.get("/")
    def index():
        assert False  # noqa: B011

    environ = {
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
    }
    path_params = {}
    request = Request(app, environ, path_params=path_params)
    loader = DictLoader({"index.html": "{{ url_for('index') }}"})
    env = Environment(loader=loader)
    templates = Jinja2Templates(env=env)

    content = templates.render(request, name="index.html")

    assert content == "http://testserver/"


def test_url_for_with_path_params(app: Application) -> None:
    @app.get("/items/{id}/")
    def item():
        assert False  # noqa: B011

    environ = {
        "wsgi.url_scheme": "http",
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
    }
    path_params = {}
    request = Request(app, environ, path_params=path_params)
    loader = DictLoader({"index.html": "{{ url_for('item', id=id) }}"})
    env = Environment(loader=loader)
    templates = Jinja2Templates(env=env)

    content = templates.render(request, name="index.html", context={"id": 1})

    assert content == "http://testserver/items/1/"
