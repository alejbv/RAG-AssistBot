# import numpy as np
# d = 64                           # dimension
# nb = 100000                      # database size
# nq = 10000                       # nb of queries
# np.random.seed(1234)             # make reproducible
# xb = np.random.random((nb, d)).astype('float32')
# xb[:, 0] += np.arange(nb) / 1000.
# xq = np.random.random((nq, d)).astype('float32')
# xq[:, 0] += np.arange(nq) / 1000.

# import faiss
# import time

# nlist = 100
# k = 4
# quantizer = faiss.IndexFlatIP(d)  # the other index
# index = faiss.IndexIVFFlat(quantizer, d, nlist)

# start_training_time = time.time()

# assert not index.is_trained
# index.train(xb)
# assert index.is_trained

# end_training_time = time.time()

# print(f"It take {end_training_time-start_training_time}seconds to traing")

# index.add(xb)    # add may be a bit slower as well
# add_time = time.time()
# print(f"It take {add_time-end_training_time}seconds to add the elements")
# D, I = index.search(xq[:2], k)     # actual search
# print(I[-5:])                  # neighbors of the 5 last queries
# index.nprobe = 10            # default nprobe is 1, try a few more
# D, I = index.search(xq[:2], k)
# print(I[-5:])                  # neighbors of the 5 last queries

# print(f"It take {time.time()-add_time}seconds to search")

from libs.lexical_retriever import LexicalRetriever
from libs.vector_retriever import VectorRetriever
from libs.hybrid_retriever import HybridRetriever
from libs.basic_document_storage import BasicStorage
# The test
import ir_datasets
dataset = ir_datasets.load("cranfield")

prep_funct = lambda x: dict(doc_id=x[0],title=x[1],text=x[2],author=x[3],bib=x[4])
docs = list(map(prep_funct,dataset.docs_iter()))
queries = list(map(lambda x: x[1],dataset.queries_iter()))



# Preparing the Indexer
index = BasicStorage()
index.add_documents(docs)

# Preparing the retrievers
vector = VectorRetriever()
lexical = LexicalRetriever()
# Preparing the hybrid retrieval
retriever = HybridRetriever(documents_=index, stores=[vector,lexical])
# Adding the documents
retriever.add(docs)
# Getting  the result
result = retriever.search(queries[0])
print(result)
