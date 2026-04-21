import os
import sys
import json
import re
import math
import statistics 
from datetime import datetime
from Limit import LimitManager
import Input
import Statistic

# ANSI Colors
C_INC = '\033[92m'  # Green (Income)
C_EXP = '\033[91m'  # Red (Expenses)
C_ANO = '\033[93m'  # Yellow (Anomalies)
C_BAR = '\033[96m'  # Cyan (Bar Charts)
C_PUR = '\033[95m'  # Purple (Input Errors)
C_RESET = '\033[0m'

def get_visual_len(text):
    """Calculates the visual width of a string in the terminal, counting CJK characters as 2 spaces."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    plain = ansi_escape.sub('', str(text))
    return sum(2 if ord(c) > 127 else 1 for c in plain)

def pad_text(text, width):
    curr_len = get_visual_len(text)
    return str(text) + (" " * max(0, width - curr_len))

def round_to_3sf(num):
    """Rounds a number to 3 significant figures for psychological limit setting"""
    if num == 0.0:
        return 0.0
    try:
        return round(num, 3 - int(math.floor(math.log10(abs(num)))) - 1)
    except ValueError:
        return 0.0

def get_char():
    """Captures single keystrokes cross-platform, protected against special characters."""
    try:
        import msvcrt
        key = msvcrt.getch()
        if key in [b'\x00', b'\xe0']:
            msvcrt.getch() 
            return ""
        return key.decode('utf-8', errors='ignore').upper() 
    except ImportError:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch.upper()
        
class FinanceSystem:
    def __init__(self):
        self.records = Input.read_input("data.json", "json")
        self.lm = LimitManager()
        self.scale = "All"
        self.target_date = None
        self.category_filter = "All"
        self.range_filter = (0.0, float('inf'))
        self.auto_suggest = True 
        
    def save(self):
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4)

    def get_filtered_records(self):
        filtered = []
        for r in self.records:
            if self.scale == "Year" and self.target_date:
                if r["year"] != self.target_date["year"]: continue
            elif self.scale == "Month" and self.target_date:
                if r["year"] != self.target_date["year"] or r["month"] != self.target_date["month"]: continue
            elif self.scale == "Day" and self.target_date:
                if r["year"] != self.target_date["year"] or r["month"] != self.target_date["month"] or r["day"] != self.target_date["day"]: continue
            
            if self.category_filter != "All" and r["category"] != self.category_filter:
                continue
            
            if not (self.range_filter[0] <= r["money"] <= self.range_filter[1]):
                continue
                
            filtered.append(r)
        return filtered

    def draw_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        filtered_recs = self.get_filtered_records()
        exp = [r for r in filtered_recs if not r.get("is_income", False)]
        inc = [r for r in filtered_recs if r.get("is_income", False)]
        
        t_exp = sum(r["money"] for r in exp)
        t_inc = sum(r["money"] for r in inc)
        
        td_str = "All"
        if self.scale == "Year" and self.target_date: td_str = f"{self.target_date['year']}"
        elif self.scale == "Month" and self.target_date: td_str = f"{self.target_date['year']}-{self.target_date['month']:02d}"
        elif self.scale == "Day" and self.target_date: td_str = f"{self.target_date['year']}-{self.target_date['month']:02d}-{self.target_date['day']:02d}"

        r_str = f"{self.range_filter[0]:.0f}-{'inf' if self.range_filter[1] == float('inf') else f'{self.range_filter[1]:.0f}'}"
        
        print("=====================================================================================")
        print(f"[T]Time:{td_str:<12} | [C]Cat:{self.category_filter:<14} | [R]Amount Range:{r_str:<10} | [L]Limits")
        print("=====================================================================================")
        
        exp_str = f"{C_EXP}Total Exp: ${t_exp:,.2f}{C_RESET}"
        inc_str = f"{C_INC}Total Inc: ${t_inc:,.2f}{C_RESET}"
        print(f"{exp_str:<45} | {inc_str}")
        print("-" * 85)
        
        print("Real-time Limit Progress:")
        is_exc, ratio, rem, limit_name, limit_val = self.lm.check_limit(exp, self.scale, self.category_filter)
        
        scale_str, target_days = Statistic.determine_scale(exp, self.scale)
        
        if self.scale == "All":
            print(f"Limit: {C_BAR}[ N/A in 'All' Time Scale ]{C_RESET} (Switch Time filter to see specific limits)")
        elif limit_val <= 1e-9:
            if self.auto_suggest:
                suggested_raw = Statistic.predict_budget(exp, target_days)
                
                if suggested_raw <= 1e-9:
                    print(f"Limit: {C_PUR}[ Not Set ]{C_RESET} (Log expenses to unlock Auto-Suggested limits!)")
                else:
                    sug_limit = round_to_3sf(suggested_raw)
                    sug_ratio = t_exp / sug_limit if sug_limit > 0 else 0
                    sug_rem = max(0.0, sug_limit - t_exp)
                    bar_len = min(20, int(sug_ratio * 20))
                    
                    if sug_ratio >= 1.0: color = C_EXP
                    elif sug_ratio >= 0.75: color = C_ANO
                    else: color = C_BAR
                        
                    bar_str = f"[{'█' * bar_len}{' ' * (20-bar_len)}]"
                    
                    print(f"Limit: {C_PUR}[ Auto-Suggested ]{C_RESET}")
                    print(f"{color}{bar_str}{C_RESET} {sug_ratio*100:.0f}%  (${t_exp:,.2f} / ${sug_limit:,.0f})  Rem: ${sug_rem:,.2f}")
            else:
                print(f"Limit: {C_BAR}[ Not Set ]{C_RESET} (Press 'L' to setup limits)")
        else:
            bar_len = min(20, int(ratio * 20))
            color = C_EXP if is_exc else C_BAR
            bar_str = f"[{'█' * bar_len}{' ' * (20-bar_len)}]"
            
            print(f"Limit ({limit_name}):")
            print(f"{color}{bar_str}{C_RESET} {ratio*100:.0f}%  (${t_exp:,.2f} / ${limit_val:,.2f})  Rem: ${rem:,.2f}")

        print("=====================================================================================")
        
        if self.scale != "All":
            pred_val = Statistic.predict_budget(exp, target_days)
            if pred_val > 1e-9:
                print(f"Predicted {scale_str} Budget: {C_INC}${round(pred_val):,.0f}{C_RESET}")
            else:
                print(f"Predicted {scale_str} Budget: {C_INC}[ Awaiting more data ]{C_RESET}")
        else:
            print(f"Predicted Budget: {C_BAR}[ N/A in 'All' Time Scale ]{C_RESET}")

        print("-" * 85)
        print("[Y] Details | [I] Input | [Q] Quit")

    def show_details(self):
        sort_mode = "original"
        sort_desc = False

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            filtered_recs = self.get_filtered_records()
            exp = [r for r in filtered_recs if not r.get("is_income", False)]
            inc = [r for r in filtered_recs if r.get("is_income", False)]
            
            if not exp and not inc:
                print("\nNo records found for current filters.")
                get_char()
                return

            if sort_mode == "time":
                exp.sort(key=lambda x: (x["year"], x["month"], x["day"]), reverse=sort_desc)
                inc.sort(key=lambda x: (x["year"], x["month"], x["day"]), reverse=sort_desc)
            elif sort_mode == "money":
                exp.sort(key=lambda x: x["money"], reverse=sort_desc)
                inc.sort(key=lambda x: x["money"], reverse=sort_desc)
            elif sort_mode == "alphabet":
                exp.sort(key=lambda x: x["category"].lower(), reverse=sort_desc)
                inc.sort(key=lambda x: x["category"].lower(), reverse=sort_desc)

            all_recs = inc + exp
            max_desc_len = max([get_visual_len(r.get("description", "")) for r in all_recs]) if all_recs else 0
            desc_width = max(15, max_desc_len + 2) 
            
            max_cat_len = max([get_visual_len(r.get("category", "")) for r in all_recs]) if all_recs else 0
            cat_width = max(14, max_cat_len + 2) 
            
            total_line_width = 61 + cat_width + desc_width
            
            def print_table(records, title, color, is_income=False):
                print(f"\n>>> {color}{title}{C_RESET}")
                if not records:
                    print(f" (No records found)")
                    return []
                
                # Retrieve both statistical baselines for the Hybrid Engine
                log_stats, raw_stats = Statistic.get_both_stats(records)
                
                m_list = [r["money"] for r in records if r["money"] > 0]
                max_v = max(m_list) if m_list else 0
                
                alarm_header = "" if is_income else "Alarm"
                print("\n" + pad_text("Idx", 5) + "| " + pad_text("Date", 12) + "| " + pad_text("Category", cat_width) + "| " + pad_text("Money", 10) + "| " + pad_text("Description", desc_width) + "| " + pad_text(alarm_header, 10) + "| Bar Chart")
                print("-" * total_line_width)
                
                warnings_list = []
                for i, r in enumerate(records, start=1):
                    date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
                    try:
                        datetime(r['year'], r['month'], r['day'])
                    except ValueError as e:
                        warnings_list.append(f"{C_ANO}ValueError: *[{title} Idx {i}]*, {str(e)}{C_RESET}")

                    if is_income:
                        alarm = ""
                    else:
                        is_ano = Statistic.is_hybrid_anomaly(r["money"], log_stats, raw_stats, pivot=1000.0, ignore_flag=r.get("ignore_anomaly", False))
                        if r.get("ignore_anomaly", False):
                            alarm = f"{C_INC}Ignored{C_RESET}"
                        else:
                            alarm = f"{C_ANO}ANOMALY{C_RESET}" if is_ano else "Normal"
                        
                    bar = f"{C_BAR}{Statistic.generate_barchart(r['money'], max_v)}{C_RESET}"
                    desc = r.get("description", "")
                    
                    money_fmt = f"{r['money']:.1f}"
                    print(f"{pad_text(str(i), 5)}| {pad_text(date, 12)}| {pad_text(r['category'], cat_width)}| {pad_text(money_fmt, 10)}| {pad_text(desc, desc_width)}| {pad_text(alarm, 10)}| {bar}")
                return warnings_list

            warnings = []
            warnings.extend(print_table(inc, "INCOME RECORDS", C_INC, is_income=True))
            warnings.extend(print_table(exp, "EXPENSE RECORDS", C_EXP, is_income=False))
            
            if warnings:
                print(f"\n{C_ANO}--- Data format Warnings ---{C_RESET}")
                for w in warnings:
                    print(w)

            if self.scale != "All":
                scale_str, target_days = Statistic.determine_scale(exp, self.scale)
                pred = Statistic.predict_budget(exp, target_days)
                if pred > 1e-9:
                    print(f"\n{C_EXP}Predicted {scale_str} Expense Budget for '{self.category_filter}': ${round(pred):,.0f}{C_RESET}")
                else:
                    print(f"\n{C_EXP}Predicted {scale_str} Expense Budget for '{self.category_filter}': [ Awaiting more data ]{C_RESET}")
            else:
                print(f"\n{C_BAR}Predicted Budget: [ N/A in 'All' Time Scale ]{C_RESET}")
            
            print("\n--- Details Options ---")
            print("[S]ort Tables | [E]dit Record | [Q]uit to Dashboard")
            cmd = get_char()
            
            if cmd == 'Q':
                break
            elif cmd == 'S':
                print("\nSort by: [O]riginal, [A]lphabet(Cat), [T]ime, [M]oney")
                s_cmd = get_char()
                if s_cmd in ['T', 'M', 'A']:
                    print("Order: [A]scending or [D]escending?")
                    o_cmd = get_char()
                    sort_desc = (o_cmd == 'D')
                    if s_cmd == 'T': sort_mode = "time"
                    elif s_cmd == 'M': sort_mode = "money"
                    elif s_cmd == 'A': sort_mode = "alphabet"
                elif s_cmd == 'O':
                    sort_mode = "original"
            elif cmd == 'E':
                print("\nEdit [I]ncome or [E]xpense record? (I/E)")
                ie_cmd = get_char()
                
                os.system('cls' if os.name == 'nt' else 'clear')
                
                if ie_cmd == 'I':
                    target_list = inc
                    t_name = "Income"
                    print_table(inc, "INCOME RECORDS", C_INC, is_income=True)
                elif ie_cmd == 'E':
                    target_list = exp
                    t_name = "Expense"
                    print_table(exp, "EXPENSE RECORDS", C_EXP, is_income=False)
                else:
                    print("Invalid choice."); get_char(); continue
                    
                if not target_list:
                    print(f"\nNo {t_name} records available to edit."); get_char(); continue

                idx_str = input(f"\nEnter Index (Idx) number from the {t_name} table to edit: ").strip()
                if idx_str.isdigit() and 1 <= int(idx_str) <= len(target_list):
                    target_r = target_list[int(idx_str) - 1]
                    print(f"\nEditing {t_name} Idx {idx_str}: {target_r['year']}-{target_r['month']:02d}-{target_r['day']:02d} | {target_r['category']} | ${target_r['money']}")
                    print("What would you like to edit?")
                    
                    if t_name == "Expense":
                        print("[T]ype (Flip I/E) | [D]ate | [C]ategory | [M]oney | [I]nfo(Description) | [A]larm Toggle | [X]Delete | [Q]Cancel")
                    else:
                        print("[T]ype (Flip I/E) | [D]ate | [C]ategory | [M]oney | [I]nfo(Description) | [X]Delete | [Q]Cancel")
                        
                    e_cmd = get_char()
                    
                    if e_cmd == 'T':
                        target_r["is_income"] = not target_r["is_income"]
                        self.save()
                        new_type = "Income" if target_r["is_income"] else "Expense"
                        print(f"\n{C_INC}Record successfully moved to the {new_type} table.{C_RESET}"); get_char()
                    elif e_cmd == 'D':
                        new_date = input("Enter new date (YYYY-MM-DD): ").strip()
                        dp = Input.validate_date(new_date, "Edit Input")
                        if dp:
                            target_r["year"], target_r["month"], target_r["day"] = dp[0], dp[1], dp[2]
                            self.save()
                    elif e_cmd == 'C':
                        new_cat = input("Enter new Category: ").strip()
                        if new_cat:
                            target_r["category"] = new_cat
                            self.save()
                    elif e_cmd == 'M':
                        try:
                            new_money = float(input("Enter new Money amount: ").strip())
                            if new_money > 0:
                                target_r["money"] = new_money
                                self.save()
                            else:
                                print("Amount must be positive."); get_char()
                        except ValueError:
                            print("Invalid amount."); get_char()
                    elif e_cmd == 'I':
                        new_desc = input("Enter new Description: ").strip()
                        target_r["description"] = new_desc
                        self.save()
                    elif e_cmd == 'A' and t_name == "Expense":
                        target_r["ignore_anomaly"] = not target_r.get("ignore_anomaly", False)
                        self.save()
                    elif e_cmd == 'X':
                        print(f"\n{C_EXP}Are you sure you want to delete this record? (Y/N){C_RESET}")
                        conf = get_char()
                        if conf == 'Y':
                            self.records.remove(target_r)
                            self.save()
                            print(f"{C_INC}Record deleted successfully.{C_RESET}")
                            get_char()
                else:
                    print("Invalid index."); get_char()

    def _handle_time_filter(self):
        print("\n--- Set Time Scale ---")
        print("[D]ay, [M]onth, [Y]ear, [A]ll")
        sub = input("Select scale (D/M/Y/A): ").strip().upper()
        if sub == 'A':
            self.scale = "All"
            self.target_date = None
        elif sub == 'Y':
            y = input("Enter Year (YYYY): ").strip()
            if y.isdigit():
                self.scale = "Year"
                self.target_date = {"year": int(y)}
        elif sub == 'M':
            m = input("Enter Month (YYYY-MM): ").strip()
            parts = m.split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                self.scale = "Month"
                self.target_date = {"year": int(parts[0]), "month": int(parts[1])}
        elif sub == 'D':
            d = input("Enter Day (YYYY-MM-DD): ").strip()
            dp = Input.validate_date(d, "Filter Input")
            if dp:
                self.scale = "Day"
                self.target_date = {"year": dp[0], "month": dp[1], "day": dp[2]}
        else:
            print("Invalid input."); get_char()

    def _handle_category_filter(self):
        cats = list(set(r["category"] for r in self.records))
        print("\n--- Select Category ---")
        print("0: All Categories")
        for i, c in enumerate(cats, 1):
            print(f"{i}: {c}")
        try:
            choice = int(input("Enter number: "))
            if choice == 0:
                self.category_filter = "All"
            elif 1 <= choice <= len(cats):
                self.category_filter = cats[choice - 1]
        except ValueError:
            print("Invalid selection.")

    def _handle_range_filter(self):
        print("\n--- Set Amount Range ---")
        try:
            l_str = input("Lower bound (default 0): ").strip()
            lower = float(l_str) if l_str else 0.0
            u_str = input("Upper bound (leave empty for inf): ").strip()
            upper = float(u_str) if u_str else float('inf')
            self.range_filter = (max(0.0, lower), upper)
        except ValueError:
            print("Error: Invalid numbers.")

    def _handle_limit_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=====================================================================================")
            print("                             LIMIT MANAGEMENT DASHBOARD                              ")
            print("=====================================================================================")
            
            t_exp = sum(r["money"] for r in self.records if not r.get("is_income", False))
            t_inc = sum(r["money"] for r in self.records if r.get("is_income", False))
            print(f" {C_EXP}Lifetime Exp: ${t_exp:,.2f}{C_RESET} | {C_INC}Lifetime Inc: ${t_inc:,.2f}{C_RESET}")
            print("-" * 85)
            
            print(f" >>> {C_BAR}ACTIVE TIME LIMITS{C_RESET}")
            active_time = False
            for k, v in self.lm.time_limits.items():
                if v > 1e-9:
                    scale_name = {"d":"Daily", "w":"Weekly", "m":"Monthly", "y":"Yearly"}.get(k, k)
                    print(f"     - {scale_name}: ${v:,.2f}")
                    active_time = True
                    
            if not active_time: 
                if self.auto_suggest:
                    exp_all = [r for r in self.records if not r.get("is_income", False)]
                    scale_str, target_days = Statistic.determine_scale(exp_all, "All")
                    sug_time = round_to_3sf(Statistic.predict_budget(exp_all, target_days))
                    
                    if sug_time > 0:
                        print(f"     (None set) {C_PUR}>> Auto-Suggested {scale_str}: ${sug_time:,.0f}{C_RESET}")
                    else:
                        print(f"     (None set) {C_PUR}>> Log data to get a personalized suggestion!{C_RESET}")
                else:
                    print("     (None set)")
            
            print(f"\n >>> {C_BAR}ACTIVE CATEGORY LIMITS{C_RESET}")
            active_cat = False
            for k, v in self.lm.category_limits.items():
                if v > 1e-9:
                    print(f"     - {k}: ${v:,.2f}")
                    active_cat = True
            if not active_cat: print("     (None set)")
            print("-" * 85)
            
            toggle_state = "ON " if self.auto_suggest else "OFF"
            print(f"{'[T] Time Limit':<27} | {'[C] Category Limit':<27} | [R] Remove Limit")
            print(f"{f'[1] Toggle Auto ({toggle_state})':<27} | {'[Y] View Details':<27} | ")
            print(f"{'[Q] Return to Main Menu':<27} | {'':<27} | ")
            
            cmd = get_char()
            if cmd == 'Q':
                break
            elif cmd == 'Y':
                self.show_details()
            elif cmd == '1':
                self.auto_suggest = not self.auto_suggest
            elif cmd == 'T':
                print("\nScale options: [d]ay, [w]eek, [m]onth, [y]ear")
                scale = input("Enter scale (d/w/m/y): ").strip().lower()
                if scale in ['d', 'w', 'm', 'y']:
                    try:
                        amt = float(input("Enter limit amount: "))
                        self.lm.set_limit("time", scale, amt)
                    except ValueError:
                        print("Error: Invalid amount."); get_char()
            elif cmd == 'C':
                print("\n")
                cat = input("Enter Category Name (e.g. Food): ").strip()
                try:
                    amt = float(input("Enter limit amount: "))
                    self.lm.set_limit("cat", cat, amt)
                except ValueError:
                    print("Error: Invalid amount."); get_char()
            elif cmd == 'R':
                print("\n")
                t_c = input("Remove [T]ime or [C]ategory limit? (T/C): ").strip().upper()
                if t_c == 'T':
                    scale = input("Scale [d/w/m/y]: ").strip().lower()
                    self.lm.set_limit("time", scale, 0.0)
                elif t_c == 'C':
                    cat = input("Category Name: ").strip()
                    self.lm.set_limit("cat", cat, 0.0)

    def _handle_input_menu(self):
        staging_buffer = []
        last_error = ""
        
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=====================================================================================")
            print("                             DATA INPUT STAGING AREA                              ")
            print("=====================================================================================")
            print(" Instructions:")
            print(" - Manual Entry: Type your data directly using this exact format:")
            print("                 [I/E] [YYYY-MM-DD] [CATEGORY] [MONEY] [DESCRIPTION]")
            print("                 (e.g., E 2026-04-21 Food 45.50 Lunch)")
            print(" - File Import:  Type 'F' followed by your filename (e.g., F test_food.txt)")
            print(" - Edit Line:    Type 'E' to select and modify (or delete) a specific line.")
            print(f" - Finish:       Type 'DONE' to save all entries to the database.")
            print(f"                 ({C_INC}Income is shown in Green{C_RESET}, {C_EXP}Expenses in Red{C_RESET}).")
            print(" - Cancel:       Type 'Q' to discard everything and return.")
            print("-" * 85)
            
            print(f" {pad_text('Idx', 4)}| {pad_text('Type', 6)}| {pad_text('Date', 12)}| {pad_text('Category', 14)}| {pad_text('Money', 10)}| Description")
            print("-" * 85)
            
            if not staging_buffer:
                print(" (No data staged yet. Start typing your entries...)")
            else:
                for i, item in enumerate(staging_buffer, start=1):
                    r = item["record"]
                    t_str = "[Inc]" if r["type"] == 'I' else "[Exp]"
                    date_str = r.get("raw_date", "")
                    cat_str = r.get("category", "")
                    money_str = r.get("raw_money", "")
                    desc_str = r.get("description", "")
                    
                    line_str = f"{pad_text(t_str, 6)}| {pad_text(date_str, 12)}| {pad_text(cat_str, 14)}| {pad_text(money_str, 10)}| {desc_str}"
                    
                    color = C_INC if r["is_income"] else C_EXP
                    print(f" {pad_text(str(i), 4)}| {color}{line_str}{C_RESET}")
            
            print("=====================================================================================")
            
            if last_error:
                print(f" {C_PUR}>> Input Error: {last_error}{C_RESET}")
                last_error = "" 
                
            if staging_buffer:
                print(" >> Are these all the data you want to add? If yes, type 'DONE'.")
                
            user_input = input("> Your Input: ").strip()
            
            if user_input.upper() == 'Q':
                break
                
            elif user_input.upper() == 'DONE':
                if staging_buffer:
                    for item in staging_buffer:
                        self.records.append(item["record"])
                    
                    self.records.sort(key=lambda x: (x["year"], x["month"], x["day"]))
                    self.save()
                    print(f"\n[System] {C_INC}{len(staging_buffer)} valid entries were successfully appended!{C_RESET}")
                    input("Press Enter to return to Dashboard...")
                break
                    
            elif user_input.upper() == 'E':
                idx_str = input("\n> Enter Idx number to edit: ").strip()
                if idx_str.isdigit():
                    idx = int(idx_str)
                    if 1 <= idx <= len(staging_buffer):
                        target_item = staging_buffer[idx-1]
                        rec = target_item["record"]
                        
                        print(f"\nEditing [{idx}]: {target_item['raw']}")
                        print("What would you like to edit?")
                        print("[T]ype (I/E) | [D]ate | [C]ategory | [M]oney | [I]nfo(Description) | [X]Delete | [Q]Cancel")
                        e_cmd = get_char()
                        
                        if e_cmd == 'X':
                            staging_buffer.pop(idx-1)
                            last_error = f"Successfully deleted record at Idx {idx} from staging area."
                            continue

                        new_type = rec["type"]
                        new_date = rec["raw_date"]
                        new_cat = rec["category"]
                        new_money = rec["raw_money"]
                        new_desc = rec["description"]

                        if e_cmd == 'T':
                            new_type = input("Enter new Type (I/E): ").strip().upper()
                        elif e_cmd == 'D':
                            new_date = input("Enter new date (YYYY-MM-DD): ").strip()
                        elif e_cmd == 'C':
                            new_cat = input("Enter new Category: ").strip()
                        elif e_cmd == 'M':
                            new_money = input("Enter new Money amount: ").strip()
                        elif e_cmd == 'I':
                            new_desc = input("Enter new Description: ").strip()
                        
                        if e_cmd in ['T', 'D', 'C', 'M', 'I']:
                            new_raw = f"{new_type} {new_date} {new_cat} {new_money} {new_desc}".strip()
                            parsed_edit = Input.parse_staged_line(new_raw)
                            if parsed_edit["valid"]:
                                staging_buffer[idx-1] = parsed_edit
                            else:
                                last_error = f"Edit failed: {parsed_edit['error']}. Line reverted."
                    else:
                        last_error = "Invalid index number."
                else:
                     last_error = "Invalid input. Please enter a number."
                     
            elif user_input.upper().startswith('F '):
                file_path = user_input[2:].strip()
                invalid_count = 0
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                file_parts = line.strip().split(" ", 3)
                                if file_parts[0].upper() not in ['I', 'E']:
                                    parsed = Input.parse_staged_line("E " + line.strip())
                                else:
                                    parsed = Input.parse_staged_line(line.strip())
                                
                                if parsed["valid"]:
                                    staging_buffer.append(parsed)
                                else:
                                    invalid_count += 1
                    if invalid_count > 0:
                         last_error = f"File contained {invalid_count} invalid lines. They were skipped."
                except FileNotFoundError:
                    last_error = f"Error: File '{file_path}' not found."
                except Exception as e:
                    last_error = f"File reading error: {e}"
            elif user_input:
                parsed = Input.parse_staged_line(user_input)
                if parsed["valid"]:
                    staging_buffer.append(parsed)
                else:
                    last_error = f"'{parsed['raw']}' -> {parsed['error']}"

    def run(self):
        try:
            while True:
                self.draw_dashboard()
                cmd = get_char()
                
                if cmd == 'Q': 
                    break
                elif cmd == 'T': 
                    self._handle_time_filter()
                elif cmd == 'C':
                    self._handle_category_filter()
                elif cmd == 'R': 
                    self._handle_range_filter()
                elif cmd == 'L':
                    self._handle_limit_menu()
                elif cmd == 'Y': 
                    self.show_details()
                elif cmd == 'I':
                    self._handle_input_menu()
        except KeyboardInterrupt:
            print("\n[System] Interrupted by user.")
        finally:
            self.save()
            print("System shutting down securely...")

if __name__ == "__main__":
    app = FinanceSystem()
    app.run()
