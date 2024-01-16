## Disclaimer
This is a project for educational purposes only. It is not intended to be used in production.

## Mini Framework
This is a mini framework for building web applications in Python.

## Features
- [x] Routing
- [ ] Routers
- [ ] Middlewares
- [ ] Filters
- [ ] Dependency Injection

## Usage
```python
# app.py
from mini_framework import Application

app = Application()


@app.get("/")
def index() -> str:
    return "Hello, World!"
```

## Running the application
You need to install [gunicorn](https://gunicorn.org/) or any other WSGI server to run the application.

### Example using gunicorn
```bash
$ gunicorn app:app
```