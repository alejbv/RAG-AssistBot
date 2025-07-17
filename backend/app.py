from fastapi import BackgroundTasks, FastAPI, File, UploadFile
from contextlib import asynccontextmanager
from models import Query
from fastapi.responses import StreamingResponse

from os import getenv
from dotenv import load_dotenv
from framework import Collection, LLM, Chatbot, Embedding, Chunker,Resolver , web_search#,retrieve_context
import markitdown
import io



# Load configuration data
load_dotenv('.env')  

# Getting the collection
collection = Collection(
        getenv("MILVUS_URI",""),
        getenv("MILVUS_TOKEN",""),
        getenv("MILVUS_COLLECTION_NAME",""),
        int(getenv("EMBEDDING_DIMENSION",""))
)

# Initializing the LLM
llm = LLM(
    getenv("BASE_URL",""),
    getenv("API_KEY",""), 
    getenv("INFERENCE_MODEL","")
)
embedding = Embedding(
    getenv("API_KEY",""),
    getenv("BASE_URL",""),
    getenv("EMBEDDING_MODEL","")
)


# Setting the chatbot
bot = Chatbot(llm)


resolver = Resolver()
resolver.register(embedding)
resolver.register(collection)

# retrieve_context = resolver.wrap(retrieve_context)
# retrieve_context = bot.tool(retrieve_context)
web_search = resolver.wrap(web_search)
web_search = bot.tool(web_search)

# Create the FastAPI app with a lifespan event handler to create the search index on startup    
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function to be executed before starting the application. It initializes the chatbot and the collection.

    Args:
        app (FastAPI): The FastAPI instace
    """
    
    app.state.bot = bot
    app.state.resolver = resolver
    app.state.collection = collection
    await app.state.collection.initialize_collection()
    
    yield
    # Closing the connection to the client
    await app.state.collection.close()

app = FastAPI(lifespan=lifespan)


# Endpoint for files POST
@app.post("/upload/")
async def add_file(tasks: BackgroundTasks, file: UploadFile = File(...),):
   document_data = await file.read()
   tasks.add_task(process_file, file.filename, document_data) # type: ignore
   
   return {"message": "File upload started", "filename": file.filename}

def process_file(file_name: str, file_data: bytes):
    """Function to process the file and store it in the database"""
     
    converter = markitdown.MarkItDown()
    result = converter.convert_stream(
        io.BytesIO(file_data), file_extension=file_name.split(".")[-1]
    )

    text = result.markdown
    
    chunker = Chunker().hierarchial_markdown_chunker()
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
    if not embedding_response or len(embedding_response) != len(chunk_texts):
        raise ValueError("Embedding creation failed. Please check the input data.")
    
    data = []
    for chunk, embedding in zip(chunks_data, embedding_response):
        header_path, content = chunk
        data.append({
            "text": content,
            "header_path": header_path,
            "embedding": embedding
        })
        
        # Store the file in the database

        
# Endpoint for query POST
@app.post("/chat/")
async def chat(query_request: Query) -> StreamingResponse:
  user_response = await app.state.bot.perform(query_request.query)
  return StreamingResponse(user_response, media_type="text/plain")


# # Endpoint for retrieval POST
# @app.post("/retrieve/")
# async def retrieve(query_request: Query) -> List[Normativa]:
#     """Function to retrieve the documents from the database using the query"""
#     normativas = await retrieve_documents(app.state.llm, app.state.collection, query_request.query)
#     return [Normativa.model_validate(doc) for doc in normativas]



    