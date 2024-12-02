from abc import ABC, abstractmethod
from typing import List,Dict

class Store(ABC):
    @abstractmethod
    def add(self, documents: List[Dict]):
        raise NotImplementedError
    
    @abstractmethod
    def search(self, query: List[str], k: int=50):
        raise NotImplementedError