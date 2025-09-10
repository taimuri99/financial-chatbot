from fpdf import FPDF
from datetime import datetime
from .utils import format_currency
from .analytics import format_percent

def create_pdf(ticker, finnhub_data, ratios, trend_summary, sec_summary, ai_insights):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Cover Page ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Financial + SEC Report for {ticker}", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.cell(0, 10, "Data Sources: Finnhub, SEC Filings", ln=True, align="C")
    pdf.ln(10)

    # --- Company Info ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "🏢 Company Info", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"Name: {finnhub_data.get('name','N/A')}\n"
                          f"Sector: {finnhub_data.get('sector','N/A')}\n"
                          f"Industry: {finnhub_data.get('industry','N/A')}\n"
                          f"Description: {finnhub_data.get('description','N/A')}")
    pdf.ln(5)
    pdf.add_page()

    # --- Financial Metrics Table ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "💹 Financial Metrics & Ratios", ln=True)
    pdf.set_font("Arial", "", 12)

    metrics_rows = [
        ["Market Cap", format_currency(finnhub_data.get('marketCap'))],
        ["Current Price", format_currency(finnhub_data.get('currentPrice'))],
        ["52 Week High", format_currency(finnhub_data.get('52WeekHigh'))],
        ["52 Week Low", format_currency(finnhub_data.get('52WeekLow'))],
    ]
    for key, val in ratios.items():
        # format percentages if applicable
        if isinstance(val, (float, int)):
            val = format_percent(val) if "%" not in str(val) else val
        metrics_rows.append([key, val])

    # Table rendering
    for row in metrics_rows:
        pdf.cell(60, 8, str(row[0]), border=1)
        pdf.cell(40, 8, str(row[1]), border=1, ln=True)
    pdf.ln(5)
    pdf.add_page()

    # --- Trend Summary ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "📈 Trend Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, trend_summary)
    pdf.ln(5)

    # --- SEC Filings ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "📄 SEC Filings Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, sec_summary or "No filings available")
    pdf.ln(5)

    # --- AI Insights ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "🤖 AI Insights", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, ai_insights)
    pdf.ln(5)

    filename = f"{ticker}_report.pdf"
    pdf.output(filename)
    return filename
