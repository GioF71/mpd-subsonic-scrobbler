import os

def get_env_value(name : str, default_value : any = None) -> any:
    val = os.getenv(name)
    if not val: return default_value
    return val
