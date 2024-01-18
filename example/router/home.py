from mini_framework import Router
from mini_framework.responses import PlainTextResponse

router = Router()


@router.get("/home/")
def home():
    return PlainTextResponse("Home")
