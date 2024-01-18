from dataclasses import dataclass, field
from functools import partial
from typing import Any

from mini_framework.routes.route import Callback, Filter
from mini_framework.utils import prepare_kwargs


@dataclass(frozen=True, slots=True, kw_only=True)
class Error:
    callback: Callback
    filters: list[Filter] = field(default_factory=list)

    def check(self, data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        if not self.filters:
            return True, data
        for filter in self.filters:
            if kwargs := prepare_kwargs(filter, data):
                filter = partial(filter, **kwargs)
            check = filter()
            if not check:
                return False, data
            if isinstance(check, dict):
                data.update(check)
        return True, data
