from backend.framework.functions import web_search
from backend.framework import Chatbot, LLM
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





web_search = bot.tool(web_search)
result = asyncio.run(bot.perform("Soy un tenedor de libros en Cuba y le llevo la contablidad a una empresa de importación y exportación. ¿De que aspectos debo tener cuidado?"))
print(result)