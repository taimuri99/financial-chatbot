# 📊 Financial + SEC Dashboard

## Financial Analysis Platform

---

A **streamlined financial analysis platform** combining **real-time market data from Finnhub, Yahoo Finance, and SEC filings, and AI-powered insights**. 

---

[DEPLOYMENT](https://financial-chatbot-taimurahmadkhan.streamlit.app/)

---

## 🏗️ Architecture Overview

### **Three-Workflow Design**
- **📊 View Reports**: Fast data retrieval and professional display (no AI processing)
- **🤖 AI Analysis**: Separate AI-powered insights workflow with context-aware analysis
- **🖥️ Rag Analysis** Additional RAG enhanced analysis using historical data *(WIP)* 

### **Tech Stack**
- **Frontend**: Streamlit with custom CSS styling
- **DATA and APIs**: Yahoo Finance, Finnhub (market data) + SEC EDGAR (filings)
- **AI**: Google Gemini (direct API integration)
- **Data Processing**: Pandas with smart caching
- **Deployment**: Streamlit Cloud
- **Debugging**: Data sourcing and storage

---

## 🔹 Features

### **Data & Analytics**
* Real-time **company profiles** and **stock quotes** from Finnhub
* **SEC filings** access (10-K, 10-Q, 8-K, etc.) with direct links
* **Financial ratio calculations** (P/E, Debt/Equity, etc.)
* **Trend analysis** and performance metrics
* **UI** with metrics cards and responsive design: mobile responsiveness

### **AI-Powered Insights**
* **Context-aware analysis** using company data and filings
* **Natural language queries** about financial performance
* **Financial analysis** with risk assessment
* **Investment insights** and market positioning analysis

---

## 🔹 How It Works

### **View Reports Workflow**
1. User selects company ticker
2. **Fast data fetching** from Finnhub API, yFinance, and SEC
3. **Professional dashboard display**:
   - Company information and description
   - Real-time financial metrics
   - Key financial ratios
   - Trend analysis
   - Recent SEC filings with direct links
4. Data cached for subsequent AI analysis

### **AI Analysis Workflow**
1. User enters custom query about the company
2. **Context preparation**: Combines all company data, ratios, and trends
3. **AI processing**: Gemini analyzes data and generates insights

---

## 🔹 Project Structure
Architecture of project can be found in DIRECTORY.md

---

## 🔹 API Requirements (potential setup)

### **Required API Keys**
1. **Finnhub API**: Free tier
   - Sign up at [finnhub.io](https://finnhub.io)
   - Add to Streamlit secrets as `FINNHUB_API_KEY`

2. **Google Gemini API**: Free tier
   - Get key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add to Streamlit secrets as `GEMINI_API_KEY`

---