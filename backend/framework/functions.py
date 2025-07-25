from typing import Union
from .embedding import Embedding
from .collection import Collection
from .resolver import Resolver
from ddgs import DDGS
import asyncio

async def web_search(query: str, limit: int = 10) -> list[str]:
    """Function to search the web using DuckDuckGo and return a list of data."""
    print(f"Searching the web for: {query}")
    results = DDGS().text(query,region='wt-wt', safesearch='off' , max_results=limit)
    await asyncio.sleep(1)  # Simulate async operation
    return [f"{result['title']}\n {result['body']}" for result in results]

async def retrieve_context(solver: Resolver, queries: Union[list[str],str], limit: int=10) -> Union[list[str],list[list[str]]]:
    """Function to retrieve the context from the database using the queries(s)
    Args:
        llm (LLM): The LLM instance to use for embedding the query
        collection (Collection): The collection instance to search for the context
        queries (Union[list[str],str]): The query or list of queries to retrieve the context for.
        limit (int, optional): The number of  chunks to retrieve for each query. Defaults to 10.
        
    Returns:
        Union[list[str], list[list[str]]]: Return the list of chunks that match each query
    """
    # Check if the queries is a string and convert it to a list
    if isinstance(queries, str):
        queries = [queries]
    
    # Resolve the embedding and collection instances from the solver
    embedding = solver.resolve(Embedding)
    collection = solver.resolve(Collection)
     
    # Get the embeddings of the queries
    query_embeddings = embedding.create(queries)
    
    
    if query_embeddings:
        # Execute the pipeline to retrieve the chunks
        retrieved_information = await collection.search(query_embeddings,limit=limit)
        return retrieved_information #type: ignore
    
    return []

    
    
    
    

#TODO: Add a function to return all the Resolution that match the query
async def retrieve_documents(solver: Resolver, query: str ,limit: int=10):
    """Function to retrieve the documents from the database
    Args:
        limit (int, optional): The number of documents to retrieve. Defaults to 10.
    Returns:
        List[Dict]: The documents retrieved from the database
    """
    retrieved_information = await retrieve_context(solver, query, limit)
    
    metadata = {}
    #return await collection.get_all(limit=limit, metadata)
    
    raise NotImplementedError

#TODO: Add a function to retrieve the metadata from the database
async def retrieve_metadata(solver: Resolver, metadata: dict[str,str], limit: int=10):
    """Function to retrieve the documents from the database using the metadata
    Args:
        metadata (Dict[str,str]): The metadata to retrieve the documents
        limit (int, optional): The number of documents to retrieve. Defaults to 10.
    Returns:
        List[Dict]: The documents retrieved from the database
    """
    # Resolve the collection instance from the solver
    collection = solver.resolve(Collection)
    return await collection.search_by_metadata(metadata,limit)