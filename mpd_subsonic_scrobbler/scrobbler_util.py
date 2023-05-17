from config_key import ConfigKey
from subsonic_server_config import SubsonicServerConfig
from config_util import get_indexed_env_value

def get_subsonic_server_config_list() -> list[SubsonicServerConfig]:
    c_list : list[SubsonicServerConfig] = list()
    config_index : int
    for config_index in range(10):
        config_file_name : str = get_indexed_env_value(ConfigKey.SUBSONIC_PARAMETERS_FILE.getKey(), config_index)
        server_url : str = get_indexed_env_value(ConfigKey.SUBSONIC_BASE_URL.getKey(), config_index)
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
    
