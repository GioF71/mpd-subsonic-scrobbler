from enum import Enum

class ConfigKey(Enum):

    SUBSONIC_FRIENDLY_NAME = 101, "SUBSONIC_FRIENDLY_NAME", ""
    SUBSONIC_BASE_URL = 102, "SUBSONIC_BASE_URL"
    SUBSONIC_PORT = 103, "SUBSONIC_PORT"
    SUBSONIC_USER = 104, "SUBSONIC_USER"
    SUBSONIC_PASSWORD = 105, "SUBSONIC_PASSWORD"
    SUBSONIC_CREDENTIALS = 106, "SUBSONIC_CREDENTIALS"
    SUBSONIC_PARAMETERS_FILE = 107, "SUBSONIC_PARAMETERS_FILE"
    
    MPD_FRIENDLY_NAME = 201, "MPD_FRIENDLY_NAME", ""
    MPD_HOST = 202, "MPD_HOST", "localhost"
    MPD_PORT = 203, "MPD_PORT", "6600"

    SLEEP_TIME = 301, "SLEEP_TIME", "1000"
    MIN_COVERAGE = 302, "MIN_COVERAGE", "50"
    ENOUGH_PLAYBACK_SEC = 303, "ENOUGH_PLAYBACK_SEC", "240"

    REDACT_CREDENTIALS = 401, "REDACT_CREDENTIALS", "1"
    VERBOSE = 402, "VERBOSE", "0"
    MAX_SUBSONIC_SERVERS = 403, "MAX_SUBSONIC_SERVERS", "10"
    MAX_MPD_INSTANCES = 404, "MAX_MPD_INSTANCES", "10"

    MPD_CLIENT_TIMEOUT_SEC = 501, "MPD_CLIENT_TIMEOUT_SEC", "0.05"
    ITERATION_DURATION_THRESHOLD_PERCENT = 502, "ITERATION_DURATION_THRESHOLD_PERCENT", "50"

    def __init__(self, num, element_key : str, default_value : str = None):
        self.num = num
        self.__key : str = element_key
        self.__default_value : str = default_value

    def get_key(self) -> str:
        return self.__key

    def get_default_value(self) -> str | None:
        return self.__default_value