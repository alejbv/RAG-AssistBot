from backend.framework import Chatbot, LLM, Resolver
from pydantic import BaseModel
from backend.framework.llm import Message
import aiohttp
from ddgs import DDGS
from bs4 import BeautifulSoup
import asyncio

llm = LLM(
    "fw_3ZNhNHReBB6qjhLDWGYsFqLR", 
    "https://api.fireworks.ai/inference/v1",
    "accounts/fireworks/models/llama-v3p1-405b-instruct"
)

bot = Chatbot(llm)

# @bot.tool
# async def prompt_callback(query: str):
#     """Función para solicitar informacion al usuario."""
#     await asyncio.sleep(1)
#     return input(f"Por favor responda a la siguiente pregunta{query}\n?>> ")



class Summary(BaseModel):
    summary: str
    relevant: bool

#@bot.tool
resolver = Resolver()

@bot.tool
@resolver.wrap
async def search_web(resolver: Resolver, query: str, limit: int = 10) -> str:
    """Busca en la web por informacion."""
    candidates = DDGS().text(query, region='wt-wt', safesearch='off', max_results=limit)
    results = []
    _llm = resolver.resolve(LLM)

# Obtener todo el texto de la página:
    for content in candidates:
        try:
            
            async with aiohttp.ClientSession() as session:
                async with session.get(content["href"], timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    page_text = await response.text()
                    soup = BeautifulSoup(page_text, 'html.parser')
                    full_text = soup.get_text()
            summary = await _llm._parse(
                messages=[
                    Message.system(
                        f"""
                        Dada la siguiente consulta, resume la información
                        en el texto para responder la consulta.

                        Consulta: {query}

                        Responde con un objeto JSON con los siguientes campos:
                        - summary: Un resumen corto con toda la información relevante para la consulta.
                        - relevant: Un booleano que indique si la información es relevante para la consulta.
                        """
                    ),
                    Message.user(full_text),
                ],
                model=Summary,
            )
            if summary.relevant:
                results.append(summary)
        except Exception as e:
            # Si hay error al hacer request o procesar la página, continuar con la siguiente
            print(f"Error processing {content['href']}: {e}")
            continue


    # Construir el prompt final con los resúmenes relevantes
    summarys = ", ".join([result.summary for result in results])
    prompt = (
        f"Genera una respuesta final para la query {query} basada en la información recopilada y el razonamiento realizado. "
        "Extrae la información más relevante de los siguientes resúmenes:\n"
        f"{summarys}\n"
        "Siempre genera una respuesta a la consulta basada en la información recopilada y el razonamiento realizado. "
        "Toda respuesta fundamentala con referencias a la legislación vigente en Cuba."
        "Se lo mas informativo posible."
    )
    messages = [Message.system(prompt)]
    
    final_response = await _llm._chat(messages)
    return final_response




resolver.register(llm)

asyncio.run(
    bot.perform("Soy un tenedor de libros para una empresa de importación y exportación de productos electrónicos en Cuba. ¿Que debo hacer para mantenerme al día con las regulaciones fiscales y aduaneras?")
)