from pathlib import Path

from mini_framework import Application
from mini_framework.templating import Jinja2Templates

app = Application()

templates = Jinja2Templates(Path(__file__).parent / "templates")


@app.get("/")
def index():
    return templates.TemplateResponse("index.html", {"name": "World"})
