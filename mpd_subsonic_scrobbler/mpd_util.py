from context import Context
from context_key import ContextKey
from enum import Enum
from mpd_status_key import MPDStatusKey

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
    mpd_status : str = (status[MPDStatusKey.STATE.getKey()] 
        if status and MPDStatusKey.STATE.getKey() in status 
        else None)
    return mpd_status

def get_mpd_status(context : Context) -> dict[str, str]:
    client : mpd.MPDClient = mpd.MPDClient()
    client.connect(context.get_config().get_mpd_host(), int(context.get_config().get_mpd_port()))
    status : dict = client.status()
    context.set(ContextKey.MPD_STATUS, status)
    client.disconnect()
    return status

def get_mpd_current_song(context : Context) -> dict[str, str]:
    client : mpd.MPDClient = mpd.MPDClient()
    client.connect(context.get_config().get_mpd_host(), int(context.get_config().get_mpd_port()))
    current_song : dict[str, str] = client.currentsong()
    context.set(ContextKey.CURRENT_MPD_SONG, current_song)
    client.disconnect()
    return current_song

def get_mpd_current_song_artist(context : Context) -> str:
    return __get_mpd_current_song_property(context, MPDStatusKey.ARTIST.getKey())

def get_mpd_current_song_title(context : Context) -> str:
    return __get_mpd_current_song_property(context, MPDStatusKey.TITLE.getKey())

def get_mpd_current_song_file(context : Context) -> str:
    return __get_mpd_current_song_property(context, MPDStatusKey.FILE.getKey())

def get_mpd_current_song_time(context : Context) -> str:
    return __get_mpd_current_song_property(context, MPDStatusKey.TIME.getKey())

def __get_mpd_current_song_property(context : Context, property : str) -> str:
    current_song : dict[str, str] = context.get(ContextKey.CURRENT_MPD_SONG)
    return current_song[property] if current_song and property in current_song else None 

