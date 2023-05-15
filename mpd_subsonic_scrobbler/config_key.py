from enum import Enum

class ConfigKey(Enum):

    SUBSONIC_BASE_URL = 0, "SUBSONIC_BASE_URL"
    SUBSONIC_PORT = 1, "SUBSONIC_PORT"
    SUBSONIC_USER = 2, "SUBSONIC_USER"
    SUBSONIC_PASSWORD = 3, "SUBSONIC_PASSWORD"
    SUBSONIC_PARAMETERS_FILE = 4, "SUBSONIC_PARAMETERS_FILE"

    def __init__(self, num, element_key : str):
        self.num = num
        self.__key : str = element_key

    def getKey(self) -> str:
        return self.__key
