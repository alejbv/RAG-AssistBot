from pydantic import BaseModel, Field, create_model
from typing import  Optional, Callable, Dict, List, Any
from .llm import LLM, Message
from .tool import Tool
from .prompts import  DEFAULT_SYSTEM_PROMPT, LEGAL_REACT_PROMPT, REPLY_PROMPT, INVOKE_ACTION, GENERATE_ARGS
import inspect


class Action(BaseModel):
    """Class to represent an action to perform with a tool."""
    name: str = Field(..., description="The name of the tool to use")
    reasoning: str = Field(..., description="The reasoning behind the action selection")

class Reasoning(BaseModel):
    question: str = Field(..., description="The question to answer")
    observation: str = Field(..., description="The current state of the task and the knowledge available")
    thought: str = Field(..., description="The thought process behind the next step")
    queries: Optional[List[str]] = Field(None, description="A list of queries to perform if information is needed")
    final: bool = Field(False, description="Whether the response is final or not")


class ToolResult(BaseModel):
    tool: str
    error: str | None = None
    result: Any | None = None


class Chatbot:
    def __init__(
        self,
        name: str,
        description: str,
        llm: LLM,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        tools: list[Tool] = [],
    ) -> None:
        
        # Setting the name and description
        self.name = name
        self.description = description
                
        # Setting parameters
        self.llm = llm
        self.system_prompt = system_prompt.format(name=name, description=description)
        self.tools: Dict[str, Tool] = {tool.name: tool for tool in tools} if tools else {}    
        
        # History
        self.messages: List[Message] = [Message.system(self.system_prompt)]
        
    
    def save(self, message: Message):
        """Function for savinig a message"""
        self.messages.append(message)

    
    def history(self, memory: Optional[int] = None) -> list[Message]:
        """Function to retrieve the history of the conversation with the user

        Args:
            memory (Union[int,None]): The number of messages to retrieve from the history.
                If memory is None, it returns all the messages in the history.

        Returns:
            list[Message]: A list with the messages history.
        """
        
        if memory:
            messages = self.messages[-memory:]  # Always returns a list

        else:
            messages = self.messages
    
        return messages.copy()


    async def generate_args(self, tool: Tool, messages: List[Message]) -> BaseModel:
        """Function to generate the arguments for a tool using the LLM."""
        
        # Preparing the parameters for generating the tool parameters
        parameters = tool.parameters()
        print(f"Parameters: {parameters}")
        
        # If parameters has only types, set default to ...
        model_fields = {}
        for param_name, param_type in parameters.items():
            if isinstance(param_type, tuple) and len(param_type) == 2:
                model_fields[param_name] = param_type
            else:
                model_fields[param_name] = (param_type, ...)
        
        tool_name_camel_case = ''.join(word.capitalize() for word in tool.name.split('_'))
        model_cls: type[BaseModel] = create_model(tool_name_camel_case, **model_fields)
        
        args_prompt = GENERATE_ARGS.format(
            name=tool.name,
            parameters=parameters,
            description=tool.description,
            format=model_cls.model_json_schema(),
        )
        
        response: BaseModel = await self.llm._parse(
            model=model_cls, 
            messages=messages + [Message.system(args_prompt)]
        )
        
        return response

    
    async def action(self,query: str, messages: List[Message]) -> ToolResult:
        """Function to select and perform an action using the tools available in the agent."""
        
        print(f"Query: {query}")
        tools = "\n".join(f"- Nombre Tool: {tool.name} Descripcion Tool: {tool.description}" for tool in self.tools.values())    
        action_prompt = INVOKE_ACTION.format(
                query=query,
                tools=tools,
                format= Action.model_json_schema()
            )
              
        action = await self.llm._parse(
            model=Action,
            messages=messages + [Message.system(action_prompt)] ,
        )
        
        # Preparando los argumentos para generar los parametros del tool
        name = action.name
        tool = self.tools[name]
        
        print(f"ACTION: {name}")
        #response = await self.generate_args(tool, messages)
        # Call the tool with the provided arguments
        #result = await tool.run(**response.model_dump())
        try:
            result = await tool.run(query=query)
        except Exception as e:
            return ToolResult(tool=tool.name, error=str(e))


        return ToolResult(
            tool=tool.name,
            result=result,
        )
    
    
    async def reply(self, query: str,messages: List[Message]) -> str:
        """Function to generate a response to the user using the LLM."""
        # Prepare the messages for the LLM
        messages.append(Message.system(REPLY_PROMPT.format(query=query)))
        # Call the LLM to generate the response
        response = await self.llm._chat(messages)
        
        # Save the response in the history
        self.save(Message.assistant(response))
        
        return response
    
    
    async def perform(self, query: str,  memory: Optional[int] = None, max_iterations: int = 5 ) -> str:
        """Function to generate an accurate response to a user need using the ReAcT pattern.
        Args:
            user_message (str):The query sent by the user
            memory (int, optional): A list with the messages history. Defaults to "None".
            
        Returns:
            str: The response of the assistant to the user
        """
        
        # Prepare the messages history
        messages = self.history(memory)
        messages.append(Message.user(query))
    
        for _ in range(max_iterations):
            # Call the LLM to generate the thinking process
            # Prepare the messages for the LLM
            messages.append(Message.system(LEGAL_REACT_PROMPT)) 
            
            reasoning = await self.llm._parse(
                model = Reasoning,
                messages=messages,
            )
            
            print(f"REASONING: {reasoning.model_dump_json()}")
            messages.append(Message.tool(reasoning.model_dump_json()))
            if reasoning.final:
                # If the reasoning is final, generate the response
                final_response = await self.reply(query, messages)
                return final_response
            
            # Check if the response contains an action to perform
            elif queries:= reasoning.queries:
                for query in queries:
                    # If the action is valid, use the corresponding tool
                    result = await self.action(query, messages)
                    # Save the current thought and the tool result
                    print(f"RESULT: {result.model_dump_json()}")
                    messages.append(Message.tool(result.model_dump_json()))

            
        final_response = await self.reply(query, messages)
        return final_response
            
   
    
        
    def tool(self, target: Callable) -> Tool:
        """
        Adds a method as a tool to the agent.

        The method must be an async function.
        """

        if isinstance(target, Tool):
            self.tools[target.name] = target
            return target

        if not callable(target):
            raise ValueError("Tool must be a callable.")

        if not inspect.iscoroutinefunction(target):
            raise ValueError("Tool must be a coroutine function.")

        tool = Tool.create_tool(target)
        self.tools[tool.name] = tool
        return tool