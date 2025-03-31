# Typer Pydantic Config

This package helps you quickly build python CLI applications with a persistent config.

1. Implement config object as pydantic class
2. Use `get_config` where every you need the current values
3. Build a normal app with typer
4. start the app with `start_config_app`

On the first invocation, prompts the user to set all values in the config file.

Your app now has an additional `config` command with the following signature:
```text
Usage: example.py config [OPTIONS] COMMAND [ARGS]...

  Interact with config: ( set | init | show | path | delete).

Options:
  --help  Show this message and exit.

Commands:
  delete  Delete config file on disk.
  init    Interactively prompt for every field in the config.
  path    Print config path.
  set     Set one or more config fields via flags.
  show    Print content of config file.
```


##  Current shortcomings 
 * Supports only the following basic types:
   * Pydantic model
   * int
   * float
   * bool
   * str
   * datetime
   * Path
