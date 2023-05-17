import time

import mpd_util
import subsonic_util
import config

from subsonic_connector.response import Response
from subsonic_connector.song import Song

from subsonic_server_config import SubsonicServerConfig

from config_key import ConfigKey
from context_key import ContextKey
from context import Context

sleep_time_msec : str = config.get_env_value("SLEEP_TIME", "1000")
print(f"SLEEP_TIME: [{sleep_time_msec}] msec")

sleep_time_sec : float = float(sleep_time_msec) / 1000.0

min_coverage : int = int(config.get_env_value("MIN_COVERAGE", "50"))
print(f"MIN_COVERAGE: [{min_coverage}%]")

enough_playback_sec : int = int(config.get_env_value("ENOUGH_PLAYBACK_SEC", "240"))
print(f"ENOUGH_PLAYBACK_SEC: [{enough_playback_sec} sec]")

verbose : bool = True if int(config.get_env_value("VERBOSE", "0")) == 1 else False
print(f"VERBOSE: [{verbose}]")

mpd_host : str = config.get_env_value(ConfigKey.MPD_HOST.getKey(), "localhost")
mpd_port : str = config.get_env_value(ConfigKey.MPD_PORT.getKey(), "6600")

print(f"MPD_HOST: [{mpd_host}]")
print(f"MPD_PORT: [{mpd_port}]")

def get_subsonic_server_config_list() -> list[SubsonicServerConfig]:
    c_list : list[SubsonicServerConfig] = list()
    config_index : int
    for config_index in range(10):
        config_file_name : str = config.get_indexed_env_value(ConfigKey.SUBSONIC_PARAMETERS_FILE.getKey(), config_index)
        server_url : str = config.get_indexed_env_value(ConfigKey.SUBSONIC_BASE_URL.getKey(), config_index)
        if config_file_name or server_url:
            current_config : SubsonicServerConfig = SubsonicServerConfig(config_index)
            c_list.append(current_config)
    return c_list

def show_subsonic_servers(scrobbler_config_list : list[SubsonicServerConfig]):
    current : SubsonicServerConfig
    cnt : int = 0
    for current in scrobbler_config_list:
        server_url : str = current.getBaseUrl()
        server_port : str = current.getPort()
        print(f"server_url[{cnt}]=[{server_url}]")
        print(f"server_port[{cnt}]==[{server_port}]")
        cnt += 1
    
def execute_scrobbling(subsonic_server_config : SubsonicServerConfig, song : Song) -> dict:
    print(f"About to scrobble subsonic TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}] now ...")
    scrobble_result : dict = subsonic_util.scrobble(subsonic_server_config, song.getId())
    print(f"Scrobbled subsonic TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}]")
    return scrobble_result

def print_current_song(context : Context):
    song_artist : str = mpd_util.get_mpd_current_song_artist(context)
    song_title : str = mpd_util.get_mpd_current_song_title(context)
    song_time : str = context.get(ContextKey.MPD_STATUS)["time"]
    if verbose: print(f"Playing TrackId:[{context.get(ContextKey.CURRENT_SUBSONIC_TRACK_ID)}] Artist:[{song_artist}] Title:[{song_title}] Time:[{song_time}]")

