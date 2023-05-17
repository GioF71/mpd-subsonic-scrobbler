from enum import Enum

class ContextKey(Enum):

    MPD_HOST = 0, "mpd_host"
    MPD_PORT = 1, "mpd_port"
    MPD_STATUS = 2, "mpd_status"
    MPD_LAST_EXCEPTION = 3, "mpd_last_exception"
    MPD_LAST_STATE = 4, "mpd_last_state"
    CURRENT_MPD_SONG = 10, "mpd_current_song"
    CURRENT_SUBSONIC_SONG_OBJECT = 30, "subsonic_song_object"
    CURRENT_SUBSONIC_TRACK_ID = 40, "subsonic_track_id"
    LAST_SCROBBLED_TRACK_ID = 50, "last_scrobbled_track_id"
    CURRENT_TRACK_HIT_COUNT = 60, "current_track_hit_count"
    CURRENT_TRACK_MIN_HIT_COUNT = 70, "current_track_min_hit_count"
    CURRENT_SUBSONIC_CONFIG = 80, "current_subsonic_config"

    def __init__(self, num, element_key : str):
        self.num = num
        self.__key : str = element_key

    def getKey(self) -> str:
        return self.__key
