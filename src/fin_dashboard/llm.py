from langchain_google_genai import ChatGoogleGenerativeAI
from src.fin_dashboard.config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE
import streamlit as st

@st.cache_resource
def init_llm():
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        google_api_key=GOOGLE_API_KEY,  # explicitly pass the key
        convert_system_message_to_human=True,
    )
    return llm
