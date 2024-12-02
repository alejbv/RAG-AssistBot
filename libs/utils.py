import requests
import numpy as np
import streamlit as st

def embed(texts):
    api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {st.secrets.API_KEY}"}
    response = requests.post(api_url, headers=headers, json={"inputs": texts, "options":{"wait_for_model":True}})
    return np.array(response.json()).astype(np.float32)
