from mini_framework import Application, Router
from mini_framework.responses import PlainTextResponse
from .home import router as home_router

router = Router(prefix="/index")


@router.get("/")
def index():
    return PlainTextResponse("Hello, World!")


def create_app() -> Application:
    app = Application()
    app.include_router(router)
    app.include_router(home_router)
    return app


app = create_app()
