from subsonic_server_config import SubsonicServerConfig
from context import Context
from mpd_util import get_mpd_current_song_file

from urllib.parse import urlparse
from urllib.parse import parse_qs

from subsonic_connector.connector import Connector

def get_connector(subsonic_server_config : SubsonicServerConfig) -> Connector:
    return Connector(subsonic_server_config)

def scrobble(subsonic_server_config : SubsonicServerConfig, song_id : str) -> dict:
    return get_connector(subsonic_server_config).scrobble(song_id)

def get_subsonic_track_id(
        context : Context, 
        scrobbler_config_list : list[SubsonicServerConfig]) -> str:
    current_config : SubsonicServerConfig
    for current_config in scrobbler_config_list:
        id : str = __get_subsonic_track_id_for_config(context, current_config)
        if id: return id, current_config

def __get_subsonic_track_id_for_config(
        context : Context, 
        subsonic_server_config : SubsonicServerConfig) -> str:
    song_file : str = get_mpd_current_song_file(context)
    parsed_url = urlparse(song_file)
    cmp_url : str = f'{parsed_url.scheme}://{parsed_url.hostname}'
    if not cmp_url == subsonic_server_config.getBaseUrl(): return None
    if not parsed_url.port == int(subsonic_server_config.getPort()): return None
    url_username : str = parse_qs(parsed_url.query)['u'][0]
    username : str = subsonic_server_config.getUserName()
    if not url_username == username: return None
    parse_result = parse_qs(parsed_url.query)
    id : str = parse_result["id"][0] if "id" in parse_result else None
    return id
