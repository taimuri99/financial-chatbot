import streamlit as st

def safe_fetch(fetch_fn, *args, **kwargs):
    """Wrap any fetch call with error handling."""
    try:
        return fetch_fn(*args, **kwargs)
    except Exception as e:
        st.error(f"⚠️ Fetch error: {e}")
        return None

def format_currency(value):
    """Format numbers as currency."""
    try:
        if value is None or value == "N/A":
            return "N/A"
        
        # Handle string inputs
        if isinstance(value, str):
            # Remove any existing formatting
            cleaned = value.replace('$', '').replace(',', '').strip()
            if cleaned == '' or cleaned == 'N/A':
                return "N/A"
            value = float(cleaned)
        
        # Format based on magnitude
        if abs(value) >= 1e12:
            return f"${value/1e12:.1f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.1f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.1f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.1f}K"
        else:
            return f"${value:.2f}"
            
    except (ValueError, TypeError):
        return "N/A"
