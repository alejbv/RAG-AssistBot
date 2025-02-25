import json
import tomli
import numpy as np
from openai import OpenAI
from typing import List


def load_client():
    with open(".secrets/config.toml", 'rb') as f:
        config = tomli.load(f)   
        client = OpenAI(base_url=config["BASE_URL"],api_key=config["API_KEY"])
        model = config["EMBEDDING_MODEL"]
        dimension = config["EMBEDDING_DIMENSION"]
        
    return client,model,dimension

def embed(documents: List[str]):
    client,model,dimension = load_client()
    embeddings = []
    try:
        for doc in documents:            
            response = client.embeddings.create(
                        input=[doc],
                        model=model,
                        dimensions=dimension#1536  
                        )
            embeddings.append(response.data[0].embedding)
    except Exception as e:
        print(e)
        
    return np.array(embeddings)    

#TODO: Revisar que funcione: Este metodo no funciona con el embedding que se esta usando(nomic)
def batch_embed(documents: List[str],batch_size=300):
    client,model,dimension = load_client()
    embeddings = []
    try:
        for rng in range(len(documents),batch_size):
            docs = documents[rng:rng+batch_size]
            # Aqui deberia ir otra api de infenercia o otro modelo
            response = client.embeddings.create(
                        input=docs,
                        model=model,
                        dimensions=dimension#1536
                        )
            embeddings.extend([np.asarray(d.embedding) for d in response.data])
    except Exception as e:
        print(e)
    
    return np.array(embeddings)

def parse_json_string(json_string):
    """
    Parses a JSON string and attempts to fix common errors before loading it into a Python dictionary.
    
    Parameters:
        json_string (str): The JSON string to parse.
        
    Returns:
        dict: The parsed JSON as a Python dictionary, or None if parsing fails.
    """
    try:
        # Attempt to load the JSON string directly
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        
        # Attempt to fix common issues in the JSON string
        # Example fixes:
        # 1. Replace single quotes with double quotes
        fixed_string = json_string.replace("'", '"')
        
        # 2. Remove trailing commas (if any)
        fixed_string = fixed_string.rstrip(", ")
        
        # 3. Add missing quotes around keys if necessary (basic check)
         # Asegura que cada par clave-valor esté correctamente formateado
        fixed_string = [
            f'"{k.strip()}": {v.strip()}' if ':' in item else item 
            for item in fixed_string.split(',')
            for k, v in [item.split(':', 1)] if ':' in item
        ]

        
        try:
            # Try loading the fixed JSON string
            return json.loads(fixed_string)
        except json.JSONDecodeError as e:
            print(f"Failed to parse fixed JSON: {e}")
            return None
  
if __name__ == "__main__":
    # Example usage:
    json_response = "{'name': 'John', 'age': 30, 'city': 'New York',}"
    parsed_data = parse_json_string(json_response)
    
    if parsed_data is not None:
        print("Parsed JSON:", parsed_data)
    else:
        print("Parsing failed.")
