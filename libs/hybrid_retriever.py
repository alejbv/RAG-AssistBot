from libs.abstract_models.document_storage import DocumentStorage
from libs.abstract_models.retriever import Retriever
from typing import Union, List,Dict

#TODO: Handling more than a query at a time(in case of use of HyDE or similar techinques)
#TODO: Add a thresholds for the document score
#TODO: Look for ways of adding concurrency in the processes for adding and searching the documents
class HybridRetriever:
    def __init__(self,documents_: DocumentStorage, retrievers: List[Retriever], weights=None) -> None:
        self.document_index = documents_
        self.retrievers_list = retrievers
        self.weights = weights if weights is not None else [1/len(retrievers)]* len(retrievers)
        
   
    def add(self, documents: List[Dict]):
        """Function for adding the documents to each of the retrivers used in the hybrid retriever

        Args:
            documents (List[Dict]): The list of each of the document to be stored for retrieval
        """
       
        num_retrievers = len(self.retrievers_list)
        texts = [document['text'] for document in documents]
        # Creating the processes for concurrently add the documents to each of the retrievers
        for retriever in self.retrievers_list:
            retriever.add(texts)
        
        
    def search(self,query: Union[str,List[str]],k: int=20):
        """This Function take a query, or list of query. Search for each of the retrievers the
        best answers to the queries in each retriever and rerank all the documents for a better result
        Args:
            query (Union[str,List[str]]): The query or queries for search
            k (int, optional): The total of document to search. Defaults to 20.

        Returns:
            A list with the index of the document that better match the queries
        """
        if isinstance(query,str):
            query = [query]
        
        # Retrieving the document matching the queries in each of the retrievers
        search_results = []
        for retriever in self.retrievers_list:
            search_results.append(retriever.search(query,k=k))
        
        # Reranking the search result
        combined_results = {}
        for result in search_results:
            # Assign ranks based on their order in the result list
            for rank, result in enumerate(result[0]):
                combined_results[result] = combined_results.get(result, 0) + (1 / (rank + 60))

        # Sort results by their combined score
        sorted_results = sorted(combined_results.items(), key=lambda x: x[1], reverse=True)
        sorted_results = [result[0] for result in sorted_results]
        # Return top k results
        documents = self.document_index.get_documents(sorted_results[:k])
        return documents
