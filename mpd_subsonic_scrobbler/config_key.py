from enum import Enum

class ConfigKey(Enum):

    SUBSONIC_BASE_URL = 0, "SUBSONIC_BASE_URL"
    SUBSONIC_PORT = 1, "SUBSONIC_PORT"
    SUBSONIC_USER = 2, "SUBSONIC_USER"
    SUBSONIC_PASSWORD = 3, "SUBSONIC_PASSWORD"
    SUBSONIC_CREDENTIALS = 4, "SUBSONIC_CREDENTIALS"
    SUBSONIC_PARAMETERS_FILE = 5, "SUBSONIC_PARAMETERS_FILE"
    
    MPD_HOST = 6, "MPD_HOST", "localhost"
    MPD_PORT = 7, "MPD_PORT", "6600"

    SLEEP_TIME = 8, "SLEEP_TIME", "1000"
    MIN_COVERAGE = 9, "MIN_COVERAGE", "50"
    ENOUGH_PLAYBACK_SEC = 10, "ENOUGH_PLAYBACK_SEC", "240"

    REDACT_CREDENTIALS = 11, "REDACT_CREDENTIALS", "1"

    VERBOSE = 10, "VERBOSE", "0"

    def __init__(self, num, element_key : str, default_value : str = None):
        self.num = num
        self.__key : str = element_key
        self.__default_value : str = default_value

    def getKey(self) -> str:
        return self.__key

    def get_default_value(self) -> str | None:
        return self.__default_value