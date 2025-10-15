# LLM and AI, RAG BASED ANALYSIS

import google.generativeai as genai
from .config import GOOGLE_API_KEY, TEMPERATURE
import streamlit as st
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from datetime import datetime

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

@st.cache_resource
def init_gemini_model():
    """Initialize Gemini model with caching"""
    model = genai.GenerativeModel('models/gemini-1.5-flash')
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
    # Check if user forced standard analysis
    force_standard = context_data.get("force_standard", False)
    
    if force_standard:
        # Skip RAG and go directly to standard analysis
        standard_analysis = get_simple_ai_analysis(context_data, user_query)
        return {
            "analysis": standard_analysis,
            "method": "Standard AI",
            "context_sources": 0
        }
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


# ------------------------------
# STREAMLIT-COMPATIBLE RAG SYSTEM
# ------------------------------

@st.cache_resource
def init_simple_rag_system():
    """Initialize lightweight RAG system for Streamlit"""
    # Use TF-IDF instead of sentence transformers (lighter)
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    return vectorizer

def prepare_financial_documents(company_data, ticker):
    """Convert multi-year financial data into searchable documents"""
    documents = []
    metadata = []
    
    multi_year_data = company_data.get('multi_year_data', {})
    financial_data = multi_year_data.get('financial_data', {})
    ratios_timeline = multi_year_data.get('ratios_timeline', {})
    
    # 1. Revenue Documents
    if 'revenue' in financial_data:
        revenue_data = financial_data['revenue']
        for i, (date, value) in enumerate(zip(revenue_data['dates'], revenue_data['values'])):
            doc = f"In {date}, {ticker} reported total revenue of ${value/1e9:.2f} billion."
            
            if i > 0:
                prev_value = revenue_data['values'][i-1]
                growth = ((value - prev_value) / prev_value) * 100
                doc += f" This represents a {growth:+.1f}% change from the previous year."
            
            documents.append(doc)
            metadata.append({
                'type': 'revenue',
                'year': date,
                'value': value,
                'ticker': ticker
            })
    
    # 2. Profitability Documents  
    if 'net_income' in financial_data:
        income_data = financial_data['net_income']
        for i, (date, value) in enumerate(zip(income_data['dates'], income_data['values'])):
            doc = f"In {date}, {ticker} reported net income of ${value/1e9:.2f} billion."
            
            if i > 0:
                prev_value = income_data['values'][i-1]
                if prev_value != 0:
                    change = ((value - prev_value) / prev_value) * 100
                    doc += f" Net income {'increased' if change > 0 else 'decreased'} by {abs(change):.1f}% year-over-year."
            
            documents.append(doc)
            metadata.append({
                'type': 'net_income',
                'year': date,
                'value': value,
                'ticker': ticker
            })
    
    # 3. Growth Rate Documents
    if 'revenue_growth' in ratios_timeline:
        growth_data = ratios_timeline['revenue_growth']
        for date, growth_rate in zip(growth_data['dates'], growth_data['values']):
            if growth_rate > 10:
                growth_desc = "strong"
            elif growth_rate > 5:
                growth_desc = "moderate"
            elif growth_rate > 0:
                growth_desc = "modest"
            else:
                growth_desc = "negative"
            
            doc = f"In {date}, {ticker} experienced {growth_desc} revenue growth of {growth_rate:+.1f}%."
            documents.append(doc)
            metadata.append({
                'type': 'revenue_growth',
                'year': date,
                'value': growth_rate,
                'ticker': ticker
            })
    
    # 4. Profit Margin Documents
    if 'profit_margin' in ratios_timeline:
        margin_data = ratios_timeline['profit_margin']
        for date, margin in zip(margin_data['dates'], margin_data['values']):
            if margin > 20:
                margin_desc = "excellent"
            elif margin > 15:
                margin_desc = "strong"
            elif margin > 10:
                margin_desc = "healthy"
            else:
                margin_desc = "concerning"
            
            doc = f"In {date}, {ticker} maintained a {margin_desc} profit margin of {margin:.1f}%."
            documents.append(doc)
            metadata.append({
                'type': 'profit_margin',
                'year': date,
                'value': margin,
                'ticker': ticker
            })
    
    # 5. Trend Analysis Documents
    if len(financial_data.get('revenue', {}).get('values', [])) >= 3:
        revenue_values = financial_data['revenue']['values'][-3:]
        revenue_dates = financial_data['revenue']['dates'][-3:]
        
        if len(revenue_values) == 3:
            growth_1 = ((revenue_values[1] - revenue_values[0]) / revenue_values[0]) * 100
            growth_2 = ((revenue_values[2] - revenue_values[1]) / revenue_values[1]) * 100
            
            if growth_2 > growth_1:
                trend = "accelerating"
            elif growth_2 < growth_1:
                trend = "decelerating"
            else:
                trend = "stable"
            
            doc = f"Over the period {revenue_dates[0]}-{revenue_dates[-1]}, {ticker} shows {trend} revenue growth patterns. "
            doc += f"Growth was {growth_1:.1f}% in {revenue_dates[1]} and {growth_2:.1f}% in {revenue_dates[2]}."
            
            documents.append(doc)
            metadata.append({
                'type': 'trend_analysis',
                'period': f"{revenue_dates[0]}-{revenue_dates[-1]}",
                'trend': trend,
                'ticker': ticker
            })
    
    # 6. Predictive Insights Documents
    if 'revenue_growth' in ratios_timeline and len(ratios_timeline['revenue_growth']['values']) >= 3:
        growth_values = ratios_timeline['revenue_growth']['values'][-3:]
        growth_dates = ratios_timeline['revenue_growth']['dates'][-3:]
        
        # Ensure we have valid positive growth values
        valid_growth_values = [abs(float(x)) for x in growth_values if x is not None]
        
        if valid_growth_values:  # ✅ FIX: Only proceed if we have valid data
            avg_growth = np.mean(valid_growth_values)
        
        avg_growth = np.mean(valid_growth_values)
        
        # Simple trend: compare last value to first value
        if len(valid_growth_values) >= 2:
            recent_growth = valid_growth_values[-1]
            earlier_growth = valid_growth_values[0]
            
            if recent_growth > earlier_growth * 1.1:
                prediction = "improving"
                next_year_growth = min(recent_growth * 1.05, 15.0)  # Cap at 15%
            elif recent_growth < earlier_growth * 0.9:
                prediction = "declining" 
                next_year_growth = max(recent_growth * 0.95, 1.0)   # Floor at 1%
            else:
                prediction = "stable"
                next_year_growth = avg_growth
        else:
            prediction = "stable"
            next_year_growth = avg_growth
        
        doc = f"Based on {ticker}'s historical performance from {growth_dates[0]} to {growth_dates[-1]}, "
        doc += f"the company shows {prediction} growth trends with average growth of {avg_growth:.1f}%. "
        doc += f"If trends continue, projected growth for next year could be around {next_year_growth:.1f}%."
        
        documents.append(doc)
        metadata.append({
            'type': 'predictive_analysis',
            'prediction': prediction,
            'projected_growth': next_year_growth,
            'confidence': 'medium',
            'ticker': ticker
        })

    # Add this at the end of prepare_financial_documents function, before return:

    # 7. Current vs Historical Comparison Documents
    current_metrics = company_data.get('metric', {})
    if current_metrics and financial_data:
        current_margin = current_metrics.get('netProfitMarginAnnual', 0)
        current_roe = current_metrics.get('roeAnnual', 0)
        
        # Compare with historical averages
        if 'profit_margin' in ratios_timeline:
            hist_margins = ratios_timeline['profit_margin']['values']
            if hist_margins:
                avg_hist_margin = sum(hist_margins) / len(hist_margins)
                comparison = "improved" if current_margin > avg_hist_margin else "declined"
                doc = f"{ticker} current profit margin of {current_margin:.1f}% has {comparison} compared to historical average of {avg_hist_margin:.1f}%."
                documents.append(doc)
                metadata.append({'type': 'comparison', 'metric': 'profit_margin', 'ticker': ticker})

    # 8. Financial Stability Documents  
    if 'revenue' in financial_data and len(financial_data['revenue']['values']) >= 2:
        revenues = financial_data['revenue']['values']
        revenue_stability = max(revenues) / min(revenues) if min(revenues) > 0 else 1
        
        if revenue_stability < 1.5:
            stability_desc = "highly stable"
        elif revenue_stability < 2.0:
            stability_desc = "moderately stable"
        else:
            stability_desc = "volatile"
        
        doc = f"{ticker} shows {stability_desc} revenue patterns with a range factor of {revenue_stability:.1f}x over the analyzed period."
        documents.append(doc)
        metadata.append({'type': 'stability', 'metric': 'revenue', 'ticker': ticker})
    
    return documents, metadata




