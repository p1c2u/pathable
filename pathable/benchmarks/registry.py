"""Implementation resolution for benchmark CLI."""

import importlib
from typing import Any

from pathable.paths import BasePath


def _resolve_qualname(module_name: str, qualname: str) -> Any:
    module = importlib.import_module(module_name)
    obj: Any = module
    for part in qualname.split("."):
        obj = getattr(obj, part)
    return obj


def resolve_impl(target: str) -> type[BasePath]:
    """Resolve an implementation target into a BasePath subclass.

    Supported formats:
    - ``module.path.ClassName``
    - ``module.path:ClassName``
    """
    if not target:
        raise ValueError("implementation target must be non-empty")

    obj: Any
    if ":" in target:
        module_name, qualname = target.split(":", 1)
        obj = _resolve_qualname(module_name, qualname)
    else:
        if "." not in target:
            raise ValueError(
                "implementation target must be dotted path or module:qualname"
            )
        module_name, qualname = target.rsplit(".", 1)
        obj = _resolve_qualname(module_name, qualname)

    if not isinstance(obj, type):
        raise TypeError(
            f"implementation target must resolve to a class: {target}"
        )
    if not issubclass(obj, BasePath):
        raise TypeError(
            "implementation target must resolve to BasePath subclass: "
            f"{target}"
        )
    return obj
