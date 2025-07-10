from typing import Union
from .llm import LLM
from .collection import Collection


async def store_file(llm: LLM, collection: Collection, data: dict):
    """Function to store the file in the database"""
    
    embedding = await llm._embedd([data["summary"]])[0]
    data["embedding"] = embedding
    
    try:
        await collection.insert([data])
        print("File Stored")
        
    except Exception as e:
        print(f"Error in store_file: {e}")
    

async def retrieve_from_queries(llm: LLM, collection: Collection, queries: Union[list[str],str], limit: int=10) -> Union[list[str],list[list[str]]]:
    """Function to retrieve the chunks from the database using the queries
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
        
    # Get the embeddings of the queries
    query_embeddings = await llm._embedd(queries)
    
    
    if query_embeddings:
        # Execute the pipeline to retrieve the chunks
        retrieved_information = await collection.search(query_embeddings,limit=limit)
        return retrieved_information #type: ignore
    
    return []


async def retrieve_context(llm: LLM, collection: Collection, queries: Union[list[str],str], limit: int=10)-> str:
    """Function to retrieve the context from the database using the queries"""
    
    # Retrive the chunks from the database using the queries
    retrieved_information = await retrieve_from_queries(llm, collection, queries, limit)
    
    # Convert the retrieved information into a context string
    ctx = []
    for chunks in retrieved_information:
        ctx.append(''.join([chunk['text'] for chunk in chunks]))
    
    return  ''.join(ctx)


#TODO: Add a function to return all the Resolution that match the query
async def retrieve_documents(llm: LLM, collection: Collection, query: str ,limit: int=10):
    """Function to retrieve the documents from the database
    Args:
        limit (int, optional): The number of documents to retrieve. Defaults to 10.
    Returns:
        List[Dict]: The documents retrieved from the database
    """
    retrieved_information = await retrieve_from_queries(llm, collection, query, limit)
    
    metadata = {}
    #return await collection.get_all(limit=limit, metadata)
    
    raise NotImplementedError

async def retrieve_metadata(collection: Collection, metadata: dict[str,str], limit: int=10):
    """Function to retrieve the documents from the database using the metadata
    Args:
        metadata (Dict[str,str]): The metadata to retrieve the documents
        limit (int, optional): The number of documents to retrieve. Defaults to 10.
    Returns:
        List[Dict]: The documents retrieved from the database
    """
    return await collection.search_by_metadata(metadata,limit)