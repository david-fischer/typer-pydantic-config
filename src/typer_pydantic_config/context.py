import click
from pydantic import BaseModel

from .constants import CONTEXT_CONFIG_KEY


def _get_config(ctx: click.Context) -> BaseModel:
    return ctx.obj[CONTEXT_CONFIG_KEY]


def set_config(ctx: click.Context, config: BaseModel) -> None:
    ctx.ensure_object(dict)
    ctx.obj[CONTEXT_CONFIG_KEY] = config


def get_config[PydanticModel: BaseModel]() -> PydanticModel:
    return _get_config(click.get_current_context())
