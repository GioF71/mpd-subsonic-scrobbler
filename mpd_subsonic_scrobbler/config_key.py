from enum import Enum

class ConfigKey(Enum):

    SUBSONIC_BASE_URL = 0, "SUBSONIC_BASE_URL"
    SUBSONIC_PORT = 1, "SUBSONIC_PORT"
    SUBSONIC_USER = 2, "SUBSONIC_USER"
    SUBSONIC_PASSWORD = 3, "SUBSONIC_PASSWORD"
    SUBSONIC_PARAMETERS_FILE = 4, "SUBSONIC_PARAMETERS_FILE"
    
    MPD_HOST = 5, "MPD_HOST"
    MPD_PORT = 6, "MPD_PORT"

    SLEEP_TIME = 7, "SLEEP_TIME"
    MIN_COVERAGE = 8, "MIN_COVERATE"
    ENOUGH_PLAYBACK_SEC = 9, "ENOUGH_PLAYBACK_SEC"

    VERBOSE = 10, "VERBOSE"

    def __init__(self, num, element_key : str):
        self.num = num
        self.__key : str = element_key

    def getKey(self) -> str:
        return self.__key
