import re 
import tomli
import psycopg
import numpy as np
from openai import OpenAI
from psycopg.rows import dict_row
from typing import List, Iterable, Dict
## Methods for loading the data and configuration
def load_config() -> Dict:
    """Load the configuration necessary for the application.

    Returns:
        Dict: The configuration data.
    """
    with open("../.secrets/config.toml", 'rb') as f:
        config = tomli.load(f)   
    return config

def load_data() -> Iterable[Dict]:
    """Load the data from the Postgres database.

    Returns:
        Iterable[Dict]: An iterable of the data contained in the database.
    """
    # Loading the configuration data
    config = load_config()
    # Setting the variables
    name=config["DATABASE"]
    user=config["USER"]
    passw=config["PASSWORD"]
    host=config["HOST"]
    port=config["PORT"]
    
    # Up a connection to the database
    conn = psycopg.connect(conninfo= f"dbname={name} user={user} password={passw} host={host} port={port}")
    # It return every row as a dictionary with the columns name as key an the values are the respective row value
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute("SELECT * from biblioteca_normativa;")        
        return cursor.fetchall()       
    
## Methods for cleaning and preprocessing the data
def __process_text(text:str) -> str:
    """Find all matches of a pattern in a text and return the correct form of the text. This method is for cleaning the text.
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
    
    # Get the correct text    
    if len(positions)>= 2:
        return text[positions[0][2]:positions[1][1]]
    
    elif len(positions)==1:
        return text[:positions[0][1]]
    
    else:
        return text    

def process_document(doc:Dict) -> Dict:
    """Preprocess the document for indexing. This method will clean the text and generate the embeddings for the summary.

    Args:
        doc (Dict): The document to preprocess

    Returns:
        Dict: A new document with the processed text and summary
    """
    # Cleaning the text    
    new_doc = doc.copy()
    new_doc["text"] = __process_text(new_doc["text"])
    
    # Processing the summary
    if new_doc["summary"] != "":
        new_doc["dense_vector"] =  get_embeddings([new_doc["summary"]])[0]
    
    elif new_doc["text"] != "":
        # Get a summary
        new_doc["summary"] = summarize_document(new_doc["text"])
        new_doc["dense_vector"] =  get_embeddings([new_doc["summary"]])[0]

    else:
        new_doc = None
    
    # Checkin if the document text have the right size
    return new_doc

def get_embeddings(documents: List[str]) -> List[np.ndarray]:
    # Loading configutation for embeddings
    config = load_config()
    # Setting the embedding
    client = OpenAI(base_url=config["BASE_URL"],api_key=config["API_KEY"])
    model = config["EMBEDDING_MODEL"]
    dimension = config["EMBEDDING_DIMENSION"]
    # Getting the embeddings
    embeddings = []
    try:
        for doc in documents:            
            response = client.embeddings.create(
                        input=[doc],
                        model=model,
                        dimensions=dimension
                    )        
            embeddings.append(response.data[0].embedding)
    
    except Exception as e:
        print(e)
        
    return np.array(embeddings)    

def summarize_document(text):
    """
    Generates a summary of a document using OpenAI.

    Parameters:
    - text (str): The text of the document you want to summarize.
    - max_tokens (int): The maximum length of the summary in tokens (default: 100).

    Returns:
    - str: The generated summary.
    """
    # Call the OpenAI API
    config = load_config()
    client = OpenAI(base_url=config["BASE_URL"], api_key=config["API_KEY"])
    model = config["INFERENCE_MODEL"]
    try:
        # Define the prompt for the summary
        prompt = (
            "Resume el siguiente texto legal de manera concisa, reteniendo todos los puntos clave, "
            "definiciones importantes, obligaciones, derechos, sanciones y cualquier detalle relevante "
            "esencial para entender la ley. El resumen debe ser claro, directo y usar la menor cantidad "
            "de tokens posible. Evita omitir información crítica, ejemplos redundantes o lenguaje superfluo. "
            "Asegúrate de mantener el tono formal y técnico del texto legal. Da la respuesta en un parrafo."
            f"Texto legal: {text}"
        )
        response = client.completions.create(
            model=model,  # Model to use
            prompt=prompt,  # Prompt for the completion
            max_tokens=256,  # Maximum number of tokens to generate
            temperature=0.3  # Controls creativity (0 = more deterministic, 1 = more creative)
        )

        # Extract and return the summary
        summary = response.choices[0].text.strip()
        return summary

    except Exception as e:
        return f"Error generating summary: {e}"


def basic_text_split(text: str, max_length: int = 256, overlap=20) -> List[str]:
    """Split the text into chunks of a given length. 

    Args:
        text (str): The text to split
        max_length (int, optional): The max size of each chunk. Defaults to 256.
        overlap (int, optional): The overlap between chunk. Defaults to 20.

    Returns:
        List[str]: The list of chunks of text.
    """
    
    tokens = text.split()
    return [" ".join(tokens[i:i + max_length])for i in range(0, len(tokens), max_length - overlap)]