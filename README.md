# 📊 Financial + SEC Dashboard

## Professional Financial Analysis Platform

**Financial + SEC Dashboard** is a **streamlined financial analysis platform** that combines **real-time market data from Finnhub, SEC filings, and AI-powered insights**. Built with modern architecture principles, it provides professional financial analysis through an intuitive two-button workflow.

---

## 🏗️ Architecture Overview

### **Two-Workflow Design**
- **📊 View Reports**: Fast data retrieval and professional display (no AI processing)
- **🤖 AI Analysis**: Separate AI-powered insights workflow with context-aware analysis

### **Tech Stack**
- **Frontend**: Streamlit with custom CSS styling
- **APIs**: Finnhub (market data) + SEC EDGAR (filings)
- **AI**: Google Gemini (direct API integration)
- **Data Processing**: Pandas with smart caching
- **Deployment**: Streamlit Cloud / Hugging Face Spaces

---

## 🔹 Features

### **Data & Analytics**
* Real-time **company profiles** and **stock quotes** from Finnhub
* **SEC filings** access (10-K, 10-Q, 8-K, etc.) with direct links
* **Financial ratio calculations** (P/E, Debt/Equity, ROE, etc.)
* **Trend analysis** and performance metrics
* **Professional UI** with metrics cards and responsive design

### **AI-Powered Insights**
* **Context-aware analysis** using company data and filings
* **Natural language queries** about financial performance
* **Professional financial analysis** with risk assessment
* **Investment insights** and market positioning analysis

### **User Experience**
* **Two-button workflow** for optimal performance
* **Session state management** - data persists between operations
* **Smart caching** prevents redundant API calls
* **Error handling** with graceful degradation
* **Mobile-responsive** design

---

## 🔹 How It Works

### **View Reports Workflow**
1. User selects company ticker
2. **Fast data fetching** from Finnhub API and SEC
3. **Professional dashboard display**:
   - Company information and description
   - Real-time financial metrics
   - Key financial ratios
   - Trend analysis
   - Recent SEC filings with direct links
4. Data cached for subsequent AI analysis

### **AI Analysis Workflow**
1. Requires previously fetched company data
2. User enters custom query about the company
3. **Context preparation**: Combines all company data, ratios, and trends
4. **AI processing**: Gemini analyzes data and generates insights
5. **Professional analysis display** with investment considerations

---

## 🔹 Project Structure

```
/
├── README.md                 # Project overview (this file)
├── requirements.txt          # Streamlined dependencies
├── app.py                   # Main Streamlit application
└── src/fin_dashboard/
    ├── config.py            # API keys and configuration
    ├── datasources.py       # Finnhub + SEC data fetchers
    ├── llm.py              # Simplified Gemini AI integration
    ├── ui.py               # Professional UI components
    ├── analytics.py        # Financial ratios and calculations
    └── utils.py            # Utility functions
```

### **Key Design Principles**
- **Separation of Concerns**: Each module has a single responsibility
- **Performance First**: Smart caching and optimized API calls
- **Error Resilience**: Graceful handling of API failures
- **User Experience**: Clear workflows and professional presentation
- **Scalability**: Modular design for easy feature additions

---

## 🔹 API Requirements

### **Required API Keys**
1. **Finnhub API**: Free tier provides 60 calls/minute
   - Sign up at [finnhub.io](https://finnhub.io)
   - Add to Streamlit secrets as `FINNHUB_API_KEY`

2. **Google Gemini API**: Free tier provides generous usage
   - Get key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add to Streamlit secrets as `GEMINI_API_KEY`

### **Streamlit Secrets Configuration**
Create `.streamlit/secrets.toml`:
```toml
FINNHUB_API_KEY = "your_finnhub_api_key_here"
GEMINI_API_KEY = "your_gemini_api_key_here"
```

---

## 🔹 Performance Features

### **Smart Caching**
- **Company Data**: 5-minute cache for real-time accuracy
- **SEC Filings**: 10-minute cache (less frequent updates)
- **AI Model**: Resource caching prevents reinitialization

### **Error Handling**
- **API Failures**: Graceful degradation with clear user feedback
- **Rate Limiting**: Automatic retry with exponential backoff
- **Data Validation**: Robust handling of missing or malformed data

### **User Experience**
- **Session State**: Data persists between button clicks
- **Loading States**: Clear progress indicators for all operations
- **Responsive Design**: Works on desktop and mobile devices


---