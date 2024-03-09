from pathlib import Path

from mini_framework import Application, Request
from mini_framework.responses import HTMLResponse
from mini_framework.templating import Jinja2Templates

app = Application()

templates = Jinja2Templates(Path(__file__).parent / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.render(
        request, name="index.html", context={"name": "World"}
    )
