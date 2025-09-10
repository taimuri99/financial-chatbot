import streamlit as st

# Hugging Face secret for Finnhub
FINNHUB_API_KEY = st.secrets["FINNHUB_API_KEY"]
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]

# Model names and parameters # --- Gemini / LLM Configuration ---
MODEL_NAME = "gemini-1.5-flash"

# --- Embeddings Model (still needed for Chroma/FAISS) ---
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.2
#DEVICE = -1  # -1 = CPU, 0 = GPU


