import requests
import streamlit as st
from tqdm import tqdm
from pypdf import PdfReader
from io import StringIO, BytesIO


URL = "http://fastapi:80"

st.title("Test Interface")

with st.sidebar:
    files = st.file_uploader("Subir archivo", type=["md", "txt","pdf", "docx"],accept_multiple_files=True)
    if files:
        for file in tqdm(files,desc="Uploading files"):
            if file.name.endswith(".pdf"):
                reader = PdfReader(BytesIO(file.getvalue()))
                # Getting the information of the current document
                content = ''.join((page.extract_text() for page in reader.pages))
            
            else:
                content = StringIO(file.getvalue().decode("utf-8",errors='replace')).read()
            
            data = {"file": content}
            resp = requests.post(f"{URL}/update",json=data)
            print("Request Send")
    
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
        
        data = {"query": user_input}
        # Process Message
        try:
            response = requests.post(f"{URL}/chat",json=data,stream=True)
            response.raise_for_status()
            iter_response = response.iter_content(chunk_size=None, decode_unicode=True)
            final_response = st.write_stream(iter_response)
        except requests.exceptions.ChunkedEncodingError:
            st.error("Connection interrupted while streaming response")
            final_response = ""
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to API server")
            final_response = ""
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
            final_response = ""
        
        if final_response:
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": final_response})