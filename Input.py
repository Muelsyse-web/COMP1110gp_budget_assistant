import json
import re
from datetime import datetime

def validate_date(date_str):
    """Strictly control date format [yyyy-mm-dd] and check for validity [cite: 124]"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.year, dt.month, dt.day
    except ValueError:
        return None

def read_input(file_path, mode="json"):
    """Reads data from external files [cite: 32-53]"""
    records = []
    try:
        if mode == "json":
            with open(file_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
        elif mode == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # Format: yyyy-mm-dd category money description
                    parts = line.strip().split(" ", 3)
                    if len(parts) >= 3:
                        date_parts = validate_date(parts[0])
                        if date_parts:
                            records.append({
                                "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                                "category": parts[1], "money": float(parts[2]),
                                "description": parts[3] if len(parts)==4 else "",
                                "is_income": False # Default to expense for simple text files
                            })
    except (FileNotFoundError, json.JSONDecodeError):
        pass 
    return records

def read_terminal():
    """Manual input with type and source selection [cite: 123-127, 386-389]"""
    print("\n--- Data Input ---")
    type_choice = input("Is this [I]ncome or [E]xpenditure? (I/E): ").upper()
    is_inc = True if type_choice == 'I' else False
    
    raw = input("Enter [yyyy-mm-dd] [category] [money] [description]: ")
    parts = raw.strip().split(" ", 3)
    
    if len(parts) >= 3:
         date_parts = validate_date(parts[0])
         if date_parts:
             return {
                 "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                 "category": parts[1], "money": float(parts[2]),
                 "description": parts[3] if len(parts)==4 else "",
                 "is_income": is_inc
             }
    print("Error: Invalid format or date.")
    return None
