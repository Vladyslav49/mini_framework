from typing import Annotated


from mini_framework import Application, Request
from mini_framework.params import Field, File
from mini_framework.datastructures import UploadFile
from mini_framework.responses import PlainTextResponse

app = Application()


@app.post("/")
def index(request: Request):
    form = request.form()
    file = form.files[0]
    file.file_object.seek(0)
    content = file.file_object.read()
    return PlainTextResponse(content)


@app.post("/hello/")
def hello(name: Annotated[str, Field()], file: Annotated[bytes, File()]):
    assert file == b"Hello, World!"
    return PlainTextResponse(f"Hello, {name}!")


@app.post("/upload-files/")
def upload_files(upload_files: list[UploadFile]):
    for i, file in enumerate(upload_files):
        assert file.file.read().decode() == f"Hello, World {i}!"
    return PlainTextResponse("Hello, World!")


@app.post("/upload-multiple-files/")
def upload_multiple_files(
    upload_file_0: UploadFile, upload_file_1: UploadFile
):
    assert upload_file_0.file.read().decode() == "Hello, World 0!"
    assert upload_file_1.file.read().decode() == "Hello, World 1!"
    return PlainTextResponse("Hello, World!")


@app.post("/upload-multiple-files-with-list/")
def upload_multiple_files_with_list(
    upload_file_0: UploadFile,
    upload_file_1: UploadFile,
    upload_files: list[UploadFile],
):
    assert upload_file_0.file.read().decode() == "Hello, World 0!"
    assert upload_file_1.file.read().decode() == "Hello, World 1!"
    for i, file in enumerate(upload_files, start=2):
        assert file.file.read().decode() == f"Hello, World {i}!"
    return PlainTextResponse("Hello, World!")
