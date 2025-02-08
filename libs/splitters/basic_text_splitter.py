from libs.abstract_models.text_splitter import TextSplitter
from typing import List,Dict

# Dudas de cual usar
# 1. Recursive
# 2. Sentence
# 3. Semantic
# 4. Character
class BasicTextSplitter(TextSplitter):
    def __init__(self,chunk_size: int = 512 , overlap: int= 20) -> None:
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
        count = 1
        document_id = 0
        
        for document in documents:
            # Split the document calling the private function __split_document for each document
            document_id += 1
            chunks = self.__split_document(document['text'])
            
            chunk_metadata = {key: value for key, value in document['metadata'].items()}
            # Save the chunks
            for i, chunk in enumerate(chunks):
                result.append({
                    'id': f"{document_id}-{i}",
                    'text': chunk,
                    'document_id': document_id,
                    'chunk_id': i,
                    'chunk_index': count,
                    **chunk_metadata
                })
                count += 1
        
        return result
    
    def __split_document(self, document: Dict) -> List[Dict]:
        """This is a private function that split a document in chunks of text

        Args:
            document (Dict): The document to split

        Returns:
            List[Dict]: The chunks of the document
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