@st.cache_data(ttl=3600, show_spinner=False)
def create_simple_rag_store(company_data, ticker):
    """Create lightweight in-memory RAG store for Streamlit"""
    try:
        vectorizer = init_simple_rag_system()
        
        # Prepare documents
        documents, metadata = prepare_financial_documents(company_data, ticker)
        
        if not documents:
            return None, [], [], "No financial data available"
        
        # Create TF-IDF vectors (much lighter than embeddings)
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
        except Exception as e:
            return None, [], [], f"Vectorization failed: {str(e)}"
        
        return vectorizer, documents, metadata, None
        
    except Exception as e:
        return None, [], [], str(e)

def query_simple_rag(vectorizer, documents, metadata, query, top_k=3):
    """Query the lightweight RAG system"""
    try:
        if not documents:
            return {'documents': [], 'metadatas': [], 'scores': []}
        
        # Transform query
        query_vector = vectorizer.transform([query])
        
        # Transform documents
        doc_vectors = vectorizer.transform(documents)
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, doc_vectors).flatten()
        
        # Get top-k results
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        return {
            # lower threshold:
            'documents': [documents[i] for i in top_indices if similarities[i] > 0.05],
            'metadatas': [metadata[i] for i in top_indices if similarities[i] > 0.1],
            'scores': [similarities[i] for i in top_indices if similarities[i] > 0.1]
        }
        
    except Exception as e:
        return {
            'documents': [],
            'metadatas': [], 
            'scores': [],
            'error': str(e)
        }

