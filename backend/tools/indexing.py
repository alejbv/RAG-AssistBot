import os
import asyncio
from tqdm import tqdm
from dotenv import load_dotenv
from backend.tools.collection import Collection
from backend.tools.utils import load_data, process_document

# Load the collection
print("### Loading the collection ###")
load_dotenv()
MILVUS_URI = os.getenv("MILVUS_URI", "")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN", "")
MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 768))


collection = Collection(MILVUS_URI, MILVUS_TOKEN, MILVUS_COLLECTION_NAME, EMBEDDING_DIMENSION)

loop = asyncio.get_event_loop()
loop.run_until_complete(collection.initialize_collection())
loop.close()

# Load the data from the database
print("### Loading the data ###")
documents = load_data()

# Preprocess the data before indexing
print("### Preparing the data ###")

data = []
for doc in tqdm(documents, desc="Creating documents"):
    new_docs = process_document(doc)
    if new_docs is not None:
        data.extend(new_docs)

# Insert the data into the collection
print("### Inserting the data in the collection ###")

size_step = int(len(data)*0.2)
for i in tqdm(range(0, len(data), size_step), desc="Inserting data"):
    collection.insert(data[i:size_step])

print("### Done ###")