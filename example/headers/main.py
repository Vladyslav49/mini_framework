from typing import Annotated

from mini_framework import Application
from mini_framework.params import Header

app = Application()


@app.get("/")
def index(name: Annotated[str, Header()]) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}
