from subsonic_server_config import SubsonicServerConfig


class SubsonicTrackId:

    def __init__(self, track_id: str, server_config: SubsonicServerConfig):
        self.__track_id: str = track_id
        self.__server_config: SubsonicServerConfig = server_config

    def get_track_id(self) -> str: return self.__track_id
    def get_server_config(self) -> SubsonicServerConfig: return self.__server_config
