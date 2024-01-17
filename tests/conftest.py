import pytest

from mini_framework import Application


@pytest.fixture
def app() -> Application:
    return Application()
