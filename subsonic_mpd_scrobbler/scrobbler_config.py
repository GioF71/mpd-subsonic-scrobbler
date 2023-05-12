from subsonic_connector.configuration import Configuration
from config import get_env_value
import dotenv
import libsonic

class ScrobblerConfig(Configuration):

    __KEY_BASE_URL : str = "SUBSONIC_BASE_URL"
    __KEY_PORT : str = "SUBSONIC_PORT"
    __KEY_USER : str = "SUBSONIC_USER"
    __KEY_PASSWORD : str = "SUBSONIC_PASSWORD"

    __PARAM_LIST : list[str] = [__KEY_BASE_URL, __KEY_PORT, __KEY_USER, __KEY_PASSWORD]

    def __init__(self):
        self.__dict = {}
        self.__subsonic_file : str = get_env_value("SUBSONIC_PARAMETERS_FILE")
        if self.__subsonic_file:
            self.__dict = dotenv.dotenv_values(dotenv_path = self.__subsonic_file)
        else:
            param_name : str
            for param_name in ScrobblerConfig.__PARAM_LIST:
                self.__dict[param_name] = get_env_value(param_name) 

    def __load_env_value(self, target_dict : dict[str, str], env_name : str):
        self.__dict[env_name] = get_env_value(env_name) 

    def getBaseUrl(self) -> str: return self.__dict[ScrobblerConfig.__KEY_BASE_URL]
    def getPort(self) -> int: return self.__dict[ScrobblerConfig.__KEY_PORT]
    def getUserName(self) -> str: return self.__dict[ScrobblerConfig.__KEY_USER]
    def getPassword(self) -> str: return self.__dict[ScrobblerConfig.__KEY_PASSWORD]
    def getApiVersion(self) -> str: return libsonic.API_VERSION
    def getAppName(self) -> str: return "upmpdcli"
