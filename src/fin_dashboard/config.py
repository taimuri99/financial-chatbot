import streamlit as st

# API Keys from Streamlit secrets, safely on deployment
FINNHUB_API_KEY = st.secrets.get("FINNHUB_API_KEY", "")
GOOGLE_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)  # Optional for LLM fallback

# Gemini/Groq Configuration
TEMPERATURE = 0.2

# App Configuration
APP_NAME = "Financial Dashboard"
APP_VERSION = "1.0.0"

# API Endpoints
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
SEC_BASE_URL = "https://data.sec.gov"

# Cache Settings (in seconds)
CACHE_TTL_SHORT = 300   # 5 minutes
CACHE_TTL_LONG = 600    # 10 minutes

# UI Configuration
DEFAULT_TICKERS = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META"]
MAX_SEC_FILINGS = 5