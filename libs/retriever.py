from libs.document_indexer import DocumentIndexer
from libs.store import Store
from typing import Union, List

class RetrieverQA:
    def __init__(self,documents_: DocumentIndexer, stores: List[Store], weights=None) -> None:
        self.document_index = documents_
        self.stores = stores
        self.weights = weights if weights is not None else [1/len(stores)]* len(stores)
        
    
    def search(self,query: Union[str,List[str]],k: int=50):
        """This Function take a query, or list of query and returns the result """
        if isinstance(query,str):
            query = [query]
        
        # Functions to retrieve results from all the retrievers
        search_results = list(map(lambda x: x.search(query,k=k),self.stores))

        combined_results = {}
    
        for result in search_results:
            # Assign ranks based on their order in the result list
            for rank, result in enumerate(result[0]):
                combined_results[result] = combined_results.get(result, 0) + 1 / (rank + 1)

        # Sort results by their combined score
        sorted_results = sorted(combined_results.items(), key=lambda x: x[1], reverse=True)
        sorted_results = list(map(lambda x: x[0], sorted_results))
        # Return top k results
        documents = self.document_index.get_documents(sorted_results[:k])
        return documents
