import tomli
import numpy as np
from typing import List,Tuple
from libs.abstract_models.retriever import Retriever
from faiss import IndexFlatIP,IndexIVFFlat
from openai import OpenAI

class VectorRetriever(Retriever):
    def __init__(self,d:int = 768, nlist:int = 25) -> None:
        self.d = d
        self.nlist=nlist
        self._quantizer = IndexFlatIP(self.d)  # the other index
        self._index = IndexIVFFlat(self._quantizer, self.d, self.nlist)
        
        # Loading the configuration file
        with open(".secrets/config.toml", 'rb') as f:
            config = tomli.load(f)            
            self.client = OpenAI(base_url=config["BASE_URL"],api_key=config["API_KEY"])
            self.model = config["EMBEDDING_MODEL"]

    def embed(self,documents: List[str]):
        embeddings = []
        try:
            for doc in documents:            
                response = self.client.embeddings.create(
                            input=[doc],
                            model=self.model,
                            dimensions=self.d#1536  
                            )

                embeddings.append(response.data[0].embedding)
        except Exception as e:
            print(e)
            
        return np.array(embeddings)    
    #TODO: Revisar que funcione: Este metodo no funciona con el embedding que se esta usando(nomic)
    def batch_embed(self,documents: List[str],batch_size=300):
        embeddings = []
        try:
            for rng in range(len(documents),batch_size):
                docs = documents[rng:rng+batch_size]
                # Aqui deberia ir otra api de infenercia o otro modelo
                response = self.client.embeddings.create(
                            input=docs,
                            model=self.model,
                            dimensions=self.d#1536
                            )
                embeddings.extend([np.asarray(d.embedding) for d in response.data])
        except Exception as e:
            print(e)
        
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
        
    def search(self, queries: List[str], k: int=20, nprobe: int=5)-> Tuple[List,List]:
        """Function for retrieving a list of document that match the given queries

        Args:
            text (List[str]): The queries used for searching the documents
            k (int, optional): The number of documents to retrieve. Defaults to 50.

        Returns:
            Tuple[List,List]: A tuple with to list, the first the firt k ranked document and 
            the second the documents ranking scores
        """
        # Get the document embedding
        query_embedding = self.embed(queries)
        # Find the closest K vectors
        self._index.nprobe=nprobe
        score,idx = self._index.search(query_embedding,k=k)
        # Retrieve the corresponding texts
        #return [self._data[i] for i in idx[0]],score
        return idx[0],score[0]