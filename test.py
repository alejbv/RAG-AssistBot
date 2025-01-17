import re
import json
from pydantic import BaseModel

class PromptFormat(BaseModel):
    context: str
    query: str
    response: str
    reasoning: str
    references: str
    feedback: str
    response_length: int
    error: str


to_json ={"context": "El contexto proporcionado incluye una lista de 17 formas de turismo diferentes, entre las que se encuentran el turismo de sol y playa, turismo cultural, turismo de reuniones, turismo deportivo, turismo náutico, turismo académico y científico, turismo de naturaleza, turismo de salud, turismo de negocios, viajes de incentivo, turismo de cruceros, turismo de intereses sociales, turismo de intercambio profesional, turismo religioso, turismo de hobbies, aficiones, turismo de bodas y lunas de miel, turismo de aventura y turismo de parques temáticos.",
"error": "",
"feedback": "",
"query": "Cuales son las distintas formas de turismo",
"reasoning": "El contexto proporcionado incluye una lista de 17 formas de turismo diferentes. Las formas de turismo mencionadas son: turismo de sol y playa, turismo cultural, turismo de reuniones, turismo deportivo, turismo náutico, turismo académico y científico, turismo de naturaleza, turismo de salud, turismo de negocios, viajes de incentivo, turismo de cruceros, turismo de intereses sociales, turismo de intercambio profesional, turismo religioso, turismo de hobbies, aficiones, turismo de bodas y lunas de miel, turismo de aventura y turismo de parques temáticos.",
"references": "El contexto proporcionado no incluye referencias específicas.",
"response": "Las distintas formas de turismo mencionadas son: turismo de sol y playa, turismo cultural, turismo de reuniones, turismo deportivo, turismo náutico, turismo académico y científico, turismo de naturaleza, turismo de salud, turismo de negocios, viajes de incentivo, turismo de cruceros, turismo de intereses sociales, turismo de intercambio profesional, turismo religioso, turismo de hobbies, aficiones, turismo de bodas y lunas de miel, turismo de aventura y turismo de parques temáticos."}

print(type(to_json))


    
    
a =PromptFormat.model_validate(to_json)
print(a.response)