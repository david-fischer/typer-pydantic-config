import types
from collections.abc import Callable
from typing import Any, Union, get_args, get_origin

import click
from pydantic import BaseModel

from .constants import ANNOTATION_MAP, FIELD_SEP
from .dict_utils import flatten_dict


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


def get_nested_fields(model: type[BaseModel]) -> dict[str, Any]:
    return {
        field_name: (
            field_model
            if not issubclass(field_model.annotation, BaseModel)
            else get_nested_fields(field_model.annotation)
        )
        for field_name, field_model in model.model_fields.items()
    }


def get_flat_fields(model: type[BaseModel]) -> dict[str, Any]:
    return flatten_dict(get_nested_fields(model))


def update_pydantic_model_command[PydanticModel: BaseModel](
    pydantic_model: type[PydanticModel],
    callback: Callable[[...], ...],
) -> click.Command:
    """Dynamically create a 'set' command with an option for each field in the model.

    The user can do:
      <myapp> config set --username new_user --api-key SECRET --timeout 60
    """
    params = [
        click.Option(
            param_decls=[
                f"--{field_name.replace('_', '-')}",
                field_name.replace(".", FIELD_SEP),
            ],
            help=(field_model.description or field_name),
            default=None,
            required=False,
            show_default=False,
            type=annotation_to_click_type(field_model.annotation),
        )
        for field_name, field_model in get_flat_fields(pydantic_model).items()
    ]
    return click.core.Command(
        name="set",
        help="Set one or more config fields via flags.",
        callback=callback,
        params=params,
    )
