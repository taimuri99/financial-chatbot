import streamlit as st
from .utils import format_currency
from .analytics import compute_ratios, summarize_trends
import streamlit as st

def init_streamlit():
    st.set_page_config(page_title="Financial + SEC Report", page_icon="📊", layout="wide")
    st.markdown("""
    <style>
    .main .block-container { background-color: #f5f7fa; color: #202124; padding: 2rem 3rem; font-family: Arial, sans-serif; }

    .report-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }

    .report-card:hover { transform: translateY(-4px); }
    .card-title { font-size: 24px; font-weight: 600; color: #1a73e8; margin-bottom: 10px; }
    .card-subtitle { font-size: 16px; color: #5f6368; margin-bottom: 12px; }
    .metric { font-size: 20px; font-weight: 500; color: #202124; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="main-title">📊 Financial + SEC Report Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Analyze company data, SEC filings, generate insights, and download PDF reports.</p>', unsafe_allow_html=True)

def display_ratios(finnhub_data):
    ratios = compute_ratios(finnhub_data)

    st.markdown("""
    <div class="report-card">
        <div class="card-title">📊 Key Financial Ratios</div>
    """, unsafe_allow_html=True)

    # Display ratios in a grid
    cols = st.columns(4)
    keys = list(ratios.keys())
    for i, key in enumerate(keys):
        value = ratios[key]
        col = cols[i % 4]
        col.metric(key, value)

    st.markdown("</div>", unsafe_allow_html=True)


def display_trend_summary(finnhub_data):
    summary = summarize_trends(finnhub_data)
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">📈 Trend Summary</div>
        <pre style="font-size: 14px; white-space: pre-wrap;">{summary}</pre>
    </div>
    """, unsafe_allow_html=True)
    return summary


def display_company_info(finnhub_data):
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">🏢 Company Info</div>
        <div class="card-subtitle">{finnhub_data['name']} | {finnhub_data['sector']} | {finnhub_data['industry']}</div>
        <p>{finnhub_data['description']}</p>
    </div>
    """, unsafe_allow_html=True)

def display_financial_metrics(finnhub_data):
    st.markdown("""
    <div class="report-card">
        <div class="card-title">💹 Financial Metrics</div>
    """, unsafe_allow_html=True)

    # Use columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Cap", format_currency(finnhub_data.get('marketCap')))
    col2.metric("Current Price", format_currency(finnhub_data.get('currentPrice')))
    col3.metric("52 Week High", format_currency(finnhub_data.get('52WeekHigh')))
    col4.metric("52 Week Low", format_currency(finnhub_data.get('52WeekLow')))
    st.markdown("</div>", unsafe_allow_html=True)

def display_sec_filings(sec_data):
    sec_summary = ""
    for f in sec_data:
        sec_summary += f"- {f['form']} filed on {f['date']}: {f['link']}\n"
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">📄 SEC Filings Summary</div>
        <p>{sec_summary}</p>
    </div>
    """, unsafe_allow_html=True)
    return sec_summary

def display_ai_insights(answer):
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">🤖 AI Insights</div>
        <p>{answer}</p>
    </div>
    """, unsafe_allow_html=True)
