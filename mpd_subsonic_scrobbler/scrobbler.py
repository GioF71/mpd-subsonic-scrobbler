import os
import time

import mpd 
from urllib.parse import urlparse
from urllib.parse import parse_qs

from config import get_env_value

from subsonic_connector.connector import Connector
from subsonic_connector.response import Response
from subsonic_connector.song import Song

from scrobbler_config import ScrobblerConfig

from context_key import ContextKey
from context import Context

sleep_time_msec : str = get_env_value("SLEEP_TIME", "1000")
print(f"sleep_time_msec [{sleep_time_msec}]")

sleep_time_sec : float = float(sleep_time_msec) / 1000.0
print(f"sleep_time_sec {sleep_time_sec}")

min_coverage : int = int(get_env_value("MIN_COVERAGE", "50"))
verbose : bool = True if int(get_env_value("VERBOSE", "0")) == 1 else False
print(f"verbose [{verbose}]")

mpd_host : str = get_env_value("MPD_HOST", "localhost")
mpd_port : str = get_env_value("MPD_PORT", "6600")

print(f"MPD_HOST=[{mpd_host}]")
print(f"MPD_PORT=[{mpd_port}]")

scrobbler_config : ScrobblerConfig = ScrobblerConfig()

server_url : str = scrobbler_config.getBaseUrl()
server_port : str = scrobbler_config.getPort()

print(f"server_url=[{scrobbler_config.getBaseUrl()}]")
print(f"server_port=[{scrobbler_config.getPort()}]")

def get_mpd_status(context : Context) -> dict[str, str]:
    client : mpd.MPDClient = mpd.MPDClient()
    client.connect(mpd_host, int(mpd_port))
    status : dict = client.status()
    context.set(ContextKey.MPD_STATUS, status)
    client.disconnect()
    return status

def is_mpd_playing(context : Context) -> bool:
    status : str = context.get(ContextKey.MPD_STATUS)
    mpd_status : str = status["state"] if status and "state" in status else None
    return mpd_status == "play"

def get_mpd_current_song(context : Context) -> dict[str, str]:
    client : mpd.MPDClient = mpd.MPDClient()
    client.connect(mpd_host, int(mpd_port))
    current_song : dict[str, str] = client.currentsong()
    context.set(ContextKey.CURRENT_MPD_SONG, current_song)
    client.disconnect()
    return current_song

def __get_mpd_current_song_property(context : Context, property : str) -> str:
    current_song : dict[str, str] = context.get(ContextKey.CURRENT_MPD_SONG)
    return current_song[property] if current_song and property in current_song else None 

def get_mpd_current_song_artist(context : Context) -> str:
    return __get_mpd_current_song_property(context, "artist")

def get_mpd_current_song_title(context : Context) -> str:
    return __get_mpd_current_song_property(context, "title")

def get_mpd_current_song_file(context : Context) -> str:
    return __get_mpd_current_song_property(context, "file")

def get_mpd_current_song_time(context : Context) -> str:
    return __get_mpd_current_song_property(context, "time")

def get_subsonic_track_id(context : Context) -> str:
    song_file : str = get_mpd_current_song_file(context)
    parsed_url = urlparse(song_file)
    cmp_url : str = f'{parsed_url.scheme}://{parsed_url.hostname}'
    if not cmp_url == scrobbler_config.getBaseUrl(): return False
    if not parsed_url.port == int(scrobbler_config.getPort()): return False
    url_username : str = parse_qs(parsed_url.query)['u'][0]
    username : str = scrobbler_config.getUserName()
    if not url_username == username: return False
    parse_result = parse_qs(parsed_url.query)
    id : str = parse_result["id"][0] if "id" in parse_result else None
    return id

def connector() -> Connector:
    return Connector(scrobbler_config)

def scrobble(song_id : str) -> dict:
    return connector().scrobble(song_id)

