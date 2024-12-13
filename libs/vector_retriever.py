import streamlit as st
import numpy as np
from typing import List,Dict
from libs.abstract_models.retriever import Retriever
from faiss import IndexFlatIP,IndexIVFFlat
from openai import OpenAI

"""
Data schema
    text: string -> The text corresponding to the chunk
    metadata: Dict-> The metadata of the document
    Returns:
"""
class VectorRetriever(Retriever):
    def __init__(self,d:int = 768, nlist:int = 25) -> None:
        self.d = d
        self.nlist=nlist
        self._quantizer = IndexFlatIP(self.d)  # the other index
        self._index = IndexIVFFlat(self._quantizer, self.d, self.nlist)
        self.client = OpenAI(base_url=st.secrets.BASE_URL,api_key=st.secrets.API_KEY)

    def embed(self,documents: List[Dict]):
        embeddings = []
        try:
            for doc in documents:            
                response = self.client.embeddings.create(
                            input=[doc],
                            model="nomic-ai/nomic-embed-text-v1.5",)

                embeddings.append(response.data[0].embedding)
        except Exception as e:
            print(doc)
            
        return np.array(embeddings)
    
        
    def add(self, documents: List[str]):
        """Function for adding new document to the index

        Args:
            documents (List[Dict]): A list of document to extend the index for retrieval
        """
        embeddings = self.embed(documents)
        
        if not self._index.is_trained:
            self._index.train(embeddings)
        
        self._index.add(embeddings)
        #self._data.extend(documents)
        
    def search(self, queries: List[str], k: int=20, nprobe: int=5) -> List[Dict]:
        """Function for retrieving a list of document that match the given queries

        Args:
            text (List[str]): The queries used for searching the documents
            k (int, optional): The number of documents to retrieve. Defaults to 50.

        Returns:
            List[Dict]: The documents that matches the queries
        """
        # Get the document embedding
        query_embedding = self.embed(queries)
        # Find the closest K vectors
        self._index.nprobe=nprobe
        score,idx = self._index.search(query_embedding,k=k)
        # Retrieve the corresponding texts
        #return [self._data[i] for i in idx[0]],score
        return idx[0],score[0]


if __name__=='__main__':
    texts = ["How do I get a replacement Medicare card?",
        "What is the monthly premium for Medicare Part B?",
        "How do I terminate my Medicare Part B (medical insurance)?",
        "How do I sign up for Medicare?",
        "Can I sign up for Medicare Part B if I am working and have health insurance through an employer?",
        "How do I sign up for Medicare Part B if I already have Part A?",
        "What are Medicare late enrollment penalties?",
        "What is Medicare and who can get it?",
        "How can I get help with my Medicare Part A and Part B premiums?",
        "What are the different parts of Medicare?",
        "Will my Medicare premiums be higher because of my higher income?",
        "What is TRICARE ?",
        "Should I sign up for Medicare Part B if I have Veterans' Benefits?"]


    corpus = [dict(text=document,metadata={}) for document in texts]
    store = VectorRetriever(nlist=5)
    store.add(corpus)
    result = store.search([texts[5]],k=5,nprobe=5)
    print(result)
