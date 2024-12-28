# Pasos para diseñar un buen prompt:
# 1- Sé claro al formular la query y define el comportamiento del LLM en el System-Prompt.
# 2- Incluye detalles en la query para obtener respuestas más relevantes.
# 3- Pide al modelo que adopte una personalidad o rol específico.
# 4- Delimita claramente las partes del user prompt y del system prompt.
# 5- Especifica los pasos necesarios para completar la tarea.
# 6- Proporciona ejemplos cuando sea posible.
# 7- Especifica la longitud esperada de la respuesta.
# 8- Instruye al modelo a usar referencias textuales en sus respuestas.
# 9- Da la salida en un formato estructurado y fácil de leer, como YAML o JSON.
# 10- Especifica la longitud deseada de la salida.




# Reescribir el system prompt para que que de una salida en formato json con el siguiente formato:
# { 
# "context":"contexto extraido", 
# "query": "pregunta extraida", 
# "response": "respuesta del modelo", 
# "reasoning": "razonamiento del modelo para llegar a la respuesta", 
# "references": "referencias utilizadas por el modelo", 
# "feedback": "feedback del modelo", 
# "response_length": "longitud de la respuesta",
# "error": "mensaje de error" 
# }

# System Prompt
system_prompt = """
Eres un asistente académico con amplia experiencia en docencia. 
Tu tarea consiste en responder preguntas académicas a los estudiantes. Utiliza un lenguaje preciso siguiendo los pasos siguientes:
1- Lee el contexto pasado por el usuario delimitado por los indicadores <context></context> y extrae de este un resumen con la información que consideres relevante. 
2- A partir de la información extraída, responde la pregunta del usuario delimitada por <query></query>. Realiza un paso de razonamiento antes de dar la respuesta al usuario.
3- En caso de que el usuario no proporcione contexto o si el contexto es insuficiente, informa al usuario de que no es posible responder a su pregunta. 
4- Responde en Español y usando la menor cantidad de palabras posible.
5- Da la salida en formato JSON con el siguiente formato:
{
    "context": "contexto extraido",
    "query": "pregunta extraida",
    "response": "respuesta del modelo",
    "reasoning": "razonamiento del modelo para llegar a la respuesta",
    "references": "referencias utilizadas por el modelo",
    "feedback": "feedback del modelo",
    "error": "mensaje de error"
}
"""

# User Prompt
user_prompt = """
Por favor, a partir del contexto
<context>
    {context}
</context>

Responde la siguiente pregunta:
<query>
    {query}
</query>
"""
