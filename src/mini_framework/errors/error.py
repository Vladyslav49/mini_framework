from dataclasses import dataclass, field
from typing import Any

from mini_framework.routes.route import CallableObject


@dataclass(slots=True, kw_only=True)
class Error(CallableObject):
    filters: list[CallableObject] = field(default_factory=list)

    def check(self, **kwargs: Any) -> tuple[bool, dict[str, Any]]:
        if not self.filters:
            return True, kwargs
        for filter in self.filters:
            check = filter.call(**kwargs)
            if not check:
                return False, kwargs
            if isinstance(check, dict):
                kwargs.update(check)
        return True, kwargs
