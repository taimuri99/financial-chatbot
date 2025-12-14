import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .config import FINNHUB_API_KEY
import streamlit as st
import logging
import time  # For retries

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
# Yahoo Finance Historical Data
# ------------------------------
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_yahoo_historical_data(symbol: str, period: str = "1mo"):
    """
    Fetch historical data from Yahoo Finance
    Args:
        symbol: Stock ticker
        period: Time period ("1mo", "3mo", "6mo", "1y", "2y", "5y")
    """
    try:
        # Create yfinance ticker object
        ticker = yf.Ticker(symbol)
        
        # Download historical data
        hist_data = ticker.history(period=period)
        
        if hist_data.empty:
            return {
                "dates": [],
                "prices": [],
                "volumes": [],
                "highs": [],
                "lows": [],
                "opens": [],  
                "error": f"No data available for {symbol}"
            }
        
        # Convert to lists for JSON serialization
        dates = hist_data.index.strftime('%Y-%m-%d').tolist()
        prices = hist_data['Close'].tolist()
        volumes = hist_data['Volume'].tolist()
        highs = hist_data['High'].tolist()
        lows = hist_data['Low'].tolist()
        opens = hist_data['Open'].tolist()  # Add this line
        
        return {
            "dates": dates,
            "prices": prices,
            "volumes": volumes,
            "highs": highs,
            "lows": lows,
            "opens": opens,     # Add this line
            "error": None,
            "source": "Yahoo Finance"
        }
        
    except Exception as e:
        return {
            "dates": [],
            "prices": [],
            "volumes": [],
            "highs": [],
            "lows": [],
            "error": str(e)
        }

# ------------------------------
# Multi-Year Financial Data for RAG
# ------------------------------
@st.cache_data(ttl=7200) # Cache for 2 hours
def get_multi_year_financial_data(symbol: str):
    """
    Fetch multi-year financial data for RAG system
    Prioritizes Finnhub (stable) with yFinance fallback + anti-block measures
    """
    financial_timeline = {}
    ratios_timeline = {}
    error = None

    try:
        # --- Primary: Finnhub Standardized Financials (reliable) ---
        finnhub_url = "https://finnhub.io/api/v1/stock/financials"
        params = {"symbol": symbol, "statement": "is", "freq": "annual", "token": FINNHUB_API_KEY}  # Income statement annual
        result = fetch_with_retry(finnhub_url, params=params)

        if result["success"] and result["data"].get("data"):
            fin_data = result["data"]["data"]  # List of yearly reports (newest first)
            revenues = []
            net_incomes = []
            dates = []

            for year_data in fin_data[:6]:  # Last ~5-6 years
                report = year_data.get("report", {})
                date = year_data.get("year") or year_data.get("date", "N/A")
                if date != "N/A":
                    dates.append(str(date))
                    revenues.append(report.get("totalRevenue", 0) or 0)
                    net_incomes.append(report.get("netIncome", 0) or 0)

            if dates:
                financial_timeline['revenue'] = {'dates': dates[::-1], 'values': revenues[::-1]}  # Oldest first
                financial_timeline['net_income'] = {'dates': dates[::-1], 'values': net_incomes[::-1]}

        # --- Fallback: yFinance with fixes if Finnhub incomplete ---
        if not financial_timeline:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            ticker = yf.Ticker(symbol)
            
            # Retry loop with delay
            for attempt in range(3):
                try:
                    financials = ticker.financials
                    if not financials.empty and 'Total Revenue' in financials.index:
                        rev = financials.loc['Total Revenue'].dropna()
                        financial_timeline['revenue'] = {
                            'dates': rev.index.strftime('%Y').tolist(),
                            'values': rev.tolist()
                        }
                    if not financials.empty and 'Net Income' in financials.index:
                        ni = financials.loc['Net Income'].dropna()
                        financial_timeline['net_income'] = {
                            'dates': ni.index.strftime('%Y').tolist(),
                            'values': ni.tolist()
                        }
                    break  # Success
                except:
                    time.sleep(2 ** attempt)  # Exponential backoff

        # Calculate ratios if we have data
        if financial_timeline:
            ratios_timeline = calculate_historical_ratios(financial_timeline)

    except Exception as e:
        error = str(e)

    return {
        "financial_data": financial_timeline,
        "ratios_timeline": ratios_timeline,
        "company_info": {},  # Not needed here
        "error": error
    }

def calculate_historical_ratios(financial_data):
    """Calculate historical financial ratios for trend analysis"""
    ratios = {}
    
    try:
        # Revenue Growth Rate
        if 'revenue' in financial_data:
            revenue_data = financial_data['revenue']
            if len(revenue_data['values']) > 1:
                growth_rates = []
                for i in range(1, len(revenue_data['values'])):
                    prev = revenue_data['values'][i-1]
                    curr = revenue_data['values'][i]
                    if prev != 0:
                        growth = ((curr - prev) / prev) * 100
                        growth_rates.append(growth)
                
                if growth_rates:
                    ratios['revenue_growth'] = {
                        'dates': revenue_data['dates'][1:],
                        'values': growth_rates
                    }
        
        # Profit Margin Trend
        if 'revenue' in financial_data and 'net_income' in financial_data:
            rev_data = financial_data['revenue']
            income_data = financial_data['net_income']
            
            # Match dates
            common_dates = set(rev_data['dates']).intersection(set(income_data['dates']))
            if common_dates:
                margins = []
                dates = []
                for date in sorted(common_dates):
                    rev_idx = rev_data['dates'].index(date)
                    inc_idx = income_data['dates'].index(date)
                    
                    revenue = rev_data['values'][rev_idx]
                    income = income_data['values'][inc_idx]
                    
                    if revenue != 0:
                        margin = (income / revenue) * 100
                        margins.append(margin)
                        dates.append(date)
                
                if margins:
                    ratios['profit_margin'] = {
                        'dates': dates,
                        'values': margins
                    }
        
        return ratios
        
    except Exception as e:
        return {}

