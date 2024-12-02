import streamlit as st
# Retriever tools
from libs.chatbot import Chatbot
from libs.vector_store import VectorStore
from libs.lexical_store import LexicalStore
from libs.document_indexer import DocumentIndexer
from libs.retriever import RetrieverQA
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
# For handling the load of documents
documents = DocumentIndexer()
# For handling the storage and retrieval of data chunks with semantic search
store = VectorStore()
# For handling the storage and retrieval of data chunks with lexical search
lexical = LexicalStore()

# A retriever for handling all the retrieval process
retriever = RetrieverQA(documents_=documents, stores=[store,lexical])
# 2. Incorporate the retriever into a question-answering chain.
# Load the Chatbot
bot = Chatbot(retriever)
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