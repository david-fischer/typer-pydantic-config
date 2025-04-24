from typing import Any

import typer
from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo
from pydantic_core._pydantic_core import PydanticUndefined  # noqa: PLC2701

from typer_pydantic_config.click_utils import get_flat_fields
from typer_pydantic_config.dict_utils import unflatten_dict


def get_simple_default(field_info: FieldInfo) -> Any:
    """
    Return the default value for a field.

    Raises
    ------
        NotImplementedError: If default_factory has arguments.
    """
    if field_info.default_factory_takes_validated_data:
        msg = "Default factories with arguments are not supported in typer-pydantic-config."
        raise NotImplementedError(msg)
    default = field_info.get_default(call_default_factory=True)
    return None if default is PydanticUndefined else default


def prompt_for_value(
    field_name: str,
    field_info: FieldInfo,
) -> Any:
    """Use typer to prompt for the value of a pydantic model field."""
    description_str = f" - {field_info.description}" if field_info.description else ""
    msg = f"[{field_name}]{description_str}"
    return typer.prompt(
        text=msg,
        default=get_simple_default(field_info),
    )


def has_init(field_info: FieldInfo) -> bool:
    """Return if a field should be part of the __init__ method."""
    return field_info.init is None or field_info.init


def init_from_prompt[PydanticModel: BaseModel](
    model_class: type[PydanticModel],
) -> PydanticModel:
    """Return initialized model from interactive user input.

    Raises:
        typer.Exit: If the pydantic model validation fails.
    """
    flat_fields = get_flat_fields(model_class)
    values = {
        field_name: prompt_for_value(field_name=field_name, field_info=field_info)
        for field_name, field_info in flat_fields.items()
        if has_init(field_info)
    }
    try:
        result = unflatten_dict(values)
        return model_class.model_validate(result)
    except ValidationError as e:
        typer.echo("Invalid input. Please correct the errors and try again.")
        typer.echo(str(e))
        raise typer.Exit(1) from e
