import config_util
from config_key import ConfigKey
from subsonic_server_config import SubsonicServerConfig
import scrobbler_util
import copy

class ScrobblerConfig:

    def __init__(self):
        self.__sleep_time_msec : str = self.__read_env(ConfigKey.SLEEP_TIME)
        self.__sleep_time_sec : float = float(self.__sleep_time_msec) / 1000.0
        self.__min_coverage : int = int(self.__read_env(ConfigKey.MIN_COVERAGE))
        self.__enough_playback_sec : int = int(self.__read_env(ConfigKey.ENOUGH_PLAYBACK_SEC))
        self.__verbose : bool = True if int(self.__read_env(ConfigKey.VERBOSE)) == 1 else False
        self.__redact_credentials : bool = True if int(self.__read_env(ConfigKey.REDACT_CREDENTIALS)) == 1 else False
        self.__mpd_host : str = self.__read_env(ConfigKey.MPD_HOST)
        self.__mpd_port : int = int(self.__read_env(ConfigKey.MPD_PORT))
        self.__server_list : list[SubsonicServerConfig] = scrobbler_util.get_subsonic_server_config_list()

    def __read_env(self, config_key : ConfigKey) -> str:
        return config_util.get_env_value(config_key.get_key(), config_key.get_default_value())

    def get_sleep_time_msec(self) -> str: return self.__sleep_time_msec
    def get_sleep_time_sec(self) -> float: return self.__sleep_time_sec    
    def get_min_coverage(self) -> int: return self.__min_coverage
    def get_enough_playback_sec(self) -> int: return self.__enough_playback_sec
    def get_verbose(self) -> bool: return self.__verbose
    def get_redact_credentials(self) -> bool: return self.__redact_credentials
    def get_mpd_host(self) -> str: return self.__mpd_host
    def get_mpd_port(self) -> int: return self.__mpd_port
    def get_server_list(self) -> list[SubsonicServerConfig]: return copy.deepcopy(self.__server_list)
