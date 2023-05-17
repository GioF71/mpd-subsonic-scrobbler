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

    __PARAM_LIST : list[str] = [__KEY_BASE_URL, __KEY_PORT, __KEY_USER, __KEY_PASSWORD]

    def __init__(self, index : int = 0):
        self.__dict = {}
        self.__subsonic_file : str = get_indexed_env_value(
            ConfigKey.SUBSONIC_PARAMETERS_FILE.getKey(), 
            index)
        if self.__subsonic_file:
            self.__dict = dotenv.dotenv_values(dotenv_path = self.__subsonic_file)
        else:
            param_name : str
            for param_name in SubsonicServerConfig.__PARAM_LIST:
                self.__dict[param_name] = get_indexed_env_value(param_name, index) 

    def getBaseUrl(self) -> str: return self.__dict[SubsonicServerConfig.__KEY_BASE_URL]
    def getPort(self) -> int: return self.__dict[SubsonicServerConfig.__KEY_PORT]
    def getUserName(self) -> str: return self.__dict[SubsonicServerConfig.__KEY_USER]
    def getPassword(self) -> str: return self.__dict[SubsonicServerConfig.__KEY_PASSWORD]
    def getApiVersion(self) -> str: return libsonic.API_VERSION
    def getAppName(self) -> str: return "upmpdcli"
