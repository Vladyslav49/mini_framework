from mini_framework import Application
from mini_framework.responses import PlainTextResponse

app = Application()


@app.get("/")
def index():
    return PlainTextResponse("Hello, World!")
