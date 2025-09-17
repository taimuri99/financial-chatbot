def format_percent(value):
    """Format numbers as percentage with 2 decimals."""
    try:
        if value is None:
            return "N/A"
        
        # Check if Finnhub returns percentages as whole numbers or decimals
        # Based on debug: grossMarginAnnual: 46.21 (this is 46.21%, not 0.4621)
        # So we DON'T multiply by 100
        return "{:.2f}%".format(float(value))
    except (ValueError, TypeError):
        return "N/A"

def format_ratio(value, decimal_places=2):
    """Format numbers as ratio with specified decimal places."""
    try:
        if value is None:
            return "N/A"
        return "{:.{}f}".format(float(value), decimal_places)
    except (ValueError, TypeError):
        return "N/A"

def compute_ratios(finnhub_data):
    """
    Compute key financial ratios from Finnhub data.
    Returns a dictionary of formatted ratio values.
    """
    if not finnhub_data:
        return {}
    
    ratios = {}
    
    try:
        metrics = finnhub_data.get("metric", {})
        
        # Core Valuation Ratios
        pe_ratio = metrics.get("peNormalizedAnnual")
        if pe_ratio and pe_ratio != 0:
            ratios["P/E Ratio"] = format_ratio(pe_ratio)
        else:
            ratios["P/E Ratio"] = "N/A"
        
        price_sales = metrics.get("psAnnual")
        if price_sales:
            ratios["Price/Sales"] = format_ratio(price_sales)
        else:
            ratios["Price/Sales"] = "N/A"
        
        # Debt and Leverage Ratios
        debt_equity = metrics.get("totalDebt/totalEquityAnnual")
        if debt_equity:
            ratios["Debt/Equity"] = format_ratio(debt_equity)
        else:
            ratios["Debt/Equity"] = "N/A"
        
        # Profitability Ratios  
        roe = metrics.get("roeAnnual")
        if roe:
            ratios["ROE"] = format_percent(roe)
        else:
            ratios["ROE"] = "N/A"
        
        gross_margin = metrics.get("grossMarginAnnual")
        if gross_margin:
            ratios["Gross Margin"] = format_percent(gross_margin)
        else:
            ratios["Gross Margin"] = "N/A"
        
        ebitda_margin = metrics.get("ebitdaMarginAnnual")
        if ebitda_margin:
            ratios["EBITDA Margin"] = format_percent(ebitda_margin)
        else:
            ratios["EBITDA Margin"] = "N/A"
        
        # Liquidity Ratios
        current_ratio = metrics.get("currentRatioAnnual")
        if current_ratio:
            ratios["Current Ratio"] = format_ratio(current_ratio)
        else:
            ratios["Current Ratio"] = "N/A"
        
        quick_ratio = metrics.get("quickRatioAnnual")
        if quick_ratio:
            ratios["Quick Ratio"] = format_ratio(quick_ratio)
        else:
            ratios["Quick Ratio"] = "N/A"
        
    except Exception as e:
        # If there's any error in computation, return empty dict
        print(f"Error computing ratios: {e}")
        return {}
    
    return ratios

def summarize_trends(finnhub_data):
    """
    Generate a comprehensive textual trend summary for display and AI analysis.
    Returns formatted string with key growth and performance metrics.
    """
    if not finnhub_data:
        return "No trend data available."
    
    try:
        metrics = finnhub_data.get("metric", {})
        
        # Extract key trend metrics
        revenue_growth = metrics.get("revenueGrowthTTMYoy")
        profit_margin = metrics.get("netProfitMarginAnnual")
        eps_growth = metrics.get("epsGrowthTTMYoy")
        roa = metrics.get("roaAnnual")
        
        # Build summary with proper formatting
        summary_lines = []
        
        # Revenue Growth
        if revenue_growth is not None:
            summary_lines.append(f"Revenue Growth (YoY): {format_percent(revenue_growth)}")
        else:
            summary_lines.append("Revenue Growth (YoY): N/A")
        
        # Profit Margin  
        if profit_margin is not None:
            summary_lines.append(f"Net Profit Margin: {format_percent(profit_margin)}")
        else:
            summary_lines.append("Net Profit Margin: N/A")
        
        # EPS Growth
        if eps_growth is not None:
            summary_lines.append(f"EPS Growth (YoY): {format_percent(eps_growth)}")
        else:
            summary_lines.append("EPS Growth (YoY): N/A")
        
        # Return on Assets
        if roa is not None:
            summary_lines.append(f"Return on Assets: {format_percent(roa)}")
        else:
            summary_lines.append("Return on Assets: N/A")
        
        # Additional metrics if available
        operating_margin = metrics.get("operatingMarginAnnual")
        if operating_margin is not None:
            summary_lines.append(f"Operating Margin: {format_percent(operating_margin)}")
        
        asset_turnover = metrics.get("assetTurnoverAnnual")
        if asset_turnover is not None:
            summary_lines.append(f"Asset Turnover: {format_ratio(asset_turnover)}")
        
        return "\n".join(summary_lines)
        
    except Exception as e:
        print(f"Error generating trend summary: {e}")
        return "Error generating trend summary. Please try again."

