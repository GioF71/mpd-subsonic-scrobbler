from context_key import ContextKey
from config_key import ConfigKey

def indexed_context_key(key : ContextKey, index : int) -> str:
    return __concat_key(key = key.get_key(), index = index)

def indexed_config_key(key : ConfigKey, index : int) -> str:
    if index == 0: return key.get_key()
    return __concat_key(key = key.get_key(), index = index)

def __concat_key(key : str, index : int) -> str:
    return f"{key}_{str(index)}"

