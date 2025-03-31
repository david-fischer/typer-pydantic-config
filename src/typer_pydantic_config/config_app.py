from pathlib import Path

import click
import typer
from platformdirs import user_config_path
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined

from .click_utils import get_flat_fields, update_pydantic_model_command
from .context import set_config
from .dict_utils import unflatten_dict
from .pydantic_writer import ConfigTomlWriter, PydanticWriter


class ConfigApp[PydanticModel: BaseModel]:
    app: typer.Typer
    _typer_click_object: click.Command
    config_cls: type[PydanticModel]
    config_writer: PydanticWriter

    def __init__(
        self,
        app: typer.Typer,
        config_cls: type[PydanticModel],
        config_filename: str = "config.toml",
    ) -> None:
        self.app = app
        self.config_cls = config_cls

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
            help="Interact with config: ( set | init | show | path | delete).",
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
        typer.confirm(
            "Do you really want to delete the current config values?", abort=True
        )
        self.config_writer.delete()

    def config_show_values(self) -> None:
        """Print content of config file."""
        typer.echo(self.config_writer.get_str_repr())

    def config_show_path(self) -> None:
        """Print config path."""
        typer.echo(self.config_writer.path)

    def config_init(self) -> None:
        """Interactively prompt for every field in the config.

        Raises:
        -------
            typer.Exit: If pydantic validation fails.
        """
        if self.config_writer.exists():
            typer.confirm(
                f"Config ({self.config_writer.path}) already exists. Overwrite?",
                abort=True,
            )

        # We'll collect the user inputs in a dict
        input_data = {}
        for field_name, field_model in get_flat_fields(self.config_cls).items():
            # Prompt the user (use default if it exists; otherwise they'll see no default)
            msg = (
                f"[{field_name}]"
                if field_model.description is None
                else f"[{field_name}] - {field_model.description}"
            )
            if field_model.init is None or field_model.init:
                user_value = typer.prompt(
                    text=msg,
                    default=field_model.default
                    if field_model.default is not PydanticUndefined
                    else None,
                )
                input_data[field_name] = user_value

        # Construct and validate the new config
        try:
            new_config = self.config_cls.model_validate(unflatten_dict(input_data))
        except ValidationError as e:
            typer.echo("Invalid input. Please correct the errors and try again.")
            typer.echo(str(e))
            raise typer.Exit(1) from e

        # Save the config
        self.config_writer.save(new_config)
        typer.echo(f"Configuration initialized and saved to {self.config_writer.path}")

    def __call__(self) -> None:
        return self._typer_click_object()


def start_config_app(app: typer.Typer, config_cls: type[BaseModel]) -> None:
    ConfigApp(app=app, config_cls=config_cls)()
