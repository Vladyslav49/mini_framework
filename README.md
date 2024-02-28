## Disclaimer
This is a project for educational purposes only. It is not intended to be used in production.

## Mini Framework
This is a mini framework for building web applications in Python.

## Usage
```python
# app.py
from mini_framework import Application
from mini_framework.responses import PlainTextResponse

app = Application()


@app.get("/")
def index():
    return PlainTextResponse("Hello, World!")
```

### Details
It is inspired by [aiogram](https://github.com/aiogram/aiogram), [starlette](https://github.com/encode/starlette) and [fastapi](https://github.com/tiangolo/fastapi)

## Running the application
You need to install [gunicorn](https://github.com/benoitc/gunicorn) or any other WSGI server to run the application.

### Example using gunicorn
```bash
$ gunicorn app:app
```