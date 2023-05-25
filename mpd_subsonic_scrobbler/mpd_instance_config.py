from subsonic_connector.configuration import Configuration
from config_util import get_indexed_env_value
from config_util import get_env_value

from config_key import ConfigKey
from indexed_key import indexed_config_key

class MpdInstanceConfig(Configuration):

    def __init__(self, index : int = 0):
        self.__mpd_friendly_name : str =  self.__read_env(ConfigKey.MPD_FRIENDLY_NAME, index)
        self.__mpd_host : str =  self.__read_env(ConfigKey.MPD_HOST, index)
        self.__mpd_port : int = int(self.__read_env(ConfigKey.MPD_PORT, index))

    def __read_env(self, config_key : ConfigKey, index : int) -> str:
        key : str = indexed_config_key(config_key, index)
        return get_env_value(key, config_key.get_default_value())

    def get_mpd_friendly_name(self) -> str:
        if self.__mpd_friendly_name and len(self.__mpd_friendly_name) > 0: return self.__mpd_friendly_name
        return f"mpd@{self.get_mpd_host()}:{self.get_mpd_port()}"

    def get_mpd_host(self) -> str: return self.__mpd_host
    def get_mpd_port(self) -> int: return self.__mpd_port
