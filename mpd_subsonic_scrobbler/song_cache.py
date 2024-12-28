"""Module providing a way to avoid to query the subsonic servers too many times."""

import time
from enum import Enum

from subsonic_connector.song import Song
from subsonic_server_config import SubsonicServerConfig
import subsonic_util
from context import Context


class SongCacheDefaults(Enum):

    MAX_AGE_SEC = float(600)


class SongCacheEntry:

    def __init__(self, song: Song):
        self.__missing: bool = song is None
        self.__song: Song = song
        self.__creation_time: float = time.time()

    @property
    def missing(self) -> bool:
        return self.__missing

    @property
    def song(self) -> Song:
        return self.__song

    @property
    def creation_time(self) -> time:
        return self.__creation_time


__song_cache: dict[str, SongCacheEntry] = {}


def __too_old(entry: SongCacheEntry) -> bool:
    now: float = time.time()
    diff: float = now - entry.creation_time
    if diff > SongCacheDefaults.MAX_AGE_SEC.value:
        print(f"Entry is too old, diff is [{diff}], purging")
        return True
    return False


def __purge_old():
    to_purge_list: list[str] = list()
    k: str
    v: Song
    for k, v in __song_cache.items():
        # too old? add to purge list
        if __too_old(v):
            to_purge_list.append(k)
    to_purge: str
    for to_purge in to_purge_list:
        del __song_cache[to_purge]


def __try_get_song(context: Context, current_config: SubsonicServerConfig, song_id: str) -> Song:
    try:
        song: Song = subsonic_util.get_song(current_config, song_id)
        return song
    except Exception as e:
        if context.get_config().get_verbose():
            print(f"Cannot load song [{song_id}] from [{current_config.get_friendly_name()}] "
                  f"due to [{type(e)}] [{e}]")
        return None


def get_song(context: Context, current_config: SubsonicServerConfig, song_id: str) -> Song:
    """Get song from configured subsonic servers, maybe caching it for a while."""
    song_key: str = f"{current_config.get_friendly_name()}-{song_id}"
    __purge_old()
    if context.get_config().get_verbose():
        print(f"get_song with track_id [{song_id}] on [{current_config.get_friendly_name()}] ...")
    song_cache_entry: SongCacheEntry = __song_cache[song_key] if song_key in __song_cache else None
    cache_hit: bool = song_cache_entry is not None
    if song_cache_entry is None:
        # get song.
        loaded: Song = __try_get_song(context, current_config, song_id)
        # add to cache even if it's empty so we keep track of that.
        song_cache_entry: SongCacheEntry = SongCacheEntry(song=loaded)
        __song_cache[song_key] = song_cache_entry
    result: Song = song_cache_entry.song
    if context.get_config().get_verbose():
        print(f"Getting cached song for [{song_id}] key [{song_key}]: [{result is not None}] Hit [{cache_hit}] ...")
    return result
