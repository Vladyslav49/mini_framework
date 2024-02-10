from collections.abc import Iterable

from mini_framework import Application
from mini_framework.responses import StreamingResponse

app = Application()


@app.get("/")
def index():
    return StreamingResponse(gen())


def gen() -> Iterable[bytes]:
    for i in range(10):
        yield str(i).encode()
