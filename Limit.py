class LimitManager:
    def __init__(self):
        self.time_limits = {"d": 0.0, "w": 0.0, "m": 1000.0, "y": 0.0} 
        self.category_limits = {} 
        self.proportion_limits = {} 

    def set_limit(self, l_type, key, value):
        if l_type == "time": self.time_limits[key] = float(value)
        elif l_type == "cat": self.category_limits[key] = float(value)
        elif l_type == "prop": self.proportion_limits[key] = float(value)

    def check_limit(self, expenses, income, limit_type="time"):
        total_exp = sum(r.get("money", 0) for r in expenses)
        total_inc = sum(r.get("money", 0) for r in income)
        
        limit_val = self.time_limits.get("m", 1000.0) 
        
        if limit_val <= 1e-9: 
            return False, 0.0, 0.0

        ratio = total_exp / limit_val
        return ratio >= 1.0, ratio, max(0.0, limit_val - total_exp)
