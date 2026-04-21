class LimitManager:
    def __init__(self):
        self.combined_limits = {} 

    def set_limit(self, scale, category, value):
        key = f"{scale}_{category}"
        self.combined_limits[key] = float(value)

    def check_limit(self, expenses, current_scale="All", current_cat="All"):
        """Returns (is_exceeded, usage_ratio, remaining, limit_name, limit_amount)"""
        scale_map = {"Day": "d", "Week": "w", "Month": "m", "Year": "y", "All": "all"}
        time_key = scale_map.get(current_scale, "all")
        
        key = f"{time_key}_{current_cat}"
        limit_val = self.combined_limits.get(key, 0.0)
        limit_name = f"{current_scale} limit for {current_cat}"
        
        # If the limit is 0 (not set), return the indicator
        if limit_val <= 1e-9: 
            return False, 0.0, 0.0, limit_name, 0.0

        total_exp = sum(r.get("money", 0) for r in expenses)
        ratio = total_exp / limit_val
        return ratio >= 1.0, ratio, max(0.0, limit_val - total_exp), limit_name, limit_val
