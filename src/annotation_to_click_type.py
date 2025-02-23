import datetime
import types
from pathlib import Path
from typing import Any, Union, get_args, get_origin

import click

ANNOTATION_MAP: dict[type, click.ParamType] = {
    int: click.INT,
    float: click.FLOAT,
    bool: click.BOOL,
    str: click.STRING,
    datetime: click.DateTime(),
    Path: click.types.Path(),
}


def annotation_to_click_type(
    annotation: type[Any] | None,
) -> click.ParamType | None:
    """Map annotation (from a Pydantic field) to suitable click.ParamType.

    Returns:
    -------
         click.ParamType | None: None if we can't find a suitable match.
    """
    origin = get_origin(annotation)
    # Handle Optional[...] => Union[T, NoneType]
    # We'll strip NoneType and recur on the remaining type if there's exactly one.
    if origin in {Union, types.UnionType}:
        args = get_args(annotation)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) >= 1:
            return annotation_to_click_type(non_none_args[0])
        return None
    return ANNOTATION_MAP.get(annotation)
