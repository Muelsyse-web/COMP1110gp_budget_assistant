class LimitManager:
    def __init__(self):
        # 1. Strictly follow the document, initial limits must be 0.0 (Not Set)
        self.time_limits = {"d": 0.0, "w": 0.0, "m": 0.0, "y": 0.0} 
        self.category_limits = {} 
        self.proportion_limits = {} 

    def set_limit(self, l_type, key, value):
        if l_type == "time": 
            self.time_limits[key] = float(value)
        elif l_type == "cat": 
            self.category_limits[key] = float(value)
        elif l_type == "prop": 
            self.proportion_limits[key] = float(value)

    def check_limit(self, expenses, current_scale="All", current_cat="All"):
        """Returns (is_exceeded, usage_ratio, remaining, limit_name, limit_amount)"""
        total_exp = sum(r.get("money", 0) for r in expenses)
        
        limit_val = 0.0
        limit_name = ""
        
        # If filtering by a specific category, prioritize the category limit
        if current_cat != "All":
            limit_val = self.category_limits.get(current_cat, 0.0)
            limit_name = f"Cat: {current_cat}"
        else:
            # Otherwise, display the limit corresponding to the time scale
            scale_map = {"Day": "d", "Week": "w", "Month": "m", "Year": "y", "All": "m"}
            time_key = scale_map.get(current_scale, "m")
            limit_val = self.time_limits.get(time_key, 0.0)
            limit_name = current_scale

        # If the limit is 0 (not set), return the indicator
        if limit_val <= 1e-9: 
            return False, 0.0, 0.0, limit_name, 0.0

        ratio = total_exp / limit_val
        return ratio >= 1.0, ratio, max(0.0, limit_val - total_exp), limit_name, limit_val
