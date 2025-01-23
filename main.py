import streamlit as st
# Retriever tools
from libs.agent.chatbot import Chatbot
from libs.retrieval.vector_retriever import VectorRetriever
from libs.retrieval.lexical_retriever import LexicalRetriever
from libs.storage.basic_document_storage import BasicStorage
from libs.retrieval.hybrid_retriever import HybridRetriever
from libs.loaders.pdf_loader import PDFLoader
from libs.splitters.basic_text_splitter import BasicTextSplitter

# Prompt Tools
from prompts.academic_assistant_prompt import system_prompt as academic_system_prompt
from prompts.academic_assistant_prompt import user_prompt as academic_user_prompt

# 1. Load, chunk and index the contents of the blog to create a retriever.
# Load the documents
pdf_loader = PDFLoader(file_filter={".pdf"})
documents = pdf_loader.load_data()
# Split the documents in chunks
splitter = BasicTextSplitter()
chunked_documents = splitter.split_documents(documents)
# Store the documents
basic_storage = BasicStorage()
basic_storage.add_documents(chunked_documents)

# 2. Create a retriever to handle the retrieval process.
# For handling the storage and retrieval of data chunks with semantic search
semantic_retriever = VectorRetriever()
# For handling the storage and retrieval of data chunks with lexical search
lexical_retriever = LexicalRetriever()
# A retriever for handling all the retrieval process
hybrid_retriever = HybridRetriever(storage_= basic_storage, retrievers=[semantic_retriever,lexical_retriever])
# Add the documents to the retriever
print("Adding documents to the retriever")
hybrid_retriever.add(chunked_documents)

# 3. Load the Chatbot with the retriever
bot = Chatbot(hybrid_retriever,
              system_prompt=academic_system_prompt, 
              user_prompt=academic_user_prompt
)

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