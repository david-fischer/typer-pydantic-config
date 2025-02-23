import datetime
from pathlib import Path
from typing import ClassVar

import typer
from pydantic import Field

from config_app import ConfigApp
from config_base import ConfigBase


class MyConfig(ConfigBase):
    config_path: ClassVar[Path] = Path(__file__).resolve().parent / "config.toml"
    username: str = Field("guest", description="Username for the service")
    api_key: str = Field(..., description="API key (required)")
    output_dir: Path = Field("./output", description="Output directory")
    init_timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC),
        description="Timestamp when config has been initialized.",
        init=False,
    )
    timeout: int | None = Field(30, description="Request timeout in seconds")


config_app = ConfigApp(
    app=typer.Typer(name="my_app", help="Example CLI using Pydantic + TOML + Typer."),
    config_cls=MyConfig,
)


@config_app.app.command()
def hello() -> None:
    """Simple command to verify we can read the config."""
    config = MyConfig.load()
    typer.echo(f"Hello, {config.username}!")
    typer.echo(f"Your API key: {config.api_key}")
    typer.echo(f"Timeout: {config.timeout} seconds")


def main() -> None:
    config_app()


if __name__ == "__main__":
    main()
