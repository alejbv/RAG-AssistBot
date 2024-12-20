from libs.abstract_models.text_splitter import TextSplitter
from typing import List

# Dudas de cual usar
# 1. Recursive
# 2. Sentence
# 3. Semantic
# 4. Character
class BasicTextSplitter(TextSplitter):
    def __init__(self,chunk_size: int = 250 , overlap: int= 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def split_text(self, document: str) -> List[str]:
        """This Function take a document and split it in chunks of the size of the chunk_size and  with and overlap of 
        the overlap size
        Args:
            documents (str): The document to process

        Returns:
            A new List with the chunks of the document
        """
        # Split the document in tokens
        tokens = document.split()
        chunks = []
        # Iterate over the tokens
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            # Join the tokens in a chunk
            current_chunk =  ' '.join(tokens[i:i + self.chunk_size])
            chunks.append(current_chunk)
        
        return chunks