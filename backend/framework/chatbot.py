from pydantic import BaseModel, Field
from typing import Union, Optional, Callable, Dict, List
from .llm import LLM, Message
from .tool import Tool
import logging
import inspect

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class Action(BaseModel):
    name: str = Field(..., description="The name of the tool to use")
    reason: str = Field(..., description="The reason for choosing this tool")
    input: Union[list,dict] = Field(..., description="The input to send to the tool")

class Choice(BaseModel):
    thought: str = Field(..., description="The reasoning behind the choice")
    final: bool = Field(False, description="Whether this is the final answer")
    action: Optional[Action] = Field(None, description="The action to take, if any")
    


LEGAL_REACT_PROMPT = """
**Contexto**: Eres un agente especializado en responder consultas legales de manera clara, precisa e intuitiva. Recibes preguntas legales de un usuario y trabajas paso a paso para reunir el contexto necesario antes de responder, utilizando únicamente la información y herramientas proporcionadas.

**Pregunta del usuario**: {query}

**Instrucciones**:
1. Analiza cuidadosamente la consulta legal del usuario, el historial y las observaciones previas para identificar:
    - Las dudas legales concretas del usuario.
    - Críticas o correcciones previas a tus respuestas (si las hay).
    - Conceptos jurídicos clave que requieren explicación.
2. Si la pregunta es muy compleja, divídela en preguntas más simples. 
3. Si la pregunta es demasiado específica, formula preguntas más generales para obtener contexto relevante.
4. Si la información disponible es insuficiente, haz preguntas concretas al usuario para obtener los detalles necesarios.
5. Antes de responder, planea y razona cuidadosamente los pasos a seguir:
    - ¿Qué información es relevante y suficiente para abordar la consulta?
    - ¿Qué aspectos requieren mayor claridad o detalle?
6. Indica explícitamente las herramientas que vas a utilizar y la pregunta del usuario que estás abordando.
7. Utiliza las herramientas disponibles (por ejemplo, bases de datos legales, buscadores jurídicos) para obtener información relevante.
8. Al generar una respuesta, explica los conceptos legales de manera clara y fundamentada, incluyendo siempre la referencia específica a la legislación, artículo, norma o documento de donde obtuviste la información (por ejemplo: "según el artículo 14 del Código Civil español...").
9. Si no puedes encontrar información suficiente tras utilizar las herramientas, indícalo y sugiere al usuario que proporcione más detalles o consulte a un profesional.

**Herramienta disponible**:
{tools}

**Recuerda**:
- Sé minucioso en tu razonamiento y planea antes de responder.
- Si la información es insuficiente o ambigua, solicita aclaraciones específicas al usuario.
- No repitas información innecesaria ni emitas juicios personales.
- Sé claro, preciso y profesional.
- Usa herramientas cuando necesites más información y referencia siempre la fuente.
- Todas las afirmaciones legales deben estar respaldadas por referencias normativas o documentales concretas.
- Si una herramienta no muestra resultados o falla, reconócelo y considera usar otra herramienta o enfoque.
- Proporciona una respuesta final solo cuando tengas suficiente información.
"""
                
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


    async def perform(self, query: str,  memory: Optional[int], max_iterations: int =5 ) -> str:
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
        prompt = self.prompt_template.format(
            query=query, 
            tools='\n'.join([str(tool.name) for tool in self.tools.values()]),
        )
        
        # Generate and save the user message 
        user_message = Message.user(prompt)
        self.save(user_message)
        
        # Prepare the messages for the LLM
        messages = self.history(memory) + [user_message] 
        
        for _ in range(max_iterations):
            # Call the LLM to generate the thinking process
            response = await self.llm._parse(
                model = Choice,
                messages=messages,
            )
                    
            # Check if the response contains an action to perform
            if action := response.action:
                # If the action is valid, use the corresponding tool
                logger.info(f"Performing action: {action.name} with input: {action.input}")
                try:
                    tool = self.tools[action.name]
                    tool_response = await tool.use(*action.input)
                    tool_result = f"Observation from {tool.name}: {tool_response}"
                
                except Exception as e:
                    logger.error(f"Error using tool {action.name}: {e}")
                    tool_result = f"Error using tool {action.name}: {e}"
                
                finally:
                    # Save the current thought and the tool result
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
        final_response = await self.llm._chat(messages)
        final_message = Message.assistant(final_response)
        self.save(final_message)
        
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