from pathlib import Path
from typing import Set
from pypdf import PdfReader
from io import BytesIO
from libs.abstract_models.document_processor import DocumentProcessor

class DocumentLoader:
    def __init__(self,processor: DocumentProcessor,data_path: str = "data/",filter = Set[str]):
        # Setting the variables for the object
        self.data_path = Path(data_path)
        self.data_filter = filter
        self.document_processor = processor
        # Call the methods for loading and prorcessing the documents in the data_path
        self.__load_data()
        self.__process_data()

            
    def __load_data(self):
        """This Function load the documents in the self._data_path
        """
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

    
    def __process_data(self):
        """This Function take the documents loaded in self.__load_data() and process all of them 
        
        """
        for document in self.documents_info.values():
            #
            document['text'] = self.document_processor.process_document(document['text'])

        
if __name__ == '__main__':
    filter = ['.pdf']
    processor = DocumentLoader(filter=filter)
    print(processor.documents_info[1]['metadata'].author)