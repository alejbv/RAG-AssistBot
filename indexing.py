from utils import load_data, load_collection, process_documents
from tqdm import tqdm 
# Load the data from the database
print("### Loading the data ###")
documents = load_data()

# Load the collection
print("### Loading the collection ###")
col = load_collection()

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
    if i+size_step > len(data):
        col.insert(data[i:])
    else:
        col.insert(data[i:i+size_step])

print("### Done ###")