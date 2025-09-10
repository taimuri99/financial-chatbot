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
        ├── reports.py           # PDF/HTML reporting
        └── utils.py             # caching, logging, helpers


📖 File/Folder Guide

Root Files

1) README.md → Project overview, installation, usage.
2) requirements.txt → Python dependencies.
3) .gitignore → Ensures caches, compiled files, and secrets are not committed.
4) DIRECTORY.md → Explains repo structure (this file).
5) .streamlit/config.toml → Custom Streamlit theme + app settings.

Data

1) data/chroma/ → Stores Chroma vector database (auto-generated, excluded from Git).

Source (src/fin_dashboard/)

1) main.py → App entrypoint, orchestrates workflow.
2) config.py → Central config: API keys, constants, endpoints.
3) ui.py → UI components (cards, metrics, charts).
4) datasources.py → Fetchers for Finnhub API + SEC filings.
5) retrieval.py → Embeddings + retriever setup (Chroma DB).
6) llm.py → Hugging Face pipeline for question answering.
7) analytics.py → Financial ratios, benchmarks, comparisons.
8) reports.py → Export styled PDF/HTML reports.
9) utils.py → Helpers: caching, logging, error handling.

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