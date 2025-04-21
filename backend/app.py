from typing import List
from chatbot import Chatbot
from fastapi import FastAPI
from contextlib import asynccontextmanager
from models import Normativa, Query
from fastapi.responses import StreamingResponse
from storage.collection import Collection
from storage.utils import load_config
from prompt import DEFAULT_SYSTEM_PROMPT,DEFAULT_USER_PROMPT

# Create the FastAPI app with a lifespan event handler to create the search index on startup    
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function to be executed before starting the application. It initializes the chatbot and the collection.

    Args:
        app (FastAPI): The FastAPI instace
    """
    # Load configuration data
    config = load_config()
    # Getting the collection
    collection = Collection(
                            uri=config["MILVUS_URI"],
                            token=config["MILVUS_TOKEN"], 
                            collection_name=config["MILVUS_COLLECTION_NAME"], 
                            dimension=config["EMBEDDING_DIMENSION"]
                        )
    
    
    # Initialize the collection and the index
    await collection.initialize_collection()

    # Setting the chatbot
    bot = Chatbot(
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        user_prompt=DEFAULT_USER_PROMPT,
        base_url=config["BASE_URL"],
        api_key=config["API_KEY"],
        inference_model=config["INFERENCE_MODEL"],
        embedding_model=config["EMBEDDING_MODEL"],
        vector_dimension=config["EMBEDDING_DIMENSION"],
        collection=collection
        )
    
    app.state.bot = bot
    
    yield
    # Closing the connection to the client
    await collection.close()

app = FastAPI(lifespan=lifespan)
        
# Endpoint for query POST
@app.post("/chat")
async def reply_query(query_request: Query) -> StreamingResponse:
  user_response = await app.state.bot.chat(query_request.query)
  return StreamingResponse(user_response, media_type="text/plain")

# Endpoint for retrieval POST
@app.post("/retrieve")
async def retrieve(query_request: Query) -> List[Normativa]:
    """Function to retrieve the documents from the database using the query"""
    normativas = await app.state.bot.retrieve_document(query_request.query)
    return normativas

# Endpoint for files POST
@app.post("/update")
async def add_file(normativa: Normativa):
   data = normativa.model_dump()
   await app.state.bot.store_file(data)
   return {"status": "ok"}