from subsonic_connector.configuration import Configuration
from config_util import get_indexed_env_value

from config_key import ConfigKey

import dotenv
import libsonic

class SubsonicServerConfig(Configuration):

    __PARAM_LIST : list[str] = [
        ConfigKey.SUBSONIC_FRIENDLY_NAME.get_key(), 
        ConfigKey.SUBSONIC_BASE_URL.get_key(), 
        ConfigKey.SUBSONIC_PORT.get_key(), 
        ConfigKey.SUBSONIC_USER.get_key(), 
        ConfigKey.SUBSONIC_PASSWORD.get_key(), 
        ConfigKey.SUBSONIC_CREDENTIALS.get_key(),
        ConfigKey.SUBSONIC_UPMPDCLI_BASE_URL.get_key(),
        ConfigKey.SUBSONIC_UPMPDCLI_PORT.get_key()]

    def __init__(self, index : int = 0):
        self.__dict : dict[str, str] = {}
        self.__subsonic_file : str = get_indexed_env_value(
            ConfigKey.SUBSONIC_PARAMETERS_FILE.get_key(), 
            index)
        if self.__subsonic_file:
            self.__dict = dotenv.dotenv_values(dotenv_path = self.__subsonic_file)
            self.__check_conflict(index, self.__dict)
            if ConfigKey.SUBSONIC_CREDENTIALS.get_key() in self.__dict:
                # replace with contents of file
                cred_dict : dict[str, str] = dotenv.dotenv_values(dotenv_path = self.__dict[ConfigKey.SUBSONIC_CREDENTIALS.get_key()])
                # check has credentials
                self.__check_credentials(index, cred_dict)
                del self.__dict[ConfigKey.SUBSONIC_CREDENTIALS.get_key()]
                self.__dict[ConfigKey.SUBSONIC_USER.get_key()] = cred_dict[ConfigKey.SUBSONIC_USER.get_key()]
                self.__dict[ConfigKey.SUBSONIC_PASSWORD.get_key()] = cred_dict[ConfigKey.SUBSONIC_PASSWORD.get_key()]
        else:
            param_name : str
            for param_name in SubsonicServerConfig.__PARAM_LIST:
                curr_value : str = get_indexed_env_value(param_name, index)
                if curr_value:
                    self.__dict[param_name] = curr_value
            self.__check_conflict(index, self.__dict)
            if ConfigKey.SUBSONIC_CREDENTIALS.get_key() in self.__dict:
                # replace with contents of file
                cred_dict : dict[str, str] = dotenv.dotenv_values(dotenv_path = self.__dict[ConfigKey.SUBSONIC_CREDENTIALS.get_key()])
                # check has credentials
                self.__check_credentials(index, cred_dict)
                del self.__dict[ConfigKey.SUBSONIC_CREDENTIALS.get_key()]
                self.__dict[ConfigKey.SUBSONIC_USER.get_key()] = cred_dict[ConfigKey.SUBSONIC_USER.get_key()]
                self.__dict[ConfigKey.SUBSONIC_PASSWORD.get_key()] = cred_dict[ConfigKey.SUBSONIC_PASSWORD.get_key()]
        self.__check(index, self.__dict)

    def __check(self, index : int, conf_dict : dict[str, str]):
        self.__check_conflict(index, conf_dict)
        self.__check_missing(index, conf_dict)
        self.__check_complete(index, conf_dict)

    def __check_credentials(self, index : int, conf_dict : dict[str, str]):
        if not (ConfigKey.SUBSONIC_USER.get_key() in conf_dict and 
            ConfigKey.SUBSONIC_PASSWORD.get_key() in conf_dict):
            raise Exception(f"Credentials not set for index {index}")

    def __check_conflict(self, index : int, conf_dict : dict[str, str]):
        if (ConfigKey.SUBSONIC_CREDENTIALS.get_key() in conf_dict and 
            ConfigKey.SUBSONIC_USER.get_key() in conf_dict and 
            ConfigKey.SUBSONIC_PASSWORD.get_key() in conf_dict):
            raise Exception(f"Credentials conflict for index {index}")

    def __check_complete(self, index : int, conf_dict : dict[str, str]):
        if not (ConfigKey.SUBSONIC_BASE_URL.get_key() in conf_dict and 
            ConfigKey.SUBSONIC_PORT.get_key() in conf_dict and 
            ConfigKey.SUBSONIC_USER.get_key() in conf_dict and 
            ConfigKey.SUBSONIC_PASSWORD.get_key() in conf_dict):
            raise Exception(f"Incomplete settings for index {index}")

    def __check_missing(self, index : int, conf_dict : dict[str, str]):
        if not (ConfigKey.SUBSONIC_USER.get_key() in conf_dict and 
            ConfigKey.SUBSONIC_PASSWORD.get_key() in conf_dict):
            raise Exception(f"Credentials missing for index {index}")

    def get_friendly_name(self) -> str:
        if ConfigKey.SUBSONIC_FRIENDLY_NAME.get_key() in self.__dict: return self.__dict[ConfigKey.SUBSONIC_FRIENDLY_NAME.get_key()]
        return f"Server[{self.getBaseUrl()}:{self.getPort()}]"

    def __ifin_else(self, config_key : ConfigKey, default_value : any = None) -> any:
        return self.__dict[config_key.get_key()] if config_key.get_key() in self.__dict else default_value

    def getBaseUrl(self) -> str: return self.__dict[ConfigKey.SUBSONIC_BASE_URL.get_key()]
    def getPort(self) -> str: return self.__dict[ConfigKey.SUBSONIC_PORT.get_key()]
    def getUserName(self) -> str: return self.__dict[ConfigKey.SUBSONIC_USER.get_key()]
    def getPassword(self) -> str: return self.__dict[ConfigKey.SUBSONIC_PASSWORD.get_key()]
    def getUpmpdcliBaseUrl(self) -> str: return self.__ifin_else(ConfigKey.SUBSONIC_UPMPDCLI_BASE_URL)
    def getUpmpdcliPort(self) -> str: return self.__ifin_else(ConfigKey.SUBSONIC_UPMPDCLI_PORT)
    def getApiVersion(self) -> str: return libsonic.API_VERSION
    def getAppName(self) -> str: return "mpd-subsonic-scrobbler"
