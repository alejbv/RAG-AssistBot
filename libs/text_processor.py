from pathlib import Path
from typing import Set
from pypdf import PdfReader
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor

class TextProcessor:
    def __init__(self,data_path: str = "data/",filter = Set[str]):
        self.data_path = Path(data_path)
        self.data_filter = filter
        self.__load_data()
            
    def __load_data(self):
        document_info = {}
        documents = 1
        for file in self.data_path.iterdir():
            if file.suffix in self.data_filter:
                # Aqui abrir cada pdf individualmente y procesarlos
                # Preparing the reader for interacting with the pdf
                reader = PdfReader(BytesIO(file.read_bytes()))
                # Getting the information of the current document
                temporal_info = {}
                temporal_info['metadata'] = reader.metadata
                temporal_info['text'] = ''.join((page.extract_text() for page in reader.pages))

                # Saving the information
                document_info[documents] = temporal_info
                documents+=1

        
        self.documents_info = document_info                

    
    def process_document(self,document):
        pass        
        
if __name__ == '__main__':
    filter = ['.pdf']
    processor = TextProcessor(filter=filter)
    print(processor.documents_info[1]['metadata'].author)