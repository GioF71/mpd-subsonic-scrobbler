from enum import Enum

class MPDStatusKey(Enum):

    TIME = 0, "time"
    ARTIST = 1, "artist"
    TITLE = 2, "title"
    FILE = 3, "file"
    STATE = 4, "state"

    def __init__(self, num, element_key : str):
        self.num = num
        self.__key : str = element_key

    def get_key(self) -> str:
        return self.__key
