import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from .utils import format_currency

def create_price_chart(price_data, company_name, ticker):
    """
    Create an interactive stock price chart
    Args:
        price_data: Dictionary with price history data
        company_name: Company name for title
        ticker: Stock ticker symbol
    """
    if not price_data or len(price_data.get('dates', [])) == 0:
        return None
    
    # Create the figure
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=price_data['dates'],
        y=price_data['prices'],
        mode='lines',
        name=f'{ticker} Price',
        line=dict(color='#667eea', width=3),
        hovertemplate='<b>%{x}</b><br>Price: $%{y:.2f}<extra></extra>'
    ))
    
    # Update layout for professional appearance
    fig.update_layout(
        title={
            'text': f'{company_name} ({ticker}) - Stock Price',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2d3748'}
        },
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_white',
        hovermode='x unified',
        showlegend=True,
        height=400,
        margin=dict(l=0, r=0, t=60, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='#e2e8f0',
            linecolor='#cbd5e0'
        ),
        yaxis=dict(
            gridcolor='#e2e8f0',
            linecolor='#cbd5e0',
            tickformat='$,.2f'
        )
    )
    
    return fig

def create_ratios_chart(ratios_data):
    """
    Create a horizontal bar chart for financial ratios
    Args:
        ratios_data: Dictionary of ratio names and values
    """
    if not ratios_data:
        return None
    
    # Filter out N/A values and prepare data
    clean_ratios = {}
    for key, value in ratios_data.items():
        if value != "N/A" and isinstance(value, str):
            try:
                # Remove % sign and convert to float
                clean_value = float(value.replace('%', ''))
                clean_ratios[key] = clean_value
            except (ValueError, AttributeError):
                continue
        elif isinstance(value, (int, float)):
            clean_ratios[key] = float(value)
    
    if not clean_ratios:
        return None
    
    # Create horizontal bar chart
    df = pd.DataFrame(list(clean_ratios.items()), columns=['Ratio', 'Value'])
    
    fig = px.bar(
        df, 
        x='Value', 
        y='Ratio',
        orientation='h',
        title='Financial Ratios Overview',
        color='Value',
        color_continuous_scale='Blues',
        text='Value'
    )
    
    # Update layout
    fig.update_layout(
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2d3748'}
        },
        template='plotly_white',
        height=400,
        showlegend=False,
        margin=dict(l=0, r=0, t=60, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False
    )
    
    # Update traces for better text display
    fig.update_traces(
        texttemplate='%{text:.1f}%' if any('Margin' in ratio for ratio in clean_ratios.keys()) else '%{text:.2f}',
        textposition='outside',
        textfont_color='#2d3748'
    )
    
    return fig

def create_metrics_gauge_chart(current_price, week_52_high, week_52_low, ticker):
    """
    Create a gauge chart showing current price vs 52-week range
    """
    try:
        current = float(current_price) if current_price != "N/A" else 0
        high = float(week_52_high) if week_52_high != "N/A" else current * 1.2
        low = float(week_52_low) if week_52_low != "N/A" else current * 0.8
        
        if current == 0 or high == low:
            return None
        
        # Calculate percentage within range
        range_position = ((current - low) / (high - low)) * 100
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{ticker} Price vs 52-Week Range", 'font': {'size': 16}},
            delta = {'reference': (high + low) / 2, 'valueformat': '.2f'},
            gauge = {
                'axis': {'range': [low * 0.9, high * 1.1], 'tickformat': '$,.0f'},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [low * 0.9, low], 'color': "#fed7d7"},
                    {'range': [low, high], 'color': "#c6f6d5"},
                    {'range': [high, high * 1.1], 'color': "#fed7d7"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': high
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        
        return fig
        
    except (ValueError, TypeError):
        return None

def create_trend_chart(trend_data):
    """
    Create a simple trend visualization
    Args:
        trend_data: Dictionary with trend metrics
    """
    if not trend_data:
        return None
    
    # Sample trend data structure
    metrics = []
    values = []
    colors = []
    
    for key, value in trend_data.items():
        if value != "N/A" and isinstance(value, str):
            try:
                # Extract numeric value from percentage
                numeric_value = float(value.replace('%', ''))
                metrics.append(key)
                values.append(numeric_value)
                # Color coding: green for positive, red for negative
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
            text=[f'{v:.1f}%' for v in values],
            textposition='outside',
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
        height=400,
        showlegend=False,
        margin=dict(l=0, r=0, t=60, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            gridcolor='#e2e8f0',
            title='Percentage (%)',
            tickformat='.1f'
        ),
        xaxis=dict(
            gridcolor='#e2e8f0',
            tickangle=45
        )
    )
    
    # Add a horizontal line at 0
    fig.add_hline(y=0, line_dash="dash", line_color="#a0aec0", opacity=0.7)
    
    return fig