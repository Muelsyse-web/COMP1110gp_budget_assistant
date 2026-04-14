import os
import sys
import json
import re
import statistics 
from Limit import LimitManager
import Input
import Statistic

# ANSI Colors
C_INC, C_EXP, C_ANO, C_BAR, C_RESET = '\033[92m', '\033[91m', '\033[93m', '\033[96m', '\033[0m'

def get_char():
    try:
        import msvcrt
        return msvcrt.getch().decode('utf-8').upper()
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

def pad_text(text, width):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    plain = ansi_escape.sub('', str(text))
    curr_len = sum(2 if ord(c) > 127 else 1 for c in plain)
    return str(text) + (" " * max(0, width - curr_len))

class FinanceSystem:
    def __init__(self):
        self.records = Input.read_input("data.json", "json")
        self.lm = LimitManager()
        
        self.scale = "All"
        self.target_date = None
        self.category_filter = "All"
        self.range_filter = (0.0, float('inf'))
        
    def save(self):
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4)
        print("\n[System] Data saved successfully.")

    def get_filtered_records(self):
        filtered = []
        for r in self.records:
            if self.scale == "Year" and self.target_date:
                if r["year"] != self.target_date["year"]: continue
            elif self.scale == "Month" and self.target_date:
                if r["year"] != self.target_date["year"] or r["month"] != self.target_date["month"]: continue
            elif self.scale == "Day" and self.target_date:
                if r["year"] != self.target_date["year"] or r["month"] != self.target_date["month"] or r["day"] != self.target_date["day"]: continue
            
            if self.category_filter != "All" and r.get("category") != self.category_filter:
                continue
            
            if not (self.range_filter[0] <= r.get("money", 0) <= self.range_filter[1]):
                continue
                
            filtered.append(r)
        return filtered

    def draw_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        filtered_recs = self.get_filtered_records()
        exp = [r for r in filtered_recs if not r.get("is_income", False)]
        inc = [r for r in filtered_recs if r.get("is_income", False)]
        
        t_exp = sum(r.get("money", 0) for r in exp)
        t_inc = sum(r.get("money", 0) for r in inc)
        
        td_str = "All"
        if self.scale == "Year" and self.target_date: td_str = f"{self.target_date['year']}"
        elif self.scale == "Month" and self.target_date: td_str = f"{self.target_date['year']}-{self.target_date['month']:02d}"
        elif self.scale == "Day" and self.target_date: td_str = f"{self.target_date['year']}-{self.target_date['month']:02d}-{self.target_date['day']:02d}"

        r_str = f"{self.range_filter[0]:.0f}-{'inf' if self.range_filter[1] == float('inf') else f'{self.range_filter[1]:.0f}'}"
        
        print("=========================================================================")
        print(f"[T]Time:{td_str:<10} | [C]Cat:{self.category_filter:<10} | [R]Range:{r_str:<10} | [L]Limits")
        print("=========================================================================")
        
        exp_str = f"{C_EXP}Total Exp: ${t_exp:,.2f}{C_RESET}"
        inc_str = f"{C_INC}Total Inc: ${t_inc:,.2f}{C_RESET}"
        print(f"{exp_str:<35} | {inc_str}")
        print("-" * 73)
        
        print("Real-time Limit Progress:")
        is_exc, ratio, rem, limit_name, limit_val = self.lm.check_limit(exp, self.scale, self.category_filter)
        
        if limit_val <= 1e-9:
            print(f"Limit ({limit_name}): {C_BAR}[ Not Set ]{C_RESET} (Press 'L' to setup limits)")
        else:
            bar_len = min(20, int(ratio * 20))
            color = C_EXP if is_exc else C_BAR
            bar_str = f"[{'█' * bar_len}{' ' * (20-bar_len)}] {ratio*100:.0f}%"
            print(f"Limit ({limit_name}): {color}{bar_str}{C_RESET} (${t_exp:,.2f}/${limit_val:,.2f}) Remaining: ${rem:,.2f}")
        print("-" * 73)
        
        print("Press [Y] Details | [I] Input Data | [Q] Exit System")

    def show_details(self):
        filtered_recs = self.get_filtered_records()
        exp = [r for r in filtered_recs if not r.get("is_income", False)]
        if not exp:
            print("\nNo expenditures found for current filters.")
            get_char(); return
            
        m_list = [r["money"] for r in exp]
        mean_v = statistics.mean(m_list)
        std_v = statistics.stdev(m_list) if len(m_list) > 1 else 0
        max_v = max(m_list) if m_list else 0

        # Description column added to header
        print("\n" + pad_text("Date", 12) + "| " + pad_text("Category", 15) + "| " + pad_text("Money", 10) + "| " + pad_text("Alarm", 10) + "| " + pad_text("Description", 20) + "| Bar Chart")
        print("-" * 110)
        
        for r in exp:
            date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            is_ano = Statistic.is_anomaly(r["money"], mean_v, std_v)
            alarm = f"{C_ANO}ANOMALY{C_RESET}" if is_ano else "Normal"
            bar = f"{C_BAR}{Statistic.generate_barchart(r['money'], max_v)}{C_RESET}"
            
            # Extract description and truncate if it's too long
            desc = r.get("description", "")
            if len(desc) > 18:
                desc = desc[:15] + "..."
            
            print(f"{pad_text(date, 12)}| {pad_text(r.get('category',''), 15)}| {pad_text(f'{r['money']:.1f}', 10)}| {pad_text(alarm, 10)}| {pad_text(desc, 20)}| {bar}")
        
        pred_recs = [r for r in self.records if (self.category_filter == "All" or r.get("category") == self.category_filter)]
        pred = Statistic.predict_budget(pred_recs)
        print(f"\n{C_INC}Predicted 30-Day Budget for '{self.category_filter}': ${pred:,.2f}{C_RESET}")
        print("\nPress any key to return...")
        get_char()

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
            dp = Input.validate_date(d)
            if dp:
                self.scale = "Day"
                self.target_date = {"year": dp[0], "month": dp[1], "day": dp[2]}

    def _handle_category_filter(self):
        cats = list(set(r.get("category") for r in self.records if "category" in r))
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
        print("\n--- Set Money Range ---")
        try:
            l_str = input("Lower bound (default 0): ").strip()
            lower = float(l_str) if l_str else 0.0
            u_str = input("Upper bound (leave empty for inf): ").strip()
            upper = float(u_str) if u_str else float('inf')
            self.range_filter = (max(0.0, lower), upper)
        except ValueError:
            print("Error: Invalid numbers.")

    def _handle_limit_menu(self):
        print("\n--- Limit Management ---")
        print("[1] Set Time Limit")
        print("[2] Set Category Limit")
        print("[3] Remove Limit (Set to 0)")
        choice = input("Choice (1/2/3): ").strip()
        
        try:
            if choice == '1':
                print("Scale options: [d]ay, [w]eek, [m]onth, [y]ear")
                scale = input("Enter scale (d/w/m/y): ").strip().lower()
                if scale in ['d', 'w', 'm', 'y']:
                    amt = float(input("Enter limit amount: "))
                    self.lm.set_limit("time", scale, amt)
                    
                    scale_map = {'d': 'Day', 'w': 'Week', 'm': 'Month', 'y': 'Year'}
                    self.scale = scale_map[scale]
                    print(f"\n[Success] Limit set! Dashboard Scale automatically changed to {self.scale}.")
                    input("Press Enter to return...") 
                    
            elif choice == '2':
                cat = input("Enter Category Name (e.g. Food): ").strip()
                amt = float(input("Enter limit amount: "))
                self.lm.set_limit("cat", cat, amt)
                
                self.category_filter = cat
                print(f"\n[Success] Limit set! Dashboard Category automatically changed to {self.category_filter}.")
                input("Press Enter to return...") 

            elif choice == '3':
                t_c = input("Remove [T]ime or [C]ategory limit? (T/C): ").strip().upper()
                if t_c == 'T':
                    scale = input("Scale [d/w/m/y]: ").strip().lower()
                    self.lm.set_limit("time", scale, 0.0)
                elif t_c == 'C':
                    cat = input("Category Name: ").strip()
                    self.lm.set_limit("cat", cat, 0.0)
        except ValueError:
            print("Error: Invalid amount.")
            input("Press Enter to return...")

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
                    print("\n")
                    while True:
                        sub = input("[F]ile or [T]erminal? (F/T): ").strip().upper()
                        if sub in ['F', 'T']:
                            break
                        print("Error: Please enter 'F' or 'T'.")
                    
                    if sub == 'F':
                        path = input("Enter file path: ").strip()
                        if path:
                            self.records.extend(Input.read_input(path, "txt"))
                    else:
                        rec = Input.read_terminal()
                        if rec: 
                            self.records.append(rec)
                    self.save()
        except KeyboardInterrupt:
            print("\n[System] Interrupted by user.")
        finally:
            self.save()
            print("System shutting down securely...")

if __name__ == "__main__":
    app = FinanceSystem()
    app.run()