def execute_scrobbling(song : Song) -> dict:
    print(f"About to scrobble subsonic TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}] now ...")
    scrobble_result : dict = scrobble(song.getId())
    print(f"Scrobbled subsonic TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}]")
    return scrobble_result

def print_current_song(context : Context):
    song_artist : str = get_mpd_current_song_artist(context)
    song_title : str = get_mpd_current_song_title(context)
    song_time : str = context.get(ContextKey.MPD_STATUS)["time"]
    if verbose: print(f"Playing TrackId:[{context.get(ContextKey.CURRENT_SUBSONIC_TRACK_ID)}] Artist:[{song_artist}] Title:[{song_title}] Time:[{song_time}]")

def iteration(context : Context):
    get_mpd_current_song(context)
    print_current_song(context)
    song_file : str = get_mpd_current_song_file(context)
    subsonic_track_id : str = get_subsonic_track_id(context) if song_file else None
    if subsonic_track_id:
        same_song : bool = True
        song : Song = context.get(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT)
        old_song : Song = None
        if not song or not song.getId() == subsonic_track_id:
            old_song = song
            same_song = False
            print(f"Song changed, loading track {subsonic_track_id} from subsonic server ...")
            response : Response[Song] = connector().getSong(subsonic_track_id)
            if response.isOk(): context.set(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT, response.getObj())
            song = response.getObj()
            print(f"TrackId:[{subsonic_track_id}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}] retrieved from subsonic server.")
        current_track_duration : float = float(song.getDuration())
        if not same_song:
            print(f"New subsonic track {subsonic_track_id} playing")
            last_scrobbled_track_id : str = context.get(ContextKey.LAST_SCROBBLED_TRACK_ID)
            if (old_song) and (not last_scrobbled_track_id == old_song.getId()):
                print(f"Last song TrackId:[{old_song.getId()}] Artist:[{old_song.getArtist()}] Title:[{old_song.getTitle()}] was not scrobbled.")
            # update current_subsonic_track_id and reset counter
            context.set(ContextKey.CURRENT_SUBSONIC_TRACK_ID, song.getId())
            current_track_hit_count : int = 1
            context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, current_track_hit_count)
            min_hit_count : int = int(((float(min_coverage) / 100.0) * current_track_duration) / sleep_time_sec)
            context.set(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT, min_hit_count)
        last_scrobbled_track_id : str = context.get(ContextKey.LAST_SCROBBLED_TRACK_ID)
        if not last_scrobbled_track_id == subsonic_track_id:
            current_track_hit_count : int = context.get(ContextKey.CURRENT_TRACK_HIT_COUNT)
            current_track_hit_count += 1
            context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, current_track_hit_count)
            curr_min_hit_count : int = context.get(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT)
            if verbose:
                print(f"Current song hit_count {current_track_hit_count} current_track_min_hit_count {curr_min_hit_count} duration {current_track_duration}")
            if current_track_hit_count >= curr_min_hit_count and not last_scrobbled_track_id == subsonic_track_id:
                execute_scrobbling(song)
                context.set(ContextKey.LAST_SCROBBLED_TRACK_ID, song.getId())   
                context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, 0)   

context : Context = Context()

while True:

    
    mpd_playing : bool = False
    try:
        status : dict = get_mpd_status(context)
        mpd_playing = is_mpd_playing(context)
        context.delete(ContextKey.MPD_LAST_EXCEPTION)
    except Exception as e:
        last_exception = context.get(ContextKey.MPD_LAST_EXCEPTION)
        same_exception : bool = last_exception and (last_exception[0] == e.args[0] and last_exception[1] == e.args[1])
        if not same_exception:
            e_tuple = (e.args[0], e.args[1])
            context.set(ContextKey.MPD_LAST_EXCEPTION, e_tuple)
        if not same_exception:
            print(f"Cannot get mpd state [{e}]")

    if mpd_playing:
        try:
            iteration(context)
        except Exception as e:
            print(f"Iteration failed [{e}]")

    time.sleep(sleep_time_sec)
    