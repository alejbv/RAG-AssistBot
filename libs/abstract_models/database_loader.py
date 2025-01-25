import tomli
from libs.abstract_models.document_loader import DocumentLoader


class DatabaseLoader(DocumentLoader):
    def __init__(self):
        with open(".secrets/config.toml", 'rb') as f:
            config=tomli.load(f)        
            self.databse=config["DATABASE"]
            self.user=config["USER"]
            self.password=config["PASSWORD"]
            self.host=config["HOST"]
            self.port=config["PORT"]