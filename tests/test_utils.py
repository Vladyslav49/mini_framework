from http import HTTPStatus

import pytest

from mini_framework.responses import PlainTextResponse
from mini_framework.utils import get_status_code_and_phrase, prepare_headers


@pytest.mark.parametrize("status", list(HTTPStatus))
def test_get_status_code_and_phrase(status: HTTPStatus) -> None:
    assert get_status_code_and_phrase(status) == f"{status} {status.phrase}"


def test_get_status_code_and_phrase_with_invalid_status_code() -> None:
    with pytest.raises(ValueError, match="Invalid status code: 999"):
        get_status_code_and_phrase(999)


def test_prepare_headers() -> None:
    content = "Hello, World!"
    response = PlainTextResponse(content=content)

    headers = prepare_headers(response, content=response.render())

    assert headers[0][0] == "Content-Type"
    assert "text/plain" in headers[0][1]
    assert headers[1] == ("Content-Length", str(len(content.encode())))
