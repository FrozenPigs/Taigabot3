"""Load and interface with config file."""
# Standard Libs
import json
from pathlib import Path
from typing import Any, Dict, Tuple, Union

Config = Dict[str, Any]


def save(config: Config, config_file: str) -> None:
    """Is used to save the specified config file."""
    with Path(config_file).resolve().open('w') as f:
        json.dump(config, f, indent=2)
        f.close()
    return None


def load(config_file: str) -> Union[Exception, Config]:
    """Is used to load the specified config file, use reload."""
    with Path(config_file).resolve().open('r') as f:
        conf = json.load(f)
        f.close()
        return conf


def reload(config_file: str, config_mtime: float) -> Union[Exception, Tuple[float, Config]]:
    """Is used to load/reload the config file."""
    new_mtime: float = Path(config_file).resolve().stat().st_mtime
    try:
        if config_mtime != new_mtime:
            if config_mtime != 0:
                print('<<< Config Reloaded')
            config = load(config_file)
    except KeyError as e:
        return e
    return new_mtime, config
