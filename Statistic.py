import math
import statistics
from datetime import datetime

EPSILON = 1e-9 # Prevent division by zero 
MAX_WIDTH = 40 # Standard width for bars
BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"] # 1/8 resolution

def calculate_log_zscore(log_value, log_mean, log_std_dev):
    """Calculate Z-score safely on log-transformed data"""
    if log_std_dev < EPSILON:
        return 0.0
    return (log_value - log_mean) / log_std_dev

def is_anomaly(value, log_mean, log_std_dev, ignore_flag=False):
    """Detect outliers based on Log-Normal Z-score threshold of > 1.96 (95% CI)."""
    if ignore_flag or value <= 0:
        return False
    log_val = math.log(value)
    z = calculate_log_zscore(log_val, log_mean, log_std_dev)
    return abs(z) > 1.96

def get_both_stats(records):
    """Extracts both log-normal and raw normal distribution parameters"""
    expenses = [r["money"] for r in records if r["money"] > 0 and not r.get("ignore_anomaly", False) and not r.get("is_income", False)]
    if not expenses:
        return (0.0, 0.0), (0.0, 0.0)
    
    log_money = [math.log(m) for m in expenses]
    log_mean = statistics.mean(log_money) if log_money else 0.0
    log_std = statistics.stdev(log_money) if len(log_money) > 1 else 0.0
    
    raw_mean = statistics.mean(expenses) if expenses else 0.0
    raw_std = statistics.stdev(expenses) if len(expenses) > 1 else 0.0
    
    return (log_mean, log_std), (raw_mean, raw_std)

def is_hybrid_anomaly(value, log_stats, raw_stats, pivot=1000.0, ignore_flag=False):
    """Uses Log-Normal for small values and standard Normal for huge values"""
    if ignore_flag or value <= 0:
        return False
    log_mean, log_std = log_stats
    raw_mean, raw_std = raw_stats
    
    if value < pivot:
        if log_std < EPSILON: return False
        z = calculate_log_zscore(math.log(value), log_mean, log_std)
    else:
        if raw_std < EPSILON: return False
        z = (value - raw_mean) / raw_std
        
    return abs(z) > 1.96

def generate_barchart(money, max_money):
    """Logarithmic Scaling for UI Visuals using Block characters"""
    if max_money < EPSILON or money < EPSILON:
        return ""
    
    exact_length = (math.log(money + 1) / math.log(max_money + 1)) * MAX_WIDTH
    full_blocks = int(exact_length)
    remainder = exact_length - full_blocks
    fractional_index = int(remainder * 8)
    
    bar = BLOCKS[8] * full_blocks
    if fractional_index > 0 and fractional_index < len(BLOCKS):
        bar += BLOCKS[fractional_index]
        
    return bar

def determine_scale(records, time_scale="All"):
    """Dynamically syncs the prediction scale with the active UI Time filter."""
    if time_scale == "Year": return "YEARLY", 365
    elif time_scale == "Month": return "MONTHLY", 30
    elif time_scale == "Day": return "DAILY", 1
    
    if not records:
        return "MONTHLY", 30
    
    try:
        sorted_recs = sorted(records, key=lambda x: (x["year"], x["month"], x["day"]))
        start = datetime(sorted_recs[0]["year"], sorted_recs[0]["month"], sorted_recs[0]["day"])
        end = datetime(sorted_recs[-1]["year"], sorted_recs[-1]["month"], sorted_recs[-1]["day"])
        days_span = (end - start).days + 1
    except ValueError:
        days_span = 30
        
    days_span = max(1, days_span)
    
    if days_span > 300: return "YEARLY", 365
    elif days_span < 7: return "WEEKLY", 7
    else: return "MONTHLY", 30

def predict_budget(records, target_days=30):
    """Clean data Trend Forecasting integrating a Bounded Momentum Factor."""
    if not records:
        return 0.0

    expenses = [r for r in records if not r.get("is_income", False)]
    if not expenses:
        return 0.0

    money_list = [r["money"] for r in expenses if r["money"] > 0]
    if not money_list:
        return 0.0
        
    log_money = [math.log(m) for m in money_list]
    log_mean = statistics.mean(log_money) if len(log_money) >= 1 else 0.0
    log_std = statistics.stdev(log_money) if len(log_money) > 1 else 0.0

    fixed_costs = 0.0
    variable_records = []

    # Clean data: Separate anomalies/ignored into Fixed Costs
    for r in expenses:
        if r.get("ignore_anomaly", False):
            fixed_costs += r["money"]
        else:
            if not is_anomaly(r["money"], log_mean, log_std):
                variable_records.append(r)

    if not variable_records:
        return fixed_costs

    try:
        sorted_var = sorted(variable_records, key=lambda x: (x["year"], x["month"], x["day"]))
        start = datetime(sorted_var[0]["year"], sorted_var[0]["month"], sorted_var[0]["day"])
        end = datetime(sorted_var[-1]["year"], sorted_var[-1]["month"], sorted_var[-1]["day"])
        days_span = (end - start).days + 1
    except (ValueError, IndexError):
        days_span = target_days 
    
    days_span = max(1, days_span)

    # Momentum Factor Calculation
    momentum = 1.0
    if len(sorted_var) >= 2 and days_span > 1:
        mid_point = days_span // 2
        first_half_sum = 0.0
        second_half_sum = 0.0
        
        for r in sorted_var:
            r_date = datetime(r["year"], r["month"], r["day"])
            if (r_date - start).days <= mid_point:
                first_half_sum += r["money"]
            else:
                second_half_sum += r["money"]
                
        first_half_avg = first_half_sum / max(1, mid_point)
        second_half_avg = second_half_sum / max(1, days_span - mid_point)
        
        if first_half_avg > EPSILON:
            raw_momentum = second_half_avg / first_half_avg
            momentum = max(0.5, min(2.0, raw_momentum))
        elif second_half_avg > EPSILON:
            momentum = 2.0

    daily_burn = sum(r["money"] for r in variable_records) / days_span
    daily_fixed = fixed_costs / days_span 
    
    variable_forecast = daily_burn * target_days * momentum
    fixed_forecast = daily_fixed * target_days
    
    forecast = variable_forecast + fixed_forecast

    if momentum > 1.1:
        forecast *= 1.10 
        
    return forecast
