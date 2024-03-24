import inspect
from typing import Any

from pydantic_core import to_jsonable_python

from mini_framework.responses import Response
from mini_framework.serialization_preparer.base import SerializationPreparer


class PydanticSerializationPreparer(SerializationPreparer):
    def prepare_response(self, obj: Any, return_type: type, /) -> Any:
        if inspect.isclass(return_type) and (
            issubclass(return_type, Response) or return_type is Any
        ):
            if isinstance(obj, Response):
                obj.content = to_jsonable_python(obj.content)
                return obj
        return to_jsonable_python(obj)
