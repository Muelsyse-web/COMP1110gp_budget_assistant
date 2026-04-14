import json
import os
from datetime import datetime

def validate_date(date_str):
    """Strictly control date format [yyyy-mm-dd] and check validity"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.year, dt.month, dt.day
    except ValueError:
        return None

def read_input(file_path, mode="json"):
    """Reads data from external files safely"""
    records = []
    if not os.path.exists(file_path):
        return records
        
    try:
        if mode == "json":
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    records = json.loads(content)
        elif mode == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(" ", 3)
                    if len(parts) >= 3:
                        date_parts = validate_date(parts[0])
                        if date_parts:
                            try:
                                money_val = float(parts[2])
                                if money_val > 0: # Ensure positive
                                    records.append({
                                        "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                                        "category": parts[1], "money": money_val,
                                        "description": parts[3] if len(parts)==4 else "",
                                        "is_income": False
                                    })
                            except ValueError:
                                pass
    except Exception as e:
        print(f"File reading error: {e}")
    return records

def read_terminal():
    """Manual input with strict validation for I/E and positive money"""
    print("\n--- Data Input ---")
    
    while True:
        type_choice = input("Is this [I]ncome or [E]xpenditure? (I/E): ").strip().upper()
        if type_choice in ['I', 'E']:
            break
        print("Error: Invalid choice. Please enter 'I' or 'E'.")
        
    is_inc = True if type_choice == 'I' else False
    
    raw = input("Enter [yyyy-mm-dd] [category] [money] [description]: ").strip()
    if not raw:
        print("Error: Empty input.")
        return None
        
    parts = raw.split(" ", 3)
    if len(parts) >= 3:
         date_parts = validate_date(parts[0])
         if date_parts:
             try:
                 money_val = float(parts[2])
                 if money_val <= 0:
                     print("Error: Money amount must be greater than 0.")
                     return None
                 return {
                     "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                     "category": parts[1], "money": money_val,
                     "description": parts[3] if len(parts)==4 else "",
                     "is_income": is_inc
                 }
             except ValueError:
                 print("Error: Money must be a valid number.")
                 return None
                 
    print("Error: Invalid format or incorrect date. Make sure you use yyyy-mm-dd.")
    return None
