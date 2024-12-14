from abc import ABC, abstractmethod
from typing import List

class DocumentProcessor(ABC):
    
    @abstractmethod
    def process_document(self,documents: List[str])-> List[str]:
        raise NotImplementedError