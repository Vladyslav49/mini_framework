from pathlib import Path

from mini_framework import Application, Request
from mini_framework.responses import HTMLResponse
from mini_framework.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent

app = Application()
app.add_staticfiles("/css/", BASE_DIR / "static" / "css", name="css")

templates = Jinja2Templates(BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> str:
    return templates.render(request, name="index.html")
