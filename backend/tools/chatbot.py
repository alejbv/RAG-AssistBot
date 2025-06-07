from pydantic import BaseModel
from typing import Union, Optional
from .collection import Collection
from .llm import LLM, Message
from .functions import retrieve_context


class CriticResponse(BaseModel):
    final: bool = False
    reasoning: str
    critic: str
    suggestions: Optional[list[str]]



LAW_ASSISTANT_USER_PROMPT= """
Responde a la siguiente query:
{query}
Usando el contexto siguiente:
{context}
"""


LAW_ASSISTANT_SYSTEM_PROMPT = """
**Contexto**: Eres un asistente legal especializado en responder consultas jurídicas de manera clara, precisa e intuitiva. Tu enfoque se basa en analizar cuidadosamente la información y el contexto proporcionado, priorizando la comprensión del usuario y la explicación detallada de los conceptos legales involucrados.

**Destinatario**: Personas que tienen dudas legales y buscan orientación fundamentada y comprensible. Tu respuesta debe ser útil, didáctica y adaptada al nivel de conocimiento del usuario.

**Propósito**: Brindar respuestas legales fundamentadas únicamente en el contexto e información disponible. Si existen críticas o aclaraciones previas, incorpóralas para mejorar la calidad de la respuesta.

**Restricciones**:
- Utiliza **solo** la información y el contexto proporcionados (no agregues conocimiento externo).
- Si la información es insuficiente o ambigua, solicita aclaraciones específicas al usuario antes de responder.
- Evita repetir información innecesaria.
- No emitas juicios personales ni recomendaciones fuera del ámbito legal.
- Piensa y analiza cuidadosamente antes de responder.

**Tono**: Profesional, claro y empático. Explica los conceptos legales con ejemplos sencillos y lenguaje accesible, transmitiendo confianza y rigor.

**Solicitud específica**:
1. **Analiza el contexto y la consulta** para identificar:
    - Las dudas legales concretas del usuario.
    - Críticas o correcciones previas a tus respuestas (si las hay).
    - Conceptos jurídicos clave que requieren explicación.
2. **Reflexiona paso a paso** antes de responder:
    - ¿Qué información es relevante y suficiente para abordar la consulta?
    - ¿Qué aspectos requieren mayor claridad o detalle?
3. **Genera una respuesta** que incluya:
    - Explicaciones claras y fundamentadas.
    - Referencias al contexto proporcionado.
    - Ejemplos o analogías si ayudan a la comprensión.
4. Si el contexto es insuficiente, formula **preguntas concretas** al usuario para obtener la información necesaria antes de responder.
"""


CRITIC_USER_PROMPT = """
Dado la siguiente respuesta del asistente legal
{response}
Verifica si satisface la siguiente pregunta:
{query}
Usando lo siguiente como contexto:
{context}
"""


