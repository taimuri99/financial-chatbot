from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain.llms import HuggingFacePipeline
from .config import MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE, DEVICE
import streamlit as st

@st.cache_resource
def init_llm():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        device=DEVICE
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    return llm
