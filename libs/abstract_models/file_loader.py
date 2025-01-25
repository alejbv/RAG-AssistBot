from pathlib import Path
from typing import Set
from libs.abstract_models.document_loader import DocumentLoader

class FileLoader(DocumentLoader):
    def __init__(self,data_path: str = "source/", file_filter: Set[str] = None):
        # Setting the variables for the object
        self.data_path = Path(data_path)
        self.file_filter = file_filter if file_filter is not None else set()
    