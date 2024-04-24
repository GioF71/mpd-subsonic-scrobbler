import time

import mpd_util
import subsonic_util
import scrobbler_util

from mpd_status_key import MPDStatusKey
from scrobbler_config import ScrobblerConfig
from subsonic_connector.song import Song
from subsonic_server_config import SubsonicServerConfig
from mpd_instance_config import MpdInstanceConfig

from context_key import ContextKey
from context import Context
from subsonic_track_id import SubsonicTrackId

import socket
import importlib.metadata

__app_name: str = "mpd-subsonic-scrobbler"
version = importlib.metadata.version(__app_name)
print(version)
__app_release: str = version


def execute_scrobbling(subsonic_server_config: SubsonicServerConfig, song: Song, index: int) -> dict:
    print(f"About to scrobble to [{subsonic_server_config.get_friendly_name()}] "
          f"TrackId:[{song.getId()}] Artist:[{song.getArtist()}] "
          f"Title:[{song.getTitle()}] now ...")
    scrobble_start: float = time.time()
    scrobble_result: dict = subsonic_util.scrobble(subsonic_server_config, song.getId())
    scrobble_elapsed: float = time.time() - scrobble_start
    context.set(
        context_key=ContextKey.ELAPSED_SS_SCROBBLE_SONG,
        index=index,
        context_value=scrobble_elapsed)
    print(f"Scrobbled to [{subsonic_server_config.get_friendly_name()}] "
          f"TrackId:[{song.getId()}] Artist:[{song.getArtist()}] Title:[{song.getTitle()}]")
    return scrobble_result


def print_current_song(context: Context, index: int, subsonic_server_config: SubsonicServerConfig):
    song_artist: str = mpd_util.get_mpd_current_song_artist(context=context, index=index)
    song_title: str = mpd_util.get_mpd_current_song_title(context=context, index=index)
    song_time: str = context.get(context_key=ContextKey.MPD_STATUS, index=index)[MPDStatusKey.TIME.get_key()]
    if context.get_config().get_verbose():
        track_id: str = context.get(context_key=ContextKey.CURRENT_SUBSONIC_TRACK_ID, index=index)
        server: str = subsonic_server_config.get_friendly_name()
        mpd: str = context.get_config().get_mpd_list()[index].get_mpd_friendly_name()
        print(f"Playing TrackId:[{track_id}] from [{server}] on [{mpd}] "
              f"Artist:[{song_artist}] Title:[{song_title}] Time:[{song_time}]")


def show_subsonic_servers(config: ScrobblerConfig):
    current: SubsonicServerConfig
    cnt: int = None
    for current in config.get_server_list():
        cnt = 0 if cnt is None else (cnt + 1)
        print(f"server[{cnt}].friendly_name=[{current.get_friendly_name()}]")
        print(f"server[{cnt}].base_url=[{current.getBaseUrl()}]")
        print(f"server[{cnt}].port=[{current.getPort()}]")
        print(f"server[{cnt}].legacyauth=[{current.getLegacyAuth()}]")
        print(f"server[{cnt}].upmpdcli_base_url=[{current.getUpmpdcliBaseUrl()}]")
        print(f"server[{cnt}].upmpdcli_port=[{current.getUpmpdcliPort()}]")
        if not config.get_redact_credentials(): print(f"server[{cnt}].user=[{current.getUserName()}]")
        if not config.get_redact_credentials(): print(f"server[{cnt}].password=[{current.getPassword()}]")


def show_mpd_instances(config: ScrobblerConfig):
    current: MpdInstanceConfig
    cnt: int = None
    for current in config.get_mpd_list():
        cnt = 0 if cnt is None else (cnt + 1)
        print(f"mpd[{cnt}].friendly_name=[{current.get_mpd_friendly_name()}]")
        print(f"mpd[{cnt}].host=[{current.get_mpd_host()}]")
        print(f"mpd[{cnt}].port=[{current.get_mpd_port()}]")


