class APIBase:
    def __init__(self):
        pass

    def getText(self, chapter_id:str) -> str:
        ...


from .api0 import API0
from .api1 import API1
from .api2 import API2
