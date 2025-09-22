import google.generativeai as genai
from .config import GOOGLE_API_KEY, TEMPERATURE
import streamlit as st
import json
from .rag import create_simple_rag_store, query_simple_rag

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

@st.cache_resource
def init_gemini_model():
    """Initialize Gemini model with caching"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def get_simple_ai_analysis(context_data, user_query):
    """
    Simple AI analysis without LangChain complexity
    Uses direct Gemini API calls
    """
    try:
        model = init_gemini_model()
        
        # Prepare context from the data
        company_info = context_data.get("company_info", {})
        ratios = context_data.get("ratios", {})
        trends = context_data.get("trends", "")
        sec_filings = context_data.get("sec_filings", [])
        
        # Create a structured prompt
        context_text = f"""
        Company Analysis Data:
        
        Company: {company_info.get('name', 'N/A')}
        Sector: {company_info.get('sector', 'N/A')}
        Current Price: ${company_info.get('currentPrice', 'N/A')}
        Market Cap: ${company_info.get('marketCap', 'N/A')}
        
        Key Financial Ratios:
        {format_ratios_for_prompt(ratios)}
        
        Financial Trends:
        {trends}
        
        Recent SEC Filings ({len(sec_filings)} filings):
        {format_sec_filings_for_prompt(sec_filings)}
        
        Company Description:
        {company_info.get('description', 'N/A')[:300]}...
        """
        
        # Create the full prompt
        full_prompt = f"""
        You are a professional financial analyst. Based on the following company data, please provide a comprehensive analysis.
        
        {context_text}
        
        User Question: {user_query}
        
        Please provide a detailed, professional analysis that includes:
        1. Key financial insights
        2. Risk factors and opportunities
        3. Market position assessment
        4. Investment considerations
        
        Keep your response informative, well-structured, and professional.
        """
        
        # Generate response
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=TEMPERATURE,
                max_output_tokens=1000,
            )
        )
        
        if response and response.text:
            return response.text
        else:
            return "Unable to generate analysis. Please try again."
            
    except Exception as e:
        st.error(f"AI Analysis Error: {str(e)}")
        return f"Error generating analysis: {str(e)}. Please check your API key and try again."
    

def get_enhanced_ai_analysis(context_data, user_query):
    """
    Enhanced AI analysis that combines standard AI with RAG when available
    Uses RAG for historical context, falls back to standard AI if no multi-year data
    """
    try:
        model = init_gemini_model()
        company_info = context_data.get("company_info", {})
        
        # Check if we have multi-year data for RAG enhancement
        multi_year_data = company_info.get('multi_year_data', {})
        has_historical_data = bool(multi_year_data.get('financial_data'))
        
        if has_historical_data:
            # Use RAG-enhanced analysis
            ticker = context_data.get("ticker", "UNKNOWN")
            
            # Create RAG store
            vectorizer, documents, metadata, error = create_simple_rag_store(company_info, ticker)
            
            if not error and documents:
                # Query RAG system for relevant context
                rag_results = query_simple_rag(vectorizer, documents, metadata, user_query, top_k=3)
                
                if rag_results['documents']:
                    # Prepare RAG context
                    rag_context = "\n".join([
                        f"Historical Context {i+1}: {doc}"
                        for i, doc in enumerate(rag_results['documents'])
                    ])
                    
                    # Current financial data
                    ratios = context_data.get("ratios", {})
                    trends = context_data.get("trends", "")
                    sec_filings = context_data.get("sec_filings", [])
                    
                    # Enhanced prompt with RAG context
                    enhanced_prompt = f"""
                    You are a professional financial analyst with access to comprehensive historical data.
                    
                    HISTORICAL FINANCIAL CONTEXT:
                    {rag_context}
                    
                    CURRENT COMPANY DATA:
                    Company: {company_info.get('name', 'N/A')}
                    Sector: {company_info.get('sector', 'N/A')}
                    Current Price: ${company_info.get('currentPrice', 'N/A')}
                    Market Cap: ${company_info.get('marketCap', 'N/A')}
                    
                    Key Financial Ratios:
                    {format_ratios_for_prompt(ratios)}
                    
                    Financial Trends:
                    {trends}
                    
                    Recent SEC Filings ({len(sec_filings)} filings):
                    {format_sec_filings_for_prompt(sec_filings)}
                    
                    User Question: {user_query}
                    
                    Based on this historical context and current data, provide a comprehensive analysis that:
                    1. References specific historical trends and patterns
                    2. Compares current performance to historical performance
                    3. Identifies key changes in business trajectory
                    4. Provides data-driven insights about future prospects
                    5. Highlights concerning or encouraging trends
                    
                    Make your analysis specific, referencing actual numbers and time periods.
                    """
                    
                    # Generate enhanced response
                    response = model.generate_content(enhanced_prompt)
                    
                    if response and response.text:
                        return {
                            "analysis": response.text,
                            "method": "RAG-Enhanced",
                            "context_sources": len(rag_results['documents'])
                        }
        
        # Fallback to standard AI analysis
        standard_analysis = get_simple_ai_analysis(context_data, user_query)
        return {
            "analysis": standard_analysis,
            "method": "Standard AI",
            "context_sources": 0
        }
        
    except Exception as e:
        # Final fallback
        return {
            "analysis": f"Enhanced analysis error: {str(e)}. Please try again.",
            "method": "Error",
            "context_sources": 0
        }

def format_ratios_for_prompt(ratios):
    """Format ratios dictionary for the prompt"""
    if not ratios:
        return "No ratio data available"
    
    formatted = []
    for key, value in ratios.items():
        if value != "N/A":
            formatted.append(f"- {key}: {value}")
    
    return "\n".join(formatted) if formatted else "No ratio data available"

def format_sec_filings_for_prompt(sec_filings):
    """Format SEC filings for the prompt"""
    if not sec_filings:
        return "No recent SEC filings available"
    
    formatted = []
    for filing in sec_filings[:3]:  # Only include first 3 for prompt brevity
        form = filing.get('form', 'N/A')
        date = filing.get('date', 'N/A')
        formatted.append(f"- {form} filed on {date}")
    
    return "\n".join(formatted) if formatted else "No recent SEC filings available"

# Backup simple analysis function for when API fails
def get_fallback_analysis(context_data, user_query):
    """Provide basic analysis when AI is unavailable"""
    company_info = context_data.get("company_info", {})
    ratios = context_data.get("ratios", {})
    
    analysis = f"""
    📊 **Basic Analysis for {company_info.get('name', 'N/A')}**
    
    **Company Overview:**
    - Sector: {company_info.get('sector', 'N/A')}
    - Current Price: ${company_info.get('currentPrice', 'N/A')}
    - Market Cap: ${company_info.get('marketCap', 'N/A')}
    
    **Key Metrics:**
    - P/E Ratio: {ratios.get('P/E Ratio', 'N/A')}
    - Debt/Equity: {ratios.get('Debt/Equity', 'N/A')}
    - ROE: {ratios.get('ROE', 'N/A')}
    
    **Note:** This is a basic analysis. AI analysis is currently unavailable.
    Please check your internet connection and API keys.
    """
    
    return analysis