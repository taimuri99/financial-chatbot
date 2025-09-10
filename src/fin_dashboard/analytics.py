#from utils import format_currency

def format_percent(value):
    """Format numbers as percentage with 2 decimals."""
    try:
        return "{:.2f}%".format(float(value) * 100)
    except (ValueError, TypeError):
        return "N/A"


def compute_ratios(finnhub_data):
    """Compute key financial ratios from Finnhub data."""
    ratios = {}
    try:
        metrics = finnhub_data.get("metric", {})

        # Core ratios
        ratios["P/E Ratio"] = metrics.get("peNormalizedAnnual", "N/A")
        ratios["Debt/Equity"] = metrics.get("totalDebt/totalEquityAnnual", "N/A")
        ratios["ROE"] = metrics.get("roeAnnual", "N/A")
        ratios["Current Ratio"] = metrics.get("currentRatioAnnual", "N/A")

        # Expanded ratios
        ratios["Price/Sales"] = metrics.get("psAnnual", "N/A")
        ratios["Quick Ratio"] = metrics.get("quickRatioAnnual", "N/A")
        ratios["Gross Margin"] = metrics.get("grossMarginAnnual", "N/A")
        ratios["EBITDA Margin"] = metrics.get("ebitdaMarginAnnual", "N/A")

    except Exception:
        pass
    return ratios


def summarize_trends(finnhub_data):
    """Return a richer textual trend summary for Streamlit display or LLM input."""
    metrics = finnhub_data.get("metric", {})

    revenue_growth = metrics.get("revenueGrowthTTMYoy", "N/A")
    profit_margin = metrics.get("netProfitMarginAnnual", "N/A")
    eps_growth = metrics.get("epsGrowthTTMYoy", "N/A")
    roa = metrics.get("roaAnnual", "N/A")

    summary = (
        f"Revenue Growth YoY: {format_percent(revenue_growth)}\n"
        f"Net Profit Margin: {format_percent(profit_margin)}\n"
        f"EPS Growth YoY: {format_percent(eps_growth)}\n"
        f"Return on Assets: {format_percent(roa)}"
    )

    return summary

