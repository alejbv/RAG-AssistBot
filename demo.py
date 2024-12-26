import json
import streamlit as st
from lib.utils import Chatbot
from prompts import *
from lib.utils import DEFAULT_SYSTEM_PROMPT

st.set_page_config(
    page_title="BotUH",
    page_icon="/app/static/escudo.png",
    initial_sidebar_state="collapsed")

hide_streamlit_style = """ <style> #MainMenu {visibility: hidden;} .stDeployButton {display:none;} footer {visibility: hidden;} </style> """ 
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

system_prompt = st.sidebar.text_area("System Prompt", value=SYSTEM_PROMPT.strip())

bot = Chatbot('open-mixtral-8x7b')

def technical_answer(query):
    "Usa esta función cuando la query del usuario tenga relación con el soporte técnico"
    # Expandiendo la query con informacion extra
    query_exp = bot.query_extend(query)
    # sustituyendo el system prompt
    bot.system_prompt = SYSTEM_PROMPT
    # sustituyendo el user prompt
    bot.user_prompt = USER_PROMPT

    return bot.submit(query,context=5,stream=False,extract="\n\n".join(query_exp))


def not_techincal_answer():
    "Usa esta función cuando la query del usuario no tenga relación con el soporte técnico"
    bot.user_prompt = NOT_TECHNICAL_PROMPT
    return bot.submit("",context=0,stream=False)

if st.sidebar.button("Limpiar conversación"):
    bot.reset()

for message in bot.history():
    with st.chat_message(message.role):
        st.write(message.content)

msg = st.chat_input()

if not msg:
    st.stop()

with st.chat_message("user"):
    st.write(msg)

with st.chat_message("assistant"):
    # Se clasifica el prompt como técnico o no
    bot.system_prompt = DEFAULT_SYSTEM_PROMPT
    bot.user_prompt = CLASSIFICATION_PROMPT
    # La respuesta del bot
    bot_response = bot.submit(msg, context=5,stream=False,store=False)
    # Se limpia la respuesta de saltos de linea indeceados 
    bot_response.replace("\n", "")
    
    # Nos interesa de la respuesta del bot solo el formato json
    start_index = bot_response.find("{")
    end_index = bot_response.find("}") + 1
    clasification = json.loads(bot_response[start_index:end_index])
        
    if clasification["CLS"].lower() == "y":
        user_response = technical_answer(msg)
    
    else:
        user_response = not_techincal_answer()
    
    st.write(user_response)