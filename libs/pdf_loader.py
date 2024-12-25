from pathlib import Path
from typing import Set
from pypdf import PdfReader
from io import BytesIO
from libs.abstract_models.document_loader import DocumentLoader

class PDFLoader(DocumentLoader):
    def __init__(self, data_path: str = "data/", file_filter: Set[str] = None):
        # Call the parent constructor with the data_path and file_filter
        super().__init__(data_path, file_filter)
        # Setting the variable for the instance
        self.documents_info = {}
            
    def load_data(self):
        """This Function load the documents in the self._data_path
        """
        documents = 1
        for file in self.data_path.iterdir():
            if file.suffix in self.file_filter:
                # Here open the file and read the content
                # Preparing the reader for interacting with the pdf
                reader = PdfReader(BytesIO(file.read_bytes()))
                # Getting the information of the current document
                temporal_info = {}
                temporal_info['metadata'] = reader.metadata
                temporal_info['text'] = ''.join((page.extract_text() for page in reader.pages))

                # Saving the information
                self.documents_info[documents] = temporal_info
                documents+=1

        return self.documents_info
        
if __name__ == '__main__':
    file_filter = ['.pdf']
    processor = PDFLoader(file_filter=set(file_filter))
    print(processor.documents_info[1]['metadata'].author)