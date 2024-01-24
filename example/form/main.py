from mini_framework import Application
from mini_framework.request import Request
from mini_framework.responses import PlainTextResponse

app = Application()


@app.post("/")
def index(request: Request):
    form = request.form()
    file = form.files[0]
    file.file_object.seek(0)
    content = file.file_object.read()
    return PlainTextResponse(content)
