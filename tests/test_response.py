from http import HTTPMethod, HTTPStatus

from mini_framework import Application, Response
from mini_framework.responses import PlainTextResponse


def test_status_code_in_response(app: Application) -> None:
    @app.get("/")
    def index():
        return PlainTextResponse(
            "Hello, World!", status_code=HTTPStatus.IM_A_TEAPOT
        )

    response: Response = app.propagate("/", method=HTTPMethod.GET)

    assert response.status_code == HTTPStatus.IM_A_TEAPOT
