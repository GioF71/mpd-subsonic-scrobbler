from context import Context
from context_key import ContextKey
from enum import Enum

import mpd 

class State(Enum):

    PLAY = 0, "play"
    STOP = 1, "stop"

    def __init__(self, num, state : str):
        self.num = num
        self.__state : str = state

    def get(self) -> str:
        return self.__state


def get_mpd_state(context : Context) -> str:
    status : str = context.get(ContextKey.MPD_STATUS)
    mpd_status : str = status["state"] if status and "state" in status else None
    return mpd_status

def get_mpd_status(context : Context) -> dict[str, str]:
    client : mpd.MPDClient = mpd.MPDClient()
    client.connect(context.get(ContextKey.MPD_HOST), int(context.get(ContextKey.MPD_PORT)))
    status : dict = client.status()
    context.set(ContextKey.MPD_STATUS, status)
    client.disconnect()
    return status

def get_mpd_current_song(context : Context) -> dict[str, str]:
    client : mpd.MPDClient = mpd.MPDClient()
    client.connect(context.get(ContextKey.MPD_HOST), int(context.get(ContextKey.MPD_PORT)))
    current_song : dict[str, str] = client.currentsong()
    context.set(ContextKey.CURRENT_MPD_SONG, current_song)
    client.disconnect()
    return current_song

def get_mpd_current_song_artist(context : Context) -> str:
    return __get_mpd_current_song_property(context, "artist")

def get_mpd_current_song_title(context : Context) -> str:
    return __get_mpd_current_song_property(context, "title")

def get_mpd_current_song_file(context : Context) -> str:
    return __get_mpd_current_song_property(context, "file")

def get_mpd_current_song_time(context : Context) -> str:
    return __get_mpd_current_song_property(context, "time")

def get_mpd_current_song_file(context : Context) -> str:
    return __get_mpd_current_song_property(context, "file")

def __get_mpd_current_song_property(context : Context, property : str) -> str:
    current_song : dict[str, str] = context.get(ContextKey.CURRENT_MPD_SONG)
    return current_song[property] if current_song and property in current_song else None 

