from mini_framework import Application
from mini_framework.request import Request
from mini_framework.responses import PlainTextResponse

app = Application()


@app.post("/")
def index(request: Request):
    if name := request.text:
        return PlainTextResponse(f"Hello, {name}!")
    return PlainTextResponse("Hello, Anonymous!")
