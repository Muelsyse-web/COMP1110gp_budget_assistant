class LimitManager:
    def __init__(self):
        self.time_limits = {"d": 0.0, "w": 0.0, "m": 0.0, "y": 0.0} # [cite: 18]
        self.category_limits = {} # Format: {"CategoryName": {"d": 0.0, "m": 0.0}} [cite: 19]
        self.proportion_limits = {} # Format: {"CategoryName": float} [cite: 20]

    def set_time_limit(self, timeframe, amount):
        if timeframe in self.time_limits:
            self.time_limits[timeframe] = float(amount)

    def set_proportion_limit(self, category, percentage):
        self.proportion_limits[category] = float(percentage)

    def check_limit(self, current_expenditure, current_income, limit_type, category=None):
        """Returns (is_exceeded, usage_ratio, remaining_amount) [cite: 36]"""
        total_exp = sum(r["amount"] for r in current_expenditure)
        total_inc = sum(r["amount"] for r in current_income)

        limit_amount = 0.0

        if limit_type == "time":
            limit_amount = self.time_limits.get("m", 0.0) # Assuming monthly focus for dashboard
        elif limit_type == "proportion" and category:
            prop = self.proportion_limits.get(category, 0.0)
            limit_amount = total_inc * prop
            
            # Filter expenditures by category
            total_exp = sum(r["amount"] for r in current_expenditure if r.get("category") == category)

        if limit_amount <= 1e-9:
            return False, 0.0, 0.0

        usage_ratio = total_exp / limit_amount
        is_exceeded = usage_ratio >= 1.0
        remaining = max(0.0, limit_amount - total_exp)

        return is_exceeded, usage_ratio, remaining
