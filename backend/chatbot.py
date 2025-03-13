from tqdm.auto import tqdm
from openai import AsyncOpenAI
from typing import Union,List,Dict, Callable
from backend.storage.collection import Collection

class Chatbot:
    def __init__(
        self,
        system_prompt: str,
        user_prompt:   str,
        base_url: str,
        api_key: str,
        inference_model: str,
        embedding_model: str,
        vector_dimension: int,
        text_split:    Callable,
        collection: Collection
    ) -> None:
        
        # Load config data
        self.text_split = text_split
        
        # DATABASE: MongoDB
        self.collection = collection
         
        # LLM Tools
        self.client = AsyncOpenAI(
                             base_url=base_url,
                             api_key=api_key
                            )
        
        self.inference_model = inference_model
        self.embedding_model = embedding_model
        self.vector_dimension= vector_dimension
        
        # Prompting Tools
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        
        # History        
        self.message_history = []
        
    
    
    def store(self, role: str, content:str):
        self.message_history.append(dict(role=role, content=content))

    def history(self, memory: Union[int,str]):
        if memory == 0:
            return []

        if memory == "all":
            messages = self.message_history
        else:
            messages = self.message_history[-memory:]

        return messages.copy()

    async def get_embeddings(self,documents:List[str]) -> List[float]:
        """Generate embeddings for the given documents using OpenAI's API.

        Args:
            documents (List[str]): The list of documents to get the embeddings

        Returns:
            ndarray: The embeddings of the documents
        """
        # Getting the embeddings
        try:      
            response = await self.client.embeddings.create(
                        input=documents,
                        model=self.embedding_model,
                        dimensions=self.vector_dimension
                        )
            return [doc.embedding for doc in response.data]
                
        except Exception as e:
            print(f"Error in get_embedding: {e}")
            return None
            
    
    async def store_file(self,data:Dict):
        """Function to store the file in the database"""
        
        embedding = await self.get_embeddings([data["summary"]])[0]
        data["embedding"] = embedding
        
        # Store the data in the database
        try:
            await self.collection.insert([data])
            print("File Stored")
            
        except Exception as e:
            print(f"Error in store_file: {e}")
        
    async def retrieve_context(self,query:str, limit: int=10):
        """Function to retrieve the file from the database"""
        # Get the embeddings of the query
        query_embedding = await self.get_embeddings([query])
        

        # Execute the pipeline to retrieve the chunks
        retrieved_chunks = await self.collection.search(query_embedding,limit=limit)
        return  ''.join([chunk['text'] for chunk in retrieved_chunks])
    
    async def _stream(self, messages: List[Dict]):
        try:
            result = []
            print("Changes Make")
            response = await self.client.chat.completions.create(
                                    messages=messages,
                                    model=self.inference_model,
                                    max_completion_tokens=2400, 
                                    temperature=0.4, 
                                    stream=True
                                )

            print("Client Ready")
            async for chunk in response :
                text = chunk.choices[0].delta.content
                
                if text:
                    current_output = text
                else:
                    current_output = ""
            
                result.append(current_output)

                yield current_output

            self.store("assistant", "".join(result))
        
        except Exception as e:
            print(f"Error in _stream: {e}")
            yield f"ERROR: {str(e)}".encode("utf-8")
            
    async def reply(
        self,
        query: str,
        memory:Union[int,str]="all",
        role:  str="user",
        store: bool=True,
    ):
        """Function to generate the response to a query

        Args:
            query (str):The query sent by the user
            memory (Union[int,str], optional): A list with the messages history. Defaults to "all".
            role (str, optional): The role of the . Defaults to "user".
            store (bool, optional): If store the query and the response. Defaults to True.

        Returns:
            _type_: _description_
        """
        # Retrieve the context 
        context = await self.retrieve_context(query) 
        # Retrive the history of the conversation with the user
        messages = self.history(memory)
        # Insert the system prompt at the beginning of the messages
        messages.insert(0, dict(role="system", content=self.system_prompt))

        # If the role is user, use the user prompt to generate the message
        if role == "user":
            current_message = self.user_prompt.format(query=query,context=context)
            # If store is True, store the message in the history
        if store:
            self.store(role, current_message)

        # Append the user message to the messages
        messages.append(dict(role=role, content=current_message))
        
        return self._stream(messages)
    