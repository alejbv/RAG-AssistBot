import json
import requests
import numpy as np
import tomli
import re

import os


EMBEDDING_MODEL = ""
API_KEY = ""

def load_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path,'conf.toml'), "rb") as f:
        data = tomli.load(f)
    return data

def embed(texts):
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/{EMBEDDING_MODEL}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
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

def find_matches_with_positions(text):
    """ Find all matches of a pattern in a text and return their positions. This method is for cleaning the text.
    Args:
        text (str): The text to search for matches.

    Returns:
        str: The cleaned text.
    """
    # Use re.finditer to get all matches
    pattern = r"_+"
    matches = re.finditer(pattern, text)
    
    # Iterate through the matches and extract the information
    positions = []
    for match in matches:
        start = match.start()  # Start index of the match
        end = match.end()      # End index of the match
        substring = match.group()  # Substring that matches the pattern
        positions.append((substring, start, end))
    
     # Print the results
    #for substring, start, end in positions:
    #    print(f"Substring: '{substring}', Start: {start}, End: {end}")
    
    if len(positions)>= 2:
        return text[positions[0][2]:positions[1][1]]
    
    elif len(positions)==1:
        return text[:positions[0][1]]
    
    else:
        return text
    
if __name__ == "__main__":
    # Example usage:
    json_response = "{'name': 'John', 'age': 30, 'city': 'New York',}"
    parsed_data = parse_json_string(json_response)
    
    if parsed_data is not None:
        print("Parsed JSON:", parsed_data)
    else:
        print("Parsing failed.")