def get_financial_health_score(finnhub_data):
    """
    Calculate a simple financial health score based on key metrics.
    Returns a score from 0-100 and a health category.
    """
    if not finnhub_data:
        return 0, "No Data"
    
    try:
        metrics = finnhub_data.get("metric", {})
        score = 0
        factors_evaluated = 0
        
        # Profitability factors (40% of score)
        roe = metrics.get("roeAnnual")
        if roe is not None:
            if roe > 0.15:  # 15%+ ROE is excellent
                score += 20
            elif roe > 0.10:  # 10-15% is good
                score += 15
            elif roe > 0.05:  # 5-10% is fair
                score += 10
            factors_evaluated += 1
        
        profit_margin = metrics.get("netProfitMarginAnnual")
        if profit_margin is not None:
            if profit_margin > 0.20:  # 20%+ margin is excellent
                score += 20
            elif profit_margin > 0.10:  # 10-20% is good
                score += 15
            elif profit_margin > 0.05:  # 5-10% is fair
                score += 10
            factors_evaluated += 1
        
        # Growth factors (30% of score)
        revenue_growth = metrics.get("revenueGrowthTTMYoy")
        if revenue_growth is not None:
            if revenue_growth > 0.20:  # 20%+ growth is excellent
                score += 15
            elif revenue_growth > 0.10:  # 10-20% is good
                score += 12
            elif revenue_growth > 0.05:  # 5-10% is fair
                score += 8
            elif revenue_growth > 0:  # Positive growth
                score += 5
            factors_evaluated += 1
        
        eps_growth = metrics.get("epsGrowthTTMYoy")
        if eps_growth is not None:
            if eps_growth > 0.20:
                score += 15
            elif eps_growth > 0.10:
                score += 12
            elif eps_growth > 0.05:
                score += 8
            elif eps_growth > 0:
                score += 5
            factors_evaluated += 1
        
        # Financial stability (30% of score)
        current_ratio = metrics.get("currentRatioAnnual")
        if current_ratio is not None:
            if current_ratio > 2.0:  # Very liquid
                score += 15
            elif current_ratio > 1.5:  # Good liquidity
                score += 12
            elif current_ratio > 1.0:  # Adequate liquidity
                score += 8
            factors_evaluated += 1
        
        debt_equity = metrics.get("totalDebt/totalEquityAnnual")
        if debt_equity is not None:
            if debt_equity < 0.3:  # Low debt
                score += 15
            elif debt_equity < 0.6:  # Moderate debt
                score += 12
            elif debt_equity < 1.0:  # Higher debt but manageable
                score += 8
            factors_evaluated += 1
        
        # Normalize score based on factors evaluated
        if factors_evaluated > 0:
            final_score = (score / factors_evaluated) * (100 / 16.67)  # Normalize to 100
            final_score = min(100, max(0, final_score))  # Clamp between 0-100
        else:
            final_score = 0
        
        # Determine health category
        if final_score >= 80:
            health_category = "Excellent"
        elif final_score >= 65:
            health_category = "Good"
        elif final_score >= 50:
            health_category = "Fair"
        elif final_score >= 30:
            health_category = "Poor"
        else:
            health_category = "Very Poor"
        
        return round(final_score, 1), health_category
        
    except Exception as e:
        print(f"Error calculating financial health score: {e}")
        return 0, "Error"