def generate_rag_enhanced_analysis(company_data, ticker, user_query):
    """Generate RAG-enhanced analysis using lightweight system"""
    try:
        # Create simple RAG store
        vectorizer, documents, metadata, error = create_simple_rag_store(company_data, ticker)
        if error:
            return f"RAG system unavailable: {error}. Using standard analysis."
        
        if not documents:
            return "No historical financial data available for enhanced analysis."
        
        # Initialize LLM
        model = init_gemini_model()
        
        # Query RAG system
        rag_results = query_simple_rag(vectorizer, documents, metadata, user_query, top_k=3)
        
        if not rag_results['documents']:
            return "No relevant historical context found. Using current data analysis."
        
        # Prepare context from RAG results
        rag_context = "\n".join([
            f"Historical Context {i+1}: {doc}"
            for i, doc in enumerate(rag_results['documents'])
        ])
        
        # Current financial data
        current_metrics = company_data.get('metric', {})
        current_info = f"""
        Current Financial Status:
        - Current Price: ${company_data.get('currentPrice', 'N/A')}
        - Market Cap: ${company_data.get('marketCap', 'N/A')}
        - P/E Ratio: {current_metrics.get('peNormalizedAnnual', 'N/A')}
        - ROE: {current_metrics.get('roeAnnual', 'N/A')}
        - Profit Margin: {current_metrics.get('netProfitMarginAnnual', 'N/A')}%
        """
        
        # Create enhanced prompt
        enhanced_prompt = f"""
        You are a senior financial analyst with access to comprehensive historical data. 
        Analyze {company_data.get('name', ticker)} ({ticker}) based on the following information:
        
        HISTORICAL FINANCIAL CONTEXT (from multi-year analysis):
        {rag_context}
        
        CURRENT FINANCIAL STATUS:
        {current_info}
        
        USER QUESTION: {user_query}
        
        Based on this historical context and current data, provide a comprehensive analysis that:
        1. References specific historical trends and patterns
        2. Compares current performance to historical performance  
        3. Identifies key changes in business trajectory
        4. Provides data-driven insights about future prospects
        5. Highlights concerning or encouraging trends
        
        Make your analysis specific, referencing actual numbers and time periods.
        Focus on actionable insights for investment decisions.
        """
        
        # Generate enhanced response
        response = model.generate_content(enhanced_prompt)
        
        if response and response.text:
            # Add RAG system metadata
            rag_info = f"\n\n---\n**Enhanced with Historical Context**: Analysis incorporates {len(rag_results['documents'])} relevant historical data points."
            return response.text + rag_info
        else:
            return "Unable to generate enhanced analysis."
            
    except Exception as e:
        return f"Enhanced analysis error: {str(e)}. Please try standard AI analysis."

def get_predictive_insights(company_data, ticker):
    """Generate predictive insights based on historical patterns"""
    try:
        multi_year_data = company_data.get('multi_year_data', {})
        ratios_timeline = multi_year_data.get('ratios_timeline', {})
        
        insights = []
        
        # Revenue Growth Prediction
        if 'revenue_growth' in ratios_timeline:
            growth_data = ratios_timeline['revenue_growth']
            if len(growth_data['values']) >= 3:
                recent_growth = [abs(float(x)) for x in growth_data['values'][-3:] if x is not None]
                
                if recent_growth:
                    avg_growth = np.mean(recent_growth)
                    
                    # Simple prediction based on recent trend
                    if len(recent_growth) >= 2:
                        latest = recent_growth[-1]
                        previous = recent_growth[-2]
                        
                        if latest > previous:
                            prediction = min(latest * 1.02, 12.0)  # Small increase, cap at 12%
                            confidence = "medium"
                        else:
                            prediction = max(latest * 0.98, 2.0)   # Small decrease, floor at 2%
                            confidence = "medium"
                    else:
                        prediction = avg_growth
                        confidence = "low"
                else:
                    prediction = 5.0  # Default reasonable prediction
                    confidence = "low"
                
                insights.append({
                    'type': 'revenue_prediction',
                    'metric': 'Revenue Growth',
                    'predicted_value': prediction,
                    'confidence': confidence,
                    'reasoning': f"Based on {len(recent_growth)} years of historical data"
                })
        
        # Profit Margin Stability
        if 'profit_margin' in ratios_timeline:
            margin_data = ratios_timeline['profit_margin']
            if len(margin_data['values']) >= 3:
                margins = margin_data['values']
                stability = np.std(margins)
                avg_margin = np.mean(margins)
                
                if stability < 2:
                    stability_desc = "highly stable"
                elif stability < 5:
                    stability_desc = "moderately stable"
                else:
                    stability_desc = "volatile"
                
                insights.append({
                    'type': 'margin_stability',
                    'metric': 'Profit Margin Stability',
                    'stability': stability_desc,
                    'average_margin': avg_margin,
                    'volatility': stability
                })
        
        return insights
        
    except Exception as e:
        return [{'error': str(e)}]