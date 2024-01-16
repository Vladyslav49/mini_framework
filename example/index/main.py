from mini_framework import Application

app = Application()


@app.get("/")
def index() -> str:
    return "Hello, World!"
