from context_key import ContextKey
from scrobbler_config import ScrobblerConfig
from indexed_key import indexed_context_key


class Context:

    def __init__(self, config: ScrobblerConfig):
        self.__config = config
        self.__dict: dict[str, str] = {}

    def get_config(self) -> ScrobblerConfig: return self.__config

    def get(self, context_key: ContextKey, index: int) -> any:
        key: str = indexed_context_key(key=context_key, index=index)
        return self.__dict[key] if key in self.__dict else None

    def set(self, context_key: ContextKey, context_value: any, index: int) -> any:
        key: str = indexed_context_key(key=context_key, index=index)
        self.__dict[key] = context_value
        return context_value

    def delete(self, context_key: ContextKey, index: int) -> any:
        existing: any = self.get(context_key=context_key, index=index)
        if existing: del self.__dict[indexed_context_key(key=context_key, index=index)]
        return existing
