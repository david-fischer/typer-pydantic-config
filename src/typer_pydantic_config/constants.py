import datetime
from pathlib import Path

import click

FIELD_SEP = "__SEP__"
ANNOTATION_MAP: dict[type, click.ParamType] = {
    int: click.INT,
    float: click.FLOAT,
    bool: click.BOOL,
    str: click.STRING,
    datetime: click.DateTime(),
    Path: click.types.Path(),
}
CONTEXT_CONFIG_KEY = "context"
