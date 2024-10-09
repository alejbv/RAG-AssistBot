from llm_client import LLMClient
from utils import load_data
HELLO_MESSAGE = """
Bienvenido soy un bot de asistencia perteneciente a la Universidad de la Habana para ayudarte a resolver todas tus dudas
"""
class ChatBot:
    def __init__(self):
        data = load_data()
        # Loading the data for the correct functioning  of the bot
        self.api_key = data['API_KEY']
        self.model = data['MODEL']
        self.client = LLMClient(self.api_key,self.model)
