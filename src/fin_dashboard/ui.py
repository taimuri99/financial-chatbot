import streamlit as st
from .utils import format_currency
from .analytics import compute_ratios, summarize_trends
from .charts import (
    create_price_chart, 
    create_ratios_chart, 
    create_metrics_gauge_chart,
    create_trend_chart,
    create_candlestick_chart,
    create_financial_trends_chart,
    create_performance_comparison,
    create_portfolio_summary
)

def init_streamlit():
    """Initialize Streamlit configuration and custom styling"""
    st.set_page_config(
        page_title="Financial + SEC Dashboard", 
        page_icon="📊", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS for professional styling
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #1a202c;
        padding: 2rem 3rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Report card styling with glassmorphism */
    .report-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .report-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }

    /* Typography with enhanced styling */
    .card-title {
        font-size: 26px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .card-subtitle {
        font-size: 16px;
        color: #718096;
        margin-bottom: 20px;
        font-weight: 500;
    }

    /* Main title with animated gradient */
    .main-title {
        font-size: 42px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 3s ease-in-out infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .sub-title {
        font-size: 20px;
        color: #4a5568;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 400;
    }

    /* Enhanced button styling */
    .stButton > button {
        font-weight: 600;
        border-radius: 15px;
        border: none;
        padding: 16px 32px;
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    /* Enhanced metrics styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        transition: transform 0.2s ease;
    }

    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* Success/Error messages with better styling */
    .stSuccess, .stError, .stInfo, .stWarning {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Chart container styling */
    .chart-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

    # Main header with enhanced styling
    st.markdown('<h1 class="main-title">📊 Financial + SEC Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Advanced financial analysis with historical data, RAG-powered insights, and predictive analytics</p>', unsafe_allow_html=True)

def display_company_info(finnhub_data):
    """Display company information in a professional card"""
    if not finnhub_data:
        st.warning("⚠️ No company information available")
        return
    
    # Get description, handle cases where it might be empty or "N/A"
    description = finnhub_data.get('description', '')
    if not description or description == "N/A" or description.strip() == "":
        description = "No company description available from data sources."
    
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">🏢 Company Overview</div>
        <div class="card-subtitle">{finnhub_data.get('name', 'N/A')} • {finnhub_data.get('sector', 'N/A')} • {finnhub_data.get('industry', 'N/A')}</div>
        <p style="color: #4a5568; line-height: 1.8; margin: 0; font-size: 16px;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

def display_financial_metrics(finnhub_data):
    """UPGRADED: Display financial metrics with advanced visualizations"""
    if not finnhub_data:
        st.warning("⚠️ No financial metrics available")
        return
        
    st.markdown("""
    <div class="report-card">
        <div class="card-title">💹 Financial Metrics Dashboard</div>
    """, unsafe_allow_html=True)

    # Key Metrics Grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        market_cap = finnhub_data.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            market_cap_formatted = format_currency(market_cap)
            market_cap_change = "↗️" if market_cap != 'N/A' else ""
        else:
            market_cap_formatted = "N/A"
            market_cap_change = ""
        st.metric("Market Cap", market_cap_formatted, delta=market_cap_change)
    
    with col2:
        current_price = finnhub_data.get('currentPrice', 'N/A')
        if current_price != 'N/A':
            price_formatted = format_currency(current_price)
        else:
            price_formatted = "N/A"
        st.metric("Current Price", price_formatted)
    
    with col3:
        week_high = finnhub_data.get('52WeekHigh', 'N/A')
        if week_high != 'N/A':
            high_formatted = format_currency(week_high)
        else:
            high_formatted = "N/A"
        st.metric("52W High", high_formatted)
    
    with col4:
        week_low = finnhub_data.get('52WeekLow', 'N/A')
        if week_low != 'N/A':
            low_formatted = format_currency(week_low)
        else:
            low_formatted = "N/A"
        st.metric("52W Low", low_formatted)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Enhanced Price Charts
    historical_data = finnhub_data.get('historical_prices', {})
    if historical_data and historical_data.get('dates') and len(historical_data['dates']) > 0:
        
        # Chart type selector
        chart_cols = st.columns([1, 1, 2])
        with chart_cols[0]:
            chart_type = st.selectbox("Chart Type", ["Line + Volume", "Candlestick"], key="price_chart_type")
        
        # Always create the card container first
        st.markdown("""
        <div class="report-card">
            <div class="card-title">📈 Interactive Price Analysis</div>
        """, unsafe_allow_html=True)
        
        # Chart rendering in isolated try-catch
        chart_rendered = False
        
        if chart_type == "Line + Volume":
            try:
                price_chart = create_price_chart(
                    historical_data, 
                    finnhub_data.get('name', 'Company'),
                    'TICKER'
                )
                if price_chart:
                    st.plotly_chart(price_chart, use_container_width=True)
                    chart_rendered = True
            except Exception as e:
                st.error(f"Line chart error: {str(e)}")
        
        else:  # Candlestick
            try:
                # Debug info
                st.write("Debug: Attempting candlestick chart...")
                st.write(f"Has highs: {bool(historical_data.get('highs'))}")
                st.write(f"Has lows: {bool(historical_data.get('lows'))}")
                
                price_chart = create_candlestick_chart(
                    historical_data,
                    finnhub_data.get('name', 'Company'),
                    'TICKER'
                )
                
                if price_chart:
                    st.plotly_chart(price_chart, use_container_width=True)
                    chart_rendered = True
                else:
                    st.warning("Candlestick chart returned None")
                    
            except Exception as e:
                st.error(f"Candlestick error: {str(e)}")
                # Show fallback
                try:
                    price_chart = create_price_chart(
                        historical_data, 
                        finnhub_data.get('name', 'Company'),
                        'TICKER'
                    )
                    if price_chart:
                        st.plotly_chart(price_chart, use_container_width=True)
                        chart_rendered = True
                except Exception as fallback_e:
                    st.error(f"Fallback chart also failed: {str(fallback_e)}")
        
        if not chart_rendered:
            st.info("Chart could not be displayed. Please try the other chart type.")
        
        if historical_data.get('source'):
            st.info(f"📊 Data source: {historical_data['source']}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Price Position Gauge
    current_price = finnhub_data.get('currentPrice', 'N/A')
    week_high = finnhub_data.get('52WeekHigh', 'N/A')
    week_low = finnhub_data.get('52WeekLow', 'N/A')
    
    if all(x != 'N/A' for x in [current_price, week_high, week_low]):
        st.markdown("""
        <div class="report-card">
            <div class="card-title">🎯 Price Position Analysis</div>
        """, unsafe_allow_html=True)
        
        gauge_chart = create_metrics_gauge_chart(
            current_price, week_high, week_low, 'TICKER'
        )
        
        if gauge_chart:
            st.plotly_chart(gauge_chart, use_container_width=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

def display_ratios(finnhub_data):
    """UPGRADED: Enhanced ratios display with advanced charts"""
    if not finnhub_data:
        st.warning("⚠️ No ratio data available")
        return
        
    ratios = compute_ratios(finnhub_data)
    if not ratios:
        st.info("ℹ️ Ratio calculations not available for this company")
        return

    st.markdown("""
    <div class="report-card">
        <div class="card-title">📊 Financial Ratios Analysis</div>
        <div class="card-subtitle">Key performance indicators with industry benchmarking</div>
    """, unsafe_allow_html=True)

    # Ratios metrics grid
    col1, col2, col3, col4 = st.columns(4)
    ratio_keys = list(ratios.keys())
    
    for i, key in enumerate(ratio_keys[:8]):  # Show up to 8 ratios
        col = [col1, col2, col3, col4][i % 4]
        value = ratios[key]
        
        if value != "N/A" and isinstance(value, (int, float, str)):
            try:
                if isinstance(value, str) and '%' in value:
                    display_value = value
                else:
                    display_value = f"{float(value):.2f}" if isinstance(value, (int, float)) else str(value)
            except:
                display_value = str(value)
        else:
            display_value = "N/A"
        
        # Add color coding based on ratio health
        if "Margin" in key or "ROE" in key:
            delta_color = "normal" if display_value != "N/A" and float(display_value.replace('%', '')) > 15 else "inverse"
        else:
            delta_color = "normal"
            
        col.metric(key, display_value)

    # Enhanced Ratios Chart
    ratios_chart = create_ratios_chart(ratios)
    if ratios_chart:
        st.plotly_chart(ratios_chart, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

def display_trend_summary(finnhub_data):
    """UPGRADED: Enhanced trend display with multi-year analysis"""
    if not finnhub_data:
        st.warning("⚠️ No trend data available")
        return
        
    summary = summarize_trends(finnhub_data)
    
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">📈 Performance Trends & Analysis</div>
        <div class="card-subtitle">Year-over-year growth and profitability metrics with historical context</div>
    """, unsafe_allow_html=True)
    
    # Current period trends chart
    trend_data = {
        'Revenue Growth (YoY)': f"{finnhub_data.get('metric', {}).get('revenueGrowthTTMYoy', 0) * 100:.1f}%",
        'Profit Margin': f"{finnhub_data.get('metric', {}).get('netProfitMarginAnnual', 0):.1f}%",
        'ROE': f"{finnhub_data.get('metric', {}).get('roeAnnual', 0) * 100:.1f}%",
        'ROA': f"{finnhub_data.get('metric', {}).get('roaAnnual', 0) * 100:.1f}%"
    }
    
    trend_chart = create_trend_chart(trend_data)
    if trend_chart:
        st.plotly_chart(trend_chart, use_container_width=True)
    
    # Multi-year trends (if available)
    multi_year_data = finnhub_data.get('multi_year_data', {})
    if multi_year_data and multi_year_data.get('financial_data'):
        st.markdown("### 📊 Multi-Year Financial Trends")
        
        financial_trends_chart = create_financial_trends_chart(multi_year_data)
        if financial_trends_chart:
            st.plotly_chart(financial_trends_chart, use_container_width=True)
        
        # Performance comparison
        current_metrics = finnhub_data.get('metric', {})
        comparison_chart = create_performance_comparison(current_metrics, multi_year_data)
        if comparison_chart:
            st.plotly_chart(comparison_chart, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return summary

def display_sec_filings(sec_data):
    """Enhanced SEC filings display"""
    if not sec_data:
        st.info("ℹ️ No SEC filings data available")
        return "No SEC filings available"
    
    sec_summary = ""
    for filing in sec_data[:1]:
        form = filing.get('form', 'N/A')
        date = filing.get('date', 'N/A')
        sec_summary += f"• Form {form} filed on {date}<br>"
    
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">📄 Recent SEC Filings</div>
        <div class="card-subtitle">Latest regulatory filings and disclosures</div>
        <div style="color: #4a5568; line-height: 2.0; font-size: 16px;">
            {sec_summary if sec_summary else "No recent filings available"}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Expandable filing links
    if sec_data:
        with st.expander("🔗 View Filing Documents", expanded=False):
            for filing in sec_data[:5]:
                form = filing.get('form', 'N/A')
                date = filing.get('date', 'N/A')
                link = filing.get('link', '#')
                if link != '#' and link != 'N/A':
                    st.markdown(f"📋 [{form} - {date}]({link})")
                else:
                    st.text(f"📋 {form} - {date} (Link unavailable)")
    
    return sec_summary

def display_ai_insights(answer):
    """Enhanced AI insights display with proper formatting"""
    if not answer:
        st.warning("⚠️ No AI insights available")
        return
    
    # Clean and format the text
    import re
    formatted_answer = str(answer)
    
    # Fix markdown bold formatting
    formatted_answer = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_answer)
    
    # Fix line breaks and paragraphs
    formatted_answer = formatted_answer.replace('\n\n', '</p><p>')
    formatted_answer = formatted_answer.replace('\n', '<br>')
    
    # Fix bullet points
    formatted_answer = re.sub(r'^[\s]*[-•*]\s*', '• ', formatted_answer, flags=re.MULTILINE)
    
    # Fix numbered lists
    formatted_answer = re.sub(r'^[\s]*(\d+)\.[\s]*', r'\1. ', formatted_answer, flags=re.MULTILINE)
    
    # Wrap in paragraphs if not already
    if not formatted_answer.startswith('<p>'):
        formatted_answer = f'<p>{formatted_answer}</p>'
    
    st.markdown(f"""
    <div class="report-card">
        <div class="card-title">🤖 AI Financial Analysis</div>
        <div class="card-subtitle">Advanced insights powered by historical data and predictive analytics</div>
        <div style="
            color: #2d3748; 
            line-height: 1.8; 
            font-size: 16px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            padding: 24px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            margin-top: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        ">
            {formatted_answer}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_portfolio_summary(finnhub_data):
    """NEW: Executive-style portfolio summary"""
    if not finnhub_data:
        return
    
    st.markdown("""
    <div class="report-card">
        <div class="card-title">🎯 Executive Dashboard</div>
        <div class="card-subtitle">Comprehensive performance overview</div>
    """, unsafe_allow_html=True)
    
    portfolio_chart = create_portfolio_summary(finnhub_data)
    if portfolio_chart:
        st.plotly_chart(portfolio_chart, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)