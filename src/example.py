import datetime
from pathlib import Path
from typing import ClassVar

import typer
from pydantic import Field
from typer import Typer

from config_app import ConfigApp
from config_base import ConfigBase


class MyConfig(ConfigBase):
    app_name: ClassVar[str] = "example_app"
    username: str = Field("guest", description="Username for the service")
    api_key: str = Field(..., description="API key (required)")
    output_dir: Path = Field("./output", description="Output directory")
    init_timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC),
        description="Timestamp when config has been initialized.",
        init=False,
    )
    timeout: int | None = Field(30, description="Request timeout in seconds")

app = Typer(name="my_app", help="Example CLI using Pydantic + TOML + Typer.")

@app.command()
def hello() -> None:
    """Simple command to verify we can read the config."""
    config = MyConfig.load()
    typer.echo(f"Hello, {config.username}!")
    typer.echo(f"Your API key: {config.api_key}")
    typer.echo(f"Timeout: {config.timeout} seconds")


if __name__ == "__main__":
    ConfigApp(
        app=app,
        config_cls=MyConfig,
    )()