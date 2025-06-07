import re 
import psycopg
from os import getenv
from pathlib import Path
from psycopg.rows import dict_row
from typing import Iterable
#import pymupdf
import pymupdf4llm
from langchain.schema import Document
#from .llm import LLM, Message
from langchain.text_splitter import MarkdownTextSplitter
 

# Methods for loading the data and configuration
def load_data() -> Iterable[dict]:
    """Load the data from the Postgres database.

    Returns:
        Iterable[dict]: An iterable of the data contained in the database.
    """
    # Loading the configuration data
    # Setting the variables
    name= getenv("DATABASE")
    user= getenv("USER")
    pasw= getenv("PASSWORD")
    host= getenv("HOST","localhost")
    port= getenv("PORT","5432")
    
    # Up a connection to the database
    conn = psycopg.connect(conninfo= f"dbname={name} user={user} password={pasw} host={host} port={port}")
    # It return every row as a dictionary with the columns name as key an the values are the respective row value
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute("SELECT * from biblioteca_normativa;")        
        return cursor.fetchall()       
    
# # Methods for processing the data
# ## Methods for cleaning and preprocessing the data
# def get_text(text:str) -> str:
#     """Find all matches of a pattern in a text and return the correct form of the text. This method is for cleaning the text.
#     Args:
#         text (str): The text to search for matches.

#     Returns:
#         str: The cleaned text.
#     """
#     # Use re.finditer to get all matches
#     pattern = r"_+"
#     matches = re.finditer(pattern, text)
    
#     # Iterate through the matches and extract the information
#     positions = []
#     for match in matches:
#         start = match.start()  # Start index of the match
#         end = match.end()      # End index of the match
#         substring = match.group()  # Substring that matches the pattern
#         positions.append((substring, start, end))
    
#     # Get the correct text    
#     if len(positions)>= 2:
#         result = text[positions[0][2]:positions[1][1]]
    
#     elif len(positions)==1:
#         result = text[:positions[0][1]]
    
#     else:
#         result = text
    
#     return result.lower()


# def process_document(llm: LLM, doc:dict) -> dict:
#     """Preprocess the document for indexing. This method will clean the text and generate the embeddings for the summary. It will
#     also generate a summary if the document does not have one and split the text into chunks if it is too long.

#     Args:
#         doc (Dict): The document to preprocess

#     Returns:
#         Dict: A new document with the processed text and summary
#     """
#     # Step 1: Get the exact text from the document
#     new_doc = doc.copy()
#     new_doc["text"] = get_text(new_doc["text"])
    
#     # Step 2: Get the summaries and embeddings
#     if new_doc["summary"] != "":
#         new_doc["dense_vector"] =  llm._embedd([new_doc["summary"]])[0]  
    
#     elif new_doc["text"] != "":
#         # Get a summary
#         new_doc["summary"] = summarize_document(new_doc["text"])
#         new_doc["dense_vector"] =  llm._embedd([new_doc["summary"]])[0]  
    
#     else:
#         new_doc = None  
#     # Checkin if the document text have the right size
#     return new_doc


# def summarize_document(llm: LLM, text: str):
#     """
#     Generates a summary of a document using OpenAI.

#     Parameters:
#     - text (str): The text of the document you want to summarize.
#     - max_tokens (int): The maximum length of the summary in tokens (default: 100).

#     Returns:
#     - str: The generated summary.
#     """
#     try:
#         # Define the prompt for the summary
#         prompt = (
#             "Resume el siguiente texto legal de manera concisa, reteniendo todos los puntos clave, "
#             "definiciones importantes, obligaciones, derechos, sanciones y cualquier detalle relevante "
#             "esencial para entender la ley. El resumen debe ser claro, directo y usar la menor cantidad "
#             "de tokens posible. Evita omitir información crítica, ejemplos redundantes o lenguaje superfluo. "
#             "Asegúrate de mantener el tono formal y técnico del texto legal. Da la respuesta en un parrafo."
#             f"Texto legal: {text}"
#         )
#         msg = Message.system( prompt)
#         summary = llm._chat([msg], tools=None)
#         # Extract and return the summary
#         return summary

