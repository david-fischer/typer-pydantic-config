from typing import Any


def flatten_dict(
    d: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """Recursively flattens a nested dictionary."""
    items: dict[str, Any] = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def unflatten_dict(d: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    """Reconstructs a nested dictionary from a flattened dictionary."""
    result: dict[str, Any] = {}
    for flat_key, value in d.items():
        keys = flat_key.split(sep)
        current = result
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
    return result
