import streamlit as st
import requests
import json
from datetime import datetime
import os

def get_api_base():
    """Get API base URL from environment or use default"""
    return os.getenv("EYESENSE_API_BASE", "http://localhost:8000")

def validate_image_file(file):
    """Validate uploaded image file"""
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
    max_size = 10 * 1024 * 1024  # 10MB
    
    if file.type not in allowed_types:
        return False, "Invalid file type. Please upload JPG, JPEG, or PNG images."
    
    if file.size > max_size:
        return False, "File too large. Maximum size is 10MB."
    
    return True, "File validated successfully"

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def get_risk_color(risk_level):
    """Get color for risk level"""
    colors = {
        'Normal': '#2ecc71',
        'Slightly High': '#f39c12', 
        'High': '#e74c3c',
        'Unknown': '#95a5a6'
    }
    return colors.get(risk_level, '#95a5a6')

def get_risk_emoji(risk_level):
    """Get emoji for risk level"""
    emojis = {
        'Normal': '✅',
        'Slightly High': '⚠️',
        'High': '🚨',
        'Unknown': '❓'
    }
    return emojis.get(risk_level, '❓')

def calculate_risk_trend(history_data):
    """Calculate risk trend from historical data"""
    if not history_data or len(history_data) < 2:
        return "stable"
    
    recent_scores = [h['analysis_result']['risk_level'] for h in history_data[-3:]]
    score_values = []
    
    for risk in recent_scores:
        if risk == 'Normal':
            score_values.append(0)
        elif risk == 'Slightly High':
            score_values.append(1)
        else:
            score_values.append(2)
    
    if len(score_values) < 2:
        return "stable"
    
    # Simple trend calculation
    if score_values[-1] > score_values[0]:
        return "increasing"
    elif score_values[-1] < score_values[0]:
        return "decreasing"
    else:
        return "stable"

def get_trend_emoji(trend):
    """Get emoji for trend"""
    emojis = {
        'increasing': '📈',
        'decreasing': '📉',
        'stable': '➡️'
    }
    return emojis.get(trend, '➡️')