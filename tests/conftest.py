from http import HTTPMethod
from unittest.mock import Mock

import pytest

from mini_framework import Application


@pytest.fixture()
def app() -> Application:
    return Application()


@pytest.fixture()
def mock_request() -> Mock:
    request = Mock()
    request.path = "/"
    request.method = HTTPMethod.GET
    return request
