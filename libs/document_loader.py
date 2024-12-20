from pathlib import Path
from typing import Set
from pypdf import PdfReader
from io import BytesIO

class DocumentLoader:
    def __init__(self,data_path: str = "data/",filter = Set[str]):
        # Setting the variables for the object
        self.data_path = Path(data_path)
        self.data_filter = filter
            
    def load_data(self):
        """This Function load the documents in the self._data_path
        """
        document_info = {}
        documents = 1
        for file in self.data_path.iterdir():
            if file.suffix in self.data_filter:
                # Here open the file and read the content
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
        
if __name__ == '__main__':
    filter = ['.pdf']
    processor = DocumentLoader(filter=filter)
    print(processor.documents_info[1]['metadata'].author)