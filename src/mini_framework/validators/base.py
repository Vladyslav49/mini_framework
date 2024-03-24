from abc import ABC, abstractmethod
from typing import Any


class Validator(ABC):
    @abstractmethod
    def validate_request(
        self, params: dict[str, Any], model: type, /
    ) -> Any:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def validate_response(
        self, obj: Any, return_type: type, /
    ) -> Any:  # pragma: no cover
        raise NotImplementedError
