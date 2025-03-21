from utils import load_data, load_config, process_documents
from collection import Collection
from tqdm import tqdm 
from sys import exit
import asyncio
# Load the collection
print("### Loading the collection ###")
conf = load_config()
collection = Collection(conf["MILVUS_URI"], conf["MILVUS_TOKEN"], conf["MILVUS_COLLECTION_NAME"], conf["EMBEDDING_DIMENSION"])

loop = asyncio.get_event_loop()
loop.run_until_complete(collection.initialize_collection())
loop.close()

exit(0)

# Load the data from the database
print("### Loading the data ###")
documents = load_data()

# Preprocess the data before indexing
print("### Preparing the data ###")
data = []

for doc in tqdm(documents, desc="Creating documents"):
    new_doc= process_documents(doc)
    if new_doc:
        data.append(new_doc)

# Insert the data into the collection
print("### Inserting the data in the collection ###")

size_step = int(len(data)*0.2)
for i in tqdm(range(0, len(data), size_step), desc="Inserting data"):
    min_step = min(i+size_step, len(data))
    collection.insert(data[i:min_step])

print("### Done ###")