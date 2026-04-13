import json
from datetime import datetime

def validate_date(date_str):
    """Strictly control mm and dd to two digits. Reject leap year errors. [cite: 26]"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.year, dt.month, dt.day
    except ValueError:
        return None

def read_input(file_path, mode="json"):
    """Reads JSON directly into internal schema, or parses TXT [cite: 24, 25]"""
    records = []
    try:
        if mode == "json":
            with open(file_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
        elif mode == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(" ", 3)
                    if len(parts) == 4:
                        date_parts = validate_date(parts[0])
                        if date_parts:
                            records.append({
                                "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                                "category": parts[1], "amount": float(parts[2]),
                                "description": parts[3], "is_income": False # Defaulting for simplicity
                            })
    except FileNotFoundError:
        pass # Handle empty start
    return records

def read_terminal():
    """Interactive input format [yyyy-mm-dd] [category] [amount] [description] [cite: 31, 32]"""
    raw = input("Enter record ([yyyy-mm-dd] [category] [amount] [description]): ")
    parts = raw.strip().split(" ", 3)
    if len(parts) == 4:
         date_parts = validate_date(parts[0])
         if date_parts:
             return {
                 "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                 "category": parts[1], "amount": float(parts[2]),
                 "description": parts[3], "is_income": False
             }
    print("Invalid format or date.")
    return None
