from mini_framework import Application
from mini_framework.request import Request
from mini_framework.responses import PlainTextResponse

app = Application()


@app.post("/")
def index(request: Request):
    if body := request.body.decode():
        return PlainTextResponse(f"Hello, {body}!")
    return PlainTextResponse("Hello, Anonymous!")
