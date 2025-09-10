import streamlit as st

def safe_fetch(fetch_fn, *args, **kwargs):
    """Wrap any fetch call with error handling."""
    try:
        return fetch_fn(*args, **kwargs)
    except Exception as e:
        st.error(f"⚠️ Fetch error: {e}")
        return None

def format_currency(value):
    """Format numbers as USD currency with commas."""
    try:
        return "${:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "N/A"