# ------------------------------
# Enhanced Finnhub with Yahoo Integration
# ------------------------------
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_finnhub_company_data(symbol: str):
    """Fetch company data from Finnhub API with Yahoo Finance historical data"""
    
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
        "metric": {},
        "historical_prices": {},  # Yahoo Finance data
        "multi_year_data": {}     # Multi-year financial data
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
    
        # 3. Basic Metrics
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
        
        # 4. Yahoo Finance Historical Prices (UPGRADED)
        historical_data = get_yahoo_historical_data(symbol, period="3mo")
        company_data["historical_prices"] = historical_data
        
        if historical_data.get("error"):
            errors.append({
                "source": "Yahoo Historical",
                "code": "YAHOO_ERROR",
                "message": historical_data["error"]
            })
        
        # 5. Multi-Year Financial Data (NEW FOR RAG)
        multi_year_data = get_multi_year_financial_data(symbol)
        company_data["multi_year_data"] = multi_year_data
        
        if multi_year_data.get("error"):
            errors.append({
                "source": "Multi-Year Data",
                "code": "MULTIYEAR_ERROR", 
                "message": multi_year_data["error"]
            })
    
    except Exception as e:
        errors.append({
            "source": "General",
            "code": "EXCEPTION",
            "message": str(e)
        })
        log_error(f"Data fetch error: {str(e)}")
    
    return {
        "data": company_data,
        "errors": errors
    }

# ------------------------------
# SEC Fetch
# ------------------------------
SEC_HEADERS = {
    "User-Agent": "FinancialDashboard/1.0 (student.research@university.edu)",
    "Accept": "application/json",
    "From": "student.research@university.edu"
}

@st.cache_data(ttl=600, show_spinner=False)
def get_sec_cik_mapping():
    """Get SEC CIK mapping data with better debugging"""
    try:
        result = fetch_with_retry(
            "https://www.sec.gov/files/company_tickers.json",
            headers=SEC_HEADERS,
            timeout=20,
            retries=3
        )
        
        if result["success"]:
            data = result["data"]
            if data and len(data) > 0:
                return data
            else:
                st.warning("⚠️ SEC returned empty data")
                return {}
        else:
            error_msg = result.get("message", "Unknown error")
            st.warning(f"⚠️ SEC CIK mapping failed: {error_msg}")
            return {}
            
    except Exception as e:
        st.error(f"❌ SEC CIK mapping exception: {str(e)}")
        return {}

@st.cache_data(ttl=600, show_spinner=False)
def get_sec_filings(symbol: str, count: int = 5):
    """Fetch SEC filings with better error handling"""
    
    try:
        # Step 1: Get CIK mapping
        cik_lookup = get_sec_cik_mapping()
        
        if not cik_lookup:
            return {
                "data": [],
                "errors": [{"source": "SEC", "code": "CIK_MAPPING_EMPTY", "message": "CIK mapping returned empty"}]
            }
        
        # Step 2: Find CIK for symbol
        cik = None
        symbol_upper = symbol.upper()
        
        for key, item in cik_lookup.items():
            item_ticker = item.get("ticker", "").upper()
            if item_ticker == symbol_upper:
                cik = str(item.get("cik_str", "")).zfill(10)
                break
        
        if not cik:
            example_tickers = []
            for key, item in list(cik_lookup.items())[:5]:
                example_tickers.append(item.get("ticker", ""))
            
            return {
                "data": [],
                "errors": [{"source": "SEC", "code": "CIK_NOT_FOUND", 
                          "message": f"No CIK found for {symbol_upper}"}]
            }
        
        # Step 3: Fetch filings for this CIK
        filings_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        result = fetch_with_retry(filings_url, headers=SEC_HEADERS, timeout=20)
        
        if not result["success"]:
            return {
                "data": [],
                "errors": [{"source": "SEC", "code": result.get("code"), 
                          "message": f"Filings fetch failed: {result.get('message')}"}]
            }
        
        # Step 4: Process filings data
        filings_data = result["data"]
        recent_filings = filings_data.get("filings", {}).get("recent", {})
        
        if not recent_filings:
            return {
                "data": [],
                "errors": [{"source": "SEC", "code": "NO_RECENT_FILINGS", 
                          "message": "No recent filings found"}]
            }
        
        # Step 5: Build filings list
        filings_list = []
        forms = recent_filings.get("form", [])
        dates = recent_filings.get("filingDate", [])
        accessions = recent_filings.get("accessionNumber", [])
        
        for i in range(min(count, len(forms))):
            if i < len(forms) and i < len(dates) and i < len(accessions):
                filing = {
                    "form": forms[i],
                    "date": dates[i],
                    "accession": accessions[i]
                }
                
                # Generate filing URL
                clean_accession = filing["accession"].replace("-", "")
                filing["link"] = f"https://www.sec.gov/Archives/edgar/data/{cik}/{clean_accession}/{filing['accession']}.txt"
                
                filings_list.append(filing)
        
        return {
            "data": filings_list,
            "errors": []
        }
        
    except Exception as e:
        error_msg = f"SEC filings error: {str(e)}"
        return {
            "data": [],
            "errors": [{"source": "SEC", "code": "EXCEPTION", "message": error_msg}]
        }