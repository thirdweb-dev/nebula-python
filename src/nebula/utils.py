from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

def parse_or_none(
    raw: dict[str, Any] | T | None,
    model: type[T]
) -> T | None:
    """
    Convert `raw` (a dict or a model instance) into an instance of `model`
    or None if `raw` is None. Raise ValueError on validation error.
    """
    if raw is None:
        return None
    if isinstance(raw, model):
        # Already the correct type
        return raw
    if isinstance(raw, dict):
        try:
            return model(**raw)  # Validate and instantiate
        except ValidationError as e:
            raise ValueError(f"Invalid format for {model.__name__}: {e!s}") from e
    raise ValueError(f"Expected None, dict, or {model.__name__}, got {type(raw)}")

