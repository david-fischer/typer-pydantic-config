from collections.abc import Callable
from pathlib import Path

import click
import typer
from platformdirs import user_config_path
from pydantic import BaseModel

from .click_utils import update_pydantic_model_command
from .context import set_config
from .prompt_utils import init_from_prompt
from .pydantic_writer import ConfigTomlWriter, PydanticWriter


class ConfigApp[PydanticModel: BaseModel]:
    app: typer.Typer
    _typer_click_object: click.Command
    config_cls: type[PydanticModel]
    config_writer: PydanticWriter
    init_config_function: Callable[[], PydanticModel]

    def __init__(
        self,
        app: typer.Typer,
        config_cls: type[PydanticModel],
        config_filename: str = "config.toml",
        init_config_fn: Callable[[], PydanticModel] | None = None,
    ) -> None:
        self.app = app
        self.config_cls = config_cls
        self.init_config_fn = init_config_fn or (lambda: init_from_prompt(config_cls))

        path = user_config_path(appname=app.info.name) / config_filename
        match Path(config_filename).suffix:
            case ".toml":
                self.config_writer = ConfigTomlWriter(
                    path=path,
                    pydantic_cls=config_cls,
                )
            case _:
                msg = "Currently only .toml is supported."
                raise NotImplementedError(msg)
        self._add_init_callback(app)
        self._typer_click_object = typer.main.get_command(app)
        self._typer_click_object.add_command(self.get_config_command_group(), "config")

    def _add_init_callback(self, app: typer.Typer) -> None:
        @app.callback(invoke_without_command=True)
        def main(ctx: typer.Context) -> None:
            if ctx.invoked_subcommand is None:
                return typer.echo(ctx.get_help())
            if ctx.invoked_subcommand == "config":
                return None
            if not self.config_writer.exists() and typer.confirm(
                "It seems that the config file does not exist. "
                "Do you want to create it?",
            ):
                self.config_init()
            set_config(ctx, self.config_writer.load())
            return None

    def get_config_command_group(self) -> click.Group:
        """Return click object with some standard functionality to init / update / show config."""
        config_click_group = click.Group(
            "config",
            help="Interact with config: (delete | init | path | set | show).",
        )
        config_click_group.add_command(
            name="set",
            cmd=update_pydantic_model_command(
                self.config_cls, self.config_writer.update_on_disk
            ),
        )
        config_click_group.command("init")(self.config_init)
        config_click_group.command("show")(self.config_show_values)
        config_click_group.command("path")(self.config_show_path)
        config_click_group.command("delete")(self.delete_config_file)
        return config_click_group

    def delete_config_file(self) -> None:
        """Delete config file on disk."""
        if not self.config_writer.exists():
            return typer.echo(
                f"Config file at {self.config_writer.path} does not exist."
            )
        typer.confirm(
            f"Do you really want to delete the current config at {self.config_writer.path}?",
            abort=True,
        )
        return self.config_writer.delete()

    def config_show_values(self) -> None:
        """Print content of config file."""
        if self.config_writer.exists():
            typer.echo(self.config_writer.get_str_repr())
        else:
            typer.echo(f"Config file at {self.config_writer.path} does not exist.")

    def config_show_path(self) -> None:
        """Print config path."""
        typer.echo(self.config_writer.path)

    def config_init(self) -> None:
        """Interactively prompt for every field in the config."""
        if self.config_writer.exists():
            typer.confirm(
                f"Config ({self.config_writer.path}) already exists. Overwrite?",
                abort=True,
            )
        new_config = self.init_config_fn()
        self.config_writer.save(new_config)
        typer.echo(f"Configuration initialized and saved to {self.config_writer.path}")

    def __call__(self) -> None:
        return self._typer_click_object()


def start_config_app[PydanticModel: BaseModel](
    app: typer.Typer,
    config_cls: type[PydanticModel],
    init_config_fn: Callable[[], PydanticModel] | None = None,
) -> None:
    ConfigApp(
        app=app,
        config_cls=config_cls,
        init_config_fn=init_config_fn,
    )()
