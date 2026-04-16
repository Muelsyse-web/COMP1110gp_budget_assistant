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

def determine_scale(records, pred_scale_setting="Auto"):
    """Intelligently guesses the best prediction scale based on data span."""
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
    
    if pred_scale_setting == "Auto":
        if days_span > 300:
            return "YEARLY", 365
        elif days_span < 7:
            return "WEEKLY", 7
        else:
            return "MONTHLY", 30
    elif pred_scale_setting == "Yearly": return "YEARLY", 365
    elif pred_scale_setting == "Weekly": return "WEEKLY", 7
    else: return "MONTHLY", 30

def predict_budget(records, target_days=30, limit_prior=0.0):
    """Bayesian Prediction scaled to specific target days."""
    if not records:
        return 0.0

    expenses = [r for r in records if not r.get("is_income", False)]
    if not expenses:
        return 0.0

    money_list = [r["money"] for r in expenses if r["money"] > 0]
    log_money = [math.log(m) for m in money_list]
    
    if len(log_money) < 2:
        log_mean = math.log(money_list[0]) if money_list else 0.0
        log_std = 0.0
    else:
        log_mean = statistics.mean(log_money)
        log_std = statistics.stdev(log_money)

    fixed_costs = 0.0
    variable_records = []

    for r in expenses:
        if r.get("ignore_anomaly", False):
            fixed_costs += r["money"]
        else:
            if not is_anomaly(r["money"], log_mean, log_std):
                variable_records.append(r)

    try:
        sorted_var = sorted(variable_records, key=lambda x: (x["year"], x["month"], x["day"]))
        start = datetime(sorted_var[0]["year"], sorted_var[0]["month"], sorted_var[0]["day"])
        end = datetime(sorted_var[-1]["year"], sorted_var[-1]["month"], sorted_var[-1]["day"])
        days_span = (end - start).days + 1
    except (ValueError, IndexError):
        days_span = 30 
    
    days_span = max(1, days_span)

    daily_burn = sum(r["money"] for r in variable_records) / days_span if variable_records else 0.0
    
    # Normalize fixed costs to a daily rate to safely scale up to Yearly or down to Weekly
    daily_fixed = fixed_costs / days_span 
    
    evidence_prediction = (daily_burn + daily_fixed) * target_days

    if limit_prior > 1e-9:
        evidence_weight = min(0.90, len(variable_records) / float(target_days)) 
        prior_weight = 1.0 - evidence_weight
        posterior_prediction = (limit_prior * prior_weight) + (evidence_prediction * evidence_weight)
        return posterior_prediction
    else:
        return evidence_prediction
