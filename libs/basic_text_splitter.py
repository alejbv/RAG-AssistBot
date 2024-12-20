from libs.abstract_models.text_splitter import TextSplitter
from typing import List,Dict

# Dudas de cual usar
# 1. Recursive
# 2. Sentence
# 3. Semantic
# 4. Character
class BasicTextSplitter(TextSplitter):
    def __init__(self,chunk_size: int = 250 , overlap: int= 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def split_documents(self, documents: List[Dict]) -> List[Dict]:
        """This Function take a list of documents and split them in chunks. 
        Each with size the `chunk_size` and  with and overlap of 
        the `overlap` size
        
        Args:
            documents (List[Dict]): The document to process

        Returns:
            List[Dict]: The documents with the chunks of text
        """
        result = []
        for document in documents:
            # Split the document
            chunks = self.__split_document(document['text'])
            # Save the chunks
            for i, chunk in enumerate(chunks):
                result.append({
                    'metadata': document['metadata'],
                    'text': chunk,
                    'chunk_id': i
                })
        
        return result
    
    def __split_document(self, document: Dict) -> List[Dict]:
        # Split the document in tokens
        tokens = document.split()
        chunks = []
        # Iterate over the tokens
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            # Join the tokens in a chunk
            current_chunk =  ' '.join(tokens[i:i + self.chunk_size])
            chunks.append(current_chunk)
        
        return chunks