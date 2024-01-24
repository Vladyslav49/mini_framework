from mini_framework import Application
from mini_framework.request import Request
from mini_framework.responses import JSONResponse, PlainTextResponse

app = Application()


@app.get("/cookies/")
def cookies(request: Request):
    response = JSONResponse(request.cookies)
    return response


@app.get("/set-cookies/")
def set_cookies():
    response = PlainTextResponse("Cookies set")
    response.set_cookie("name", "John")
    response.set_cookie("age", "20", httponly=True)
    return response


@app.get("/clear-cookie-name/")
def clear_cookies():
    response = PlainTextResponse("Cookies cleared")
    response.delete_cookie("name")
    return response
