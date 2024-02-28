from mini_framework import Application
from mini_framework.responses import PlainTextResponse, JSONResponse

app = Application(default_response_class=JSONResponse)


@app.get("/plain-text/", response_class=PlainTextResponse)
def plain_text():
    return "Hello, World!"


@app.get("/json/")
def json() -> dict[str, str]:
    return {"message": "Hello, World!"}
