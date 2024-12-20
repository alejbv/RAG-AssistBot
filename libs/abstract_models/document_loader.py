from abc import ABC,abstractmethod
from typing import List,Dict


class DocumentLoader(ABC):
    
    @abstractmethod
    def load_data(self) -> None:
        raise NotImplementedError
    