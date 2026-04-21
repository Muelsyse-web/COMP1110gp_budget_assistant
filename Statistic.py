import math
import statistics
from datetime import datetime

EPSILON = 1e-9 # Prevent division by zero 
MAX_WIDTH = 40 # Standard width for bars
BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"] # 1/8 resolution

def get_both_stats(records):
    """
    Calculates both Arithmetic (Raw) and Geometric (Log) baselines simultaneously.
    Uses trimming to prevent the Masking Effect from massive outliers.
    """
    valid_money = [r["money"] for r in records if r["money"] > 0 and not r.get("ignore_anomaly", False)]
    if not valid_money:
        return (0.0, 0.0), (0.0, 0.0)

    # Trim top/bottom 10% to find the true behavioral core
    sorted_money = sorted(valid_money)
    if len(sorted_money) > 5:
        trim_idx = max(1, int(len(sorted_money) * 0.1))
        core_money = sorted_money[trim_idx:-trim_idx]
    else:
        core_money = sorted_money

    # 1. Raw Normal Baseline
    raw_mean = statistics.mean(core_money) if core_money else 0.0
    raw_std = statistics.stdev(core_money) if len(core_money) > 1 else 0.0

    # 2. Log-Normal Baseline
    core_logs = [math.log(m) for m in core_money]
    log_mean = statistics.mean(core_logs) if core_logs else 0.0
    log_std = statistics.stdev(core_logs) if len(core_logs) > 1 else 0.0

    return (log_mean, log_std), (raw_mean, raw_std)

def is_hybrid_anomaly(value, log_stats, raw_stats, pivot=1000.0, ignore_flag=False):
    """
    Multi-Model Switching Logic:
    - Values > Pivot: Log-Normal distribution (Forgives proportional changes on big bills).
    - Values <= Pivot: Normal distribution (Catches absolute dollar spikes on daily habits).
    """
    if ignore_flag or value <= 0:
        return False

    log_mean, log_std = log_stats
    raw_mean, raw_std = raw_stats

    # Tier 1: High-Value Logic (Log-Normal)
    if value > pivot:
        log_val = math.log(value)
        z_log = (log_val - log_mean) / (log_std + EPSILON)
        return abs(z_log) > 1.96

    # Tier 2: Lifestyle Logic (Raw Normal)
    else:
        z_raw = (value - raw_mean) / (raw_std + EPSILON)
        return abs(z_raw) >= 2.0

def generate_barchart(money, max_money):
    """Logarithmic Scaling for UI Visuals"""
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

    # Fetch both baselines for the hybrid cleaning phase
    log_stats, raw_stats = get_both_stats(expenses)

    fixed_costs = 0.0
    variable_records = []

    # Clean data: Separate hybrid anomalies/ignored into Fixed Costs
    for r in expenses:
        if r.get("ignore_anomaly", False):
            fixed_costs += r["money"]
        else:
            if not is_hybrid_anomaly(r["money"], log_stats, raw_stats):
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
