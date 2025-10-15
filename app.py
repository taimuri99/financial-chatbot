import streamlit as st
import google.generativeai as genai
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
    ["🏘️ Home", "🔍 Debug Finnhub API", "🔍 Debug SEC API", "🔍 Clear Cache", "🔍 Debug Gemini Models"],
    key="debug_selector"
)

# Handle debug actions
if debug_option == "🔍 Debug Finnhub API":
    debug_finnhub_api()
    if st.sidebar.button("🏠 Back to Main"):
        st.rerun()
    st.stop()
    
elif debug_option == "🔍 Debug SEC API":
    debug_sec_api()
    if st.sidebar.button("🏠 Back to Main"):
        st.rerun()
    st.stop()
    
elif debug_option == "🔍 Clear Cache":
    st.cache_data.clear()
    st.cache_resource.clear()
    st.sidebar.success("✅ Cache cleared!")
    if st.sidebar.button("🏠 Back to Main"):
        st.rerun()

elif debug_option == "🔍 Debug Gemini Models":
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.write("**Available Models:**")
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                st.success(f"✅ {model.name}")
                st.code(f"Use: genai.GenerativeModel('{model.name}')")
    st.stop()

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
# Two-Button Architecture
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    view_reports = st.button("📊 View Reports", type="primary", use_container_width=True)
    
