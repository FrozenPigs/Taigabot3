# Standard Libs
from typing import Any, Callable, Dict, List, Union

# First Party
from bot import Client

ServerConfigType = Dict[str, Union[str, List[str]]]
FullConfigType = Dict[str,
                      Union[str, List[str], Dict[str, str], ServerConfigType]]
PluginType = Callable[[Client, Any], None]
PlugsType = Dict[str, Dict[str, PluginType]]
