import math
import statistics
from datetime import datetime

EPSILON = 1e-9 # Prevent division by zero 
MAX_WIDTH = 40 # Standard width for bars
BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"] # 1/8 resolution [cite: 168-174]

def calculate_zscore(value, mean, std_dev):
    """Calculate Z-score: Z=(x-μ)/σ [cite: 321]"""
    if std_dev < EPSILON:
        return 0.0
    return (value - mean) / std_dev

def is_anomaly(value, mean, std_dev):
    """Detect outliers based on Z-score threshold of 2.0 [cite: 189, 322]"""
    z = calculate_zscore(value, mean, std_dev)
    return abs(z) >= 2.0

def generate_barchart(money, max_money):
    """Logarithmic Scaling to handle extreme value differences [cite: 183]"""
    if max_money < EPSILON:
        return ""
    
    # Formula: ExactLength = (log(val+1)/log(max+1)) * MAX_WIDTH
    exact_length = (math.log(money + 1) / math.log(max_money + 1)) * MAX_WIDTH
    
    full_blocks = int(exact_length)
    remainder = exact_length - full_blocks
    fractional_index = int(remainder * 8)
    
    bar = BLOCKS[8] * full_blocks
    if fractional_index > 0:
        bar += BLOCKS[fractional_index]
        
    return bar

def predict_budget(records):
    """Predictive Budget using Linear Regression & Split-Half Momentum [cite: 192, 324, 337]"""
    if not records:
        return 0.0

    # Extract non-income money values
    money_list = [r["money"] for r in records if not r["is_income"]]
    if len(money_list) < 2:
        return sum(money_list)

    mean_val = statistics.mean(money_list)
    std_dev = statistics.stdev(money_list)

    # Step 1: Data Cleaning (Exclude Anomalies) [cite: 332]
    normal_records = [r for r in records if not r["is_income"] and not is_anomaly(r["money"], mean_val, std_dev)]
    if not normal_records:
        return 0.0

    # Step 2: Split-half Momentum Analysis [cite: 337-341]
    normal_records.sort(key=lambda x: (x["year"], x["month"], x["day"]))
    mid = len(normal_records) // 2
    first_half = normal_records[:mid]
    second_half = normal_records[mid:]

    first_avg = sum(r["money"] for r in first_half) / len(first_half) if first_half else 0.0
    second_avg = sum(r["money"] for r in second_half) / len(second_half) if second_half else 0.0

    momentum = (second_avg / first_avg) if first_avg > EPSILON else 1.0

    # Step 3: Forecast based on actual daily burn rate [cite: 334]
    start = datetime(normal_records[0]["year"], normal_records[0]["month"], normal_records[0]["day"])
    end = datetime(normal_records[-1]["year"], normal_records[-1]["month"], normal_records[-1]["day"])
    days = (end - start).days + 1

    daily_burn = sum(r["money"] for r in normal_records) / days if days > 0 else 0.0
    predicted = (daily_burn * 30) * momentum

    # Step 4: Safety Adjustment for upward trends [cite: 355]
    if momentum > 1.1:
        predicted *= 1.10

    return predicted
