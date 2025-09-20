📂 Project Directory Structure

This document explains the structure of the Financial + SEC Dashboard project.
The app combines Finnhub market data + SEC filings, runs them through LLMs, and produces intuitive insights and reports.

📌 Directory Tree

/
├── README.md
├── requirements.txt
├── DIRECTORY.md
├── app.py              # Streamlit entrypoint
└── src/
    └── fin_dashboard/
        ├── config.py            # API keys, constants
        ├── ui.py                # layouts, components, charts
        ├── datasources.py       # SEC, yFinance sourcing + Finnhub API fetchers
        ├── charts.py            # viz - main page
        ├── llm.py               # geminiapi llm structure
        ├── analytics.py         # ratios + comparisons, formatting
        └── rag.py               # rag analysis - historical data WIP


📖 File/Folder Guide

Root Files

1) README.md → Project overview, installation, usage.
2) requirements.txt → Python dependencies.
3) DIRECTORY.md → Explains repo structure (this file).
4) app.py → App entrypoint, orchestrates workflow - Main Procedure Data

Source (src/fin_dashboard/)

1) config.py → Central config: API keys, constants, endpoints.
2) ui.py → UI components (cards, metrics, charts).
3) datasources.py → Fetchers for Finnhub API + SEC filings.
4) charts.py → Visualizations (analytics) main page.
5) llm.py → Gemini AI LLM pipeline for question answering.
6) analytics.py → Financial ratios, benchmarks, comparisons, formatting
7) rag.py → analytics.py → Financial ratios, benchmarks, comparisons.

🔄 Workflow Diagram

User → UI (Streamlit) → Data Sources (Finnhub, yFinance, SEC)
         ↓
    LLM (Google Gemini QA)
         ↓
    Analytics Layer (ratios, comparisons)
         ↓
    UI Output (cards, charts, AI Analysis)