from mini_framework import Application
from mini_framework.request import Request
from mini_framework.responses import PlainTextResponse

app = Application()


@app.get("/")
def index(request: Request):
    names = request.query_params.get("name", ["Anonymous"])
    return PlainTextResponse(f"Hello, {names[0]}!")
