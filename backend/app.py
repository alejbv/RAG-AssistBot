from typing import List
from fastapi import BackgroundTasks, FastAPI, File, Body, UploadFile
from contextlib import asynccontextmanager
from models import Normativa, Query
from fastapi.responses import StreamingResponse

from os import getenv
from dotenv import load_dotenv
from tools import Collection, LLM, Chatbot
from tools import store_file,  retrieve_documents

# Create the FastAPI app with a lifespan event handler to create the search index on startup    
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function to be executed before starting the application. It initializes the chatbot and the collection.

    Args:
        app (FastAPI): The FastAPI instace
    """
    # Load configuration data
    load_dotenv('.env')  
    
    # Getting the collection
    collection = Collection(
                            getenv("MILVUS_URI",""),
                            getenv("MILVUS_TOKEN",""),
                            getenv("MILVUS_COLLECTION_NAME",""),
                            int(getenv("EMBEDDING_DIMENSION",""))
                        )
    
    # Initialize the collection and the index
    await collection.initialize_collection()
    
    # Initializing the LLM
    llm = LLM(
        getenv("BASE_URL",""),
        getenv("API_KEY",""), 
        getenv("INFERENCE_MODEL",""),
        getenv("EMBEDDING_MODEL",""),
        int(getenv("EMBEDDING_DIMENSION",""))
    )

    
    # Setting the chatbot
    bot = Chatbot(
                llm,
                collection
            )
    
    
    app.state.collection = collection
    app.state.llm = llm
    app.state.bot = bot
    
    yield
    # Closing the connection to the client
    await collection.close()

app = FastAPI(lifespan=lifespan)
        
# Endpoint for query POST
@app.post("/chat/")
async def chat(query_request: Query) -> StreamingResponse:
  user_response = await app.state.bot.chat(query_request.query)
  return StreamingResponse(user_response, media_type="text/plain")

# Endpoint for retrieval POST
@app.post("/retrieve")
async def retrieve(query_request: Query) -> List[Normativa]:
    """Function to retrieve the documents from the database using the query"""
    normativas = await retrieve_documents(app.state.llm, app.state.collection, query_request.query)
    return [Normativa.model_validate(doc) for doc in normativas]

# Endpoint for files POST
@app.post("/upload/")
async def add_file(tasks: BackgroundTasks, file: UploadFile = File(...),):
   document_data = await file.read()
   tasks.add_task(process_file, file.filename, document_data) # type: ignore
   
   return {"message": "File upload started", "filename": file.filename}

def process_file(document_id: str, document_data: bytes):
    """Function to process the file and store it in the database"""
     
    # Fetch the document using esorm
    document = await Document.get(document_id)

    converter = markitdown.MarkItDown()
    result = converter.convert_stream(
        io.BytesIO(document_data), file_extension=document.filename.split(".")[-1]
    )

    text = result.markdown
    text = clean_text(text)

    # Use the chunker to split the text into (header_path, content) tuples
    chunks_data = chunker(text)
    for chunks in chunks_data:
        print("CHUNK", chunks)
    
    if not chunks_data:
        raise ValueError("No chunks found")

    # Extract just the text content for bulk embedding
    chunk_texts = [chunk_text for _, chunk_text in chunks_data]
    
    # Get embeddings in bulk
    embedding_response = app.state.embedding.create(chunk_texts)
    