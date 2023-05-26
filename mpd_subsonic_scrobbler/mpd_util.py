from context import Context
from context_key import ContextKey
from enum import Enum
from mpd_status_key import MPDStatusKey
from mpd_instance_config import MpdInstanceConfig
from scrobbler_config import ScrobblerConfig

import mpd 

class State(Enum):

    PLAY = 0, "play"
    STOP = 1, "stop"

    def __init__(self, num, state : str):
        self.num = num
        self.__state : str = state

    def get(self) -> str:
        return self.__state

def get_mpd_state(context : Context, mpd_index : int = 0) -> str:
    status : str = context.get(context_key = ContextKey.MPD_STATUS, index = mpd_index)
    mpd_status : str = (status[MPDStatusKey.STATE.get_key()] 
        if status and MPDStatusKey.STATE.get_key() in status 
        else None)
    return mpd_status

def __get_connected_client(context : Context, mpd_index : int = 0) -> mpd.MPDClient:
    config : ScrobblerConfig = context.get_config()
    mpd_list : list[MpdInstanceConfig] = config.get_mpd_list()
    client : mpd.MPDClient = mpd.MPDClient()
    timeout : float = config.get_mpd_client_timeout_sec()
    if timeout: client.timeout = config.get_mpd_client_timeout_sec()
    mpd_host : str = mpd_list[mpd_index].get_mpd_host()
    mpd_port : int = mpd_list[mpd_index].get_mpd_port()
    client.connect(mpd_host, mpd_port)
    return client

def get_mpd_status(context : Context, mpd_index : int = 0) -> dict[str, str]:
    client : mpd.MPDClient = __get_connected_client(context = context, mpd_index = mpd_index)
    status : dict = client.status()
    context.set(context_key = ContextKey.MPD_STATUS, index = mpd_index, context_value = status)
    current_song : dict[str, str] = client.currentsong()
    context.set(context_key = ContextKey.CURRENT_MPD_SONG, index = mpd_index, context_value = current_song)
    client.disconnect()
    return status

def get_mpd_current_song_artist(context : Context, index : int) -> str:
    return __get_mpd_current_song_property(context = context, index = index, property = MPDStatusKey.ARTIST.get_key())

def get_mpd_current_song_title(context : Context, index : int) -> str:
    return __get_mpd_current_song_property(context = context, index = index, property = MPDStatusKey.TITLE.get_key())

def get_mpd_current_song_file(context : Context, index : int) -> str:
    return __get_mpd_current_song_property(context = context, index = index, property = MPDStatusKey.FILE.get_key())

def get_mpd_current_song_time(context : Context, index : int) -> str:
    return __get_mpd_current_song_property(context = context, index = index, property = MPDStatusKey.TIME.get_key())

def __get_mpd_current_song_property(context : Context, index : int, property : str) -> str:
    current_song : dict[str, str] = context.get(context_key = ContextKey.CURRENT_MPD_SONG, index = index)
    return current_song[property] if current_song and property in current_song else None 

