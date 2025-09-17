📂 Project Directory Structure

This document explains the structure of the Financial + SEC Dashboard project.
The app combines Finnhub market data + SEC filings, runs them through LLMs, and produces intuitive insights and reports.

📌 Directory Tree

/
├── README.md
├── requirements.txt
├── DIRECTORY.md
├── main.py              # Streamlit entrypoint
└── src/
    └── fin_dashboard/
        ├── config.py            # API keys, constants
        ├── ui.py                # layouts, components, charts
        ├── datasources.py       # SEC + Finnhub API fetchers
        ├── retrieval.py         # embeddings + retriever
        ├── llm.py               # Hugging Face LLM wrapper
        ├── analytics.py         # ratios + comparisons
        └── utils.py             # caching, logging, helpers


📖 File/Folder Guide

Root Files

1) README.md → Project overview, installation, usage.
2) requirements.txt → Python dependencies.
3) DIRECTORY.md → Explains repo structure (this file).

Main Procedure Data

1) app.py → App entrypoint, orchestrates workflow.

Source (src/fin_dashboard/)

1) config.py → Central config: API keys, constants, endpoints.
2) ui.py → UI components (cards, metrics, charts).
3) datasources.py → Fetchers for Finnhub API + SEC filings.
4) retrieval.py → Embeddings + retriever setup (Chroma DB).
5) llm.py → Hugging Face pipeline for question answering.
6) analytics.py → Financial ratios, benchmarks, comparisons.
7) utils.py → Helpers: caching, logging, error handling.

🔄 Workflow Diagram

User → UI (Streamlit) → Data Sources (Finnhub + SEC)
         ↓
    Retrieval (Chroma DB)
         ↓
    LLM (Hugging Face QA)
         ↓
    Analytics Layer (ratios, comparisons)
         ↓
    UI Output (cards, charts, PDF report)