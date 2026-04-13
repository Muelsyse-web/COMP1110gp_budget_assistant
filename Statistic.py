import math
import statistics
from datetime import datetime

EPSILON = 1e-9 # Prevent division by zero 
MAX_WIDTH = 40 # Standard width for bars
BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"] # 1/8 resolution

def calculate_zscore(value, mean, std_dev):
    """Calculate Z-score safely"""
    if std_dev < EPSILON:
        return 0.0
    return (value - mean) / std_dev

def is_anomaly(value, mean, std_dev):
    """Detect outliers based on Z-score threshold of 2.0"""
    z = calculate_zscore(value, mean, std_dev)
    return abs(z) >= 2.0

def generate_barchart(money, max_money):
    """Logarithmic Scaling to handle extreme value differences"""
    if max_money < EPSILON or money < EPSILON:
        return ""
    
    # Formula: ExactLength = (log(val+1)/log(max+1)) * MAX_WIDTH
    exact_length = (math.log(money + 1) / math.log(max_money + 1)) * MAX_WIDTH
    
    full_blocks = int(exact_length)
    remainder = exact_length - full_blocks
    fractional_index = int(remainder * 8)
    
    bar = BLOCKS[8] * full_blocks
    if fractional_index > 0 and fractional_index < len(BLOCKS):
        bar += BLOCKS[fractional_index]
        
    return bar

def predict_budget(records):
    """Predictive Budget using Linear Regression & Split-Half Momentum"""
    if not records:
        return 0.0

    money_list = [r["money"] for r in records if not r.get("is_income", False)]
    if len(money_list) < 2:
        return sum(money_list)

    mean_val = statistics.mean(money_list)
    std_dev = statistics.stdev(money_list)

    normal_records = [r for r in records if not r.get("is_income", False) and not is_anomaly(r["money"], mean_val, std_dev)]
    if not normal_records:
        return 0.0

    normal_records.sort(key=lambda x: (x["year"], x["month"], x["day"]))
    mid = len(normal_records) // 2
    first_half = normal_records[:mid]
    second_half = normal_records[mid:]

    first_avg = sum(r["money"] for r in first_half) / len(first_half) if first_half else 0.0
    second_avg = sum(r["money"] for r in second_half) / len(second_half) if second_half else 0.0

    momentum = (second_avg / first_avg) if first_avg > EPSILON else 1.0

    start = datetime(normal_records[0]["year"], normal_records[0]["month"], normal_records[0]["day"])
    end = datetime(normal_records[-1]["year"], normal_records[-1]["month"], normal_records[-1]["day"])
    days = (end - start).days + 1

    daily_burn = sum(r["money"] for r in normal_records) / days if days > 0 else 0.0
    predicted = (daily_burn * 30) * momentum

    if momentum > 1.1:
        predicted *= 1.10

    return predicted
