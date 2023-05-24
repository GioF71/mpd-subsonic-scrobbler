from context_key import ContextKey
from scrobbler_config import ScrobblerConfig

class Context:

    def __init__(self, config : ScrobblerConfig):
        self.__config = config;
        self.__dict : dict[str, str] = {}

    def __compose_key(self, context_key : ContextKey, index : int) -> str:
        return f"{context_key.get_key()}_{str(index)}"

    def get_config(self) -> ScrobblerConfig: return self.__config

    def get(self, context_key : ContextKey, index : int) -> any:
        key : str = self.__compose_key(context_key = context_key, index = index)
        return self.__dict[key] if key in self.__dict else None
    
    def set(self, context_key : ContextKey, context_value : any, index : int) -> any:
        key : str = self.__compose_key(context_key = context_key, index = index)
        self.__dict[key] = context_value
        return context_value
    
    def delete(self, context_key : ContextKey, index : int) -> any:
        existing : any = self.get(context_key = context_key, index = index)
        if existing: del self.__dict[self.__compose_key(context_key = context_key, index = index)]
        return existing
