、import math
import statistics
from datetime import datetime

EPSILON = 1e-9 # Prevent division by zero 
MAX_WIDTH = 50 
BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"] # 1/8 resolution [cite: 100]

def calculate_zscore(value, mean, std_dev):
    """Formula: Z=(x-μ)/σ [cite: 39]"""
    if std_dev < EPSILON:
        return 0.0
    return (value - mean) / std_dev

def is_anomaly(value, mean, std_dev):
    """If |Z| >= 2.0, return True [cite: 40]"""
    z = calculate_zscore(value, mean, std_dev)
    return abs(z) >= 2.0

def generate_barchart(value, max_value):
    """Logarithmic Scaling: Length=(log(value+1)/log(max_value+1))*MAX_WIDTH [cite: 43]"""
    if max_value < EPSILON:
        max_value = EPSILON
    
    # Calculate exact length
    exact_length = (math.log(value + 1) / math.log(max_value + 1)) * MAX_WIDTH
    
    full_blocks = int(exact_length)
    remainder = exact_length - full_blocks
    fractional_index = int(remainder * 8)
    
    bar = BLOCKS[8] * full_blocks
    if fractional_index > 0:
        bar += BLOCKS[fractional_index]
        
    return bar

def predict_budget(records):
    """Predictive Budget (Linear Regression & Split-Half Momentum) [cite: 44, 46]"""
    if not records:
        return 0.0

    amounts = [r["amount"] for r in records if not r["is_income"]]
    if len(amounts) < 2:
        return sum(amounts)

    mean_val = statistics.mean(amounts)
    std_dev = statistics.stdev(amounts)

    # Step 1: Clean data [cite: 45]
    normal_records = [r for r in records if not r["is_income"] and not is_anomaly(r["amount"], mean_val, std_dev)]
    if not normal_records:
        return 0.0

    # Step 2: Momentum (Split-half) [cite: 46]
    normal_records.sort(key=lambda x: (x["year"], x["month"], x["day"]))
    mid_point = len(normal_records) // 2
    first_half = normal_records[:mid_point]
    second_half = normal_records[mid_point:]

    first_half_avg = sum(r["amount"] for r in first_half) / len(first_half) if first_half else 0.0
    second_half_avg = sum(r["amount"] for r in second_half) / len(second_half) if second_half else 0.0

    momentum = (second_half_avg / first_half_avg) if first_half_avg > EPSILON else 1.0 # [cite: 47]

    # Step 3: Forecast based on daily burn rate [cite: 48, 146]
    start_date = datetime(normal_records[0]["year"], normal_records[0]["month"], normal_records[0]["day"])
    end_date = datetime(normal_records[-1]["year"], normal_records[-1]["month"], normal_records[-1]["day"])
    total_days = (end_date - start_date).days + 1

    daily_burn_rate = sum(r["amount"] for r in normal_records) / total_days if total_days > 0 else 0.0
    predicted_total = (daily_burn_rate * 30) * momentum # [cite: 147]

    # Step 4: Adjustment [cite: 51]
    if momentum > 1.1:
        predicted_total *= 1.10

    return predicted_total
