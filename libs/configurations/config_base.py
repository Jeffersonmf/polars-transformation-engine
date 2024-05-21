from typing import Any, Optional


class ConfigBase:
    """
    Super class to provide centralized environment settings control.
    """

    def __init__(self, params):
        self._config = params  # set it to conf

    def _get_property(self, property_name) -> Optional[Any]:
        if property_name not in self._config.keys():  # we don't want KeyError
            return None  # just return None if not found
        return self._config[property_name]
