import os
import sys
import json
from Limit import LimitManager
import Input
import Statistic

# ANSI Color Codes [cite: 81, 82, 185-188]
C_INCOME = '\033[92m'  # Green
C_EXPENSE = '\033[91m' # Red
C_ANOMALY = '\033[93m' # Yellow
C_BAR = '\033[96m'     # Cyan
C_RESET = '\033[0m'

def get_char():
    """Cross-platform non-blocking keypress listener."""
    try:
        import msvcrt
        return msvcrt.getch().decode('utf-8').upper()
    except ImportError:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.upper()

def cjk_len(text):
    """CJK Alignment: Chinese=2, English=1 """
    return sum(2 if ord(c) > 127 else 1 for c in str(text))

def pad_text(text, width):
    """Pad string considering CJK character widths."""
    current_len = cjk_len(text)
    padding = width - current_len
    return str(text) + (" " * max(0, padding))

class FinanceSystem:
    def __init__(self):
        self.all_records = Input.read_input("data.json", "json")
        self.limit_mgr = LimitManager()
        self.current_time_scale = "Month"
        
    def save_data(self):
        """Data Persistence [cite: 84]"""
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.all_records, f, indent=4)

    def draw_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Split records [cite: 10, 104, 106]
        expenses = [r for r in self.all_records if not r.get("is_income")]
        income = [r for r in self.all_records if r.get("is_income")]
        
        total_exp = sum(r["amount"] for r in expenses)
        total_inc = sum(r["amount"] for r in income)
        
        print("="*60)
        print(f"[T]Time: {self.current_time_scale} | [C] Cat: All | [A] Range: All | [L]Limits | [I]nput [Q]uit") # [cite: 66, 152]
        print("="*60)
        print(f"{C_EXPENSE}Total Exp: ${total_exp:,.2f}{C_RESET}") # [cite: 68]
        print(f"{C_INCOME}Total Inc: ${total_inc:,.2f}{C_RESET}") # [cite: 69]
        print("Real-time Limit Progress:") # [cite: 70]
        
        # Dummy limit check for display
        self.limit_mgr.set_time_limit("m", 1000)
        is_exc, ratio, rem = self.limit_mgr.check_limit(expenses, income, "time")
        bar_len = int(ratio * 20)
        bar_str = f"[{'█' * bar_len}{' ' * (20-bar_len)}] {ratio*100:.0f}%"
        print(f"Total (M): {C_BAR}{bar_str}{C_RESET} Remaining: ${rem:,.2f}")
        
        print("\nPress [Y] for Details") # [cite: 78]

    def show_details(self):
        expenses = [r for r in self.all_records if not r.get("is_income")]
        if not expenses:
            print("No records found for current filters") # [cite: 190]
            get_char()
            return
            
        mean_val = statistics.mean([r["amount"] for r in expenses]) if expenses else 0
        std_dev = statistics.stdev([r["amount"] for r in expenses]) if len(expenses) > 1 else 0
        max_val = max((r["amount"] for r in expenses), default=0)

        print("\n" + "="*80)
        print(f"{pad_text('Time', 12)}| {pad_text('Category', 15)}| {pad_text('Amount', 10)}| {pad_text('Alarm', 10)}| Bar Chart")
        print("-" * 80)
        
        for r in expenses:
            date_str = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            amt_str = f"{r['amount']:.1f}"
            
            is_anom = Statistic.is_anomaly(r["amount"], mean_val, std_dev)
            alarm_str = f"{C_ANOMALY}ANOMALY{C_RESET}" if is_anom else "Normal" # [cite: 172]
            
            bar_chart = f"{C_BAR}{Statistic.generate_barchart(r['amount'], max_val)}{C_RESET}"
            
            # Using custom pad_text for CJK safety
            print(f"{pad_text(date_str, 12)}| {pad_text(r['category'], 15)}| {pad_text(amt_str, 10)}| {pad_text(is_anom and 'ANOMALY' or 'Normal', 10)}| {bar_chart}")
        
        get_char()

    def run(self):
        while True:
            self.draw_dashboard()
            choice = get_char()
            
            if choice == 'Q':
                self.save_data()
                break
            elif choice == 'T':
                # Cycle time logic [cite: 54]
                times = ["Day", "Week", "Month", "Year", "All"]
                idx = times.index(self.current_time_scale)
                self.current_time_scale = times[(idx + 1) % len(times)]
            elif choice == 'I': # [cite: 58]
                new_rec = Input.read_terminal()
                if new_rec:
                    self.all_records.append(new_rec)
                    self.save_data()
            elif choice == 'Y':
                self.show_details()

if __name__ == "__main__":
    app = FinanceSystem()
    app.run()
