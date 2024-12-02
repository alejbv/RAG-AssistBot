from typing import Dict, List
from libs.document_indexer import DocumentIndexer


class BasicIndexer(DocumentIndexer):
    def __init__(self) -> None:
        self.documents = []
        
        
    def add_documents(self, documents: List[Dict]) -> None:
        self.documents.extend(documents)
        
    
    def get_documents(self, indexs: List[int]) -> List[Dict]:
        result = []
        for index in indexs:
            result.append(self.documents[index])
        
        return result
    