from mini_framework import Application

app = Application()


@app.get("/")
def index() -> dict[str, str]:
    return {"message": "Hello, World!"}
