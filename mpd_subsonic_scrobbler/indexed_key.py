from context_key import ContextKey
from config_key import ConfigKey

def indexed_context_key(key : ContextKey, index : int) -> str:
    return __indexed_config_key(key = key.get_key(), index = index)

def indexed_config_key(key : ConfigKey, index : int) -> str:
    return __indexed_config_key(key = key.get_key(), index = index)

def __indexed_config_key(key : str, index : int) -> str:
    return f"{key}_{str(index)}"

