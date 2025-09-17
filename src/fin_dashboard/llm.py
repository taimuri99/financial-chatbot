import google.generativeai as genai
from .config import GOOGLE_API_KEY, TEMPERATURE
import streamlit as st
import json

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