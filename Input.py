import json
import os
import sys
from datetime import datetime

# ANSI Colors for Error Handling
C_EXP, C_RESET = '\033[91m', '\033[0m'

def validate_date(date_str, context=""):
    """Strictly control date format [yyyy-mm-dd] and check validity"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.year, dt.month, dt.day
    except ValueError as e:
        if context:
            print(f"{C_EXP}ValueError: *{context}*, {str(e)}{C_RESET}")
        return None

def parse_staged_line(raw):
    """Parses a single line for the staging area, retaining partial data even if invalid."""
    raw_clean = raw.replace('[I]', 'I').replace('[E]', 'E').strip()
    parts = raw_clean.split(" ", 4)
    
    # Initialize a default record structure to ensure UI table alignment never breaks
    record = {
        "type": "E", "raw_date": "", "category": "", "raw_money": "", "description": "",
        "year": 0, "month": 0, "day": 0, "money": 0.0, "is_income": False, "ignore_anomaly": False
    }
    
    if len(parts) >= 1: record["type"] = parts[0].upper()
    if len(parts) >= 2: record["raw_date"] = parts[1]
    if len(parts) >= 3: record["category"] = parts[2]
    if len(parts) >= 4: record["raw_money"] = parts[3]
    if len(parts) >= 5: record["description"] = parts[4]

    valid = True
    error = ""

    # 1. Validate Type
    if record["type"] not in ['I', 'E']:
        valid = False
        error = "Type must be 'I' (Income) or 'E' (Expense)"
    else:
        record["is_income"] = (record["type"] == 'I')

    # 2. Check Completeness
    if valid and len(parts) < 4:
        valid = False
        error = "Missing fields. Format: I/E YYYY-MM-DD Category Money Description"

    # 3. Validate Date (Extracting exact error for out-of-range dates)
    if valid:
        try:
            dt = datetime.strptime(record["raw_date"], "%Y-%m-%d")
            record["year"], record["month"], record["day"] = dt.year, dt.month, dt.day
        except ValueError as e:
            valid = False
            # e.g., will print "time data '2026-10-41' does not match format..." or "day is out of range for month"
            error = f"Date error: {str(e).capitalize()}"

    # 4. Validate Money
    if valid:
        try:
            money_val = float(record["raw_money"])
            if money_val <= 0:
                valid = False
                error = "Money must be greater than 0"
            else:
                record["money"] = money_val
        except ValueError:
            valid = False
            error = "Money must be a valid number"

    return {"valid": valid, "raw": raw_clean, "error": error, "record": record}

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
                line_num = 1
                for line in f:
                    parts = line.strip().split(" ", 3)
                    if len(parts) >= 3:
                        date_parts = validate_date(parts[0], f"[Line {line_num}]")
                        if date_parts:
                            try:
                                money_val = float(parts[2])
                                if money_val > 0: 
                                    records.append({
                                        "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                                        "category": parts[1], "money": money_val,
                                        "description": parts[3] if len(parts)==4 else "",
                                        "is_income": False,
                                        "ignore_anomaly": False
                                    })
                            except ValueError:
                                pass
                    line_num += 1
    except json.JSONDecodeError as e:
        print(f"\n{C_EXP}[CRITICAL SYSTEM HALT] {file_path} is corrupted: {e}{C_RESET}")
        print(f"{C_EXP}To prevent permanent data loss, the system will not boot until the JSON syntax is fixed.{C_RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"File reading error: {e}")
    return records
