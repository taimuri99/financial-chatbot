<!-- ---
title: Financial Report Assistant
emoji: "📊"
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.30.0"  # <-- Use a real Streamlit version
app_file: app.py
pinned: false
--- -->

# 📊 Financial + SEC Dashboard

## Friendly Neighbourhood Finance Guy

**Financial + SEC Dashboard** is a **professional portfolio project** combining **real-time market data, SEC filings, and AI-powered insights**. Users can query companies in natural language and generate **intuitive financial reports**.

The app is **deployable on Hugging Face Spaces** and demonstrates skills in **data engineering, NLP, AI pipelines, and financial analytics**.

---

## 🔹 Features

* Real-time **company data** from Finnhub (profile, quotes, metrics)
* Access recent **SEC filings** (10-K, 10-Q, 8-K, etc.)
* **AI-powered insights** via Hugging Face LLM + embeddings
* **Financial analytics**: ratios, benchmarks, and peer comparisons
* **Downloadable PDF/HTML reports**
* Professional **UI** with metrics cards and charts

---

## 🔹 How It Works

1. User selects a company ticker or enters a custom one.
2. Data is fetched from **Finnhub API** and **SEC EDGAR**.
3. Documents are processed into **chunks and embedded** for semantic retrieval.
4. User questions are answered using a **Hugging Face LLM**.
5. **Analytics layer** computes financial ratios, comparisons, and insights.
6. Results displayed in **cards and charts**, with optional **PDF download**.

---

## 🔹 Workflow Diagram

User → UI (Streamlit) → Data Sources (Finnhub + SEC)
↓
Retrieval (Chroma DB)
↓
LLM (Hugging Face QA)
↓
Analytics Layer (ratios, comparisons)
↓
UI Output (cards, charts, PDF report)

---

## 🔹 Deployment

* **STREAMLIT Spaces**

  * Ensure `app.py` is your entrypoint
  * `requirements.txt` contains all dependencies
  <!-- * `.streamlit/config.toml` sets theme and layout -->

* **Local Run**
  pip install -r requirements.txt
  streamlit run src/fin\_dashboard/main.py

* **Other Deployments**
  Compatible with Docker, Heroku, or other cloud services.

---

## 🔹 Project Structure

See `DIRECTORY.md` for a full explanation of files, folders, and workflow and `requirements.txt` for necessary requirements for deployment.

---

## 🔹 Professional Notes

* Lean, modular design: one file per concern
* Clear separation of UI, data, LLM, analytics, and reporting
* Portfolio-ready and recruiter-friendly
* Production-ready: caching, error handling, PDF reporting included
* Scalable: can grow to multiple LLMs, analytics modules, or front-end frameworks

---
