import rich
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import TypeVar, Type, Union

T = TypeVar("T", bound=BaseModel)
Vector = list[float]


class Message(BaseModel):
    role: str
    content: str

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(role="assistant", content=content)




class LLM:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        inference_model: str,
        embedding_model: str,
        embedding_dimension: int,
        verbose:bool = False,
    ) -> None:
        
       
        self.verbose = verbose
        # Load configuration data
        self.inference_model = inference_model
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension
        # LLM Tools
        self.client = AsyncOpenAI(
                             base_url=base_url,
                             api_key=api_key,
                            )
        
    
    async def _chat(self, messages: list[Message], tools: Union[str,None] = None) -> str:
        
        params = {
            "messages": messages,
            "model": self.inference_model,
            "max_completion_tokens": 2400, 
            "temperature": 0.1, 
            "stream": True
        }
        
        if tools:
            params["tools"] = tools
        
        try:
            result = []
            async for chunk in await self.client.chat.completions.create(**params):
                content = chunk.choices[0].delta.content

                if content is None:
                    continue
                
                if self.verbose:
                    rich.print(content)
                
                result.append(content)

            
            return "".join(result)
                
        except Exception as e:
            print(f"Error in _chat: {e}")
            return f"ERROR: {str(e)}"
                
    
    async def _parse(self, model: Type[T], messages: list[Message], **kwargs) -> T:
        response = await self.client.beta.chat.completions.parse(
            model=self.inference_model,
            messages=[message.model_dump() for message in messages], # type: ignore
            response_format=model,
            **kwargs,
        )

        result = response.choices[0].message.parsed

        if self.verbose:
            rich.print(result)

        return result # type: ignore