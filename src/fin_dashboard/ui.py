import streamlit as st
from .utils import format_currency
from .analytics import compute_ratios, summarize_trends

def init_streamlit():
    """Initialize Streamlit configuration and custom styling"""
    st.set_page_config(
        page_title="Financial + SEC Dashboard", 
        page_icon="📊", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        background-color: #f8fafc;
        color: #1a202c;
        padding: 2rem 3rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Report card styling */
    .report-card {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }

    .report-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    /* Typography */
    .card-title {
        font-size: 24px;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .card-subtitle {
        font-size: 16px;
        color: #718096;
        margin-bottom: 16px;
        font-weight: 500;
    }

    .metric-value {
        font-size: 20px;
        font-weight: 600;
        color: #2d3748;
    }

    /* Main title styling */
    .main-title {
        font-size: 36px;
        font-weight: 800;
        color: #2d3748;
        text-align: center;
        margin-bottom: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .sub-title {
        font-size: 18px;
        color: #718096;
        text-align: center;
        margin-bottom: 32px;
        font-weight: 400;
    }

    /* Button styling */
    .stButton > button {
        font-weight: 600;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f7fafc;
    }

    /* Metrics styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        border: 1px solid #e2e8f0;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* Success/Error message styling */
    .stSuccess {
        border-radius: 12px;
        border-left: 4px solid #48bb78;
    }

    .stError {
        border-radius: 12px;
        border-left: 4px solid #f56565;
    }

    .stInfo {
        border-radius: 12px;
        border-left: 4px solid #4299e1;
    }

    .stWarning {
        border-radius: 12px;
        border-left: 4px solid #ed8936;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main header
    st.markdown('<h1 class="main-title">📊 Financial + SEC Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Professional financial analysis with real-time data and AI insights</p>', unsafe_allow_html=True)

def display_company_info(finnhub_data):
    """Display company information in a professional card"""
    if not finnhub_data:
        st.warning("⚠️ No company information available")
        return
    
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">🏢 Company Overview</div>
        <div class="card-subtitle">{finnhub_data.get('name', 'N/A')} • {finnhub_data.get('sector', 'N/A')} • {finnhub_data.get('industry', 'N/A')}</div>
        <p style="color: #4a5568; line-height: 1.6; margin: 0;">{finnhub_data.get('description', 'No description available.')}</p>
    </div>
    """, unsafe_allow_html=True)

def display_financial_metrics(finnhub_data):
    """Display key financial metrics in a grid layout"""
    if not finnhub_data:
        st.warning("⚠️ No financial metrics available")
        return
        
    st.markdown("""
    <div class="report-card">
        <div class="card-title">💹 Key Financial Metrics</div>
    """, unsafe_allow_html=True)

    # Create metrics grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        market_cap = finnhub_data.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap = format_currency(market_cap)
        st.metric("Market Cap", market_cap)
    
    with col2:
        current_price = finnhub_data.get('currentPrice', 'N/A')
        if current_price != 'N/A':
            current_price = format_currency(current_price)
        st.metric("Current Price", current_price)
    
    with col3:
        week_high = finnhub_data.get('52WeekHigh', 'N/A')
        if week_high != 'N/A':
            week_high = format_currency(week_high)
        st.metric("52W High", week_high)
    
    with col4:
        week_low = finnhub_data.get('52WeekLow', 'N/A')
        if week_low != 'N/A':
            week_low = format_currency(week_low)
        st.metric("52W Low", week_low)
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_ratios(finnhub_data):
    """Display financial ratios in a professional layout"""
    if not finnhub_data:
        st.warning("⚠️ No ratio data available")
        return
        
    ratios = compute_ratios(finnhub_data)
    if not ratios:
        st.info("ℹ️ Ratio calculations not available for this company")
        return

    st.markdown("""
    <div class="report-card">
        <div class="card-title">📊 Financial Ratios</div>
        <div class="card-subtitle">Key performance indicators and valuation metrics</div>
    """, unsafe_allow_html=True)

    # Display ratios in a 4-column grid
    ratio_keys = list(ratios.keys())
    cols = st.columns(4)
    
    for i, key in enumerate(ratio_keys):
        col = cols[i % 4]
        value = ratios[key]
        
        # Format value for display
        if value != "N/A" and isinstance(value, (int, float)):
            if "Ratio" in key or key in ["P/E Ratio", "Current Ratio", "Quick Ratio"]:
                display_value = f"{value:.2f}"
            elif "Margin" in key or key == "ROE":
                display_value = f"{value:.2%}" if value else "N/A"
            else:
                display_value = f"{value:.2f}"
        else:
            display_value = str(value)
        
        col.metric(key, display_value)

    st.markdown("</div>", unsafe_allow_html=True)

def display_trend_summary(finnhub_data):
    """Display trend analysis summary"""
    if not finnhub_data:
        st.warning("⚠️ No trend data available")
        return
        
    summary = summarize_trends(finnhub_data)
    
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">📈 Performance Trends</div>
        <div class="card-subtitle">Year-over-year growth and profitability metrics</div>
        <pre style="
            font-size: 14px; 
            line-height: 1.6; 
            white-space: pre-wrap; 
            background-color: #f7fafc; 
            padding: 16px; 
            border-radius: 8px; 
            border: 1px solid #e2e8f0;
            color: #4a5568;
            margin: 0;
        ">{summary}</pre>
    </div>
    """, unsafe_allow_html=True)
    
    return summary

def display_sec_filings(sec_data):
    """Display SEC filings information"""
    if not sec_data:
        st.info("ℹ️ No SEC filings data available")
        return "No SEC filings available"
    
    # Format filings summary
    sec_summary = ""
    for filing in sec_data[:5]:  # Show max 5 filings
        form = filing.get('form', 'N/A')
        date = filing.get('date', 'N/A')
        link = filing.get('link', '#')
        sec_summary += f"• **{form}** filed on {date}\n"
    
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">📄 Recent SEC Filings</div>
        <div class="card-subtitle">Latest regulatory filings and disclosures</div>
        <div style="color: #4a5568; line-height: 1.8;">
            {sec_summary if sec_summary else "No recent filings available"}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create expandable section with filing links
    if sec_data:
        with st.expander("🔗 View Filing Links"):
            for filing in sec_data[:5]:
                form = filing.get('form', 'N/A')
                date = filing.get('date', 'N/A')
                link = filing.get('link', '#')
                if link != '#' and link != 'N/A':
                    st.markdown(f"[{form} - {date}]({link})")
                else:
                    st.text(f"{form} - {date} (Link unavailable)")
    
    return sec_summary

def display_ai_insights(answer):
    """Display AI analysis results"""
    if not answer:
        st.warning("⚠️ No AI insights available")
        return
    
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">🤖 AI Financial Analysis</div>
        <div class="card-subtitle">Professional insights generated by AI</div>
        <div style="
            color: #4a5568; 
            line-height: 1.7; 
            font-size: 16px;
            background-color: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            margin-top: 16px;
        ">
            {answer.replace('**', '<strong>').replace('**', '</strong>')}
        </div>
    </div>
    """, unsafe_allow_html=True)