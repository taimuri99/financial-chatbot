# 📊 Financial + SEC Dashboard

## Financial Analysis Platform

---

A **streamlined financial analysis platform** combining **real-time market data from Finnhub, Yahoo Finance, and SEC filings, with powerful AI-powered insights**.

---

[DEPLOYMENT](https://financial-chatbot-taimurahmadkhan.streamlit.app/)

---

## 🏗️ Architecture Overview

### **Two-Workflow Design**
- **📊 View Reports**: Fast data retrieval and professional display (no AI processing)
- **🤖 AI Analysis**: Separate AI-powered insights workflow with context-aware analysis
   - **🖥️ RAG Analysis**: Optional enhanced analysis using multi-year historical financial data

### **Tech Stack**
- **Frontend**: Streamlit with custom CSS styling
- **Data & APIs**: Finnhub (primary for financials & metrics), Yahoo Finance (historical prices), SEC EDGAR (filings)
- **AI**: Google Gemini (primary) with **Groq (Llama 3.3 70B)** automatic fallback on quota limits
- **Data Processing**: Pandas with smart caching
- **Deployment**: Streamlit Cloud
- **Debugging**: Built-in data sourcing and error logging

---

## 🔹 Features

### **Data & Analytics**
* Real-time **company profiles**, **stock quotes**, and **key metrics** from Finnhub
* **Multi-year financial statements** (revenue, net income, growth trends) via reliable Finnhub + yFinance fallback
* **SEC filings** access (10-K, 10-Q, 8-K, etc.) with direct links
* **Financial ratio calculations** (P/E, Debt/Equity, ROE, etc.)
* **Trend analysis** and performance metrics
* Responsive UI with metrics cards and mobile-friendly design

### **AI-Powered Insights**
* **Context-aware analysis** using current and historical company data
* **Natural language queries** about financial performance, risks, and opportunities
* **RAG-enhanced analysis** referencing specific historical trends and patterns when available
* **Investment insights** and market positioning assessment
* **Automatic fallback** to Groq (Llama 3.3 70B) if Gemini quota is exceeded — no interruptions

---

## 🔹 How It Works

### **View Reports Workflow**
1. User selects company ticker
2. Fast data fetching from Finnhub (financials/metrics), yFinance (prices), and SEC
3. Professional dashboard display:
   - Company information and description
   - Real-time price and key metrics
   - Financial ratios and trends
   - Recent SEC filings with direct links
4. Data cached for AI analysis

### **AI Analysis Workflow**
1. User enters custom query about the company
2. Context preparation: Combines current data + multi-year historicals (if available)
3. AI processing: 
   - Primary: Google Gemini
   - Automatic seamless fallback to Groq (Llama 3.3 70B) on quota/rate limits
4. Returns detailed, professional financial analysis

---

## 🔹 Project Structure
Architecture details in `DIRECTORY.md`

---

## 🔹 API Requirements

### **Required API Keys**

1. **Finnhub API** (Free tier recommended)
   - Sign up: [finnhub.io/register](https://finnhub.io/register)
   - Add to Streamlit secrets as `FINNHUB_API_KEY`

2. **Google Gemini API** (Free tier)
   - Get key: [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Add to Streamlit secrets as `GEMINI_API_KEY`

3. **Groq API** (Optional but **highly recommended** for uninterrupted AI)
   - Free tier with fast inference and generous limits
   - Sign up: [console.groq.com/keys](https://console.groq.com/keys)
   - Add to Streamlit secrets as `GROQ_API_KEY`
   - Enables automatic fallback when Gemini quota is reached

---

Enjoy powerful, resilient financial analysis! 🚀