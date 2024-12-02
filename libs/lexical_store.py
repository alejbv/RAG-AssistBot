import spacy
import nltk
from bm25s import BM25
from typing import List,Dict
from functools import partial
from libs.store import Store
class LexicalStore(Store):
    def __init__(self) -> None:        
        self.retriever = BM25()
        self.nlp = spacy.load("es_core_news_sm")
        self.stopwords = set(nltk.corpus.stopwords.words('spanish'))
        #self._data = []
    
    def tokenize(self, documents):
        """Function 
        Args:
            documents (List[Dict]): List of documents for tokenize
        Returns:
            List[List[str]]: List of all the tokens sequence with a set of documents
        """
        # Filters   
        filter_punctuation = partial(filter,lambda token: not token.is_punct)
        filter_stopwords = partial(filter,lambda token: token.text not in self.stopwords)
        
        # Function for converting spacy.Token to str
        converter = partial(map,lambda token: token.text)
        
        # First: tokenize the corpus
        firs_tokens = [[token for token in self.nlp(document.lower())] for document in documents]
        
        # Second: remove the punctuation sings
        no_punctuation = [list(filter_punctuation(tokens)) for tokens in firs_tokens]    
        
        # Third: remove the stopwords
        no_stopwords   = [list(filter_stopwords(tokens))   for tokens in no_punctuation]
        
        # Fourth: convert the tokens to string
        corpus_tokens   = [list(converter(tokens))   for tokens in no_stopwords]
        
        return corpus_tokens
    
    def add(self, documents: List[Dict]):
        """ Function por add a new set of documents to the corpus
        Args:
            documents (List[Dict]): The list of new documents to add to the corpus
        """
        # First: Tokenize the corpus
        to_tokenize = map(lambda x: x["text"],documents)
        corpus_tokens = self.tokenize(to_tokenize)
        
        # Second: Indexing the corpus in the BM25 model
        self.retriever.index(corpus_tokens)
        
        # Last: Extend the currente dataset
        #self._data.extend(documents)

    def search(self, query: List[str], k: int=50):
        """Function for searching given a query a set of document similar to that query

        Args:
            query (List[str]): The queries for search
            k (int, optional): The number of document to retrieve. Defaults to 20.

        Returns:
            Tuple[List[str],List[float]]:Return the document retrieve given the query and the ranking score for each one
        """
        # First: Tokenize the query
        query_tokens = self.tokenize(query)
        
        # Second: Get top-k results as a tuple of (doc ids, scores). Both are arrays of shape (n_queries, k)
        results, scores = self.retriever.retrieve(query_tokens, k=k)
        return results[0],scores[0]

    
    
if __name__ == '__main__':
    from spacy.lang.es.examples import sentences 
    corpus = [dict(text=document,metadata={}) for document in sentences]
    store = LexicalStore()
    store.add(corpus)
    print(store.search([sentences[1]],k=5))
    
    
    
    
    