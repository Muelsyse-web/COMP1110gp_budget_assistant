class LimitManager:
    def __init__(self):
        # Default limits [cite: 27-29, 372-385]
        self.time_limits = {"d": 0.0, "w": 0.0, "m": 1000.0, "y": 0.0} 
        self.category_limits = {} 
        self.proportion_limits = {} # Percentage of total income [cite: 431]

    def set_limit(self, l_type, key, value):
        if l_type == "time": self.time_limits[key] = float(value)
        elif l_type == "cat": self.category_limits[key] = float(value)
        elif l_type == "prop": self.proportion_limits[key] = float(value)

    def check_limit(self, expenses, income, limit_type="time"):
        """Returns (is_exceeded, usage_ratio, remaining) [cite: 151-163]"""
        total_exp = sum(r["money"] for r in expenses)
        total_inc = sum(r["money"] for r in income)
        
        limit_val = self.time_limits.get("m", 0.0) # Default to monthly
        
        if total_inc > 0 and self.proportion_limits:
            # Example: check total proportions
            pass 

        if limit_val <= 0: return False, 0.0, 0.0

        ratio = total_exp / limit_val
        return ratio >= 1.0, ratio, max(0.0, limit_val - total_exp)
