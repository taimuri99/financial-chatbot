import asyncio
import httpx
from .config import FINNHUB_API_KEY
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
    st.warning(message)

def log_error(message):
    logging.error(message)
    st.error(message)

# ------------------------------
# Async fetch with retry
# ------------------------------
async def fetch_with_retry_async(client, url, headers=None, params=None, retries=3, delay=2, timeout=5):
    """Async GET request with retries, logging errors outside loop to avoid hidden logs."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            res = await client.get(url, headers=headers, params=params, timeout=timeout)
            if res.status_code == 200:
                return {"success": True, "response": res}
            elif res.status_code == 404:
                last_error = {"code": 404, "message": "Not Found"}
                break
            elif res.status_code == 429 or 500 <= res.status_code < 600:
                last_error = {"code": res.status_code, "message": "Retryable error"}
            else:
                last_error = {"code": res.status_code, "message": "Unexpected response"}
        except httpx.RequestError as e:
            last_error = {"code": "REQUEST_EXCEPTION", "message": str(e)}
        await asyncio.sleep(delay)

    if last_error:
        log_error(f"Failed to fetch {url}: {last_error['code']} | {last_error['message']}")
    return {"success": False, **(last_error or {"code": "UNKNOWN", "message": "Unknown error"})}

# ------------------------------
# Finnhub Fetch
# ------------------------------
async def _fetch_finnhub(symbol: str):
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

        errors = []
        profile = profile_res.get("response").json() if profile_res.get("success") else {}
        quote = quote_res.get("response").json() if quote_res.get("success") else {}
        metrics = metrics_res.get("response").json().get("metric", {}) if metrics_res.get("success") else {}

        # Collect errors
        for res, name in zip([profile_res, quote_res, metrics_res], ["Profile", "Quote", "Metrics"]):
            if not res.get("success"):
                errors.append({"source": name, "code": res.get("code"), "message": res.get("message")})

        return {
            "data": {
                "name": profile.get("name", "N/A"),
                "sector": profile.get("finnhubIndustry", "N/A"),
                "industry": profile.get("finnhubIndustry", "N/A"),
                "marketCap": metrics.get("marketCapitalization", "N/A"),
                "currentPrice": quote.get("c", "N/A"),
                "52WeekHigh": metrics.get("52WeekHigh", "N/A"),
                "52WeekLow": metrics.get("52WeekLow", "N/A"),
                "description": profile.get("description", "N/A"),
                "metric": metrics
            },
            "errors": errors
        }

def get_finnhub_company_data(symbol: str):
    """Safe wrapper for Streamlit async context."""
    try:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(_fetch_finnhub(symbol))
    except RuntimeError:
        return asyncio.run(_fetch_finnhub(symbol))

# ------------------------------
# SEC Fetch
# ------------------------------
SEC_HEADERS = {"User-Agent": "MyPortfolioApp/1.0 (your-email@example.com)"}

async def _fetch_sec_cik_mapping():
    url = "https://www.sec.gov/files/company_tickers.json"
    async with httpx.AsyncClient() as client:
        res = await fetch_with_retry_async(client, url, headers=SEC_HEADERS)
        if not res.get("success"):
            return {}, res.get("code"), res.get("message")
        return res.get("response").json(), None, None

def get_sec_cik_mapping():
    try:
        loop = asyncio.get_running_loop()
        mapping, code, message = loop.run_until_complete(_fetch_sec_cik_mapping())
    except RuntimeError:
        mapping, code, message = asyncio.run(_fetch_sec_cik_mapping())

    if code:
        log_error(f"SEC CIK mapping error: {code} | {message}")
    return mapping

async def _fetch_sec_filings(symbol: str, count: int = 5):
    cik_lookup = get_sec_cik_mapping()
    cik = None
    for item in cik_lookup.values():
        if item.get("ticker", "").upper() == symbol.upper():
            cik = str(item.get("cik_str", "")).zfill(10)
            break
    if not cik:
        log_warning(f"No CIK found for ticker {symbol}")
        return {"data": [], "errors": [{"source": "SEC", "code": "CIK_NOT_FOUND", "message": "No CIK mapping"}]}

    base_url = "https://data.sec.gov/submissions/"
    async with httpx.AsyncClient() as client:
        filings_res = await fetch_with_retry_async(client, f"{base_url}CIK{cik}.json", headers=SEC_HEADERS)
        if not filings_res.get("success"):
            return {"data": [], "errors": [{"source": "SEC", "code": filings_res.get("code"), "message": filings_res.get("message")}]}

        filings_data = filings_res.get("response").json()
        recent_filings = filings_data.get("filings", {}).get("recent", {})
        filings_list = []
        for i in range(min(count, len(recent_filings.get("accessionNumber", [])))):
            filings_list.append({
                "form": recent_filings.get("form", ["N/A"])[i],
                "date": recent_filings.get("filingDate", ["N/A"])[i],
                "link": f"https://www.sec.gov/Archives/edgar/data/{cik}/{recent_filings.get('accessionNumber', [''])[i].replace('-', '')}/{recent_filings.get('accessionNumber', [''])[i]}.txt"
            })
        return {"data": filings_list, "errors": []}

def get_sec_filings(symbol: str, count: int = 5):
    try:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(_fetch_sec_filings(symbol, count))
    except RuntimeError:
        return asyncio.run(_fetch_sec_filings(symbol, count))
