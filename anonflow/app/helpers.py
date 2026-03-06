from contextlib import contextmanager
from typing import Any, Generator

from .exceptions import NotInitializedError


@contextmanager
def require(obj, *names) -> Generator[Any, Any, None]:
    values = []
    for name in names:
        value = getattr(obj, name, None)
        if value is None:
            raise NotInitializedError(name)
        values.append(value)

    if len(values) == 1:
        yield values[0]
    else:
        yield tuple(values)
