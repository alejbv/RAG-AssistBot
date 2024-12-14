from typing import Dict, List
from libs.abstract_models.document_storage import DocumentStorage


class BasicStorage(DocumentStorage):
    def __init__(self) -> None:
        self.documents = []
        
        
    def add_documents(self, documents: List[Dict]) -> None:
        self.documents.extend(documents)
        
    def get_all_documents(self):
        return self.documents
    
    def get_documents(self, indexs: List[int]) -> List[Dict]:
        result = []
        for index in indexs:
            result.append(self.documents[index])
        
        return result
    