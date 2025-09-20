import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import streamlit as st
from .utils import format_currency

# ------------------------------
# Price Charts with Volume
# ------------------------------
def create_price_chart(price_data, company_name, ticker):
    """
    Create an interactive stock price chart with volume
    UPGRADES: Volume subplot, better styling, candlestick option
    """
    if not price_data or len(price_data.get('dates', [])) == 0:
        return None
    
    # Create subplot with secondary y-axis for volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Stock Price', 'Volume'),
        row_heights=[0.7, 0.3]
    )
    
    # Price line chart
    fig.add_trace(
        go.Scatter(
            x=price_data['dates'],
            y=price_data['prices'],
            mode='lines',
            name=f'{ticker} Price',
            line=dict(color='#667eea', width=3),
            hovertemplate='<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Volume bar chart (if available)
    if price_data.get('volumes') and len(price_data['volumes']) > 0:
        fig.add_trace(
            go.Bar(
                x=price_data['dates'],
                y=price_data['volumes'],
                name='Volume',
                marker_color='rgba(102, 126, 234, 0.6)',
                hovertemplate='<b>%{x}</b><br>Volume: %{y:,.0f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'{company_name} ({ticker}) - Stock Price & Volume',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2d3748'}
        },
        template='plotly_white',
        hovermode='x unified',
        height=500,
        margin=dict(l=0, r=0, t=60, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True
    )
    
    # Update axes
    fig.update_xaxes(gridcolor='#e2e8f0', linecolor='#cbd5e0')
    fig.update_yaxes(gridcolor='#e2e8f0', linecolor='#cbd5e0', tickformat='$,.2f', row=1, col=1)
    fig.update_yaxes(gridcolor='#e2e8f0', linecolor='#cbd5e0', tickformat=',.0f', row=2, col=1)
    
    return fig

# ------------------------------
# Candlestick Chart
# ------------------------------
def create_candlestick_chart(price_data, company_name, ticker):
    """
    Create candlestick chart for detailed price analysis
    """
    if not price_data or not price_data.get('highs') or len(price_data['dates']) == 0:
        return None
    
    fig = go.Figure(data=go.Candlestick(
        x=price_data['dates'],
        open=price_data.get('opens', price_data['prices']),  # Fallback to close if no open
        high=price_data['highs'],
        low=price_data['lows'],
        close=price_data['prices'],
        name=f'{ticker}',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    fig.update_layout(
        title={
            'text': f'{company_name} ({ticker}) - Candlestick Chart',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2d3748'}
        },
        template='plotly_white',
        height=400,
        xaxis_title='Date',
        yaxis_title='Price ($)',
        margin=dict(l=0, r=0, t=60, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(gridcolor='#e2e8f0', linecolor='#cbd5e0')
    fig.update_yaxes(gridcolor='#e2e8f0', linecolor='#cbd5e0', tickformat='$,.2f')
    
    return fig

# ------------------------------
# Multi-Year Financial Trends
# ------------------------------
def create_financial_trends_chart(multi_year_data):
    """
    Create multi-year financial trends visualization
    NEW FEATURE: Revenue, profit, growth trends over years
    """
    if not multi_year_data or not multi_year_data.get('financial_data'):
        return None
    
    financial_data = multi_year_data['financial_data']
    
    # Create subplot for multiple metrics
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Revenue Trend', 'Net Income Trend', 'Revenue Growth %', 'Profit Margin %'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Revenue trend
    if 'revenue' in financial_data:
        revenue = financial_data['revenue']
        # Sort by date to ensure proper ordering
        sorted_data = sorted(zip(revenue['dates'], revenue['values']))
        dates, values = zip(*sorted_data)
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=[v/1e9 for v in values],  # Convert to billions
                mode='lines+markers',
                name='Revenue ($B)',
                line=dict(color='#4299e1', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
    
    # Net Income trend
    if 'net_income' in financial_data:
        income = financial_data['net_income']
        # Sort by date to ensure chronological order (left to right)
        sorted_data = sorted(zip(income['dates'], income['values']))
        dates, values = zip(*sorted_data)
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=[v/1e9 for v in values],  # Convert to billions
                mode='lines+markers',
                name='Net Income ($B)',
                line=dict(color='#48bb78', width=3),
                marker=dict(size=8)
            ),
            row=1, col=2
        )

    # Revenue Growth
    ratios = multi_year_data.get('ratios_timeline', {})
    if 'revenue_growth' in ratios:
        growth = ratios['revenue_growth']
        # Sort by date to ensure chronological order
        sorted_data = sorted(zip(growth['dates'], growth['values']))
        dates, values = zip(*sorted_data)
        colors = ['#48bb78' if x >= 0 else '#f56565' for x in values]
        fig.add_trace(
            go.Bar(
                x=dates,
                y=values,
                name='Revenue Growth %',
                marker_color=colors
            ),
            row=2, col=1
        )

    # Profit Margin
    if 'profit_margin' in ratios:
        margin = ratios['profit_margin']
        # Sort by date to ensure chronological order
        sorted_data = sorted(zip(margin['dates'], margin['values']))
        dates, values = zip(*sorted_data)
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name='Profit Margin %',
                line=dict(color='#9f7aea', width=3),
                marker=dict(size=8)
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        title={
            'text': 'Multi-Year Financial Performance',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2d3748'}
        },
        template='plotly_white',
        height=600,
        showlegend=False,
        margin=dict(l=0, r=0, t=80, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    # Update all axes
    for i in range(1, 3):
        for j in range(1, 3):
            fig.update_xaxes(gridcolor='#e2e8f0', linecolor='#cbd5e0', row=i, col=j)
            fig.update_yaxes(gridcolor='#e2e8f0', linecolor='#cbd5e0', row=i, col=j)
    
    return fig

# ------------------------------
# Ratios Chart
# ------------------------------
def create_ratios_chart(ratios_data):
    """
    Create enhanced horizontal bar chart for financial ratios
    UPGRADES: Better color coding, benchmarks, improved styling
    """
    if not ratios_data:
        return None
    
    # Filter and prepare data
    clean_ratios = {}
    benchmark_ranges = {
        'P/E Ratio': {'good': (10, 25), 'color': '#4299e1'},
        'Debt/Equity': {'good': (0, 0.6), 'color': '#f56565'},
        'ROE': {'good': (15, 30), 'color': '#48bb78'},
        'Current Ratio': {'good': (1.2, 2.0), 'color': '#9f7aea'},
        'Gross Margin': {'good': (20, 50), 'color': '#ed8936'},
        'EBITDA Margin': {'good': (10, 30), 'color': '#38b2ac'}
    }
    
    for key, value in ratios_data.items():
        if value != "N/A" and isinstance(value, str):
            try:
                clean_value = float(value.replace('%', ''))
                clean_ratios[key] = clean_value
            except (ValueError, AttributeError):
                continue
        elif isinstance(value, (int, float)):
            clean_ratios[key] = float(value)
    
    if not clean_ratios:
        return None
    
    # Create chart with color coding
    ratios = list(clean_ratios.keys())
    values = list(clean_ratios.values())
    colors = []
    
    for ratio in ratios:
        if ratio in benchmark_ranges:
            good_range = benchmark_ranges[ratio]['good']
            value = clean_ratios[ratio]
            if good_range[0] <= value <= good_range[1]:
                colors.append('#48bb78')  # Green for good
            else:
                colors.append('#f56565')  # Red for concerning
        else:
            colors.append('#4299e1')  # Default blue
    
    fig = go.Figure(data=[
        go.Bar(
            x=values,
            y=ratios,
            orientation='h',
            marker_color=colors,
            text=[f'{v:.1f}%' if 'Margin' in r or 'ROE' in r else f'{v:.2f}' 
                  for r, v in zip(ratios, values)],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Value: %{text}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Financial Ratios Analysis',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2d3748'}
        },
        template='plotly_white',
        height=400,
        showlegend=False,
        margin=dict(l=120, r=0, t=60, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#e2e8f0', linecolor='#cbd5e0'),
        yaxis=dict(gridcolor='#e2e8f0', linecolor='#cbd5e0')
    )
    
    return fig

# ------------------------------
# Performance Comparison Chart
# ------------------------------
def create_performance_comparison(current_data, historical_data):
    """
    Compare current performance vs historical averages
    NEW FEATURE: Performance benchmarking visualization
    """
    if not current_data or not historical_data:
        return None
    
    # Calculate historical averages for comparison
    metrics = ['Revenue Growth', 'Profit Margin', 'ROE']
    current_values = []
    historical_averages = []
    
    for metric in metrics:
        if metric == 'Revenue Growth':
            current = current_data.get('revenueGrowthTTMYoy', 0) * 100
            hist_data = historical_data.get('ratios_timeline', {}).get('revenue_growth', {})
            if hist_data.get('values'):
                hist_avg = np.mean(hist_data['values'])
            else:
                hist_avg = 0
        elif metric == 'Profit Margin':
            current = current_data.get('netProfitMarginAnnual', 0)
            hist_data = historical_data.get('ratios_timeline', {}).get('profit_margin', {})
            if hist_data.get('values'):
                hist_avg = np.mean(hist_data['values'])
            else:
                hist_avg = 0
        elif metric == 'ROE':
            current = current_data.get('roeAnnual', 0) * 100
            hist_avg = current  # Fallback if no historical ROE
        
        current_values.append(current)
        historical_averages.append(hist_avg)
    
    # Create grouped bar chart
    fig = go.Figure(data=[
        go.Bar(name='Current', x=metrics, y=current_values, marker_color='#4299e1'),
        go.Bar(name='Historical Avg', x=metrics, y=historical_averages, marker_color='#a0aec0')
    ])
    
    fig.update_layout(
        title={
            'text': 'Current vs Historical Performance',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2d3748'}
        },
        barmode='group',
        template='plotly_white',
        height=350,
        margin=dict(l=0, r=0, t=60, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='#e2e8f0', linecolor='#cbd5e0'),
        yaxis=dict(gridcolor='#e2e8f0', linecolor='#cbd5e0', title='Percentage (%)')
    )
    
    return fig

# ------------------------------
# E-FUNCTIONS
# ------------------------------
def create_metrics_gauge_chart(current_price, week_52_high, week_52_low, ticker):
    """Enhanced gauge chart with better styling"""
    try:
        current = float(current_price) if current_price != "N/A" else 0
        high = float(week_52_high) if week_52_high != "N/A" else current * 1.2
        low = float(week_52_low) if week_52_low != "N/A" else current * 0.8
        
        if current == 0 or high == low:
            return None
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{ticker} Price Position", 'font': {'size': 16, 'color': '#2d3748'}},
            delta = {'reference': (high + low) / 2, 'valueformat': '.2f'},
            gauge = {
                'axis': {'range': [low * 0.9, high * 1.1], 'tickformat': '$,.0f'},
                'bar': {'color': "#667eea", 'thickness': 0.8},
                'steps': [
                    {'range': [low * 0.9, low], 'color': "#fed7d7"},
                    {'range': [low, high * 0.8], 'color': "#c6f6d5"},
                    {'range': [high * 0.8, high], 'color': "#fbb6ce"},
                    {'range': [high, high * 1.1], 'color': "#fed7d7"}
                ],
                'threshold': {
                    'line': {'color': "#e53e3e", 'width': 4},
                    'thickness': 0.75,
                    'value': high * 0.9
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#2d3748'}
        )
        
        return fig
        
    except (ValueError, TypeError):
        return None

def create_trend_chart(trend_data):
    """Enhanced trend visualization with better styling"""
    if not trend_data:
        return None
    
    metrics = []
    values = []
    colors = []
    
    for key, value in trend_data.items():
        if value != "N/A" and isinstance(value, str):
            try:
                numeric_value = float(value.replace('%', ''))
                metrics.append(key.replace('Growth (YoY)', 'Growth').replace('Margin', 'Margin %'))
                values.append(numeric_value)
                colors.append('#48bb78' if numeric_value >= 0 else '#f56565')
            except (ValueError, AttributeError):
                continue
    
    if not metrics:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            marker_color=colors,
            text=[f'{v:+.1f}%' for v in values],
            textposition='outside',
            textfont={'color': '#2d3748', 'size': 12},
            hovertemplate='<b>%{x}</b><br>Value: %{text}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Performance Trends',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2d3748'}
        },
        template='plotly_white',
        height=350,
        showlegend=False,
        margin=dict(l=0, r=0, t=60, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            gridcolor='#e2e8f0',
            title='Percentage (%)',
            tickformat='.1f',
            linecolor='#cbd5e0'
        ),
        xaxis=dict(
            gridcolor='#e2e8f0',
            linecolor='#cbd5e0',
            tickangle=0
        )
    )
    
    # Add horizontal line at 0
    fig.add_hline(y=0, line_dash="dash", line_color="#a0aec0", opacity=0.7)
    
    return fig

# ------------------------------
# Portfolio-Style Summary Chart
# ------------------------------
def create_portfolio_summary(company_data):
    """
    Create a comprehensive portfolio-style summary visualization
    NEW FEATURE: Executive dashboard style chart
    """
    if not company_data:
        return None
    
    # Create 2x2 subplot grid
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Market Position', 'Financial Health', 'Growth Metrics', 'Risk Indicators'),
        specs=[[{"type": "indicator"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Market Position (Gauge)
    current_price = company_data.get('currentPrice', 0)
    week_high = company_data.get('52WeekHigh', 0)
    week_low = company_data.get('52WeekLow', 0)
    
    if all(x != "N/A" and x != 0 for x in [current_price, week_high, week_low]):
        try:
            current = float(current_price)
            high = float(week_high)
            low = float(week_low)
            position = ((current - low) / (high - low)) * 100
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=position,
                    title={'text': "52-Week Position %"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 33], 'color': "#fed7d7"},
                            {'range': [33, 66], 'color': "#ffeaa7"},
                            {'range': [66, 100], 'color': "#c6f6d5"}
                        ]
                    }
                ),
                row=1, col=1
            )
        except (ValueError, TypeError):
            pass
    
    # Financial Health Scores
    metrics = company_data.get('metric', {})
    health_scores = []
    health_labels = []

    # ROE Score
    roe = metrics.get('roeAnnual', 0)
    if roe and roe != "N/A" and roe != 0:
        try:
            roe_val = float(roe) * 100  # Convert decimal to percentage
            roe_score = min(100, max(0, (roe_val / 20) * 100))  # 20% ROE = 100 score
            health_scores.append(roe_score)
            health_labels.append('ROE')
        except (ValueError, TypeError):
            pass

    # Debt Score (inverse - lower debt = higher score)
    debt_equity = metrics.get('totalDebt/totalEquityAnnual', 0)
    if debt_equity and debt_equity != "N/A" and debt_equity != 0:
        try:
            debt_val = float(debt_equity)
            debt_score = max(0, 100 - (debt_val * 100))  # Lower debt = higher score
            health_scores.append(debt_score)
            health_labels.append('Debt Mgmt')
        except (ValueError, TypeError):
            pass

    # Add Current Ratio Score
    current_ratio = metrics.get('currentRatioAnnual', 0)
    if current_ratio and current_ratio != "N/A" and current_ratio != 0:
        try:
            ratio_val = float(current_ratio)
            ratio_score = min(100, max(0, (ratio_val / 2.0) * 100))  # 2.0 ratio = 100 score
            health_scores.append(ratio_score)
            health_labels.append('Liquidity')
        except (ValueError, TypeError):
            pass

    if health_scores:
        colors = ['#48bb78' if score >= 70 else '#ed8936' if score >= 40 else '#f56565' 
                for score in health_scores]
        
        fig.add_trace(
            go.Bar(
                x=health_labels,
                y=health_scores,
                marker_color=colors,
                name="Health Scores",
                text=[f'{score:.0f}' for score in health_scores],
                textposition='outside'
            ),
            row=1, col=2
        )
    else:
        # Show message when no health data available
        fig.add_annotation(
            text="Health metrics not available",
            xref="paper", yref="paper",
            x=0.75, y=0.75,
            showarrow=False,
            font=dict(size=14, color="#718096")
        )
    
    fig.update_layout(
        title={
            'text': 'Executive Dashboard Summary',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2d3748'}
        },
        template='plotly_white',
        height=500,
        showlegend=False,
        margin=dict(l=0, r=0, t=80, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig