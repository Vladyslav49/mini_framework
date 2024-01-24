from mini_framework import Application
from mini_framework.responses import RedirectResponse

app = Application()


@app.get("/")
def index():
    return RedirectResponse("/hello/")
