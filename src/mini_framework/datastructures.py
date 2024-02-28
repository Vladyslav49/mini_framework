from dataclasses import dataclass, field
from typing import BinaryIO

try:
    from multipart.multipart import Field, File
except ImportError:  # pragma: no cover
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class Address:
    host: str
    port: int


@dataclass(frozen=True, slots=True, kw_only=True)
class FormData:
    fields: list["Field"]
    files: list["File"]


@dataclass(frozen=True, slots=True)
class UploadFile:
    file: BinaryIO
    size: int | None = field(default=None, kw_only=True)
    filename: str | None = field(default=None, kw_only=True)
