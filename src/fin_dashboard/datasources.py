import requests
from .config import FINNHUB_API_KEY
from .utils import safe_fetch
import streamlit as st
import logging
import os

# ------------------------------
# Logging setup
# ------------------------------
LOG_FILE = "logs/datasources.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)

# ------------------------------
# Finnhub Data Fetch
# ------------------------------
@st.cache_data(ttl=3600)  # cache for 1 hour
def get_finnhub_company_data(symbol: str):
    base_url = "https://finnhub.io/api/v1"

    # Safe profile fetch
    profile_res = safe_fetch(requests.get, f"{base_url}/stock/profile2",
                             params={"symbol": symbol, "token": FINNHUB_API_KEY})
    profile = profile_res.json() if profile_res and profile_res.ok else {}
    if not profile:
        log_warning(f"Finnhub profile fetch failed for {symbol}")

    # Safe quote fetch
    quote_res = safe_fetch(requests.get, f"{base_url}/quote",
                           params={"symbol": symbol, "token": FINNHUB_API_KEY})
    quote = quote_res.json() if quote_res and quote_res.ok else {}
    if not quote:
        log_warning(f"Finnhub quote fetch failed for {symbol}")

    # Safe metrics fetch
    metrics_res = safe_fetch(requests.get, f"{base_url}/stock/metric",
                             params={"symbol": symbol, "metric": "all", "token": FINNHUB_API_KEY})
    metrics = metrics_res.json().get("metric", {}) if metrics_res and metrics_res.ok else {}
    if not metrics:
        log_warning(f"Finnhub metrics fetch failed for {symbol}")

    return {
        "name": profile.get("name", "N/A"),
        "sector": profile.get("finnhubIndustry", "N/A"),
        "industry": profile.get("finnhubIndustry", "N/A"),
        "marketCap": metrics.get("marketCapitalization", "N/A"),
        "currentPrice": quote.get("c", "N/A"),
        "52WeekHigh": metrics.get("52WeekHigh", "N/A"),
        "52WeekLow": metrics.get("52WeekLow", "N/A"),
        "description": profile.get("description", "N/A"),
        "metric": metrics  # include full metrics for analytics.py
    }

# ------------------------------
# SEC Filings Fetch
# ------------------------------
@st.cache_data(ttl=3600)  # cache for 1 hour
def get_sec_filings(symbol: str, count: int = 5):
    base_url = "https://data.sec.gov/submissions/"

    # Safe CIK lookup
    cik_lookup_res = safe_fetch(requests.get, "https://www.sec.gov/files/company_tickers.json")
    if not cik_lookup_res or not cik_lookup_res.ok:
        log_warning(f"SEC CIK mapping fetch failed for {symbol}")
        return []

    cik_lookup = cik_lookup_res.json()
    cik = None
    for item in cik_lookup.values():
        if item['ticker'].upper() == symbol.upper():
            cik = str(item['cik_str']).zfill(10)
            break
    if not cik:
        log_warning(f"No CIK found for ticker {symbol}")
        return []

    # Safe filings fetch
    filings_res = safe_fetch(requests.get, f"{base_url}CIK{cik}.json")
    if not filings_res or not filings_res.ok:
        log_warning(f"SEC filings fetch failed for {symbol}")
        return []

    filings_data = filings_res.json()
    recent_filings = filings_data.get("filings", {}).get("recent", {})
    filings_list = []
    for i in range(min(count, len(recent_filings.get("accessionNumber", [])))):
        filings_list.append({
            "form": recent_filings.get("form", ["N/A"])[i],
            "date": recent_filings.get("filingDate", ["N/A"])[i],
            "link": f"https://www.sec.gov/Archives/edgar/data/{cik}/{recent_filings.get('accessionNumber', [''])[i].replace('-', '')}/{recent_filings.get('accessionNumber', [''])[i]}.txt"
        })
    return filings_list
