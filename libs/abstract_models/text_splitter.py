from abc import ABC, abstractmethod
from typing import List

class TextSplitter(ABC):
    
    @abstractmethod
    def split_text(self,documents: List[str]) -> List[str]:
        raise NotImplementedError