with col2:
    if st.button("🧠 AI RAG Analysis", type="secondary", use_container_width=True):
        st.session_state['show_ai_analysis'] = True


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
# Enhanced AI Analysis Workflow with User Choice, sub buttons
# ---------------------------
if st.session_state.get('show_ai_analysis', False):
    # Back to Home button at the top
    if st.button("🏠 Back to Home"):
        if 'show_ai_analysis' in st.session_state:
            del st.session_state['show_ai_analysis']
        st.rerun()
    st.markdown("---")  # Visual separator
    # Check if we need fresh data for new ticker
    current_ticker = ticker.upper()
    if (not st.session_state.finnhub_data or 
        st.session_state.ticker_symbol != current_ticker):
        
        st.info(f"🔍 Fetching company data for {current_ticker}...")
        with st.spinner(f"Loading data for {current_ticker}..."):
            finnhub_result = get_finnhub_company_data(current_ticker)
            sec_result = get_sec_filings(current_ticker, count=5)
            
            st.session_state.finnhub_data = finnhub_result.get("data", {})
            st.session_state.sec_data = sec_result.get("data", [])
            st.session_state.ticker_symbol = current_ticker
    
    # Check available data
    multi_year_data = st.session_state.finnhub_data.get('multi_year_data', {})
    has_historical_data = bool(multi_year_data.get('financial_data'))
    
    # User query input (always show)
    user_query = st.text_area(
        "Ask a question about this company:",
        "Provide a comprehensive analysis of the company's financial performance, including historical trends and future outlook.",
        key="enhanced_ai_query",  # Different key to avoid conflicts
        height=100
    )
    
    # Analysis type selection with sub-buttons
    st.markdown("### Choose Analysis Method:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if has_historical_data:
            run_rag_analysis = st.button(
                "🧠 RAG-Enhanced Analysis", 
                help="Uses historical data + AI for deep insights",
                use_container_width=True,
                type="primary"
            )
        else:
            st.button(
                "🧠 RAG-Enhanced Analysis", 
                help="No historical data available",
                use_container_width=True,
                disabled=True
            )
            run_rag_analysis = False
    
    with col2:
        run_standard_analysis = st.button(
            "🤖 Standard AI Analysis",
            help="Current financial data + AI insights",
            use_container_width=True
        )
    
    # Show data availability info
    if has_historical_data:
        st.info(f"✅ Historical data available - RAG analysis will use multi-year financial records")
    else:
        st.warning("⚠️ No historical data found - Only standard analysis available")
    
    # Process analysis based on button clicked
    # Run analysis immediately when button is clicked
    if run_rag_analysis:
        st.session_state['analysis_type'] = 'RAG'
    elif run_standard_analysis:
        st.session_state['analysis_type'] = 'Standard'

    # Process analysis if a type was selected
    if st.session_state.get('analysis_type'):
        analysis_type = st.session_state['analysis_type']
        
        # Clear the selection after processing
        del st.session_state['analysis_type']

        try:
            query = user_query or "Provide a comprehensive financial analysis with historical context and predictive insights."
            
            # Prepare context data
            context_data = {
                "company_info": st.session_state.finnhub_data,
                "sec_filings": st.session_state.sec_data,
                "ratios": compute_ratios(st.session_state.finnhub_data),
                "trends": summarize_trends(st.session_state.finnhub_data),
                "ticker": st.session_state.ticker_symbol or ticker.upper(),
                "force_standard": run_standard_analysis  # Force standard if standard button clicked
            }
            
            # Run analysis with appropriate spinner
            if run_rag_analysis:
                with st.spinner("🧠 Generating RAG-enhanced analysis with historical context..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📊 Processing multi-year financial data...")
                    progress_bar.progress(25)
                    
                    status_text.text("🔍 Creating document vectors...")
                    progress_bar.progress(50)
                    
                    status_text.text("🧠 Retrieving relevant historical context...")
                    progress_bar.progress(75)
                    
                    enhanced_response = get_enhanced_ai_analysis(context_data, query)
                    
                    status_text.text("✅ RAG-enhanced analysis complete!")
                    progress_bar.progress(100)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
            else:
                with st.spinner("🤖 Generating standard AI analysis..."):
                    enhanced_response = get_enhanced_ai_analysis(context_data, query)
            
            st.session_state.analysis_data = enhanced_response
            
            # Display results with professional styling
            if st.session_state.analysis_data:
                analysis_result = st.session_state.analysis_data
                method_used = analysis_result.get("method", "Unknown")
                context_sources = analysis_result.get("context_sources", 0)
                analysis_text = analysis_result.get("analysis", "No analysis available")
            
                # Clean text formatting - more robust approach
                import re
                formatted_text = str(analysis_text)

                # Debug: Check what we're getting
                if formatted_text.startswith('<div') or 'long_conversation_reminder' in formatted_text:
                    st.error("❌ Analysis text corrupted. Retrying...")
                    st.stop()

                # Clean markdown symbols
                formatted_text = re.sub(r'#{1,6}\s*', '', formatted_text)
                formatted_text = re.sub(r'\*\*(.*?)\*\*', r'\1', formatted_text)
                formatted_text = re.sub(r'\*(.*?)\*', r'\1', formatted_text)
                formatted_text = formatted_text.replace('*', '')  # Remove any remaining asterisks
                formatted_text = formatted_text.strip()

                # Ensure we have actual content
                if len(formatted_text) < 50:
                    st.error("❌ Analysis text too short. Please try again.")
                    st.stop()
                
                # Professional Financial Report Display
                if method_used == "RAG-Enhanced":
                    st.success(f"✅ Enhanced Analysis Complete • {context_sources} Historical Data Points")
                    
                    # Executive Summary Header
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #1a365d 0%, #2d3748 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 15px 15px 0 0;
                        margin: 20px 0 0 0;
                    ">
                        <div style="font-size: 28px; font-weight: 800; margin-bottom: 8px;">
                            📊 FINANCIAL INTELLIGENCE REPORT
                        </div>
                        <div style="font-size: 16px; opacity: 0.9; font-weight: 500;">
                            Enhanced Analysis • {context_sources} Multi-Year Data Points • RAG-Powered Insights
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Main Analysis Content
                    st.markdown(f"""<div style="
                        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                        border-left: 6px solid #38b2ac;
                        padding: 0;
                        margin: 0 0 20px 0;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                        color: #2d3748;
                    ">
                        <div style="
                            background: rgba(56, 178, 172, 0.1);
                            padding: 20px 30px;
                            border-bottom: 2px solid rgba(56, 178, 172, 0.2);
                        ">
                            <div style="font-size: 20px; font-weight: 700; color: #2d3748; margin-bottom: 5px;">
                                📈 EXECUTIVE ANALYSIS
                            </div>
                            <div style="font-size: 14px; color: #4a5568; font-weight: 500;">
                                Historical Context Integration & Predictive Modeling
                            </div>
                        </div>
                            {formatted_text}
                        </div>
                    </div>""", unsafe_allow_html=True)
                    
                    # Methodology Footer
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #38b2ac 0%, #319795 100%);
                        color: white;
                        padding: 25px 30px;
                        border-radius: 0 0 15px 15px;
                        margin: 0;
                    ">
                        <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
                            🔬 METHODOLOGY & DATA SOURCES
                        </div>
                        <div style="font-size: 14px; opacity: 0.95; line-height: 1.6;">
                            Advanced RAG system analyzed {context_sources} historical data points spanning multiple fiscal years. 
                            Real-time market data integrated with historical patterns using AI-powered retrieval and synthesis.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.success("✅ AI Financial Analysis Complete")
                    
                    # Standard Analysis Header
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #553c9a 0%, #667eea 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 15px 15px 0 0;
                        margin: 20px 0 0 0;
                    ">
                        <div style="font-size: 28px; font-weight: 800; margin-bottom: 8px;">
                            🤖 AI FINANCIAL REPORT
                        </div>
                        <div style="font-size: 16px; opacity: 0.9; font-weight: 500;">
                            Professional Analysis • Current Market Data • AI-Generated Insights
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Main Analysis Content
                    st.markdown(f"""<div style="
                        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                        border-left: 6px solid #667eea;
                        padding: 0;
                        margin: 0 0 20px 0;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                        color: #2d3748;
                    ">
                        <div style="
                            background: rgba(102, 126, 234, 0.1);
                            padding: 20px 30px;
                            border-bottom: 2px solid rgba(102, 126, 234, 0.2);
                        ">
                            <div style="font-size: 20px; font-weight: 700; color: #2d3748; margin-bottom: 5px;">
                                📋 FINANCIAL ASSESSMENT
                            </div>
                            <div style="font-size: 14px; color: #4a5568; font-weight: 500;">
                                Current Market Analysis & Performance Evaluation
                            </div>
                        </div>
                            {formatted_text}
                        </div>
                    </div>""", unsafe_allow_html=True)
                    
                    # Standard Analysis Footer
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #553c9a 100%);
                        color: white;
                        padding: 25px 30px;
                        border-radius: 0 0 15px 15px;
                        margin: 0;
                    ">
                        <div style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
                            📊 ANALYSIS SCOPE
                        </div>
                        <div style="font-size: 14px; opacity: 0.95; line-height: 1.6;">
                            Analysis based on current financial metrics and real-time market data. 
                            For enhanced historical context and predictive modeling, multi-year data is required.
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
if not view_reports and not st.session_state.get('show_ai_analysis', False):
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
                • RAG-enhanced Historical data integration<br>
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