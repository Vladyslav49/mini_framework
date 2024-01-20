import importlib
from unittest.mock import patch

import jinja2
import pytest

from mini_framework.templating import Jinja2Templates


def test_create_jinja2_template_specifying_directory() -> None:
    Jinja2Templates(directory="templates")


def test_create_jinja2_template_specifying_env() -> None:
    Jinja2Templates(env=jinja2.Environment())


def test_create_jinja2_template_specifying_both_directory_and_env() -> None:
    with pytest.raises(
        ValueError, match="Cannot specify both 'directory' and 'env'"
    ):
        Jinja2Templates(directory="templates", env=jinja2.Environment())


def test_create_jinja2_template_specifying_neither_directory_nor_env() -> None:
    with pytest.raises(
        ValueError, match="Must specify either 'directory' or 'env'"
    ):
        Jinja2Templates()


def test_get_template() -> None:
    templates = Jinja2Templates(directory="templates")

    with patch.object(
        jinja2.Environment, "get_template", return_value=jinja2.Template("")
    ):
        template = templates.get_template("index.html")

    assert isinstance(template, jinja2.Template)


def test_create_jinja2_templates_when_jinja2_is_not_installed() -> None:
    with patch.dict("sys.modules", {"jinja2": None}):
        import mini_framework.templating

        importlib.reload(mini_framework.templating)
        with pytest.raises(AssertionError, match="jinja2 must be installed"):
            Jinja2Templates(directory="templates")
