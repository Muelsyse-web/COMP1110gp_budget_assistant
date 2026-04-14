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
        input("Press Enter to continue...") # FIX 2: Pause to let user read error
        return None
        
    parts = raw.split(" ", 3)
    if len(parts) >= 3:
         date_parts = validate_date(parts[0])
         if date_parts:
             try:
                 money_val = float(parts[2])
                 if money_val <= 0:
                     print("Error: Money amount must be greater than 0.")
                     input("Press Enter to continue...")
                     return None
                 return {
                     "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                     "category": parts[1], "money": money_val,
                     "description": parts[3] if len(parts)==4 else "",
                     "is_income": is_inc
                 }
             except ValueError:
                 print("Error: Money must be a valid number.")
                 input("Press Enter to continue...")
                 return None
         else:
             # FIX 2: Explicit error for invalid calendar dates
             print(f"Error: Invalid date '{parts[0]}'. The date does not exist (e.g. 2026-02-30) or format is wrong.")
             input("Press Enter to continue...")
             return None
                 
    print("Error: Missing fields. Format must be [yyyy-mm-dd] [category] [money] [description].")
    input("Press Enter to continue...")
    return None
