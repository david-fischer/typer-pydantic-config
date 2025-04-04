from time import sleep

import typer
from pydantic import BaseModel, Field

from typer_pydantic_config import get_config, start_config_app


class ApiConfig(BaseModel):
    url: str = Field(..., description="The URL of the Endpoint")
    username: str = Field("guest", description="Username for the service")
    api_key: str = Field(..., description="API key")


app = typer.Typer(
    # Setting the name of the app is required. Also this has to be unique.
    name="minimal_example_app",
    help="Example CLI using Pydantic + Typer.",
)


@app.command()
def mock_request() -> None:
    """Simple command to verify we can read the config."""
    config = get_config()
    typer.echo(f"Mocking API request at {config.url!r}...")
    with typer.progressbar(range(100), length=100) as progress:
        for _ in progress:
            sleep(0.03)
    typer.echo(
        f"Request as user {config.username!r} with key {config.api_key!r} successful."
    )


if __name__ == "__main__":
    start_config_app(app=app, config_cls=ApiConfig)