def iteration(context : Context):
    mpd_util.get_mpd_current_song(context)
    print_current_song(context)
    song_file : str = mpd_util.get_mpd_current_song_file(context)
    current_config : SubsonicServerConfig
    subsonic_track_id : str
    subsonic_track_id, current_config = (subsonic_util.get_subsonic_track_id(context, scrobbler_config_list) 
        if song_file 
        else None)
    if subsonic_track_id:
        context.set(ContextKey.CURRENT_SUBSONIC_CONFIG, current_config)
        same_song : bool = True
        song : Song = context.get(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT)
        old_song : Song = None
        if not song or not song.getId() == subsonic_track_id:
            old_song = song
            same_song = False
            print(f"Song changed, loading track {subsonic_track_id} from subsonic server ...")
            song = subsonic_util.get_song(current_config, subsonic_track_id)
            context.set(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT, song)
            print(f"TrackId:[{subsonic_track_id}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}] retrieved from subsonic server.")
        current_track_duration : float = float(song.getDuration())
        if not same_song:
            print(f"New subsonic track {subsonic_track_id} playing")
            last_scrobbled_track_id : str = context.get(ContextKey.LAST_SCROBBLED_TRACK_ID)
            if (old_song) and (not last_scrobbled_track_id == old_song.getId()):
                print(f"Last song TrackId:[{old_song.getId()}] Artist:[{old_song.getArtist()}] Title:[{old_song.getTitle()}] was not scrobbled.")
            # update current_subsonic_track_id and reset counter
            pb_start : float = time.time()
            context.set(ContextKey.CURRENT_SUBSONIC_TRACK_ID, song.getId())
            current_track_hit_count : int = 1
            context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, current_track_hit_count)
            min_hit_count : int = int(((float(min_coverage) / 100.0) * current_track_duration) / sleep_time_sec)
            context.set(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT, min_hit_count)
            context.set(ContextKey.CURRENT_TRACK_PLAYBACK_START, pb_start)
        last_scrobbled_track_id : str = context.get(ContextKey.LAST_SCROBBLED_TRACK_ID)
        if not last_scrobbled_track_id == subsonic_track_id:
            scrobble_required : bool = False
            current_track_hit_count : int = context.get(ContextKey.CURRENT_TRACK_HIT_COUNT)
            current_track_playback_start : float = context.get(ContextKey.CURRENT_TRACK_PLAYBACK_START)
            current_time : float =time.time()
            played_time : float = current_time - current_track_playback_start
            if played_time >= float(enough_playback_sec):
                if verbose: print(f"Scrobble required because enough playback time [{enough_playback_sec}] sec has elapsed")
                scrobble_required = True
            if not scrobble_required: 
                current_track_hit_count += 1
                context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, current_track_hit_count)
                curr_min_hit_count : int = context.get(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT)
                if verbose: print(f"Current song hit_count:[{current_track_hit_count}] current_track_min_hit_count:[{curr_min_hit_count}] duration:[{current_track_duration}]")
                if current_track_hit_count >= curr_min_hit_count and not last_scrobbled_track_id == subsonic_track_id:
                    if verbose: print(f"Scrobble required because min playback time has elapsed")
                    scrobble_required = True
            if scrobble_required:
                execute_scrobbling(current_config, song)
                context.set(ContextKey.LAST_SCROBBLED_TRACK_ID, song.getId())   
                context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, 0)   

def clean_playback_state(context : Context):
    context.delete(ContextKey.CURRENT_MPD_SONG)
    context.delete(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT)
    context.delete(ContextKey.CURRENT_SUBSONIC_TRACK_ID)
    context.delete(ContextKey.CURRENT_TRACK_HIT_COUNT)
    context.delete(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT)
    context.delete(ContextKey.CURRENT_TRACK_PLAYBACK_START)
    context.delete(ContextKey.LAST_SCROBBLED_TRACK_ID)

scrobbler_config_list : list[SubsonicServerConfig] = get_subsonic_server_config_list()

show_subsonic_servers(scrobbler_config_list)
context : Context = Context()

context.set(ContextKey.MPD_HOST, mpd_host)
context.set(ContextKey.MPD_PORT, int(mpd_port))

while True:
    start_time : float = time.time()
    last_state : str = context.get(ContextKey.MPD_LAST_STATE)
    current_state : str = None
    try:
        status : dict = mpd_util.get_mpd_status(context)
        current_state : str = mpd_util.get_mpd_state(context)
        if not current_state == last_state:
            context.set(ContextKey.MPD_LAST_STATE, current_state)
            print(f"Current state is [{current_state}]")
        context.delete(ContextKey.MPD_LAST_EXCEPTION)
    except Exception as e:
        last_exception = context.get(ContextKey.MPD_LAST_EXCEPTION)
        same_exception : bool = (last_exception and 
            (last_exception[0] == e.args[0] and 
             last_exception[1] == e.args[1]))
        if not same_exception:
            e_tuple : tuple[any, any] = (e.args[0], e.args[1])
            context.set(ContextKey.MPD_LAST_EXCEPTION, e_tuple)
        if not same_exception:
            print(f"Cannot get mpd state [{e}]")

    if mpd_util.State.PLAY.get() == current_state:
        try:
            iteration(context)
        except Exception as e:
            print(f"Iteration failed [{e}]")
    elif (last_state and 
            mpd_util.State.STOP.get() == current_state and 
            not last_state == current_state):
        if verbose: print(f"Remove some data from context ...")
        clean_playback_state(context)
        if verbose: print(f"Data removal complete.")

    # reduce drifting
    iteration_elapsed_sec : float = time.time() - start_time
    to_wait_sec : float = sleep_time_sec - iteration_elapsed_sec

    if to_wait_sec > 0.0: time.sleep(sleep_time_sec)
    