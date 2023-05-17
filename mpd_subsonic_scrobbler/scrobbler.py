import time

import mpd_util
import subsonic_util
import scrobbler_util

from scrobbler_config import ScrobblerConfig
from subsonic_connector.song import Song
from subsonic_server_config import SubsonicServerConfig

from context_key import ContextKey
from context import Context
from subsonic_track_id import SubsonicTrackId

__app_name : str = "mpd-subsonic-scrobbler"
__app_release : str = "0.1.2"

def execute_scrobbling(subsonic_server_config : SubsonicServerConfig, song : Song) -> dict:
    print(f"About to scrobble subsonic TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}] now ...")
    scrobble_result : dict = subsonic_util.scrobble(subsonic_server_config, song.getId())
    print(f"Scrobbled subsonic TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}]")
    return scrobble_result

def print_current_song(context : Context):
    song_artist : str = mpd_util.get_mpd_current_song_artist(context)
    song_title : str = mpd_util.get_mpd_current_song_title(context)
    song_time : str = context.get(ContextKey.MPD_STATUS)["time"]
    if context.get_config().get_verbose(): print(f"Playing TrackId:[{context.get(ContextKey.CURRENT_SUBSONIC_TRACK_ID)}] Artist:[{song_artist}] Title:[{song_title}] Time:[{song_time}]")

def clean_playback_state(context : Context):
    context.delete(ContextKey.CURRENT_MPD_SONG)
    context.delete(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT)
    context.delete(ContextKey.CURRENT_SUBSONIC_TRACK_ID)
    context.delete(ContextKey.CURRENT_TRACK_HIT_COUNT)
    context.delete(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT)
    context.delete(ContextKey.CURRENT_TRACK_PLAYBACK_START)
    context.delete(ContextKey.LAST_SCROBBLED_TRACK_ID)

def iteration(context : Context):
    mpd_util.get_mpd_current_song(context)
    print_current_song(context)
    song_file : str = mpd_util.get_mpd_current_song_file(context)
    subsonic_track_id_result : SubsonicTrackId = (subsonic_util.get_subsonic_track_id(context, scrobbler_config_list) 
        if song_file 
        else None)
    if subsonic_track_id_result and subsonic_track_id_result.get_track_id():
        subsonic_track_id : str = subsonic_track_id_result.get_track_id()
        current_config : SubsonicServerConfig = subsonic_track_id_result.get_server_config() 
        context.set(ContextKey.CURRENT_SUBSONIC_CONFIG, current_config)
        same_song : bool = True
        song : Song = context.get(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT)
        old_song : Song = None
        if not song or not song.getId() == subsonic_track_id:
            changed : str = "new" if not song else "changed"
            old_song = song
            same_song = False
            print(f"Song [{changed}], loading track {subsonic_track_id} from subsonic server ...")
            song = subsonic_util.get_song(current_config, subsonic_track_id)
            context.set(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT, song)
            print(f"TrackId:[{subsonic_track_id}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}] retrieved from subsonic server.")
        current_track_duration : float = float(song.getDuration())
        if not same_song:
            print(f"New subsonic track {subsonic_track_id} playing")
            last_scrobbled_track_id : str = context.get(ContextKey.LAST_SCROBBLED_TRACK_ID)
            if (old_song) and (not last_scrobbled_track_id == old_song.getId()):
                scrobbler_util.was_not_scrobbled(old_song)
            # update current_subsonic_track_id and reset counter
            pb_start : float = time.time()
            context.set(ContextKey.CURRENT_SUBSONIC_TRACK_ID, song.getId())
            current_track_hit_count : int = 1
            context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, current_track_hit_count)
            min_hit_count : int = int(((float(context.get_config().get_min_coverage()) / 100.0) * current_track_duration) / sleep_time_sec)
            context.set(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT, min_hit_count)
            context.set(ContextKey.CURRENT_TRACK_PLAYBACK_START, pb_start)
        last_scrobbled_track_id : str = context.get(ContextKey.LAST_SCROBBLED_TRACK_ID)
        if not last_scrobbled_track_id == subsonic_track_id:
            scrobble_required : bool = False
            current_track_playback_start : float = context.get(ContextKey.CURRENT_TRACK_PLAYBACK_START)
            current_time : float =time.time()
            played_time : float = current_time - current_track_playback_start
            if played_time >= float(context.get_config().get_enough_playback_sec()):
                if context.get_config().get_verbose(): print(f"Scrobble required because enough playback time [{context.get_config().get_enough_playback_sec()}] sec has elapsed")
                scrobble_required = True
            if not scrobble_required: 
                current_track_hit_count : int = context.get(ContextKey.CURRENT_TRACK_HIT_COUNT)
                current_track_hit_count += 1
                context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, current_track_hit_count)
                curr_min_hit_count : int = context.get(ContextKey.CURRENT_TRACK_MIN_HIT_COUNT)
                if context.get_config().get_verbose(): print(f"Current song hit_count:[{current_track_hit_count}] current_track_min_hit_count:[{curr_min_hit_count}] duration:[{current_track_duration}]")
                if current_track_hit_count >= curr_min_hit_count and not last_scrobbled_track_id == subsonic_track_id:
                    if context.get_config().get_verbose(): print(f"Scrobble required because min playback time has elapsed")
                    scrobble_required = True
            if scrobble_required:
                execute_scrobbling(current_config, song)
                context.set(ContextKey.LAST_SCROBBLED_TRACK_ID, song.getId())   
                context.set(ContextKey.CURRENT_TRACK_HIT_COUNT, 0)   

print(f"{__app_name} version {__app_release}")

context : Context = Context(ScrobblerConfig())

sleep_time_msec : str = context.get_config().get_sleep_time_msec()
print(f"SLEEP_TIME: [{sleep_time_msec}] msec")

sleep_time_sec : float = context.get_config().get_sleep_time_sec()

print(f"MIN_COVERAGE: [{context.get_config().get_min_coverage()}%]")
print(f"ENOUGH_PLAYBACK_SEC: [{context.get_config().get_enough_playback_sec()} sec]")
print(f"VERBOSE: [{context.get_config().get_verbose()}]")

print(f"MPD_HOST: [{context.get_config().get_mpd_host()}]")
print(f"MPD_PORT: [{context.get_config().get_mpd_port()}]")

scrobbler_config_list : list[SubsonicServerConfig] = context.get_config().get_server_list()
scrobbler_util.show_subsonic_servers(scrobbler_config_list)

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
    elif mpd_util.State.STOP.get() == current_state:
        # report something not scrobbled?
        last_scrobbled : str = context.get(ContextKey.LAST_SCROBBLED_TRACK_ID)
        current_song_id : str = context.get(ContextKey.CURRENT_SUBSONIC_TRACK_ID)
        if current_song_id and (not current_song_id == last_scrobbled):
            song : Song = context.get(ContextKey.CURRENT_SUBSONIC_SONG_OBJECT)
            scrobbler_util.was_not_scrobbled(song)
        # do cleanup?
        if (last_state and 
            mpd_util.State.STOP.get() == current_state and 
            not last_state == current_state):
            if context.get_config().get_verbose(): print(f"Remove some data from context ...")
            clean_playback_state(context)
            if context.get_config().get_verbose(): print(f"Data removal complete.")

    # reduce drifting
    iteration_elapsed_sec : float = time.time() - start_time
    to_wait_sec : float = context.get_config().get_sleep_time_sec() - iteration_elapsed_sec

    # wait as needed
    if to_wait_sec > 0.0: time.sleep(to_wait_sec)
    