import tomli
from openai import OpenAI

from typing import Union,List,Dict
from libs.retrieval.hybrid_retriever import HybridRetriever
from libs.prompts.prompt import *
from pydantic import BaseModel

class PromptFormat(BaseModel):
    #context: str
    query: str
    reasoning_steps: str
    response: str



class Chatbot:
    def __init__(
        self,
        retriever: HybridRetriever,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        user_prompt:   str = DEFAULT_USER_PROMPT,
    ) -> None:
        # Retrieve Tools
        self.retriever = retriever
        
        # LLM Tools
        with open(".secrets/config.toml", 'rb') as f:
            config = tomli.load(f)
            self.client = OpenAI(
                                 base_url=config["BASE_URL"],   
                                 api_key=config["API_KEY"]
                                )
        
        self.model = config["INFERENCE_MODEL"],
        # Prompting Tools
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        
        # History        
        self.message_history = []
        self.store("system", self.system_prompt)

    def reset(self):
        self.message_history.clear()

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

    def _stream(self, messages: List[Dict]):
        result = []

        for chunk in self.client.chat.completions.create(messages=messages,max_tokens=256,temperature=0.4,stream=True):
            text = chunk.choices[0].delta.content
            result.append(text)
            yield text

        self.store("assistant", "".join(result))

    def _chat(self, messages: List[Dict]):
        response = (
            self.client.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2400,
                temperature=0.4,
                response_format={"type": "json", "value": PromptFormat.model_json_schema()},
            )
            .choices[0]
            .message
        )
        #print(response.content, flush=True)
        return PromptFormat.model_validate_json(response.content)

    def submit(
        self,
        query: str,
        memory:Union[int,str]="all",
        context: str="",
        role:  str="user",
        store: bool=True,
        stream:bool=True
    ):
        # Retrive the history of the conversation with the user
        messages = self.history(memory)
        # If the memory is not all, insert the system prompt at the beginning of the messages
        if memory != "all":
            messages.insert(0, dict(role="system", content=self.system_prompt))

        # If the role is user, use the user prompt to generate the message
        if role == "user":
            current_message = self.user_prompt.format(context=context,query=query)
            # If store is True, store the message in the history
        if store:
            self.store(role, current_message)

        # Append the user message to the messages
        messages.append(dict(role=role, content=current_message))
        
        if stream:
            return self._stream(messages)
        else:
            message = self._chat(messages)
            # Store the response in the history
            self.store("assistant", message.response)
            return message.response

    def reply(self,query):
        """Function for reply to the user input. Also it handle the necessary steps to build the answer"""
        # First: Retrieve the context
        retrieved_chunkst = self.retriever.search(query)
        #Get only the text context
        context = ''.join([chunk['text'] for chunk in retrieved_chunkst])
        # Last : Generate a response for the user using the given context
        return self.submit(query,store=True,context=context,stream=False)