from libs.abstract_models.text_splitter import TextSplitter
from typing import List

# Dudas de cual usar
# 1. Recursive
# 2. Sentence
# 3. Semantic
# 4. Character
class BasicTextSplitter(TextSplitter):
    
    def split_text(self, documents: List[str]) -> List[str]:
        """This Function take a list of document and process them for a more easy way 

        Args:
            documents (List[str]): The list of document to process

        Returns:
            A new List of the document after they were processes
        """