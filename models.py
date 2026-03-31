class Transaction:
    def __init__(self, date, category, amount, description=""):
        self.date = date
        self.category = category
        self.amount = float(amount)
        self.description = description

    def to_dict(self):
        return {
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['date'], data['category'], data['amount'], data.get('description', ''))

class BudgetRule:
    def __init__(self, category, limit_amount, time_scale="monthly"):
        self.category = category
        self.limit_amount = float(limit_amount)
        self.time_scale = time_scale # e.g., "daily", "monthly"

    def to_dict(self):
        return {
            "category": self.category,
            "limit_amount": self.limit_amount,
            "time_scale": self.time_scale
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['category'], data['limit_amount'], data['time_scale'])
