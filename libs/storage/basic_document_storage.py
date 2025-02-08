from redis import Redis
from typing import Dict, List
from libs.abstract_models.document_storage import DocumentStorage
import json

# Implement the use redis for storage the documents and the metadata
class BasicStorage(DocumentStorage):
    def __init__(self) -> None:
        self.redis = Redis(host='localhost', port=6379, decode_responses=True)
        self.documents_ids = []
        
    def add_documents(self, documents: List[Dict]) -> None:
        """ Add the documents to the redis database.
        Args:
            documents (List[Dict]): A list of dictionaries with the documents to add.
        """
        # Add the documents to the redis database with the id as the key
        docs = {}
        for document in documents:
            doc_copy = document.copy()
            doc_id = doc_copy.pop("id")
            docs[doc_id]=json.dumps(doc_copy)
            
            self.documents_ids.append(doc_id)
        
        self.redis.mset(docs)
            
        
    def get_all_documents(self) -> List[str]:
        """
        Get all the documents from the redis database.
        Returns:
            List[str]: List of document texts that match the filter.
        """ 
        documents = []
        documents = map(lambda key: json.loads(self.redis.get(key))["text"], self.redis.keys())
        
        return list(documents)
    
    def get_documents(self, indexs: List[int]) -> List[Dict]:
        """
        Retrieve the documents from the redis database with the corresponing ids.

        Args:
            indexs (List[int]): A list with the index of the documents to retrieve.

        Returns:
            List[Dict]: A list with the text documents that match the ids.
        """
        if self.documents_ids:
            keys = [self.documents_ids[index] for index in indexs]
            result = list(map(lambda encoded_doc: json.loads(encoded_doc)["text"], self.redis.mget(keys)))
            
            return result
        
        return []
