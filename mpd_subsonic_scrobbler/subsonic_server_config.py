from subsonic_connector.configuration import Configuration
from config_util import get_indexed_env_value

from config_key import ConfigKey

import dotenv
import libsonic

class SubsonicServerConfig(Configuration):

    __KEY_BASE_URL : str = ConfigKey.SUBSONIC_BASE_URL.getKey()
    __KEY_PORT : str = ConfigKey.SUBSONIC_PORT.getKey()
    __KEY_USER : str = ConfigKey.SUBSONIC_USER.getKey()
    __KEY_PASSWORD : str = ConfigKey.SUBSONIC_PASSWORD.getKey()
    __KEY_CREDENTIALS : str = ConfigKey.SUBSONIC_CREDENTIALS.getKey()

    __PARAM_LIST : list[str] = [__KEY_BASE_URL, __KEY_PORT, __KEY_USER, __KEY_PASSWORD, __KEY_CREDENTIALS]

    def __init__(self, index : int = 0):
        self.__dict : dict[str, str] = {}
        self.__subsonic_file : str = get_indexed_env_value(
            ConfigKey.SUBSONIC_PARAMETERS_FILE.getKey(), 
            index)
        if self.__subsonic_file:
            self.__dict = dotenv.dotenv_values(dotenv_path = self.__subsonic_file)
            self.__check_conflict(index, self.__dict)
            if SubsonicServerConfig.__KEY_CREDENTIALS in self.__dict:
                # replace with contents of file
                cred_dict : dict[str, str] = dotenv.dotenv_values(dotenv_path = self.__dict[SubsonicServerConfig.__KEY_CREDENTIALS])
                # check has credentials
                self.__check_credentials(index, cred_dict)
                del self.__dict[SubsonicServerConfig.__KEY_CREDENTIALS]
                self.__dict[SubsonicServerConfig.__KEY_USER] = cred_dict[SubsonicServerConfig.__KEY_USER]
                self.__dict[SubsonicServerConfig.__KEY_PASSWORD] = cred_dict[SubsonicServerConfig.__KEY_PASSWORD]
        else:
            param_name : str
            for param_name in SubsonicServerConfig.__PARAM_LIST:
                curr_value : str = get_indexed_env_value(param_name, index)
                if curr_value:
                    self.__dict[param_name] = curr_value
            self.__check_conflict(index, self.__dict)
            if SubsonicServerConfig.__KEY_CREDENTIALS in self.__dict:
                # replace with contents of file
                cred_dict : dict[str, str] = dotenv.dotenv_values(dotenv_path = self.__dict[SubsonicServerConfig.__KEY_CREDENTIALS])
                # check has credentials
                self.__check_credentials(index, cred_dict)
                del self.__dict[SubsonicServerConfig.__KEY_CREDENTIALS]
                self.__dict[SubsonicServerConfig.__KEY_USER] = cred_dict[SubsonicServerConfig.__KEY_USER]
                self.__dict[SubsonicServerConfig.__KEY_PASSWORD] = cred_dict[SubsonicServerConfig.__KEY_PASSWORD]
        self.__check(index, self.__dict)

    def __check(self, index : int, conf_dict : dict[str, str]):
        self.__check_conflict(index, conf_dict)
        self.__check_missing(index, conf_dict)
        self.__check_complete(index, conf_dict)

    def __check_credentials(self, index : int, conf_dict : dict[str, str]):
        if not (SubsonicServerConfig.__KEY_USER in conf_dict and 
            SubsonicServerConfig.__KEY_PASSWORD in conf_dict):
            raise Exception(f"Credentials not set for index {index}")

    def __check_conflict(self, index : int, conf_dict : dict[str, str]):
        if (SubsonicServerConfig.__KEY_CREDENTIALS in conf_dict and 
            SubsonicServerConfig.__KEY_USER in conf_dict and 
            SubsonicServerConfig.__KEY_PASSWORD in conf_dict):
            raise Exception(f"Credentials conflict for index {index}")

    def __check_complete(self, index : int, conf_dict : dict[str, str]):
        if not (SubsonicServerConfig.__KEY_BASE_URL in conf_dict and 
            SubsonicServerConfig.__KEY_PORT in conf_dict and 
            SubsonicServerConfig.__KEY_USER in conf_dict and 
            SubsonicServerConfig.__KEY_PASSWORD in conf_dict):
            raise Exception(f"Incomplete settings for index {index}")

    def __check_missing(self, index : int, conf_dict : dict[str, str]):
        if not (SubsonicServerConfig.__KEY_USER in conf_dict and 
            SubsonicServerConfig.__KEY_PASSWORD in conf_dict):
            raise Exception(f"Credentials missing for index {index}")

    def getBaseUrl(self) -> str: return self.__dict[SubsonicServerConfig.__KEY_BASE_URL]
    def getPort(self) -> int: return self.__dict[SubsonicServerConfig.__KEY_PORT]
    def getUserName(self) -> str: return self.__dict[SubsonicServerConfig.__KEY_USER]
    def getPassword(self) -> str: return self.__dict[SubsonicServerConfig.__KEY_PASSWORD]
    def getApiVersion(self) -> str: return libsonic.API_VERSION
    def getAppName(self) -> str: return "mpd-subsonic-scrobbler"
