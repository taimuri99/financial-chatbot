import streamlit as st
from src.fin_dashboard.ui import (
    init_streamlit,
    display_company_info,
    display_financial_metrics,
    display_sec_filings,
    display_ai_insights,
    display_ratios,
    display_trend_summary
)
from src.fin_dashboard.datasources import get_finnhub_company_data, get_sec_filings
from src.fin_dashboard.llm import get_simple_ai_analysis
from src.fin_dashboard.analytics import compute_ratios, summarize_trends
import traceback

# ---------------------------
# Initialize Streamlit UI
# ---------------------------
init_streamlit()

# ---------------------------
# Sidebar controls
# ---------------------------
st.sidebar.header("⚙️ Controls")
example_tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
ticker = st.sidebar.selectbox(
    "Select or enter Stock Ticker:", example_tickers + ["Custom..."]
)
if ticker == "Custom...":
    ticker = st.sidebar.text_input("Enter your ticker:", "AAPL")

# Initialize session state for data persistence
if 'finnhub_data' not in st.session_state:
    st.session_state.finnhub_data = None
if 'sec_data' not in st.session_state:
    st.session_state.sec_data = None
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

# ---------------------------
# Two-Button Architecture
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    view_reports = st.button("📊 View Reports", type="primary", use_container_width=True)
    
with col2:
    ai_analysis = st.button("🤖 AI Analysis", type="secondary", use_container_width=True)

# User query for AI analysis
if ai_analysis:
    user_query = st.text_area(
        "Ask a question about this company:",
        "Summarize the financial performance and key metrics.",
        key="ai_query"
    )

# ---------------------------
# View Reports Workflow (Simple Data Display)
# ---------------------------
if view_reports:
    try:
        with st.spinner(f"🔍 Fetching data for {ticker.upper()}..."):
            # Fetch data with error handling
            finnhub_result = get_finnhub_company_data(ticker.upper())
            sec_result = get_sec_filings(ticker.upper(), count=5)
            
            # Store in session state
            st.session_state.finnhub_data = finnhub_result.get("data", {})
            st.session_state.sec_data = sec_result.get("data", [])
            
            # Display any API errors
            for err in finnhub_result.get("errors", []):
                st.error(f"Finnhub Error: {err.get('message', 'Unknown error')}")
            
            for err in sec_result.get("errors", []):
                st.warning(f"SEC Warning: {err.get('message', 'Unknown error')}")
        
        # Display data if available
        if st.session_state.finnhub_data:
            st.success("✅ Data fetched successfully!")
            
            # Display all sections
            display_company_info(st.session_state.finnhub_data)
            display_financial_metrics(st.session_state.finnhub_data)
            display_ratios(st.session_state.finnhub_data)
            display_trend_summary(st.session_state.finnhub_data)
            
            if st.session_state.sec_data:
                display_sec_filings(st.session_state.sec_data)
            else:
                st.info("ℹ️ No SEC filings data available")
                
        else:
            st.error(f"❌ Could not fetch data for {ticker.upper()}. Please check the ticker symbol.")
            
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.error("Please try again or contact support if the issue persists.")
        # Debug info (remove in production)
        with st.expander("Debug Information"):
            st.code(traceback.format_exc())

# ---------------------------
# AI Analysis Workflow (Separate LLM Processing)
# ---------------------------
if ai_analysis:
    # Check if we have data to analyze
    if not st.session_state.finnhub_data:
        st.warning("⚠️ Please fetch company data first using 'View Reports' button")
        st.stop()
    
    try:
        # Get user query
        query = st.session_state.get("ai_query", "Summarize the financial performance and key metrics.")
        
        with st.spinner("🤖 Generating AI insights..."):
            # Prepare context data
            context_data = {
                "company_info": st.session_state.finnhub_data,
                "sec_filings": st.session_state.sec_data,
                "ratios": compute_ratios(st.session_state.finnhub_data),
                "trends": summarize_trends(st.session_state.finnhub_data)
            }
            
            # Get AI analysis (simplified - no vector store)
            ai_response = get_simple_ai_analysis(context_data, query)
            st.session_state.analysis_data = ai_response
        
        # Display AI insights
        if st.session_state.analysis_data:
            st.success("✅ AI analysis complete!")
            display_ai_insights(st.session_state.analysis_data)
        else:
            st.error("❌ Could not generate AI analysis. Please try again.")
            
    except Exception as e:
        st.error(f"❌ AI Analysis error: {str(e)}")
        st.info("💡 Tip: Try a simpler question or check your API keys in Streamlit secrets.")
        # Debug info (remove in production)
        with st.expander("Debug Information"):
            st.code(traceback.format_exc())

# ---------------------------
# Display cached data if available
# ---------------------------
if not view_reports and not ai_analysis:
    # Show instructions
    st.info("👆 Choose an option above to get started!")
    
    # Display previously loaded data if available
    if st.session_state.finnhub_data:
        st.markdown("---")
        st.markdown("### 📋 Previously Loaded Data")
        display_company_info(st.session_state.finnhub_data)
        
        if st.session_state.analysis_data:
            display_ai_insights(st.session_state.analysis_data)