# Typer Pydantic Config

This package helps you quickly build python CLI applications with a persistent config using [typer](https://typer.tiangolo.com/) & [pydantic](https://docs.pydantic.dev/latest/).

![minimal_example.gif](https://github.com/david-fischer/typer-pydantic-config/blob/main/assets/minimal_example.gif)

See [minimal.py](src/examples/minimal.py) and [example.py](src/examples/example.py) for two simple examples.

## Installation
Install it from [pypi](https://pypi.org/project/typer-pydantic-config/) using your preferred method, e.g. through [uv](https://github.com/astral-sh/uv):
```bash
uv pip install typer-pydantic-config
```

## Usage

1. Implement config object as [pydantic](https://docs.pydantic.dev/latest/) class
2. Use `get_config` where every you need the config object
3. Build your [typer](https://typer.tiangolo.com/) app
4. Start the app with `start_config_app(app, <YourConfigPydanticClass>)`

On the first invocation, prompts the user to set all values in the config file.

Your app now has an additional `config` command with the following signature:
```text
$ python example.py config --help
Usage: example.py config [OPTIONS] COMMAND [ARGS]...

  Interact with config: (delete | init | path | set | show).

Options:
  --help  Show this message and exit.

Commands:
  delete  Delete config file on disk.
  init    Interactively prompt for every field in the config.
  path    Print config path.
  set     Set one or more config fields via flags.
  show    Print content of config file.
```


## ⚠ Current Limitations ⚠
 * The package is still an early draft and not yet thoroughly tested
 * Only `default_factory` without arguments is supported
 * Does not support optional fields yet
 * The following types are supported as attributes of your config class:
   * int
   * float
   * bool
   * str
   * datetime
   * Path
   * another subclass of pydantic's `BaseModel`
 * Config values are available as `ctx.obj["config"]` (see [click docs: Context](https://click.palletsprojects.com/en/stable/api/#click.Context)).
   * This is only available when one of the endpoint functions is called.
   * Do not overwrite the `ctx.obj` (at least not the `"config"` key).
 * Unique app name required:
   * Set a unique name: `app = typer.Typer(name="<some_unique_name>")`
   * This name is used by [platformdirs](https://github.com/tox-dev/platformdirs) to construct the path of the config.
