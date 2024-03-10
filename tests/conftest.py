from http import HTTPMethod
from unittest.mock import Mock, create_autospec

import pytest

from mini_framework import Application, Request


@pytest.fixture()
def app() -> Application:
    return Application()


@pytest.fixture()
def mocked_request() -> Mock:
    request = create_autospec(Request)
    request.path = "/"
    request.method = HTTPMethod.GET
    return request
