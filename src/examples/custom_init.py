import typer

from examples.minimal import ApiConfig, app
from typer_pydantic_config import start_config_app


def custom_init() -> ApiConfig:
    default_config = ApiConfig(
        api_key="password", username="username", url="test.api.com"
    )
    typer.confirm(
        f"The following config will be set as default:\n{default_config}\nPlease confirm.",
        abort=True,
    )
    return default_config


if __name__ == "__main__":
    start_config_app(app=app, config_cls=ApiConfig, init_config_fn=custom_init)
