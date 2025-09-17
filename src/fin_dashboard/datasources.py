import requests
import time
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
    """Log warning and display in Streamlit"""
    logging.warning(message)

def log_error(message):
    """Log error and display in Streamlit"""
    logging.error(message)

# ------------------------------
# Sync fetch with retry (simplified)
# ------------------------------
def fetch_with_retry(url, headers=None, params=None, retries=2, delay=1, timeout=10):
    """Synchronous GET request with retries"""
    last_error = None
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                timeout=timeout
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 404:
                return {"success": False, "code": 404, "message": "Not Found"}
            elif response.status_code == 429:
                # Rate limited - wait longer
                time.sleep(delay * 2)
                continue
            else:
                last_error = {
                    "code": response.status_code, 
                    "message": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            last_error = {"code": "TIMEOUT", "message": "Request timed out"}
        except requests.exceptions.ConnectionError:
            last_error = {"code": "CONNECTION", "message": "Connection failed"}
        except requests.exceptions.RequestException as e:
            last_error = {"code": "REQUEST_ERROR", "message": str(e)}
        except Exception as e:
            last_error = {"code": "UNKNOWN", "message": str(e)}
        
        if attempt < retries:
            time.sleep(delay)
    
    return {"success": False, **last_error}

# ------------------------------
# Finnhub Fetch (Simplified)
# ------------------------------
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_finnhub_company_data(symbol: str):
    """Fetch company data from Finnhub API"""
    
    base_url = "https://finnhub.io/api/v1"
    params = {"symbol": symbol, "token": FINNHUB_API_KEY}
    
    # Initialize results
    errors = []
    company_data = {
        "name": "N/A",
        "sector": "N/A", 
        "industry": "N/A",
        "marketCap": "N/A",
        "currentPrice": "N/A",
        "52WeekHigh": "N/A",
        "52WeekLow": "N/A",
        "description": "N/A",
        "metric": {}
    }
    
    try:
        # 1. Company Profile
        profile_result = fetch_with_retry(f"{base_url}/stock/profile2", params=params)
        if profile_result["success"]:
            profile = profile_result["data"]
            company_data.update({
                "name": profile.get("name", "N/A"),
                "sector": profile.get("finnhubIndustry", "N/A"),
                "industry": profile.get("finnhubIndustry", "N/A"),
                "description": profile.get("description", "N/A")[:500] + "..." if len(profile.get("description", "")) > 500 else profile.get("description", "N/A")
            })
        else:
            errors.append({
                "source": "Profile",
                "code": profile_result.get("code"),
                "message": profile_result.get("message")
            })
    
        # 2. Stock Quote
        quote_result = fetch_with_retry(f"{base_url}/quote", params=params)
        if quote_result["success"]:
            quote = quote_result["data"]
            company_data.update({
                "currentPrice": quote.get("c", "N/A"),
            })
        else:
            errors.append({
                "source": "Quote",
                "code": quote_result.get("code"),
                "message": quote_result.get("message")
            })
    
        # 3. Basic Metrics (simplified)
        metrics_params = {**params, "metric": "all"}
        metrics_result = fetch_with_retry(f"{base_url}/stock/metric", params=metrics_params)
        if metrics_result["success"]:
            metrics_data = metrics_result["data"]
            metrics = metrics_data.get("metric", {})
            company_data.update({
                "marketCap": metrics.get("marketCapitalization", "N/A"),
                "52WeekHigh": metrics.get("52WeekHigh", "N/A"),
                "52WeekLow": metrics.get("52WeekLow", "N/A"),
                "metric": metrics
            })
        else:
            errors.append({
                "source": "Metrics",
                "code": metrics_result.get("code"),
                "message": metrics_result.get("message")
            })
    
    except Exception as e:
        errors.append({
            "source": "General",
            "code": "EXCEPTION",
            "message": str(e)
        })
        log_error(f"Finnhub fetch error: {str(e)}")
    
    return {
        "data": company_data,
        "errors": errors
    }

# ------------------------------
# SEC Fetch (Simplified)
# ------------------------------
SEC_HEADERS = {"User-Agent": "FinancialDashboard/1.0"}

@st.cache_data(ttl=600)  # Cache for 10 minutes  
def get_sec_cik_mapping():
    """Get SEC CIK mapping data"""
    try:
        result = fetch_with_retry(
            "https://www.sec.gov/files/company_tickers.json",
            headers=SEC_HEADERS,
            timeout=15
        )
        if result["success"]:
            return result["data"]
        else:
            log_error(f"SEC CIK mapping error: {result.get('message')}")
            return {}
    except Exception as e:
        log_error(f"SEC CIK mapping exception: {str(e)}")
        return {}

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_sec_filings(symbol: str, count: int = 5):
    """Fetch SEC filings for a company"""
    
    try:
        # Get CIK mapping
        cik_lookup = get_sec_cik_mapping()
        if not cik_lookup:
            return {
                "data": [],
                "errors": [{"source": "SEC", "code": "CIK_MAPPING", "message": "Could not load CIK mapping"}]
            }
        
        # Find CIK for symbol
        cik = None
        for item in cik_lookup.values():
            if item.get("ticker", "").upper() == symbol.upper():
                cik = str(item.get("cik_str", "")).zfill(10)
                break
        
        if not cik:
            return {
                "data": [],
                "errors": [{"source": "SEC", "code": "CIK_NOT_FOUND", "message": f"No CIK found for {symbol}"}]
            }
        
        # Fetch filings
        filings_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        result = fetch_with_retry(filings_url, headers=SEC_HEADERS, timeout=15)
        
        if not result["success"]:
            return {
                "data": [],
                "errors": [{"source": "SEC", "code": result.get("code"), "message": result.get("message")}]
            }
        
        # Process filings data
        filings_data = result["data"]
        recent_filings = filings_data.get("filings", {}).get("recent", {})
        
        filings_list = []
        forms = recent_filings.get("form", [])
        dates = recent_filings.get("filingDate", [])
        accessions = recent_filings.get("accessionNumber", [])
        
        for i in range(min(count, len(forms))):
            filing = {
                "form": forms[i] if i < len(forms) else "N/A",
                "date": dates[i] if i < len(dates) else "N/A",
                "accession": accessions[i] if i < len(accessions) else "N/A"
            }
            
            # Generate filing URL
            if filing["accession"] != "N/A":
                clean_accession = filing["accession"].replace("-", "")
                filing["link"] = f"https://www.sec.gov/Archives/edgar/data/{cik}/{clean_accession}/{filing['accession']}.txt"
            else:
                filing["link"] = "N/A"
                
            filings_list.append(filing)
        
        return {
            "data": filings_list,
            "errors": []
        }
        
    except Exception as e:
        log_error(f"SEC filings error: {str(e)}")
        return {
            "data": [],
            "errors": [{"source": "SEC", "code": "EXCEPTION", "message": str(e)}]
        }