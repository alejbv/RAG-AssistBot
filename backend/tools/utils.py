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
#from langchain.text_splitter import MarkdownTextSplitter
from langchain.text_splitter import  MarkdownHeaderTextSplitter

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


def split_hierarchy(doc: dict, hierarchy: tuple) -> list[dict]:
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


def split_text(texts: str, headers) -> list[Document]:
    """Split the text into chunks of a given length. 

    Args:
        text (str): The text to split
        chunk_size (int, optional): The size of each chunk. Defaults to 2048.
        chunk_overlap (int, optional): The overlap between chunks. Defaults to 516.

    Returns:
        List[str]: The list of chunks of text.
    """
    # Split the text into chunks
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers,strip_headers=False)
    return splitter.split_text(texts)


def save_md(md_text:bytes, file_path: Path):
    output_path = Path("test/")
    file_name = file_path.name.split('.')[0]
    file_output = output_path/Path(f'{file_name}.md')
    file_output.write_bytes(md_text)
    
    
def pdf_to_md(file_path: Path) -> str:
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
        
        
    Posible metadata:
        - Título
        - Fecha de publicación
        - Número de gaceta
        - Organismo emisor
        - Tipo de normativa
        - Estado (vigente, derogada, etc.)
        - Texto completo
        - Enlace al documento completo
    """
    # Define a regex pattern to match the metadata
    METADATA_SEP = [
                (r"\n#{1,6} ","Encabezados"), 
                (r"\*\*.*?\*\*","Enunciados")
            ]
    
    matches = []
    for pattern, key in METADATA_SEP:
        found = re.findall(pattern, document)
        for value in found:
            matches.append((key, value))
    
    # Create a dictionary from the matches
    metadata = {key.strip(): value.strip() for key, value in matches}
    
    return metadata

def process_document(document:str):
    """
    Delimitadores y patrones para identificar secciones y subsecciones
    
    ______: Separador de pagina: Esto separa cada pagina del documento
    
    """
    # Separar por paginas usando RESOLUTION_SEP
    RESOLUTION_SEP = r"^___+\n"
    pages = re.split(RESOLUTION_SEP, document, flags=re.MULTILINE)
    
    metadata = extract_metadata(pages[0])
    # Separar por secciones jerarquicas usando DOCUMENT_SEP
    DOCUMENT_SEP = [
            (r"CAP[IÍ]TULO","Capitulo"),
            (r"ART[IÍ]CULO","Articulo"),
            (r"ACUERDO","Acuerdo"),
            (r"ANEXO","Anexo"),
            (r"^[A-Z]+:","Declaración"),
            (r"\d+\.\s","Numeración"),
            (r"[a-z]\)","Inciso"),
            (r"\n\n","Parrafo"),
            (r"\n","Saltos de linea")
        ]
    
    chunks = []
    
    for page in pages[1:]:
        # Before chunking, clean the text
        # Header
        page = re.sub(r"\*\*Gaceta Oficial de la República\*\*","",page)
        page = re.sub(r"GACETA OFICIAL", "", page)
        # Page Number
        page = re.sub(r"\*\*\d+\*\*","",page)
        
        # Dates
        page = re.sub(r"\*\*\d{2}/\d{2}/\d{4}\*\*","",page)
        
        page = re.sub(r'GOC-\d{4}-.+',"",page)
        # In case de some asterics left
        page = re.sub(r"\*{2,4}","",page)
        
        # Multiple lines
        page = re.sub(r"\n{3,}","\n\n",page)
        
        page_chunks = split_text(page,DOCUMENT_SEP)
        # page_chunks = hierarchical_chunking(
        #     {"text": page, **metadata}, 
        #     DOCUMENT_SEP, 
        #     max_length=2048 
        # )
        chunks.extend(page_chunks)
    
    return chunks

if __name__=='__main__':
    #documents = read_documents()
    file = "test/GO_151_29_Diciembre_2021_ordinaria.md"#"test/GO_01_04_Enero_2024_ordinaria.md"
    file = Path(file).read_text()
    r = process_document(file)
    for p in r:
        print(p)
        print("_____")
    #chunks = split_text(documents[:5])
    #print(chunks[0])