from config_key import ConfigKey
from subsonic_server_config import SubsonicServerConfig
from config_util import get_indexed_env_value
from subsonic_connector.song import Song
from context_key import ContextKey

from typing import Callable

def clean_playback_state(context_remover : Callable[[ContextKey], any]):
    context_remover(ContextKey.CURRENT_MPD_SONG)
    context_remover(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT)
    context_remover(ContextKey.CURRENT_SUBSONIC_TRACK_ID)
    context_remover(ContextKey.CURRENT_TRACK_HIT_COUNT)
    context_remover(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT)
    context_remover(ContextKey.CURRENT_TRACK_PLAYBACK_START)
    context_remover(ContextKey.LAST_SCROBBLED_TRACK_ID)

def was_not_scrobbled(song : Song):
    print(f"Song TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}] was not scrobbled.")    

def get_subsonic_server_config_list() -> list[SubsonicServerConfig]:
    c_list : list[SubsonicServerConfig] = list()
    config_index : int
    for config_index in range(10):
        config_file_name : str = get_indexed_env_value(ConfigKey.SUBSONIC_PARAMETERS_FILE.get_key(), config_index)
        server_url : str = get_indexed_env_value(ConfigKey.SUBSONIC_BASE_URL.get_key(), config_index)
        if config_file_name or server_url:
            current_config : SubsonicServerConfig = SubsonicServerConfig(config_index)
            c_list.append(current_config)
    return c_list

    
