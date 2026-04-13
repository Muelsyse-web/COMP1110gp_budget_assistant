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
        self.scale = "Month"
        
    def save(self):
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4)
        print("\n[System] Data saved successfully.")

    def draw_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        exp = [r for r in self.records if not r.get("is_income", False)]
        inc = [r for r in self.records if r.get("is_income", False)]
        
        t_exp = sum(r["money"] for r in exp)
        t_inc = sum(r["money"] for r in inc)
        
        print("============================================================")
        print(f"[T]Time:{self.scale:<5} | [C]Cat:All | [A]Range:All | [L]Limits")
        print("============================================================")
        
        exp_str = f"{C_EXP}Total Exp: ${t_exp:,.2f}{C_RESET}"
        inc_str = f"{C_INC}Total Inc: ${t_inc:,.2f}{C_RESET}"
        print(f"{exp_str:<35} | {inc_str}")
        print("-" * 60)
        
        print("Real-time Limit Progress:")
        is_exc, ratio, rem = self.lm.check_limit(exp, inc)
        bar_len = min(20, int(ratio * 20))
        color = C_EXP if is_exc else C_BAR
        bar_str = f"[{'█' * bar_len}{' ' * (20-bar_len)}] {ratio*100:.0f}%"
        limit_val = self.lm.time_limits.get("m", 1000.0) 
        print(f"Monthly Limit: {color}{bar_str}{C_RESET} (${t_exp:,.2f}/${limit_val:,.2f})")
        print("-" * 60)
        
        print("Press [Y] for Details | [I] Input Data | [Q] Exit System")

    def show_details(self):
        exp = [r for r in self.records if not r.get("is_income", False)]
        if not exp:
            print("\nNo expenditures found.")
            get_char(); return
            
        m_list = [r["money"] for r in exp]
        mean_v = statistics.mean(m_list)
        std_v = statistics.stdev(m_list) if len(m_list) > 1 else 0
        max_v = max(m_list) if m_list else 0

        print("\n" + pad_text("Date", 12) + "| " + pad_text("Category", 15) + "| " + pad_text("Money", 10) + "| " + pad_text("Alarm", 10) + "| Bar Chart")
        print("-" * 85)
        
        for r in exp:
            date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            is_ano = Statistic.is_anomaly(r["money"], mean_v, std_v)
            alarm = f"{C_ANO}ANOMALY{C_RESET}" if is_ano else "Normal"
            bar = f"{C_BAR}{Statistic.generate_barchart(r['money'], max_v)}{C_RESET}"
            
            print(f"{pad_text(date, 12)}| {pad_text(r['category'], 15)}| {pad_text(f'{r['money']:.1f}', 10)}| {pad_text(alarm, 10)}| {bar}")
        
        pred = Statistic.predict_budget(self.records)
        print(f"\n{C_INC}Predicted Next Month Budget: ${pred:,.2f}{C_RESET}")
        print("\nPress any key to return...")
        get_char()

    def run(self):
        try:
            while True:
                self.draw_dashboard()
                cmd = get_char()
                
                if cmd == 'Q': 
                    break
                elif cmd == 'T': 
                    scales = ["Day", "Week", "Month", "Year", "All"]
                    self.scale = scales[(scales.index(self.scale)+1)%5]
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
            # Handles unexpected Ctrl+C termination smoothly
            print("\n[System] Interrupted by user.")
        finally:
            # Guarantee data is saved even if it crashes
            self.save()
            print("System shutting down securely...")

if __name__ == "__main__":
    app = FinanceSystem()
    app.run()
