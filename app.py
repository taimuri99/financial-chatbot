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
from src.fin_dashboard.datasources import get_finnhub_company_data, get_sec_filings, log_warning
from src.fin_dashboard.retrieval import create_retriever
from src.fin_dashboard.reports import create_pdf
from src.fin_dashboard.analytics import compute_ratios, summarize_trends

# ---------------------------
# Initialize Streamlit UI
# ---------------------------
init_streamlit()

# ---------------------------
# Sidebar controls with session_state fix
# ---------------------------
st.sidebar.header("⚙️ Controls")
example_tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

# Initialize session_state for ticker
if "ticker" not in st.session_state:
    st.session_state["ticker"] = example_tickers[0]

# Selectbox for tickers
ticker = st.sidebar.selectbox(
    "Select or enter Stock Ticker:",
    example_tickers + ["Custom..."],
    index=example_tickers.index(st.session_state["ticker"])
)

# Handle custom ticker input
if ticker == "Custom...":
    custom_input = st.sidebar.text_input(
        "Enter your ticker:", value=str(st.session_state.get("ticker", "AAPL"))
    )
    if custom_input:
        ticker = str(custom_input.strip().upper())

st.session_state["ticker"] = ticker

# ---------------------------
# User Query Input
# ---------------------------
user_query = st.text_area(
    "Ask a question about this company:",
    "Summarize financial data and SEC filings.",
)

# ---------------------------
# Main Workflow
# ---------------------------
if st.button("🔍 Analyze"):
    output_box = st.empty()

    try:
        output_box.info(f"Fetching data for **{ticker}** ...")

        # 1. Get Data
        with st.spinner(f"Fetching data for {ticker} ..."):
            finnhub_result = get_finnhub_company_data(ticker)
            sec_result = get_sec_filings(ticker, count=5)

        finnhub_data = finnhub_result.get("data", {})
        finnhub_errors = finnhub_result.get("errors", [])
        sec_data = sec_result.get("data", [])
        sec_errors = sec_result.get("errors", [])

        # Display API errors
        for err in finnhub_errors + sec_errors:
            st.error(f"{err['source']} API Error: {err['code']} | {err['message']}")

        if not finnhub_data:
            output_box.error(f"❌ Could not fetch Finnhub data for {ticker}.")
            log_warning(f"Finnhub data missing for {ticker}")

        if not sec_data:
            st.warning(f"⚠️ No SEC filings found for {ticker} or SEC API is unreachable.")
            log_warning(f"SEC filings missing for {ticker}")

        # 2. Run Analytics
        with st.spinner("Computing financial ratios and trends..."):
            ratios = compute_ratios(finnhub_data)
            trend_summary = summarize_trends(finnhub_data)

        # 3. Display Data
        display_company_info(finnhub_data)
        display_financial_metrics(finnhub_data)
        display_ratios(finnhub_data)
        display_trend_summary(finnhub_data)
        sec_summary = display_sec_filings(sec_data)

        # 4. AI Insights
        combined_text = f"""
        {finnhub_data.get('description', 'No description available.')}

        Trends:
        {trend_summary}

        SEC Filings:
        {sec_summary or 'No filings available.'}
        """

        with st.spinner("Generating AI insights..."):
            qa_chain = create_retriever(combined_text)
            answer = qa_chain.run(user_query)
        display_ai_insights(answer)

        # 5. PDF Export
        with st.spinner("Generating PDF report..."):
            pdf_file = create_pdf(
                ticker,
                f"{finnhub_data}\n\nRatios:\n{ratios}\n\nTrends:\n{trend_summary}\n\nSEC Filings:\n{sec_summary}\n\nAI Insights:\n{answer}",
            )
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 Download Report as PDF",
                data=f,
                file_name=pdf_file,
                mime="application/pdf",
            )

        output_box.success("✅ Analysis complete!")

    except Exception as e:
        output_box.error(f"❌ Error: {e}")
