from abc import ABC,abstractmethod
from typing import List,Dict
class DocumentIndexer(ABC):
    
    @abstractmethod
    def add_documents(self,documents:List[Dict]) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def get_documents(self,indexs: List[int]) -> List[Dict]:
        raise NotImplementedError