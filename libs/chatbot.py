import streamlit as st
from typing import Union,List,Dict
from libs.hybrid_retriever import RetrieverQA
from huggingface_hub import InferenceClient
from prompts.prompt import *


class Chatbot:
    def __init__(
        self,
        retriever: RetrieverQA,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        user_prompt:    str = DEFAULT_USER_PROMPT,
    ) -> None:
        # Retrieve Tools
        self.retriever = retriever
        
        # LLM Tools
        self.model = st.secrets.model
        self.client = InferenceClient(model=self.model,token=st.secrets.api_key)

        # Prompting Tools
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        
        if "history" not in st.session_state:
            st.session_state.history = []

    def reset(self):
        st.session_state.history.clear()

    def store(self, role: str, content:str):
        st.session_state.history.append(dict(role=role, content=content))

    def history(self, memory: Union[int,str]):
        if memory == 0:
            return []

        if memory == "all":
            messages = st.session_state.history
        else:
            messages = st.session_state.history[-memory:]

        return messages

    def _stream(self, messages: List[Dict]):
        result = []

        for chunk in self.client.chat.completions.create(messages=messages,max_tokens=256,temperature=0.4,stream=True):
            text = chunk.choices[0].delta.content
            result.append(text)
            yield text

        self.store("assistant", "".join(result))

    def _chat(self, messages: List[Dict]):
        response = (
            self.client.chat.completions.create(
                messages=messages,
                max_tokens=256,
                temperature=0.4
            )
            .choices[0]
            .message
        )
        print(response, flush=True)
        self.store("assistant", response.content)
        return response.content

    def submit(
        self,
        query: str,
        memory:Union[int,str]="all",
        role:  str="user",
        stream:bool=True,
        store: bool=True,
        user_prompt: str=None,
        **kwargs,
    ):
        messages = self.history(memory)
        if store:
            self.store(role, query)

        messages.insert(0, dict(role="system", content=self.system_prompt))

        if role == "user":
            if user_prompt is None:
                user_prompt = self.user_prompt

            query = user_prompt.format(input=query, **kwargs)

        messages.append(dict(role=role, content=query))

        if role == "user":
            if stream:
                return self._stream(messages)
            else:
                return self._chat(messages)

    def reply(self,query):
        """Function for reply to the user input. Also it handle the necessary steps to build the answer"""
        # First: Retrieve the context
        context = self.retriever.search(query)
        # Last : Generate a response for the user using the given context
        self.submit(query,store=True,stream=False,context=context)