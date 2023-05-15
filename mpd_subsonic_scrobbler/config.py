import os

def get_env_value(name : str, default_value : any = None) -> any:
    if not name: raise Exception(f"name cannot be empty")
    val = os.getenv(name)
    if not val: return default_value
    return val

def _get_indexed_name(name : str, index : int = 0) -> str:
    if not name: raise Exception(f"name cannot be empty")
    if index:
        if not isinstance(index, int): raise Exception("index is not int")
        # it's int now for sure
        if index < 0: raise Exception("index must be >= 0")
    ndx : int = int(index) if index else 0
    ndx_name : str = name if ndx == 0 else f"{name}_{ndx}"
    return ndx_name

def get_indexed_env_value(name : str, index : int = 0, default_value : any = None) -> any:
    ndx_name : str = _get_indexed_name(name, index)
    return get_env_value(name = ndx_name, default_value = default_value)

#test
print(_get_indexed_name("A"))
print(_get_indexed_name("A", 0))
print(_get_indexed_name("A", 1))