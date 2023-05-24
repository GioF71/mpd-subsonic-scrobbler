from subsonic_connector.configuration import Configuration
from config_util import get_indexed_env_value

from config_key import ConfigKey

import dotenv
import libsonic

class MpdInstanceConfig(Configuration):

    def __init__(self, index : int = 0):
        self.__mpd_host : str = get_indexed_env_value(
            ConfigKey.MPD_HOST.get_key(), 
            index)
        self.__mpd_port : int = int(get_indexed_env_value(
            ConfigKey.MPD_PORT.get_key(), 
            index))

    def get_mpd_host(self) -> str: return self.__mpd_host
    def get_mpd_port(self) -> int: return self.__mpd_port
