import streamlit as st
import requests
import traceback
from src.fin_dashboard.ui import (
    init_streamlit,
    display_company_info,
    display_financial_metrics,
    display_sec_filings,
    display_ai_insights,
    display_ratios,
    display_trend_summary,
    display_portfolio_summary
)
from src.fin_dashboard.datasources import get_finnhub_company_data, get_sec_filings
from src.fin_dashboard.llm import get_enhanced_ai_analysis, get_predictive_insights
from src.fin_dashboard.analytics import compute_ratios, summarize_trends
from src.fin_dashboard.config import FINNHUB_API_KEY

# ---------------------------
# DEBUG FUNCTIONS
# ---------------------------
def debug_finnhub_api():
    """Debug function to check Finnhub API response"""
    st.write("🔍 **Debugging Finnhub API**")
    
    if not FINNHUB_API_KEY:
        st.error("❌ No Finnhub API key found in secrets!")
        return
    
    st.write(f"**API Key Length:** {len(FINNHUB_API_KEY)} characters")
    st.write(f"**API Key Preview:** {FINNHUB_API_KEY[:8]}...")
    
    test_url = "https://finnhub.io/api/v1/stock/profile2"
    test_params = {"symbol": "AAPL", "token": FINNHUB_API_KEY}
    
    try:
        st.write("**Testing Profile Endpoint...**")
        response = requests.get(test_url, params=test_params, timeout=10)
        st.write(f"**Status Code:** {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            st.write("**✅ Profile Data (First few fields):**")
            st.json({k: v for k, v in list(data.items())[:5]} if data else "Empty response")
        else:
            st.error(f"**❌ Profile Error:** {response.text}")
            
        st.write("**Testing Metrics Endpoint...**")
        metrics_url = "https://finnhub.io/api/v1/stock/metric"
        metrics_params = {"symbol": "AAPL", "metric": "all", "token": FINNHUB_API_KEY}
        
        metrics_response = requests.get(metrics_url, params=metrics_params, timeout=10)
        st.write(f"**Metrics Status:** {metrics_response.status_code}")
        
        if metrics_response.status_code == 200:
            metrics_data = metrics_response.json()
            st.write("**✅ Metrics Data Structure:**")
            if metrics_data and 'metric' in metrics_data:
                key_metrics = {
                    'peNormalizedAnnual': metrics_data['metric'].get('peNormalizedAnnual'),
                    'grossMarginAnnual': metrics_data['metric'].get('grossMarginAnnual'),
                    'netProfitMarginAnnual': metrics_data['metric'].get('netProfitMarginAnnual'),
                    'revenueGrowthTTMYoy': metrics_data['metric'].get('revenueGrowthTTMYoy'),
                    'marketCapitalization': metrics_data['metric'].get('marketCapitalization')
                }
                st.json(key_metrics)
            else:
                st.json(metrics_data)
        else:
            st.error(f"**❌ Metrics Error:** {metrics_response.text}")
            
    except Exception as e:
        st.error(f"**❌ API Debug Error:** {e}")

def debug_sec_api():
    """Debug SEC API access"""
    st.write("🔍 **Debugging SEC API**")
    
    urls_to_test = [
        "https://www.sec.gov/files/company_tickers.json",
        "https://data.sec.gov/files/company_tickers.json"
    ]
    
    headers = {
        "User-Agent": "FinancialDashboard/1.0 (student.project@email.com)",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    }
    
    for url in urls_to_test:
        st.write(f"**Testing:** {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            st.write(f"**Status:** {response.status_code}")
            st.write(f"**Headers:** {dict(list(response.headers.items())[:3])}")
            
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ Success! Got {len(data)} companies")
                if data:
                    first_key = list(data.keys())[0]
                    st.json({first_key: data[first_key]})
                break
            else:
                st.error(f"❌ Failed: {response.text[:200]}")
                
        except Exception as e:
            st.error(f"❌ Exception: {str(e)}")

# ---------------------------
# Initialize Streamlit UI
# ---------------------------
init_streamlit()

# ---------------------------
# Sidebar controls + DEBUG DROPDOWN
# ---------------------------
st.sidebar.header("⚙️ Controls")

# Debug dropdown
debug_option = st.sidebar.selectbox(
    "🔧 Debug Tools",
    ["None", "Debug Finnhub API", "Debug SEC API", "Clear Cache"],
    key="debug_selector"
)

# Handle debug actions
if debug_option == "Debug Finnhub API":
    debug_finnhub_api()
    if st.sidebar.button("🏠 Back to Main"):
        st.rerun()
    st.stop()
    
elif debug_option == "Debug SEC API":
    debug_sec_api()
    if st.sidebar.button("🏠 Back to Main"):
        st.rerun()
    st.stop()
    
elif debug_option == "Clear Cache":
    st.cache_data.clear()
    st.cache_resource.clear()
    st.sidebar.success("✅ Cache cleared!")
    if st.sidebar.button("🏠 Back to Main"):
        st.rerun()

# Regular controls
example_tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]
ticker = st.sidebar.selectbox(
    "Select or enter Stock Ticker:", example_tickers + ["Custom..."]
)
if ticker == "Custom...":
    ticker = st.sidebar.text_input("Enter your ticker:", "AAPL")

# Analysis options
st.sidebar.header("📊 Analysis Options")
enable_rag = st.sidebar.checkbox("🧠 Enable RAG Analysis", value=True, help="Use historical data for enhanced insights")
enable_predictions = st.sidebar.checkbox("🔮 Enable Predictions", value=True, help="Generate predictive insights")

# Initialize session state for data persistence
if 'finnhub_data' not in st.session_state:
    st.session_state.finnhub_data = None
if 'sec_data' not in st.session_state:
    st.session_state.sec_data = None
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'ticker_symbol' not in st.session_state:
    st.session_state.ticker_symbol = None

# ---------------------------
# Three-Button Architecture
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    view_reports = st.button("📊 View Reports", type="primary", use_container_width=True)
    
with col2:
    enhanced_ai_analysis = st.button("🧠 AI RAG Analysis", type="secondary", use_container_width=True)

# User query for AI analysis
if  enhanced_ai_analysis:
    user_query = st.text_area(
        "Ask a question about this company:",
        "Provide a comprehensive analysis of the company's financial performance, including historical trends and future outlook.",
        key="ai_query",
        height=100
    )

# ---------------------------
# View Reports Workflow
# ---------------------------
if view_reports:
    try:
        with st.spinner(f"🔍 Fetching comprehensive data for {ticker.upper()}..."):
            # Fetch data with error handling
            finnhub_result = get_finnhub_company_data(ticker.upper())
            sec_result = get_sec_filings(ticker.upper(), count=5)
            
            # Store in session state
            st.session_state.finnhub_data = finnhub_result.get("data", {})
            st.session_state.sec_data = sec_result.get("data", [])
            st.session_state.ticker_symbol = ticker.upper()
            
            # Display any API errors
            for err in finnhub_result.get("errors", []):
                if err.get('source') not in ['Yahoo Historical', 'Multi-Year Data']:
                    st.error(f"Finnhub Error: {err.get('message', 'Unknown error')}")
            
            for err in sec_result.get("errors", []):
                st.warning(f"SEC Warning: {err.get('message', 'Unknown error')}")
        
        # Display data if available
        if st.session_state.finnhub_data:
            st.success("✅ Data fetched successfully!")
            
            # UPGRADED: Enhanced display sections
            display_company_info(st.session_state.finnhub_data)
            display_financial_metrics(st.session_state.finnhub_data)
            display_ratios(st.session_state.finnhub_data)
            display_trend_summary(st.session_state.finnhub_data)
            
            # Portfolio-style summary (if ui.py supports it)
            try:
                display_portfolio_summary(st.session_state.finnhub_data)
            except:
                pass  # Skip if function doesn't exist yet
            
            # SEC filings
            if st.session_state.sec_data:
                display_sec_filings(st.session_state.sec_data)
            else:
                st.info("ℹ️ No SEC filings data available")
            
            # Predictive insights (if enabled)
            if enable_predictions:
                with st.spinner("🔮 Generating predictive insights..."):
                    try:
                        insights = get_predictive_insights(st.session_state.finnhub_data, st.session_state.ticker_symbol)
                        
                        if insights and not any('error' in insight for insight in insights):
                            st.markdown("""
                            <div class="report-card">
                                <div class="card-title">🔮 Predictive Insights</div>
                                <div class="card-subtitle">AI-powered predictions based on historical patterns</div>
                            """, unsafe_allow_html=True)
                            
                            for insight in insights:
                                if insight.get('type') == 'revenue_prediction':
                                    st.metric(
                                        "Predicted Revenue Growth", 
                                        f"{insight['predicted_value']:.1f}%",
                                        help=f"Confidence: {insight['confidence']} - {insight['reasoning']}"
                                    )
                                elif insight.get('type') == 'margin_stability':
                                    st.info(f"📊 Profit margins are {insight['stability']} with average of {insight['average_margin']:.1f}%")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("🔮 Predictive insights require multi-year historical data.")
                    except Exception as e:
                        st.warning(f"⚠️ Predictive analysis unavailable: {str(e)}")
                
        else:
            st.error(f"❌ Could not fetch data for {ticker.upper()}. Please check the ticker symbol.")
            
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.error("Please try again or contact support if the issue persists.")
        with st.expander("Debug Information"):
            st.code(traceback.format_exc())

# ---------------------------
# Enhanced AI Analysis Workflow (Replace both AI and RAG sections)
# ---------------------------
if enhanced_ai_analysis:
    if not st.session_state.finnhub_data:
        st.info("🔍 Fetching company data for enhanced RAG analysis...")
        with st.spinner(f"Loading data for {ticker.upper()}..."):
            finnhub_result = get_finnhub_company_data(ticker.upper())
            sec_result = get_sec_filings(ticker.upper(), count=5)
            
            st.session_state.finnhub_data = finnhub_result.get("data", {})
            st.session_state.sec_data = sec_result.get("data", [])
            st.session_state.ticker_symbol = ticker.upper()
    
    try:
        query = st.session_state.get("ai_query", "Provide a comprehensive financial analysis with historical context and predictive insights.")
        
        # Check if we have multi-year data for enhanced analysis
        multi_year_data = st.session_state.finnhub_data.get('multi_year_data', {})
        has_historical_data = bool(multi_year_data.get('financial_data'))
        
        if has_historical_data:
            with st.spinner("🧠 Generating enhanced AI RAG analysis with historical context..."):
                # Progress indicators for RAG-enhanced analysis
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("📊 Processing multi-year financial data...")
                progress_bar.progress(25)
                
                status_text.text("🔍 Creating document vectors...")
                progress_bar.progress(50)
                
                status_text.text("🧠 Retrieving relevant historical context...")
                progress_bar.progress(75)
                
                # Prepare context data
                context_data = {
                    "company_info": st.session_state.finnhub_data,
                    "sec_filings": st.session_state.sec_data,
                    "ratios": compute_ratios(st.session_state.finnhub_data),
                    "trends": summarize_trends(st.session_state.finnhub_data),
                    "ticker": st.session_state.ticker_symbol or ticker.upper()
                }
                
                # Use enhanced AI analysis
                enhanced_response = get_enhanced_ai_analysis(context_data, query)
                
                status_text.text("✅ Enhanced AI RAG analysis complete!")
                progress_bar.progress(100)
                
                st.session_state.analysis_data = enhanced_response
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
        else:
            with st.spinner("🤖 Generating RAG AI analysis..."):
                # Standard AI analysis for companies without multi-year data
                context_data = {
                    "company_info": st.session_state.finnhub_data,
                    "sec_filings": st.session_state.sec_data,
                    "ratios": compute_ratios(st.session_state.finnhub_data),
                    "trends": summarize_trends(st.session_state.finnhub_data)
                }
                
                enhanced_response = get_enhanced_ai_analysis(context_data, query)
                st.session_state.analysis_data = enhanced_response
        
        # Display results
        if st.session_state.analysis_data:
            analysis_result = st.session_state.analysis_data
            method_used = analysis_result.get("method", "Unknown")
            context_sources = analysis_result.get("context_sources", 0)
            analysis_text = analysis_result.get("analysis", "No analysis available")
            
            # Format the analysis text
            import re
            formatted_text = str(analysis_text)
            formatted_text = str(analysis_text)
            # Clean markdown formatting
            formatted_text = re.sub(r'#{1,6}\s*(.*)', r'<h3 style="color: #2d3748; margin: 24px 0 16px 0; font-weight: 700;">\1</h3>', formatted_text)
            formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_text)
            formatted_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_text)
            formatted_text = re.sub(r'^[\s]*[•*-]\s*', '• ', formatted_text, flags=re.MULTILINE)
            # Convert paragraphs
            paragraphs = formatted_text.split('\n\n')
            formatted_paragraphs = []
            for p in paragraphs:
                if p.strip():
                    # Replace single newlines with spaces within paragraphs
                    p = p.replace('\n', ' ').strip()
                    formatted_paragraphs.append(f'<p style="margin-bottom: 16px; text-align: justify;">{p}</p>')
            formatted_text = ''.join(formatted_paragraphs)
            
            if not formatted_text.startswith('<p>'):
                formatted_text = f'<p>{formatted_text}</p>'
            
            # Professional combined display
            if method_used == "RAG-Enhanced":
                st.success(f"✅ Enhanced Analysis Complete • {context_sources} Historical Data Points Integrated")
                
                st.markdown(f"""
                <div class="report-card" style="
                    background: linear-gradient(135deg, rgba(56, 178, 172, 0.05) 0%, rgba(72, 187, 120, 0.05) 100%);
                    border: 2px solid rgba(56, 178, 172, 0.3);
                    border-radius: 20px;
                    overflow: hidden;
                ">
                    <div style="
                        background: linear-gradient(135deg, #38b2ac 0%, #48bb78 100%);
                        color: white;
                        padding: 24px;
                        margin: -28px -28px 20px -28px;
                    ">
                        <div style="font-size: 24px; font-weight: 700; margin-bottom: 8px;">
                            🧠 Advanced Financial Intelligence Report
                        </div>
                        <div style="font-size: 16px; opacity: 0.9;">
                            Powered by AI + Historical Data Analysis • {context_sources} Multi-Year Data Points
                        </div>
                    </div>
                    
                    <div style="
                        color: #2d3748; 
                        line-height: 1.8; 
                        font-size: 17px;
                        background: rgba(255, 255, 255, 0.9);
                        padding: 32px;
                        border-radius: 15px;
                        margin: 0 -8px;
                        box-shadow: inset 0 2px 8px rgba(0,0,0,0.06);
                        border-left: 4px solid #38b2ac;
                    ">
                        {formatted_text}
                    </div>
                    
                    <div style="
                        background: linear-gradient(135deg, rgba(56, 178, 172, 0.1) 0%, rgba(72, 187, 120, 0.1) 100%);
                        border-radius: 12px;
                        padding: 20px;
                        margin-top: 20px;
                        border: 1px solid rgba(56, 178, 172, 0.2);
                    ">
                        <div style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">
                            📊 Analysis Methodology
                        </div>
                        <div style="color: #4a5568; font-size: 15px; line-height: 1.6;">
                            This report combines current financial metrics with {context_sources} historical data points 
                            spanning multiple years. Our RAG-enhanced AI system retrieved relevant historical patterns 
                            and integrated them with real-time market data to provide comprehensive investment insights.
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.success("✅ AI Financial Analysis Complete")
                
                st.markdown(f"""
                <div class="report-card" style="
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(159, 122, 234, 0.05) 100%);
                    border: 2px solid rgba(102, 126, 234, 0.3);
                    border-radius: 20px;
                    overflow: hidden;
                ">
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #9f7aea 100%);
                        color: white;
                        padding: 24px;
                        margin: -28px -28px 20px -28px;
                    ">
                        <div style="font-size: 24px; font-weight: 700; margin-bottom: 8px;">
                            🤖 AI Financial Analysis Report
                        </div>
                        <div style="font-size: 16px; opacity: 0.9;">
                            Professional insights based on current financial data
                        </div>
                    </div>
                    
                    <div style="
                        color: #2d3748; 
                        line-height: 1.8; 
                        font-size: 17px;
                        background: rgba(255, 255, 255, 0.9);
                        padding: 32px;
                        border-radius: 15px;
                        margin: 0 -8px;
                        box-shadow: inset 0 2px 8px rgba(0,0,0,0.06);
                        border-left: 4px solid #667eea;
                    ">
                        {formatted_text}
                    </div>
                    
                    <div style="
                        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(159, 122, 234, 0.1) 100%);
                        border-radius: 12px;
                        padding: 20px;
                        margin-top: 20px;
                        border: 1px solid rgba(102, 126, 234, 0.2);
                    ">
                        <div style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">
                            📋 Analysis Note
                        </div>
                        <div style="color: #4a5568; font-size: 15px; line-height: 1.6;">
                            This analysis is based on current financial data and market metrics. 
                            For enhanced insights with historical context, multi-year financial data is required.
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ Could not generate enhanced analysis. Please try again.")
    
    except Exception as e:
        st.error(f"❌ Enhanced Analysis error: {str(e)}")
        st.info("💡 Tip: Try refreshing the page or check your API keys in Streamlit secrets.")
        with st.expander("Debug Information"):
            st.code(traceback.format_exc())

