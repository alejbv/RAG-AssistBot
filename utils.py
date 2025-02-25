import re 
import tomli
import psycopg
import numpy as np
from openai import OpenAI
from psycopg.rows import dict_row
from typing import List, Iterable, Dict
from pymilvus import (
    connections,    
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
## Methods for loading the data and configuration
def load_config() -> Dict:
    """Load the configuration necessary for the application.

    Returns:
        Dict: The cnfiguration data.
    """
    with open(".secrets/config.toml", 'rb') as f:
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
    
def load_collection() -> Collection:
    """Load the collection from the Milvus database. If the collection does not exist, it will be created.

    Returns:
        Collection: The collection object.
    """
    config = load_config()
    
    # Connect to the database
    connections.connect(
        uri=config["MILVUS_URI"],
        token=config["MILVUS_API_KEY"],
    )
    
    # Check of collection exist. If not create collection
    if not utility.has_collection(config["MILVUS_COLLECTION_NAME"]):
        # Specify the data schema for the new Collection
        fields = [
        # Use the documents id as primary key
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="summary", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="organism", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="state", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="year", dtype=DataType.INT32),
            FieldSchema(name="normtype", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="number", dtype=DataType.INT32),
            FieldSchema(name="read_count", dtype=DataType.INT32),
            FieldSchema(name="slug", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="gazette", dtype=DataType.VARCHAR, max_length=256),
            # The vectors for hybrid retrieval
            #FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR),
            FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, dim=config["EMBEDDING_DIMENSION"]),
        ]

        # Create the collection schema
        schema = CollectionSchema(fields)
        # Create the collection with the schema
        col = Collection(config["MILVUS_COLLECTION_NAME"], schema, consistency_level="Strong")
        # To make vector search efficient, we need to create indices for the vector fields
        #sparse_index = {"index_type": "SPARSE_INVERTED_INDEX", "metric_type": "IP"}
        #col.create_index("sparse_vector", sparse_index)
        dense_index = {"index_type": "AUTOINDEX", "metric_type": "IP"}
        col.create_index("dense_vector", dense_index)

    else:
        # Load the existing collection
        col = Collection(config["MILVUS_COLLECTION_NAME"])
    
    # Load the data from the database
    col.load()
    
    return col

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

def process_documents(doc:Dict) -> Dict:
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
    
    return new_doc

## Methods for tokenizing and embedding the data
# def tokenize(documents: List[str]):
#     """Tokenize the documents using the spaCy library.
#     Args:
#         documents (List[Dict]): List of documents for tokenize
#     Returns:
#         List[List[str]]: List of tokenized documents
#     """
#     # Setting the variables
#     nlp = spacy.load("es_core_news_sm")
#     stopwords = set(nltk.corpus.stopwords.words('spanish'))
    
#     # Filters   
#     filter_punctuation = partial(filter,lambda token: not token.is_punct)
#     filter_stopwords = partial(filter,lambda token: token.lemma_ not in stopwords)
    
#     # Function for converting spacy.Token to str
#     converter = partial(map,lambda token: token.lemma_)
    
#     # First: tokenize the corpus
#     tokens = [[token for token in nlp(document.lower())] for document in documents]
    
#     # Second: remove the punctuation sings
#     no_punctuation = [list(filter_punctuation(tokens)) for tokens in tokens]    
    
#     # Third: remove the stopwords
#     no_stopwords   = [list(filter_stopwords(tokens)) for tokens in no_punctuation]
    
#     # Fourth: convert the tokens to string
#     corpus_tokens   = [list(converter(tokens))  for tokens in no_stopwords]
    
#     return corpus_tokens

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
                        dimensions=dimension#1536  
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
