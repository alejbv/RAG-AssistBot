import requests
import numpy as np
import streamlit as st

def embed(texts):
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/{st.secrets.EMBEDDING_MODEL}"
    headers = {"Authorization": f"Bearer {st.secrets.API_KEY}"}
    # Si no hay problemas con el tiempo de espera cuando se hace la solicitud
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": texts, "options":{"wait_for_model":True}})
        result = np.array(response.json()).astype(np.float32)
    
    # Si hay un límite con la cantidad de solicitudes
    except Exception as e:
        m = len(texts)
        first_half = embed(texts[:m])
        second_half = embed(texts[m:])
        result = np.concatenate([first_half,second_half])
    
    return result
    
