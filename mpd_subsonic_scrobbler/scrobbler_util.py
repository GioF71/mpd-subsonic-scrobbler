from config_key import ConfigKey
from subsonic_server_config import SubsonicServerConfig
from mpd_instance_config import MpdInstanceConfig
from config_util import get_indexed_env_value
from subsonic_connector.song import Song
from context_key import ContextKey

from typing import Callable

def clean_playback_state(context_remover : Callable[[ContextKey], any], index : int):
    context_remover(context_key = ContextKey.CURRENT_MPD_SONG, index = index)
    context_remover(context_key = ContextKey.CURRENT_SUBSONIC_SONG_OBJECT, index = index)
    context_remover(context_key = ContextKey.CURRENT_SUBSONIC_TRACK_ID, index = index)
    context_remover(context_key = ContextKey.CURRENT_TRACK_HIT_COUNT, index = index)
    context_remover(context_key = ContextKey.CURRENT_TRACK_MIN_HIT_COUNT, index = index)
    context_remover(context_key = ContextKey.CURRENT_TRACK_PLAYBACK_START, index = index)
    context_remover(context_key = ContextKey.LAST_SCROBBLED_TRACK_ID, index = index)

def was_not_scrobbled(song : Song):
    print(f"Song TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}] was not scrobbled.")    

def get_subsonic_server_config_list(max_servers : int) -> list[SubsonicServerConfig]:
    c_list : list[SubsonicServerConfig] = list()
    config_index : int
    for config_index in range(max_servers):
        config_file_name : str = get_indexed_env_value(ConfigKey.SUBSONIC_PARAMETERS_FILE.get_key(), config_index)
        server_url : str = get_indexed_env_value(ConfigKey.SUBSONIC_BASE_URL.get_key(), config_index)
        if config_file_name or server_url:
            current_config : SubsonicServerConfig = SubsonicServerConfig(config_index)
            c_list.append(current_config)
    return c_list

def get_mpd_instances_list(max_instances : int) -> list[MpdInstanceConfig]:
    c_list : list[MpdInstanceConfig] = list()
    config_index : int
    for config_index in range(max_instances):
        mpd_host : str = get_indexed_env_value(ConfigKey.MPD_HOST.get_key(), config_index)
        if mpd_host:
            current_config : MpdInstanceConfig = MpdInstanceConfig(config_index)
            c_list.append(current_config)
    return c_list

    
