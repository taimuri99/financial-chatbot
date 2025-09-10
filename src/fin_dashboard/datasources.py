import asyncio
import httpx
from .config import FINNHUB_API_KEY
from .utils import safe_fetch
import streamlit as st
import logging

# ------------------------------
# Logging setup
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log_warning(message):
    logging.warning(message)
    st.warning(message)  # display warning in Streamlit

def log_error(message):
    logging.error(message)
    st.error(message)  # display error in Streamlit

# ------------------------------
# Async fetch with retry and API error logging
# ------------------------------
async def fetch_with_retry_async(client, url, headers=None, params=None, retries=3, delay=2, timeout=5):
    """Async GET requests with retries and explicit API error logging."""
    for attempt in range(1, retries + 1):
        try:
            res = await client.get(url, headers=headers, params=params, timeout=timeout)
            if res.status_code == 200:
                return res
            else:
                log_error(f"API request failed | URL: {url} | Status Code: {res.status_code} | Attempt {attempt}")
        except httpx.RequestError as e:
            log_error(f"API request exception: {e} | URL: {url} | Attempt {attempt}")
        await asyncio.sleep(delay)
    log_error(f"All retries failed for API URL: {url}")
    return None

# ------------------------------
# Finnhub Async Data Fetch
# ------------------------------
@st.cache_data(ttl=3600)
def get_finnhub_company_data(symbol: str):
    async def _fetch():
        async with httpx.AsyncClient() as client:
            base_url = "https://finnhub.io/api/v1"

            urls = {
                "profile": f"{base_url}/stock/profile2",
                "quote": f"{base_url}/quote",
                "metrics": f"{base_url}/stock/metric"
            }
            params_profile = {"symbol": symbol, "token": FINNHUB_API_KEY}
            params_quote = {"symbol": symbol, "token": FINNHUB_API_KEY}
            params_metrics = {"symbol": symbol, "metric": "all", "token": FINNHUB_API_KEY}

            tasks = [
                fetch_with_retry_async(client, urls["profile"], params=params_profile),
                fetch_with_retry_async(client, urls["quote"], params=params_quote),
                fetch_with_retry_async(client, urls["metrics"], params=params_metrics)
            ]

            profile_res, quote_res, metrics_res = await asyncio.gather(*tasks)

            profile = profile_res.json() if profile_res else {}
            quote = quote_res.json() if quote_res else {}
            metrics = metrics_res.json().get("metric", {}) if metrics_res else {}

            if not profile:
                log_warning(f"Finnhub profile fetch returned empty for {symbol}")
            if not quote:
                log_warning(f"Finnhub quote fetch returned empty for {symbol}")
            if not metrics:
                log_warning(f"Finnhub metrics fetch returned empty for {symbol}")

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

    return asyncio.run(_fetch())

# ------------------------------
# SEC Async Filings Fetch
# ------------------------------
SEC_HEADERS = {"User-Agent": "MyPortfolioApp/1.0 (your-email@example.com)"}

@st.cache_data(ttl=86400)
def get_sec_cik_mapping():
    async def _fetch():
        url = "https://www.sec.gov/files/company_tickers.json"
        async with httpx.AsyncClient() as client:
            res = await fetch_with_retry_async(client, url, headers=SEC_HEADERS)
            if not res:
                log_error("SEC CIK mapping fetch failed (API issue)")
                return {}
            return res.json()
    return asyncio.run(_fetch())

@st.cache_data(ttl=3600)
def get_sec_filings(symbol: str, count: int = 5):
    async def _fetch():
        cik_lookup = get_sec_cik_mapping()
        cik = None
        for item in cik_lookup.values():
            if item.get('ticker', '').upper() == symbol.upper():
                cik = str(item.get('cik_str', '')).zfill(10)
                break
        if not cik:
            log_warning(f"No CIK found for ticker {symbol}")
            return []

        base_url = "https://data.sec.gov/submissions/"
        async with httpx.AsyncClient() as client:
            filings_res = await fetch_with_retry_async(client, f"{base_url}CIK{cik}.json", headers=SEC_HEADERS)
            if not filings_res:
                log_error(f"SEC filings fetch failed for {symbol} (API issue)")
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

    return asyncio.run(_fetch())
