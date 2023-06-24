from collections import defaultdict
from typing import Any


class NestedDefaultDict(defaultdict):
    """Multi-level `defaultdict` which automatically adds as many levels as needed."""

    def __init__(self, *args, **kwargs):
        super().__init__(NestedDefaultDict, *args, **kwargs)

    def setdefault(self, keys: list, default=None) -> Any:
        """Similar to `dict.setdefault` except that it accepts an arbitrary number of keys."""
        assert keys
        key = keys[0]
        if len(keys) == 1:
            return super().setdefault(key, default)
        return self[key].setdefault(keys[1:], default)