# ---------------------------
# Welcome Screen
# ---------------------------
if not view_reports and not enhanced_ai_analysis:
    # Welcome message with feature highlights 
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎯 Welcome to the Financial Analysis Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Financial insights with AI and predictive analytics</div>', unsafe_allow_html=True)

    # Create three columns for the feature cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 24px; background: linear-gradient(135deg, #e6f3ff 0%, #f0f8ff 100%); border-radius: 15px; border: 2px solid rgba(66, 153, 225, 0.2); margin-bottom: 20px;">
            <h3 style="color: #2b6cb0; margin-bottom: 12px;">📊 View Reports</h3>
            <p style="color: #4a5568; font-size: 14px; line-height: 1.6; margin: 0;">
                • Interactive price & volume charts<br>
                • Multi-year financial trends<br>
                • Professional ratio analysis<br>
                • Predictive insights
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 24px; background: linear-gradient(135deg, #f0fff4 0%, #f7fafc 100%); border-radius: 15px; border: 2px solid rgba(56, 161, 105, 0.2); margin-bottom: 20px;">
            <h3 style="color: #38a169; margin-bottom: 12px;">🧠 Enhanced AI Analysis</h3>
            <p style="color: #4a5568; font-size: 14px; line-height: 1.6; margin: 0;">
                • Gemini-powered insights<br>
                • Historical data integration<br>
                • RAG-enhanced when available<br>
                • Custom query responses<br>
                • Predictive recommendations
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display previously loaded data if available
    if st.session_state.finnhub_data:
        st.markdown("---")
        st.markdown("### 📋 Previously Loaded Data")
        display_company_info(st.session_state.finnhub_data)
        
        if st.session_state.analysis_data:
            display_ai_insights(st.session_state.analysis_data)