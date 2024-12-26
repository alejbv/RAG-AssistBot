from abc import ABC, abstractmethod
from typing import List,Dict

class TextSplitter(ABC):
    
    @abstractmethod
    def split_documents(self,documents: List[Dict]) -> List[Dict]:
        raise NotImplementedError