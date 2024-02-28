from mini_framework import Router
from mini_framework.responses import PlainTextResponse

router = Router(prefix="/index/home")


@router.get("/")
def home():
    return PlainTextResponse("Home")
