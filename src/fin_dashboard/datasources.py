import requests
from .config import FINNHUB_API_KEY
from .utils import safe_fetch
import streamlit as st
import logging
import time

# ------------------------------
# Logging setup
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)

# ------------------------------
# Retry utility for robust API calls
# ------------------------------
def fetch_with_retry(url, headers=None, params=None, retries=3, delay=2, timeout=5):
    """Retry GET requests with delay and timeout if it fails."""
    for attempt in range(1, retries + 1):
        try:
            res = requests.get(url, headers=headers, params=params, timeout=timeout)
            if res.ok:
                return res
            else:
                log_warning(f"Request failed ({res.status_code}) | URL: {url}")
        except requests.RequestException as e:
            log_warning(f"Request exception: {e} | URL: {url}")
        time.sleep(delay)
    log_warning(f"All retries failed for URL: {url}")
    return None

# ------------------------------
# Finnhub Data Fetch
# ------------------------------
@st.cache_data(ttl=3600)
def get_finnhub_company_data(symbol: str):
    base_url = "https://finnhub.io/api/v1"

    # Profile
    profile_res = safe_fetch(
        requests.get, f"{base_url}/stock/profile2",
        params={"symbol": symbol, "token": FINNHUB_API_KEY},
        timeout=5
    )
    profile = profile_res.json() if profile_res and profile_res.ok else {}
    if not profile:
        log_warning(f"Finnhub profile fetch failed for {symbol}")

    # Quote
    quote_res = safe_fetch(
        requests.get, f"{base_url}/quote",
        params={"symbol": symbol, "token": FINNHUB_API_KEY},
        timeout=5
    )
    quote = quote_res.json() if quote_res and quote_res.ok else {}
    if not quote:
        log_warning(f"Finnhub quote fetch failed for {symbol}")

    # Metrics
    metrics_res = safe_fetch(
        requests.get, f"{base_url}/stock/metric",
        params={"symbol": symbol, "metric": "all", "token": FINNHUB_API_KEY},
        timeout=5
    )
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
        "metric": metrics
    }

# ------------------------------
# SEC Filings Fetch
# ------------------------------
SEC_HEADERS = {"User-Agent": "MyPortfolioApp/1.0 (your-email@example.com)"}

@st.cache_data(ttl=86400)
def get_sec_cik_mapping():
    """Fetch SEC ticker → CIK mapping once and cache."""
    url = "https://www.sec.gov/files/company_tickers.json"
    res = fetch_with_retry(url, headers=SEC_HEADERS)
    if not res:
        log_warning("Failed to fetch SEC CIK mapping")
        return {}
    return res.json()

@st.cache_data(ttl=3600)
def get_sec_filings(symbol: str, count: int = 5):
    base_url = "https://data.sec.gov/submissions/"

    # Lookup CIK
    cik_lookup = get_sec_cik_mapping()
    cik = None
    for item in cik_lookup.values():
        if item.get('ticker', '').upper() == symbol.upper():
            cik = str(item.get('cik_str', '')).zfill(10)
            break
    if not cik:
        log_warning(f"No CIK found for ticker {symbol}")
        return []

    # Fetch filings
    filings_res = fetch_with_retry(f"{base_url}CIK{cik}.json", headers=SEC_HEADERS)
    if not filings_res:
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
