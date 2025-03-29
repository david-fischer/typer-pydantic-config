import datetime
from pathlib import Path

import typer
from pydantic import BaseModel, Field

from typer_pydantic_config import get_config, start_config_app


class ApiCredentials(BaseModel):
    username: str = Field("guest", description="Username for the service")
    api_key: str = Field(..., description="API key (required)")


class ApiConfig(BaseModel):
    credentials: ApiCredentials
    output_dir: Path = Field("./output", description="Output directory")
    init_timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.UTC),
        description="Timestamp when config has been initialized.",
        init=False,
    )
    timeout: int | None = Field(30, description="Request timeout in seconds")


app = typer.Typer(
    name="example_app_api",
    help="Example CLI using Pydantic + Typer.",
)


@app.command()
def hello() -> None:
    """Simple command to verify we can read the config."""
    config: ApiConfig = get_config()
    typer.echo(f"Hello, {config.credentials.username}!")
    typer.echo(f"Your API key: {config.credentials.api_key}")
    typer.echo(f"Timeout: {config.timeout} seconds")
    typer.echo(f"Init timestamp: {config.init_timestamp}")
    typer.echo(f"Output path: {config.output_dir}")


if __name__ == "__main__":
    start_config_app(app=app, config_cls=ApiConfig)