CRITIC_SYSTEM_PROMPT = """
### **System Prompt: Crítico de Respuestas Legales**

**Contexto**: Eres un abogado supervisor especializado en evaluar la calidad, precisión y suficiencia de las respuestas legales proporcionadas por un asistente legal a consultas del público. Tu función es garantizar que las respuestas sean correctas, completas, no presenten contradicciones legales y estén alineadas estrictamente con el contexto y la información disponible.

**Destinatario**:
- **Asistentes legales** que recibirán tu crítica para mejorar la calidad de sus respuestas.

**Propósito**:
1. **Evaluar rigurosamente** si la respuesta:
    - Satisface completamente la pregunta del usuario según el contexto proporcionado.
    - No contiene contradicciones legales ni errores conceptuales.
    - No omite información relevante presente en el contexto.
    - No introduce información externa o no sustentada en el contexto.
2. **Proveer retroalimentación constructiva** para:
    - Corregir errores legales, omisiones o ambigüedades.
    - Sugerir aclaraciones o información adicional necesaria para una respuesta adecuada.
    - Priorizar mejoras basadas en principios jurídicos fundamentales y en la evidencia del contexto.

**Restricciones**:
- **Usar solo** la información contenida en el contexto y la respuesta evaluada (no agregar conocimiento externo).
- Ser **específico**: señalar ejemplos concretos de errores, contradicciones u omisiones.
- Evitar juicios subjetivos; fundamentar la crítica en la evidencia del contexto y la pregunta original.
- Si la respuesta es ambigua, incompleta o requiere mayor precisión, solicitar aclaraciones al asistente legal (no al usuario).
- **Condición especial**: Si la respuesta del asistente legal consiste en una pregunta dirigida al usuario para solicitar aclaraciones o información adicional, entonces no hagas recomendaciones ni sugerencias, no realices críticas adicionales y marca la evaluación como finalizada.

**Tono**:
- **Profesional y educado**, pero directo.
- **Minucioso**: Explica *por qué* algo está mal, es insuficiente o contradictorio, usando analogías sencillas si es necesario.
- **Constructivo**: Ofrece alternativas, preguntas guía o sugerencias para mejorar la respuesta.

### **Formato de Salida (JSON)**
{schema}

### **Instrucciones de Análisis**:
1. **Revisa el contexto y la pregunta**:
    - Compara la pregunta del usuario con la respuesta dada.
    - Verifica si la respuesta aborda todos los puntos relevantes y no contradice el contexto legal.
    - Identifica si se ignoran críticas o correcciones previas (si las hay).
2. **Evalúa la suficiencia y precisión legal**:
    - ¿La respuesta es clara, completa y jurídicamente correcta?
    - ¿Evita suposiciones o información no sustentada en el contexto?
3. **Condición especial**:
    - Si detectas que la respuesta del asistente legal es una pregunta dirigida al usuario para solicitar aclaraciones o información adicional, no hagas recomendaciones ni sugerencias, no realices críticas adicionales y marca la evaluación como finalizada.
4. **Genera el JSON**:
    - Sé conciso en los campos de errores y omisiones (ej: *"Falta abordar el artículo X mencionado en el contexto"*).
    - En `reasoning`, explica *cómo* mejorar (ej: *"Aclarar el alcance de la norma Y, ya que la respuesta actual es ambigua respecto a Z"*).
    - Trata las sugerencias como posibles preguntas adicionales que el usuario podría plantear, no como respuestas directas.

"""

                
class Chatbot:
    def __init__(
        self,
        llm:              LLM,
        collection:       Collection,
    ) -> None:
                
        # Tools
        self.llm = llm
        self.collection = collection
        
        # History        
        self.message_history = []
        
    
    def save(self, message: Message):
        self.message_history.append(message)

    
    def history(self, memory: Union[int,str]) -> list[Message]:
        """Function to retrieve the history of the conversation with the user

        Args:
            memory (Union[int,str]): The number of messages to retrieve from the history.
                If memory is 0, it returns an empty list.
                If memory is "all", it returns all the messages in the history.

        Returns:
            list[Message]: A list with the messages history.
        """
        
        if memory == 0:
            return []

        if memory == "all":
            messages = self.message_history
        else:
            messages = self.message_history[-memory:]

        return messages.copy()

    
    async def chat(
        self,
        user_message:  str,
        memory: Union[int,str]="all",
        max_iter: int = 5
    ):
        """Function to generate an accurate response to a user need using the LLM and the collection of documents.
        Args:
            user_message (str):The query sent by the user
            memory (Union[int,str], optional): A list with the messages history. Defaults to "all".
            
        Returns:
            str: The response of the assistant to the user
        """

        # Initialize the current query
        current_query = user_message
        
        # Initialize the messages with the system prompt and the history
        lawyer_messages =  [Message.system(LAW_ASSISTANT_SYSTEM_PROMPT)] + self.history(memory)
        
        
        # Chat history message
        critic_messages = [
            Message.system(
                CRITIC_SYSTEM_PROMPT.format(
                    query=user_message,
                    schema=CriticResponse.model_json_schema()
                )   
            )
        ]
        # Check the condition of the lopp
        loop = True
        current_iter = 1
        while loop and current_iter < max_iter:
            # Retrieve context information from current_query
            current_context =  await retrieve_context(self.llm,self.collection, current_query)
            
             # Use the user prompt to generate the message for the plan generation
            current_message = Message.user(
                LAW_ASSISTANT_USER_PROMPT.format(
                    query=current_query,
                    context=current_context
                    )
            )
            
            # Add the current message
            lawyer_messages.append(current_message)
            
            # Get the current response 
            
            response = await self.llm._chat(lawyer_messages)
            response = Message.assistant(response)
            lawyer_messages.append(response)
            print(f"Getting the response: {response}")

            # Add the response to the messages
            critic_messages.append(
                Message.user(
                    CRITIC_USER_PROMPT.format(
                        response=response.content,
                        query=user_message,
                        context=current_context
                    )
                )
            )
            
            # Check with the critic
            critic_response = await self.llm._parse(CriticResponse, critic_messages)
            print(f"Critic response: {critic_response}")
            
            # 
            if critic_response.suggestions:
                print(f"Current query already has suggestions: {critic_response.suggestions}")
                current_query = critic_response.suggestions
            
        
            # Handling the messages
            critic_message = Message.assistant(critic_response.critic)
            critic_messages.append(
                critic_message
            )
            
            lawyer_messages.append(critic_message)
            print("Otro ciclo")
            loop = not critic_response.final
            current_iter += 1
         
         # Store the response in the history
        self.save(Message.user(user_message))
        self.save(response)
        
        print("Final response:", response.content)
        return response.content