from subsonic_server_config import SubsonicServerConfig
from context import Context
from mpd_util import get_mpd_current_song_file

from urllib.parse import urlparse
from urllib.parse import parse_qs

from subsonic_connector.connector import Connector
from subsonic_connector.response import Response
from subsonic_connector.song import Song
from subsonic_track_id import SubsonicTrackId
from libsonic.errors import DataNotFoundError

from urllib.error import URLError

import os
import song_cache


def __get_connector(subsonic_server_config: SubsonicServerConfig) -> Connector:
    return Connector(subsonic_server_config)


def get_song(
        current_config: SubsonicServerConfig,
        song_id: str) -> Song:
    response: Response[Song] = __get_connector(current_config).getSong(song_id)
    if response.isOk(): return response.getObj()
    raise Exception(f"Cannot get song for id {song_id}")


def scrobble(subsonic_server_config: SubsonicServerConfig, song_id: str) -> dict:
    return __get_connector(subsonic_server_config).scrobble(song_id)


def get_subsonic_track_id(
        context: Context,
        index: int,
        scrobbler_config_list: list[SubsonicServerConfig]) -> SubsonicTrackId:
    current_config: SubsonicServerConfig
    for current_config in scrobbler_config_list:
        id: str = __get_subsonic_track_id_for_config(
            context=context,
            index=index,
            subsonic_server_config=current_config)
        if id: return SubsonicTrackId(id, current_config)


def __get_subsonic_track_id_for_config(
        context: Context,
        index: int,
        subsonic_server_config: SubsonicServerConfig) -> str:
    song_file: str = get_mpd_current_song_file(context=context, index=index)
    parsed_url = urlparse(song_file)
    cmp_url: str = f'{parsed_url.scheme}://{parsed_url.hostname}'
    if cmp_url == subsonic_server_config.getBaseUrl() and parsed_url.port == int(subsonic_server_config.getPort()):
        url_username: str = parse_qs(parsed_url.query)['u'][0]
        username: str = subsonic_server_config.getUserName()
        if not url_username == username: return None
        parse_result = parse_qs(parsed_url.query)
        id: str = parse_result["id"][0] if "id" in parse_result else None
        return id
    else:
        # try upmpdcli trackid
        notset: bool = not subsonic_server_config.getUpmpdcliBaseUrl() and not subsonic_server_config.getUpmpdcliPort()
        match: bool = notset or (cmp_url == subsonic_server_config.getUpmpdcliBaseUrl() and
                                 parsed_url.port == int(subsonic_server_config.getUpmpdcliPort()))
        if match:
            path: str = parsed_url.path
            if path:
                splitted_path = os.path.split(path) if path else None
                if not splitted_path or not len(splitted_path) == 2: return None
                left: str = splitted_path[0]
                if not left == "/subsonic/track/version/1/trackId": return False
                right: str = splitted_path[1]
                # must check if track belongs to server in this case
                song: Song = None
                try:
                    song = song_cache.get_song(context=context, current_config=subsonic_server_config, song_id=right)
                except DataNotFoundError:
                    # Song does not belong to current server
                    pass
                except URLError:
                    # server is probably unavailable
                    pass
                except Exception as anyExc:
                    print("__get_subsonic_track_id_for_config failed on "
                          f"[{subsonic_server_config.get_friendly_name()}] "
                          f"[{type(anyExc)}] [{anyExc}]")
                return right if song else None
