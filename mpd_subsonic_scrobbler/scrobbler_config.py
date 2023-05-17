import config_util
from config_key import ConfigKey
from subsonic_server_config import SubsonicServerConfig
import scrobbler_util
import copy

class ScrobblerConfig:

    def __init__(self):
        self.__sleep_time_msec : str = config_util.get_env_value(ConfigKey.SLEEP_TIME.getKey(), "1000")
        self.__sleep_time_sec : float = float(self.__sleep_time_msec) / 1000.0
        self.__min_coverage : int = int(config_util.get_env_value(ConfigKey.MIN_COVERAGE.getKey(), "50"))
        self.__enough_playback_sec : int = int(config_util.get_env_value(ConfigKey.ENOUGH_PLAYBACK_SEC.getKey(), "240"))
        self.__verbose : bool = True if int(config_util.get_env_value(ConfigKey.VERBOSE.getKey(), "0")) == 1 else False
        self.__mpd_host : str = config_util.get_env_value(ConfigKey.MPD_HOST.getKey(), "localhost")
        self.__mpd_port : str = config_util.get_env_value(ConfigKey.MPD_PORT.getKey(), "6600")
        self.__server_list : list[SubsonicServerConfig] = scrobbler_util.get_subsonic_server_config_list()

    def get_sleep_time_msec(self) -> str: return self.__sleep_time_msec
    def get_sleep_time_sec(self) -> float: return self.__sleep_time_sec    
    def get_min_coverage(self) -> int: return self.__min_coverage
    def get_enough_playback_sec(self) -> int: return self.__enough_playback_sec
    def get_verbose(self) -> bool: return self.__verbose
    def get_mpd_host(self) -> str: return self.__mpd_host
    def get_mpd_port(self) -> str: return self.__mpd_port
    def get_server_list(self) -> list[SubsonicServerConfig]: return copy.deepcopy(self.__server_list)
