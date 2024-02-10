from pathlib import Path

from mini_framework import Application
from mini_framework.responses import FileResponse

app = Application()


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "files" / "file.txt")
