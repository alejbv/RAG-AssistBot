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
    

async def retrieve_context(llm: LLM, collection: Collection, query: str, limit: int=10):
    """Function to retrieve the context from the database using the query
    Args:
        query (str): The query for retrieving the context
        limit (int, optional): The number of context to retrieve. Defaults to 10.
    Returns:
        List[str]: The context retrieved from the database
    """
    # Get the embeddings of the query
    query_embedding = await llm._embedd([query])[0]
    
    # Execute the pipeline to retrieve the chunks
    retrieved_chunks = await collection.search(query_embedding,limit=limit)
    
    return  ''.join([chunk['text'] for chunk in retrieved_chunks])

#TODO: Add a function to return all the Resolution that match the query
async def retrieve_documents(llm: LLM, collection: Collection, query: str, limit: int=10):
    """Function to retrieve the documents from the database
    Args:
        limit (int, optional): The number of documents to retrieve. Defaults to 10.
    Returns:
        List[Dict]: The documents retrieved from the database
    """
    return await collection.get_all(limit=limit)

async def retrieve_metadata(collection: Collection, metadata: dict[str,str], limit: int=10):
    """Function to retrieve the documents from the database using the metadata
    Args:
        metadata (Dict[str,str]): The metadata to retrieve the documents
        limit (int, optional): The number of documents to retrieve. Defaults to 10.
    Returns:
        List[Dict]: The documents retrieved from the database
    """
    return await collection.search_by_metadata(metadata,limit)