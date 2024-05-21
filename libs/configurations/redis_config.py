from typing import Optional

from decouple import config as env_config
from traitlets import Any

from libs.configurations.config_base import ConfigBase

# loaded config
config_redis = {
    "host": env_config("REDIS_HOST", default="localhost"),
    "port": env_config("REDIS_PORT", default=6379),
    "db": env_config("REDIS_DB", default=0),
    "password": env_config("REDIS_PASSWORD", default=""),
    "socket_timeout": env_config("REDIS_SOCKET_TIMEOUT", default=None),
}


class RedisConfig(ConfigBase):
    """
    Specialized class to provide centralized environment settings
    control of Redis Database Memory.
    """

    def __init__(self) -> None:
        super().__init__(self.get_default_config())

    def get_host(self) -> Optional[str | Any]:
        return super()._get_property("host")

    def get_host_with_prefix(self) -> Optional[str | Any]:
        return "{}{}".format("redis://", str(super()._get_property("host")))

    @classmethod
    def get_default_config(self):
        return config_redis


def static_get_host():
    config = RedisConfig()
    config.get_host()