#     except Exception as e:
#         return f"Error generating summary: {e}"


def hierarchical_chunking(doc: dict, hierarchy: list[tuple] ,max_length: int = 2048) -> list[dict]:
    """Split the document into chunks based on the hierarchy. The hierarchy is a list of strings that represent the
    hierarchy of the document. 
    Args:
        doct (str): The text to split
        hierarchy (List[str]): The list of strings that represent the hierarchy of the document.
        max_length (int, optional): The max size of each chunk. Defaults to 1024.

    Returns:
        List[str]: The list of chunks of text.
    """
    # Split the text into sentences
    current_chunk = [doc]
    for h in hierarchy:
        new_chunk = []
        for chunk in current_chunk:
            # Check if the chunk is too long
            if len(chunk["text"]) > max_length:
            # Split the chunk into sentences
                new_chunk.extend(split_hierarchy(chunk, h))
            else:
                new_chunk.append(chunk)
        current_chunk = new_chunk
    
    return current_chunk


def split_hierarchy(doc: str, hierarchy: tuple) -> list[Document]:
    """Split the text into chunks of a given length. 

    Args:
        text (str): The text to split
        hierarchy (str): The string that represents the hierarchy of the document.
    Returns:
        List[Dict]: The list of chunks of text split by the hierarchy.
    """
    
    # Split the text into sentences
    chunks_iterator = list(re.split(hierarchy[0], doc["text"]))
    
    if len(chunks_iterator) == 1:
        return [doc]
    
    chunks = []
    for index,current in enumerate(chunks_iterator,start=1):
        new_chunk = doc.copy()
        new_chunk.update({
            "text": current,
            hierarchy[1]: index
        })
        chunks.append(new_chunk)
        
         
    return chunks


def split_text(texts: list[str], chunk_size: int = 2049, chunk_overlap: int = 516) -> list[str]:
    """Split the text into chunks of a given length. 

    Args:
        text (str): The text to split
        chunk_size (int, optional): The size of each chunk. Defaults to 2048.
        chunk_overlap (int, optional): The overlap between chunks. Defaults to 516.

    Returns:
        List[str]: The list of chunks of text.
    """
    # Split the text into chunks
    splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.create_documents(texts)


def save_md(md_text:bytes, file_path: Path):
    output_path = Path("test/")
    file_name = file_path.name.split('.')[0]
    file_output = output_path/Path(f'{file_name}.md')
    file_output.write_bytes(md_text)
    
    
def pdf_to_md(file_path: str) -> dict:
    """Function for extracting the gacetas information of each pdf file

    Args:
        file_path (str): The path of the pdf file to process

    Returns:
        dict: The information exctracted from the pdf file
    """
    
    md_text = pymupdf4llm.to_markdown(file_path)
    save_md(md_text.encode(),file_path)
    return md_text
    
    
def read_documents () -> list[dict]:
    """Function for loading and processing the data to store in the vector database

    Returns:
        list[dict]: A list with the metadata for each law/resolution
    """
    path = Path("gacetas/")
    documents = []
    for file_path in path.rglob("*.pdf"):
        documents.append(pdf_to_md(file_path))
    return documents


def extract_metadata(document: str) -> dict:
    """Extract the metadata from the document front page.
    Args:
        document (str): The text of the document to extract the metadata from.

    Returns:
        dict: A dictionary with the metadata of the document.
    """
    # Define a regex pattern to match the metadata
    pattern = r"(?P<key>[\w\s]+):\s*(?P<value>.+)"
    matches = re.findall(pattern, document)
    
    # Create a dictionary from the matches
    metadata = {key.strip(): value.strip() for key, value in matches}
    
    return metadata

def process_document(document:str):
    """
    Delimitadores y patrones para identificar secciones y subsecciones
    
    ______: Separador de pagina: Esto separa cada pagina del documento
    
    """
    raise NotImplementedError

if __name__=='__main__':
    documents = read_documents()
    #chunks = split_text(documents[:5])
    #print(chunks[0])