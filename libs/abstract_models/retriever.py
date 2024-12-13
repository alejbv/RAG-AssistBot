from abc import ABC, abstractmethod
from typing import List

class Retriever(ABC):
    @abstractmethod
    def add(self, documents: List[str]):
        raise NotImplementedError
    
    @abstractmethod
    def search(self, queries: List[str], k: int=50):
        raise NotImplementedError