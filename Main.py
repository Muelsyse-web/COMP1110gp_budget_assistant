import os
import sys
import json
import re
import statistics # Fixed: Added missing import to resolve NameError
from Limit import LimitManager
import Input
import Statistic

# ANSI Colors [cite: 366, 185-188]
C_INC, C_EXP, C_ANO, C_BAR, C_RESET = '\033[92m', '\033[91m', '\033[93m', '\033[96m', '\033[0m'

def get_char():
    """Cross-platform one-letter trigger [cite: 224-228, 412]"""
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
    """Correct padding by ignoring ANSI escape codes for width calculation [cite: 218]"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    plain = ansi_escape.sub('', str(text))
    # Chinese chars count as 2, English as 1
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

    def draw_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        exp = [r for r in self.records if not r["is_income"]]
        inc = [r for r in self.records if r["is_income"]]
        
        t_exp, t_inc = sum(r["money"] for r in exp), sum(r["money"] for r in inc)
        
        print("="*65)
        print(f"[T]Scale: {self.scale} | [L]Limits | [I]nput | [Y]Details | [Q]uit")
        print("="*65)
        print(f"{C_EXP}Total Expenses: ${t_exp:,.2f}{C_RESET}")
        print(f"{C_INC}Total Income:   ${t_inc:,.2f}{C_RESET}")
        
        # Fixed: Cap bar length to 20 to prevent overflow
        is_exc, ratio, rem = self.lm.check_limit(exp, inc)
        bar_len = min(20, int(ratio * 20))
        color = C_EXP if is_exc else C_BAR
        bar_str = f"[{'█' * bar_len}{' ' * (20-bar_len)}] {ratio*100:.0f}%"
        print(f"Monthly Limit: {color}{bar_str}{C_RESET} Remaining: ${rem:,.2f}")

    def show_details(self):
        exp = [r for r in self.records if not r["is_income"]]
        if not exp:
            print("\nNo expenditures found.")
            get_char(); return
            
        m_list = [r["money"] for r in exp]
        mean_v, std_v = statistics.mean(m_list), (statistics.stdev(m_list) if len(m_list)>1 else 0)
        max_v = max(m_list)

        print("\n" + pad_text("Date", 12) + "| " + pad_text("Category", 15) + "| " + pad_text("Money", 10) + "| " + pad_text("Alarm", 10) + "| Bar Chart")
        print("-" * 85)
        
        for r in exp:
            date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            is_ano = Statistic.is_anomaly(r["money"], mean_v, std_v)
            alarm = f"{C_ANO}ANOMALY{C_RESET}" if is_ano else "Normal"
            bar = f"{C_BAR}{Statistic.generate_barchart(r['money'], max_v)}{C_RESET}"
            
            print(f"{pad_text(date, 12)}| {pad_text(r['category'], 15)}| {pad_text(r['money'], 10)}| {pad_text(alarm, 10)}| {bar}")
        
        print(f"\n{C_INC}Predicted Next Month Budget: ${Statistic.predict_budget(self.records):,.2f}{C_RESET}")
        get_char()

    def run(self):
        while True:
            self.draw_dashboard()
            cmd = get_char()
            if cmd == 'Q': self.save(); break
            if cmd == 'T': 
                scales = ["Day", "Week", "Month", "Year", "All"]
                self.scale = scales[(scales.index(self.scale)+1)%5]
            if cmd == 'Y': self.show_details()
            if cmd == 'I':
                sub = input("\n[F]ile or [T]erminal? ").upper()
                if sub == 'F':
                    path = input("Enter path: ")
                    self.records.extend(Input.read_input(path, "txt"))
                else:
                    rec = Input.read_terminal()
                    if rec: self.records.append(rec)
                self.save()

if __name__ == "__main__":
    FinanceSystem().run()
