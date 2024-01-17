from mini_framework import Router

router = Router()


@router.get("/home/")
def home() -> str:
    return "Home"
