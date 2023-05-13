from context_key import ContextKey

class Context:

    def __init__(self):
        self.__dict : dict[str, str] = {}

    def get(self, context_key : ContextKey) -> any:
        return self.__dict[context_key.getKey()] if context_key.getKey() in self.__dict else None
    
    def set(self, context_key : ContextKey, context_value : any) -> any:
        self.__dict[context_key.getKey()] = context_value
        return context_value
    
    def delete(self, context_key : ContextKey) -> any:
        existing : any = self.get(context_key)
        if existing: del self.__dict[context_key.getKey()]
        return existing
