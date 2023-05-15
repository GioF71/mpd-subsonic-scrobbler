from subsonic_connector.configuration import Configuration
from config import get_env_value, get_indexed_env_value
from config_key import ConfigKey

import dotenv
import libsonic


class ScrobblerConfig(Configuration):

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
            for param_name in ScrobblerConfig.__PARAM_LIST:
                self.__dict[param_name] = get_indexed_env_value(param_name, index) 

    #def __load_env_value(self, target_dict : dict[str, str], env_name : str):
    #    self.__dict[env_name] = get_env_value(env_name) 

    def getBaseUrl(self) -> str: return self.__dict[ScrobblerConfig.__KEY_BASE_URL]
    def getPort(self) -> int: return self.__dict[ScrobblerConfig.__KEY_PORT]
    def getUserName(self) -> str: return self.__dict[ScrobblerConfig.__KEY_USER]
    def getPassword(self) -> str: return self.__dict[ScrobblerConfig.__KEY_PASSWORD]
    def getApiVersion(self) -> str: return libsonic.API_VERSION
    def getAppName(self) -> str: return "upmpdcli"
