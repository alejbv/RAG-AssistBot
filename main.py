import streamlit as st
# Retriever tools
from libs.chatbot import Chatbot
from libs.vector_retriever import VectorRetriever
from libs.lexical_retriever import LexicalRetriever
from libs.abstract_models.document_storage import DocumentStorage
from libs.hybrid_retriever import HybridRetriever
from libs.pdf_loader import PDFLoader
from libs.basic_text_splitter import BasicTextSplitter

"""WalkTrough
Indexing
Retrieve and Generation
1-User Query Input
    1.1-Query Analysis Techniques?
    1.2- Rewrite the query using the conversational history? (query, conversation history) -> LLM -> rephrased query -> retriever
2-Retrieve Chunks
    2.1-Chunk Strategies: 
    2.2-Index Strategies: Parent Document Retriever
    2.3-Retrieve Strategies: Hybrid Search with BM25 and Vector Embedding(Reranker)
    2.4-Contextual Compressor and Filters:
3-Augment Prompt
    3.1-Augment The Prompt with the data retrieved and the conversation history
    3.2-Manage Conversation History(Compress it)
4-Ask the model
5-Give the User the Response
"""
# 1. Load, chunk and index the contents of the blog to create a retriever.
# Load the documents
pdf_loader = PDFLoader()
documents = pdf_loader.load_data()
# Split the documents in chunks
splitter = BasicTextSplitter()
chunked_documents = splitter.split_documents(documents)
# Store the documents
storage = DocumentStorage()
storage.add_documents(chunked_documents)

# 2. Create a retriever to handle the retrieval process.
# For handling the storage and retrieval of data chunks with semantic search
semantic_retriever = VectorRetriever()
# For handling the storage and retrieval of data chunks with lexical search
lexical_retriever = LexicalRetriever()
# A retriever for handling all the retrieval process
hybrid_retriever = HybridRetriever(storage_= storage, retrievers=[semantic_retriever,lexical_retriever])

# 3. Load the Chatbot with the retriever
bot = Chatbot(hybrid_retriever)
st.title("Bot de Servicios Legales")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Input"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # The entire message history is passed to the model except for the last user entry, 
        # which will be passed to the model as a query.
        messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]
        # Passing the user input and the retrieved context to the bot
        #response = st.write_stream(bot.reply(user_input))
        response = st.write(bot.reply(user_input))
    st.session_state.messages.append({"role": "assistant", "content": response})