import os
import redis
import httpx
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler,
    MessageHandler,
    filters,
)

# name: Bot de asistencia Cimex
# username: asistencia_cimex_bot
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN","") #"7746203495:AAEX8Eo4dC3eLOyxyGnFf8h2IaZ-qoondH4"
REDIS_URL = os.getenv("REDIS_URL","")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
URL = "http://api:8000/"  # URL of the API service, adjust as needed

def get_redis_client():
    return redis.from_url(REDIS_URL)


def get_message(conversation_id: str):
    redis_client = get_redis_client().pubsub()
    redis_client.subscribe(conversation_id)

    while True:
        msg = redis_client.get_message(ignore_subscribe_messages=True, timeout=60)

        if msg is None:
            continue

        if msg["type"] == "message":
            payload = msg["data"].decode("utf8")

            if payload == "[DONE]":
                break

            yield payload

    redis_client.unsubscribe()
    redis_client.close()


def send_message(message: str, conversation: str):
    with httpx.Client() as client:
        response = client.post(
            f"{URL}chat/",
            json={
                "message": {"role": "user", "content": message},
                "conversation_id": conversation,
            },
            follow_redirects=True,
        )
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        return response.json()


async def upload_file(conversation_id: str, file_name: str, file_type: str, file_content: bytes):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{URL}doc/",
            files={"file": (file_name, file_content, file_type)},
            data={"conversation_id": conversation_id},
            follow_redirects=True,
        )
        return response.json()



def start_session(username: str):
    with httpx.Client() as client:
        response = client.post(
            f"{URL}session",
            json={"username": username},
            follow_redirects=True,
        )
        return response.json()


class ConvesationalBot:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.url = REDIS_URL
        self.username = 'bot'
        self.conversation_id = None
    
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response  = start_session(self.username)
        self.conversation_id = response["conversation_id"]
        await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! Soy tu bot. Envíame un mensaje y te responderé.") # type: ignore


    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text  #type: ignore
        r = send_message(text,self.conversation_id) #type:ignore 
        
        response = []
        for response_msg  in get_message(r["conversation_id"]):
            response.append(response_msg)
            
        await context.bot.send_message(chat_id=update.effective_chat.id, text="".join(response))  #type: ignore
    
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        document = update.message.document #type:ignore 
        file_data = update.message.document.file_name.split(".")    #type: ignore
        # Descargar el archivo
        bot = context.bot
        file = await bot.get_file(document.file_id)# type:ignore

        # Descargar el contenido del archivo
        async with httpx.AsyncClient() as client:
            response = await client.get(file.file_path) #type:ignore
            file_content = response.content
  
        
        await upload_file(self.conversation_id, file_data[0], file_data[1], file_content) #type:ignore

        
    def start_bot(self):
        # Build app
        application = ApplicationBuilder().token(self.token).build()
         
        # Adding handlers to app
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat))
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        
        # Start running
        application.run_polling()
        


if __name__ == '__main__':
    bot = ConvesationalBot()
    bot.start_bot()
    







