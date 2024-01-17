from mini_framework import Application, Router
from .home import router as home_router

router = Router()


@router.get("/")
def index() -> str:
    return "Hello, World!"


def create_app() -> Application:
    app = Application()
    app.include_router(router)
    app.include_router(home_router)
    return app


app = create_app()