def handle_playback(context: Context, index: int):
    song_file: str = mpd_util.get_mpd_current_song_file(context=context, index=index)
    subsonic_track_id_result: SubsonicTrackId = (subsonic_util.get_subsonic_track_id(
        context=context,
        index=index,
        scrobbler_config_list=scrobbler_config_list)
        if song_file
        else None)
    if subsonic_track_id_result and subsonic_track_id_result.get_track_id():
        print_current_song(
            context=context,
            index=index,
            subsonic_server_config=subsonic_track_id_result.get_server_config())
        subsonic_track_id: str = subsonic_track_id_result.get_track_id()
        current_config: SubsonicServerConfig = subsonic_track_id_result.get_server_config()
        same_song: bool = True
        song: Song = context.get(context_key=ContextKey.CURRENT_SUBSONIC_SONG_OBJECT, index=index)
        old_song: Song = None
        if not song or not song.getId() == subsonic_track_id:
            changed: str = "new" if not song else "changed"
            old_song = song
            same_song = False
            print(f"Song [{changed}], loading TrackId:[{subsonic_track_id}] "
                  f"from subsonic server [{current_config.get_friendly_name()}] ...")
            get_ss_start: float = time.time()
            song = subsonic_util.get_song(current_config, subsonic_track_id)
            get_ss_elapsed: float = time.time() - get_ss_start
            context.set(context_key=ContextKey.ELAPSED_SS_GET_SONG_INFO, index=index, context_value=get_ss_elapsed)
            context.set(context_key=ContextKey.CURRENT_SUBSONIC_SONG_OBJECT, index=index, context_value=song)
            print(f"TrackId:[{subsonic_track_id}] Artist:[{song.getArtist()}] "
                  f"Title:[{song.getTitle()}] retrieved from "
                  f"subsonic server [{current_config.get_friendly_name()}].")
        if not same_song:
            print(f"Subsonic TrackId:[{subsonic_track_id}] from [{current_config.get_friendly_name()}] "
                  f"is playing on player [{context.get_config().get_mpd_list()[index].get_mpd_friendly_name()}] ...")
            last_scrobbled_track_id: str = context.get(context_key=ContextKey.LAST_SCROBBLED_TRACK_ID, index=index)
            if (old_song) and (not last_scrobbled_track_id == old_song.getId()):
                scrobbler_util.was_not_scrobbled(old_song)
            # update current_subsonic_track_id and reset counter
            pb_start: float = time.time()
            context.set(
                context_key=ContextKey.CURRENT_SUBSONIC_TRACK_ID,
                index=index,
                context_value=song.getId())
            current_track_hit_count: int = 1
            context.set(
                context_key=ContextKey.CURRENT_TRACK_HIT_COUNT,
                index=index,
                context_value=current_track_hit_count)
            min_hit_count: int = (int(((float(context.get_config().get_min_coverage()) / 100.0) * song.getDuration()) /
                                      sleep_time_sec))
            context.set(
                context_key=ContextKey.CURRENT_TRACK_MIN_HIT_COUNT,
                index=index,
                context_value=min_hit_count)
            context.set(
                context_key=ContextKey.CURRENT_TRACK_PLAYBACK_START,
                index=index,
                context_value=pb_start)
        last_scrobbled_track_id: str = context.get(
            context_key=ContextKey.LAST_SCROBBLED_TRACK_ID,
            index=index)
        if not last_scrobbled_track_id == subsonic_track_id:
            scrobble_required: bool = False
            current_track_playback_start: float = context.get(
                context_key=ContextKey.CURRENT_TRACK_PLAYBACK_START,
                index=index)
            current_time: float = time.time()
            played_time: float = current_time - current_track_playback_start
            if played_time >= float(context.get_config().get_enough_playback_sec()):
                if context.get_config().get_verbose():
                    print("Scrobble required because enough "
                          f"playback time [{context.get_config().get_enough_playback_sec()}] sec has elapsed")
                scrobble_required = True
            if not scrobble_required:
                current_track_hit_count: int = context.get(
                    context_key=ContextKey.CURRENT_TRACK_HIT_COUNT,
                    index=index)
                current_track_hit_count += 1
                context.set(
                    context_key=ContextKey.CURRENT_TRACK_HIT_COUNT,
                    index=index,
                    context_value=current_track_hit_count)
                curr_min_hit_count: int = context.get(
                    context_key=ContextKey.CURRENT_TRACK_MIN_HIT_COUNT,
                    index=index)
                if context.get_config().get_verbose():
                    print(f"Current song hit_count:[{current_track_hit_count}] "
                          f"current_track_min_hit_count:[{curr_min_hit_count}] "
                          f"duration:[{song.getDuration()}]")
                if current_track_hit_count >= curr_min_hit_count and not last_scrobbled_track_id == subsonic_track_id:
                    if context.get_config().get_verbose():
                        print("Scrobble required because min playback time has elapsed")
                    scrobble_required = True
            if scrobble_required:
                execute_scrobbling(subsonic_server_config=current_config, song=song, index=index)
                context.set(context_key=ContextKey.LAST_SCROBBLED_TRACK_ID, index=index, context_value=song.getId())
                context.set(context_key=ContextKey.CURRENT_TRACK_HIT_COUNT, index=index, context_value=0)


