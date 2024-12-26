from abc import ABC,abstractmethod
from pathlib import Path
from typing import Set


class DocumentLoader(ABC):
    def __init__(self,data_path: str = "data/", file_filter: Set[str] = None):
        # Setting the variables for the object
        self.data_path = Path(data_path)
        self.file_filter = file_filter if file_filter is not None else set()
        
    @abstractmethod
    def load_data(self) -> None:
        raise NotImplementedError
    