import click
import typer
from pydantic import ValidationError
from pydantic_core import PydanticUndefined

from annotation_to_click_type import annotation_to_click_type
from config_base import ConfigBase


class ConfigApp:
    app: typer.Typer
    _typer_click_object: click.Command
    config_cls: type[ConfigBase]

    def create_set_command(self) -> click.core.Command:
        """
        Dynamically create a 'set' command with an option for each field
        in the MyConfig model.

        The user can do:
          myapp config set --username new_user --api-key SECRET --timeout 60
        """
        params = [
            click.Option(
                param_decls=[f"--{field_name.replace('_', '-')}"],
                help=(field_model.description or field_name),
                default=None,
                required=False,
                show_default=False,
                type=annotation_to_click_type(field_model.annotation),
            )
            for field_name, field_model in self.config_cls.model_fields.items()
        ]
        return click.core.Command(
            name="set_config",
            help="Set one or more config fields via flags.",
            callback=self.config_cls.update_on_disk,
            params=params,
        )

    def show_config(self) -> None:
        typer.echo(self.config_cls.load())

    def init(self) -> None:
        """Interactively prompt for every field in the config.

        Raises:
        -------
            typer.Exit: If pydantic validation fails.
        """

        # We'll collect the user inputs in a dict
        input_data = {}
        for field_name, field_model in self.config_cls.model_fields.items():
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
            new_config = self.config_cls(**input_data)
        except ValidationError as e:
            typer.echo("Invalid input. Please correct the errors and try again.")
            typer.echo(str(e))
            raise typer.Exit(1) from e

        # Save the config
        new_config.save()
        typer.echo(f"Configuration initialized and saved to {new_config.config_path}")

    def __init__(
        self,
        app: typer.Typer,
        config_cls: type[ConfigBase],
    ) -> None:
        self.app = app
        self.config_cls = config_cls
        self._init_callback(app)
        self._typer_click_object = typer.main.get_command(app)
        config_click_group = click.Group("config")
        config_click_group.add_command(name="set", cmd=self.create_set_command())
        config_click_group.command("init")(self.init)
        config_click_group.command("show")(self.show_config)
        self._typer_click_object.add_command(config_click_group, "config")

    def _init_callback(self, app: typer.Typer) -> None:
        @app.callback(invoke_without_command=True)
        def main(ctx: typer.Context) -> None:
            if ctx.invoked_subcommand is not None:
                return None
            if not self.config_cls.config_path.exists() and typer.confirm(
                "It seems that the config file does not exist. "
                "Do you want to create it?"
            ):
                return self.init()
            return typer.echo(ctx.get_help())

    def __call__(self) -> None:
        return self._typer_click_object()