def delete_elapsed_stats(context: ContextKey, index: int):
    context.delete(context_key=ContextKey.ELAPSED_MPD_STATE, index=index)
    context.delete(context_key=ContextKey.ELAPSED_SS_GET_SONG_INFO, index=index)
    context.delete(context_key=ContextKey.ELAPSED_SS_SCROBBLE_SONG, index=index)


print(f"{__app_name} version {__app_release}")

context: Context = Context(ScrobblerConfig())

sleep_time_msec: str = context.get_config().get_sleep_time_msec()
print(f"SLEEP_TIME: [{sleep_time_msec}] msec")

sleep_time_sec: float = context.get_config().get_sleep_time_sec()

print(f"MIN_COVERAGE: [{context.get_config().get_min_coverage()}%]")
print(f"ENOUGH_PLAYBACK_SEC: [{context.get_config().get_enough_playback_sec()} sec]")
print(f"VERBOSE: [{context.get_config().get_verbose()}]")

scrobbler_config_list: list[SubsonicServerConfig] = context.get_config().get_server_list()
mpd_list: list[MpdInstanceConfig] = context.get_config().get_mpd_list()

show_subsonic_servers(context.get_config())
show_mpd_instances(context.get_config())

while True:
    start_time: float = time.time()
    mpd_index: int
    for mpd_index in range(len(mpd_list)):
        imposed_sleep_iteration_count: int = mpd_util.must_sleep_for(context=context, mpd_index=mpd_index)
        if imposed_sleep_iteration_count and imposed_sleep_iteration_count > 0: continue
        delete_elapsed_stats(context=context, index=mpd_index)
        last_state: str = context.get(context_key=ContextKey.MPD_LAST_STATE, index=mpd_index)
        current_state: str = None
        mpd_get_status_start: float
        try:
            mpd_get_status_start = time.time()
            status: dict = mpd_util.get_mpd_status(context, mpd_index=mpd_index)
            mpd_get_status_elapsed: float = time.time() - mpd_get_status_start
            context.set(context_key=ContextKey.ELAPSED_MPD_STATE, index=mpd_index, context_value=mpd_get_status_elapsed)
            current_state: str = mpd_util.get_mpd_state(context, mpd_index=mpd_index)
            if not current_state == last_state:
                context.set(
                    context_key=ContextKey.MPD_LAST_STATE,
                    index=mpd_index,
                    context_value=current_state)
                print("Current mpd state for "
                      f"index {mpd_index} [{context.get_config().get_mpd_list()[mpd_index].get_mpd_friendly_name()}] "
                      f"is [{current_state}]")
            context.delete(
                context_key=ContextKey.MPD_LAST_EXCEPTION,
                index=mpd_index)
        except Exception as e:
            mpd_get_status_elapsed: float = time.time() - mpd_get_status_start
            context.set(context_key=ContextKey.ELAPSED_MPD_STATE, index=mpd_index, context_value=mpd_get_status_elapsed)
            if ((isinstance(e, OSError) and (e.errno == 113 or e.errno == 111)) or
                    isinstance(e, socket.timeout)):
                # no route to host, impose sleep on player
                sleep_iteration_count: int = context.get_config().get_mpd_imposed_sleep_iteration_count()
                if context.get_config().get_verbose():
                    print(f"Player [{mpd_index}] "
                          f"[{context.get_config().get_mpd_list()[mpd_index].get_mpd_friendly_name()}] "
                          f"will sleep for [{sleep_iteration_count}] iteration(s)")
                context.set(
                    context_key=ContextKey.MPD_IMPOSED_SLEEP_ITERATIONS,
                    index=mpd_index,
                    context_value=sleep_iteration_count)
            last_exception = context.get(context_key=ContextKey.MPD_LAST_EXCEPTION, index=mpd_index)
            last_1: any = last_exception[1] if last_exception and len(last_exception) > 1 else None
            e_1: any = e.args[1] if e and e.args and len(e.args) > 1 else None
            same_exception: bool = (last_exception and
                                    (last_exception[0] == e.args[0] and
                                        last_1 == e_1))
            if not same_exception:
                e_tuple: tuple[any, any] = (e.args[0], e.args[1] if len(e.args) > 1 else None)
                context.set(context_key=ContextKey.MPD_LAST_EXCEPTION, index=mpd_index, context_value=e_tuple)
            if not same_exception:
                print(f"Cannot get mpd state for index [{mpd_index}] "
                      f"[{context.get_config().get_mpd_list()[mpd_index].get_mpd_friendly_name()}] "
                      f"[{type(e)}] [{e}]")
        if mpd_util.State.PLAY.get() == current_state:
            try:
                handle_playback(context=context, index=mpd_index)
            except Exception as e:
                print(f"Playback management failed at index {mpd_index} "
                      f"[{context.get_config().get_mpd_list()[mpd_index].get_mpd_friendly_name()}] "
                      f"[{type(e)}] [{e}]")
        elif mpd_util.State.STOP.get() == current_state:
            # report something not scrobbled?
            last_scrobbled: str = context.get(context_key=ContextKey.LAST_SCROBBLED_TRACK_ID, index=mpd_index)
            current_song_id: str = context.get(context_key=ContextKey.CURRENT_SUBSONIC_TRACK_ID, index=mpd_index)
            if current_song_id and (not current_song_id == last_scrobbled):
                song: Song = context.get(context_key=ContextKey.CURRENT_SUBSONIC_SONG_OBJECT, index=mpd_index)
                scrobbler_util.was_not_scrobbled(song)
            # do cleanup?
            if (last_state and
                mpd_util.State.STOP.get() == current_state and
                    not last_state == current_state):
                if context.get_config().get_verbose(): print(f"Remove some data from context for index {mpd_index} ...")
                scrobbler_util.clean_playback_state(
                    lambda x, y: context.delete(
                        context_key=x,
                        index=y),
                    index=mpd_index)
                if context.get_config().get_verbose(): print(f"Data removal for index {mpd_index} complete.")
    # reduce drifting
    iteration_elapsed_sec: float = time.time() - start_time
    to_wait_sec: float = context.get_config().get_sleep_time_sec() - iteration_elapsed_sec
    percent_duration: float = 100.0 * (float(iteration_elapsed_sec) / float(context.get_config().get_sleep_time_sec()))
    if percent_duration > float(context.get_config().get_iteration_duration_threshold_percent()):
        print(f"Playback management is taking too long [{iteration_elapsed_sec} sec] or "
              f"[{percent_duration}%] of sleep_time [{context.get_config().get_sleep_time_sec()} sec]")
        print("Please consider reducing mpd timeout, increasing sleep_time, "
              "increasing the threshold and/or creating dedicated instances of this scrobbler")
        elapsed_index: int
        for elapsed_index in range(len(context.get_config().get_mpd_list())):
            print(f"  [{elapsed_index}] Get Mpd Status: "
                  f"{context.get(context_key=ContextKey.ELAPSED_MPD_STATE, index=elapsed_index)}")
            print(f"  [{elapsed_index}] Get Song Info:  "
                  f"{context.get(context_key=ContextKey.ELAPSED_SS_GET_SONG_INFO, index=elapsed_index)}")
            print(f"  [{elapsed_index}] Scrobbling:     "
                  f"{context.get(context_key=ContextKey.ELAPSED_SS_SCROBBLE_SONG, index=elapsed_index)}")
    # wait as needed
    if to_wait_sec > 0.0:
        time.sleep(to_wait_sec)
