from pydantic import BaseModel, Field, create_model
from typing import  Optional, Callable, Dict, List
from .llm import LLM, Message
from .tool import Tool
from .prompts import LEGAL_REACT_PROMPT, INVOKE_ACTION, GENERATE_ARGS
import inspect


class Action(BaseModel):
    """Class to represent an action to perform with a tool."""
    name: str = Field(..., description="The name of the tool to use")
    thought: str = Field(..., description="The thought process behind the action")

class Reasoning(BaseModel):
    observation: str
    thought: str
    query: str | None = None
    final: bool    


class Chatbot:
    def __init__(
        self,
        llm: LLM,
        prompt_template: str = LEGAL_REACT_PROMPT,
        tools: list[Tool] = [],
    ) -> None:
                
        # Setting parameters
        self.llm = llm
        self.prompt_template = prompt_template
        self.tools: Dict[str, Tool] = {tool.name: tool for tool in tools} if tools else {}    
        # History
        self.messages: List[Message] = []
        
        
    
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


    async def action(self,query: str, messages: List[Message]) -> str:
        """Function to select and perform an action using the tools available in the agent."""
        
        print(f"Query: {query}")
        tools = "\n".join(f"- Nombre Tool: {tool.name} Descripcion Tool: {tool.description}" for tool in self.tools.values())    
        action_prompt = INVOKE_ACTION.format(
                query=query,
                tools=tools
            )
              
        action = await self.llm._parse(
            model=Action,
            messages=messages + [Message.system(action_prompt)] ,
        )
        
        
        # Preparando los argumentos para generar los parametros del tool
        name = action.name
        tool = self.tools[name]
        
        parameters = tool.parameters()
        
        print(f"Action: {action.thought}")
        print(f"Tool: {name} ")   
        tool_name_camel_case = ''.join(word.capitalize() for word in tool.name.split('_'))

        # parameters debe ser un dict con nombre: (tipo, default)
        # Si parameters tiene solo tipos, poner default en ...
        model_fields = {}
        for param_name, param_type in parameters.items():
            if isinstance(param_type, tuple) and len(param_type) == 2:
                model_fields[param_name] = param_type
            else:
                model_fields[param_name] = (param_type, ...)
        model_cls: type[BaseModel] = create_model(tool_name_camel_case, **model_fields)

        
        
        args_prompt = GENERATE_ARGS.format(
            name=tool.name,
            parameters= parameters,
            description=tool.description,
            format=model_cls.model_json_schema(),
        )

        
        response: BaseModel = await self.llm._parse(
            model=model_cls, 
            messages=messages + [Message.system(args_prompt)]
        )

        
        # Call the tool with the provided arguments
        result = await tool.run(**response.model_dump())
        
        return f"Observation from tool {name} executed with result: {result}"
    
    
    async def perform(self, query: str,  memory: Optional[int] = None, max_iterations: int =5 ) -> str:
        """Function to generate an accurate response to a user need using the ReAcT pattern.
        Args:
            user_message (str):The query sent by the user
            memory (int, optional): A list with the messages history. Defaults to "None".
            
        Returns:
            str: The response of the assistant to the user
        """
        
        # Prepare the messages history
        messages = self.history(memory)
        
        # Generate the prompt for the agent 
        prompt = self.prompt_template.format(query=query)


        # Generate and save the user message 
        user_message = Message.user(prompt)
        self.save(user_message)
        
        # Prepare the messages for the LLM
        messages.append(user_message) 
        
        for _ in range(max_iterations):
            # Call the LLM to generate the thinking process
            response = await self.llm._parse(
                model = Reasoning,
                messages=messages,
            )
            print(f"Observation: {response.observation}")
            print(f"Thought: {response.thought}")       
            # Check if the response contains an action to perform
            if new_query:= response.query:
                # If the action is valid, use the corresponding tool
                try:
                    tool_result = await self.action(new_query, messages)
                
                except Exception as e:
                    print(f"Error using generation actions: {e}")
                    tool_result = f"Error using generation actions: {e}"
                
                
                # Save the current thought and the tool result
                print(f"Tool Result: {tool_result}")
                messages.extend([
                    Message.assistant(f"Thought: {response.thought}"),
                    Message.tool(f"Tool Result: {tool_result}")
                ])    

            elif response.final:
                # Save the final thought
                
                messages.append(
                    Message.assistant(f"Final Thought: {response.thought}")
                )
                break
            
                
        # Generating the response to the user 
        messages.append(
            Message.system(content="Genera una respuesta final para el usuario basada en la información recopilada y el razonamiento realizado.")
        )
        final_response = await self.llm._chat(messages)
        self.save(Message.assistant(final_response))
        
        print(f"Final Response: {final_response}")
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