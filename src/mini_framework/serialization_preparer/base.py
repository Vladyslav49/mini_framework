from abc import ABC, abstractmethod
from typing import Any


class SerializationPreparer(ABC):
    @abstractmethod
    def prepare_response(
        self, obj: Any, return_type: type, /
    ) -> Any:  # pragma: no cover
        raise NotImplementedError
