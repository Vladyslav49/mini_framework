from mini_framework import Application
from mini_framework.request import Request
from mini_framework.responses import JSONResponse

app = Application()


@app.post("/")
def index(request: Request):
    json = request.json()
    return JSONResponse(json)
