import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import math
import statistics
from datetime import datetime

# Import existing modules
from Limit import LimitManager
import Input
import Statistic

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Budget & Spending Assistant - COMP1110")
        self.root.geometry("1050x750")
        self.root.minsize(900, 600)

        # Initialize core data and logic modules
        self.records = Input.read_input("data.json", "json")
        self.lm = LimitManager()
        self.auto_suggest = True
        
        # UI State Variables
        self.scale_var = tk.StringVar(value="All")
        self.target_date_var = tk.StringVar(value="")
        self.cat_var = tk.StringVar(value="All")
        
        self.setup_ui()
        self.update_categories()
        self.refresh_dashboard()

    def setup_ui(self):
        # Apply a simple theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- TOP FRAME: Filters ---
        top_frame = ttk.LabelFrame(self.root, text=" Filter Settings ", padding=10)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text="Time Scale:").pack(side="left", padx=(0, 5))
        scale_cb = ttk.Combobox(top_frame, textvariable=self.scale_var, values=["All", "Year", "Month", "Day"], state="readonly", width=8)
        scale_cb.pack(side="left", padx=5)
        
        ttk.Label(top_frame, text="Target Date (YYYY/YYYY-MM/YYYY-MM-DD):").pack(side="left", padx=(15, 5))
        ttk.Entry(top_frame, textvariable=self.target_date_var, width=15).pack(side="left", padx=5)
        
        ttk.Label(top_frame, text="Category:").pack(side="left", padx=(15, 5))
        self.cat_cb = ttk.Combobox(top_frame, textvariable=self.cat_var, state="readonly", width=15)
        self.cat_cb.pack(side="left", padx=5)
        
        ttk.Button(top_frame, text="Apply Filters", command=self.refresh_dashboard).pack(side="left", padx=20)

        # --- MIDDLE FRAME: Dashboard & Limits ---
        self.dash_frame = ttk.LabelFrame(self.root, text=" Real-time Dashboard ", padding=10)
        self.dash_frame.pack(fill="x", padx=10, pady=5)
        
        # Summary Labels
        info_frame = ttk.Frame(self.dash_frame)
        info_frame.pack(fill="x")
        
        self.lbl_exp = ttk.Label(info_frame, text="Total Exp: $0.00", font=("Arial", 12, "bold"), foreground="red")
        self.lbl_exp.pack(side="left", expand=True)
        
        self.lbl_inc = ttk.Label(info_frame, text="Total Inc: $0.00", font=("Arial", 12, "bold"), foreground="green")
        self.lbl_inc.pack(side="left", expand=True)
        
        self.lbl_pred = ttk.Label(info_frame, text="Predicted Budget: N/A", font=("Arial", 12, "bold"), foreground="blue")
        self.lbl_pred.pack(side="left", expand=True)

        # Progress Bar section
        prog_frame = ttk.Frame(self.dash_frame)
        prog_frame.pack(fill="x", pady=(15, 5))
        
        self.lbl_limit_status = ttk.Label(prog_frame, text="Limit Status: Not Set", font=("Arial", 10))
        self.lbl_limit_status.pack(anchor="w")
        
        self.progress = ttk.Progressbar(prog_frame, length=100, mode='determinate')
        self.progress.pack(fill="x", pady=5)

        # --- BOTTOM FRAME: Data Table (Treeview) ---
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("date", "category", "money", "type", "alarm", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("money", text="Amount ($)")
        self.tree.heading("type", text="Type")
        self.tree.heading("alarm", text="Status / Alarm")
        self.tree.heading("description", text="Description")
        
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("money", width=100, anchor="e")
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("alarm", width=120, anchor="center")
        self.tree.column("description", width=300, anchor="w")
        
        # Tag configuration for colors
        self.tree.tag_configure("anomaly", background="#ffcccc", foreground="#990000")
        self.tree.tag_configure("income", background="#e6ffe6", foreground="#006600")
        self.tree.tag_configure("ignored", background="#f0f0f0", foreground="#888888")

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # --- ACTION FRAME: Buttons ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Import Text File", command=self.import_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Add Record Manually", command=self.add_record).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Set Budget Limit", command=self.set_limit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Toggle Auto-Suggest", command=self.toggle_auto).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save & Exit", command=self.exit_app).pack(side="right", padx=5)

    def update_categories(self):
        """Update the category dropdown list based on existing records"""
        cats = list(set(r["category"] for r in self.records))
        cats.sort()
        self.cat_cb['values'] = ["All"] + cats

    def get_filtered_records(self):
        """Filter records based on UI inputs"""
        filtered = []
        scale = self.scale_var.get()
        td_str = self.target_date_var.get().strip()
        cat = self.cat_var.get()
        
        target_y, target_m, target_d = None, None, None
        
        if scale != "All" and td_str:
            parts = td_str.split('-')
            try:
                if scale == "Year" and len(parts) >= 1: target_y = int(parts[0])
                elif scale == "Month" and len(parts) >= 2: target_y, target_m = int(parts[0]), int(parts[1])
                elif scale == "Day" and len(parts) >= 3: target_y, target_m, target_d = int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                pass # Invalid date format typed, ignore filter
                
        for r in self.records:
            if scale == "Year" and target_y:
                if r["year"] != target_y: continue
            elif scale == "Month" and target_y and target_m:
                if r["year"] != target_y or r["month"] != target_m: continue
            elif scale == "Day" and target_y and target_m and target_d:
                if r["year"] != target_y or r["month"] != target_m or r["day"] != target_d: continue
            
            if cat != "All" and r["category"] != cat:
                continue
                
            filtered.append(r)
        return filtered

    def refresh_dashboard(self):
        """Update all UI elements based on current data and filters"""
        filtered_recs = self.get_filtered_records()
        
        exp = [r for r in filtered_recs if not r.get("is_income", False)]
        inc = [r for r in filtered_recs if r.get("is_income", False)]
        
        t_exp = sum(r["money"] for r in exp)
        t_inc = sum(r["money"] for r in inc)
        
        # 1. Update Summary Text
        self.lbl_exp.config(text=f"Total Exp: ${t_exp:,.2f}")
        self.lbl_inc.config(text=f"Total Inc: ${t_inc:,.2f}")
        
        # 2. Update Prediction
        scale_val = self.scale_var.get()
        if scale_val != "All":
            scale_str, target_days = Statistic.determine_scale(exp, scale_val)
            pred_val = Statistic.predict_budget(exp, target_days)
            if pred_val > 1e-9:
                self.lbl_pred.config(text=f"Predicted {scale_str} Budget: ${pred_val:,.0f}")
            else:
                self.lbl_pred.config(text=f"Predicted {scale_str} Budget: Need more data")
        else:
            self.lbl_pred.config(text="Predicted Budget: N/A in 'All'")

        # 3. Update Progress Bar & Limits
        cat_val = self.cat_var.get()
        is_exc, ratio, rem, limit_name, limit_val = self.lm.check_limit(exp, scale_val, cat_val)
        
        self.progress['value'] = min(100, ratio * 100)
        
        if scale_val == "All" and cat_val == "All":
             self.lbl_limit_status.config(text="Limit Status: Please select a Time Scale or Category to view limits.")
             self.progress['value'] = 0
        elif limit_val > 1e-9:
            status_text = f"Limit ({limit_name}): {ratio*100:.1f}% used | ${t_exp:,.2f} / ${limit_val:,.2f} | Remaining: ${rem:,.2f}"
            if is_exc:
                status_text = "[EXCEEDED] " + status_text
                self.lbl_limit_status.config(text=status_text, foreground="red")
            else:
                self.lbl_limit_status.config(text=status_text, foreground="black")
        elif self.auto_suggest and scale_val != "All":
            # Auto suggest logic
            scale_str, target_days = Statistic.determine_scale(exp, scale_val)
            sug_limit = Statistic.predict_budget(exp, target_days)
            if sug_limit > 1e-9:
                sug_ratio = t_exp / sug_limit
                self.progress['value'] = min(100, sug_ratio * 100)
                self.lbl_limit_status.config(text=f"Limit [Auto-Suggested]: {sug_ratio*100:.1f}% used | ${t_exp:,.2f} / ${sug_limit:,.0f}", foreground="purple")
            else:
                self.lbl_limit_status.config(text="Limit Status: Not Set (Log expenses to unlock Auto-Suggest)", foreground="black")
                self.progress['value'] = 0
        else:
            self.lbl_limit_status.config(text="Limit Status: Not Set", foreground="black")
            self.progress['value'] = 0

        # 4. Update Data Table (Treeview)
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        m_list = [r["money"] for r in exp if r["money"] > 0]
        log_m_list = [math.log(m) for m in m_list]
        log_mean_v = statistics.mean(log_m_list) if log_m_list else 0.0
        log_std_v = statistics.stdev(log_m_list) if len(log_m_list) > 1 else 0.0

        for r in filtered_recs:
            date_str = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            r_type = "Income" if r.get("is_income", False) else "Expense"
            
            alarm_status = "Normal"
            tag = ""
            
            if r_type == "Income":
                tag = "income"
                alarm_status = "-"
            elif r.get("ignore_anomaly", False):
                tag = "ignored"
                alarm_status = "Ignored"
            else:
                is_ano = Statistic.is_anomaly(r["money"], log_mean_v, log_std_v, False)
                if is_ano:
                    tag = "anomaly"
                    alarm_status = "ANOMALY"

            self.tree.insert("", "end", values=(
                date_str, 
                r["category"], 
                f"{r['money']:.2f}", 
                r_type, 
                alarm_status, 
                r.get("description", "")
            ), tags=(tag,))

    def toggle_auto(self):
        self.auto_suggest = not self.auto_suggest
        state = "ON" if self.auto_suggest else "OFF"
        messagebox.showinfo("Auto-Suggest", f"Auto-Suggested limits are now {state}.")
        self.refresh_dashboard()

    def import_file(self):
        filepath = filedialog.askopenfilename(title="Select Text Data File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            new_records = Input.read_input(filepath, "txt")
            if new_records:
                self.records.extend(new_records)
                self.save_data()
                self.update_categories()
                self.refresh_dashboard()
                messagebox.showinfo("Success", f"Imported {len(new_records)} records successfully.")
            else:
                messagebox.showwarning("Warning", "No valid records found in file.")

    def add_record(self):
        # Create a custom popup window for manual input
        win = tk.Toplevel(self.root)
        win.title("Add Record")
        win.geometry("350x300")
        win.grab_set()

        ttk.Label(win, text="Type:").pack(pady=(10, 0))
        type_var = tk.StringVar(value="E")
        ttk.Radiobutton(win, text="Expense", variable=type_var, value="E").pack()
        ttk.Radiobutton(win, text="Income", variable=type_var, value="I").pack()

        ttk.Label(win, text="Date (YYYY-MM-DD):").pack(pady=(5, 0))
        ent_date = ttk.Entry(win)
        ent_date.pack()

        ttk.Label(win, text="Category:").pack(pady=(5, 0))
        ent_cat = ttk.Entry(win)
        ent_cat.pack()

        ttk.Label(win, text="Amount ($):").pack(pady=(5, 0))
        ent_money = ttk.Entry(win)
        ent_money.pack()

        ttk.Label(win, text="Description:").pack(pady=(5, 0))
        ent_desc = ttk.Entry(win)
        ent_desc.pack()

        def submit():
            date_val = ent_date.get().strip()
            cat_val = ent_cat.get().strip()
            money_val = ent_money.get().strip()
            desc_val = ent_desc.get().strip()

            date_parts = Input.validate_date(date_val)
            if not date_parts:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
                return
            
            try:
                money_float = float(money_val)
                if money_float <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Amount must be a positive number.")
                return
                
            if not cat_val:
                messagebox.showerror("Error", "Category cannot be empty.")
                return

            new_rec = {
                "year": date_parts[0], "month": date_parts[1], "day": date_parts[2],
                "category": cat_val, 
                "money": money_float,
                "description": desc_val,
                "is_income": (type_var.get() == "I"),
                "ignore_anomaly": False
            }
            
            self.records.append(new_rec)
            self.save_data()
            self.update_categories()
            self.refresh_dashboard()
            win.destroy()
            messagebox.showinfo("Success", "Record added successfully.")

        ttk.Button(win, text="Submit", command=submit).pack(pady=15)

    def set_limit(self):
        win = tk.Toplevel(self.root)
        win.title("Set Budget Limit")
        win.geometry("300x250")
        win.grab_set()

        ttk.Label(win, text="Limit Type:").pack(pady=(10, 0))
        l_type = tk.StringVar(value="time")
        ttk.Radiobutton(win, text="Time-based", variable=l_type, value="time").pack()
        ttk.Radiobutton(win, text="Category-based", variable=l_type, value="cat").pack()

        ttk.Label(win, text="Key (e.g. 'm' for month, or 'Food'):").pack(pady=(10, 0))
        ent_key = ttk.Entry(win)
        ent_key.pack()
        ttk.Label(win, text="Time keys: d(Day), w(Week), m(Month), y(Year)", font=("Arial", 8)).pack()

        ttk.Label(win, text="Limit Amount ($):").pack(pady=(10, 0))
        ent_amt = ttk.Entry(win)
        ent_amt.pack()

        def submit_limit():
            try:
                amt = float(ent_amt.get().strip())
                key = ent_key.get().strip()
                if not key: raise ValueError
                self.lm.set_limit(l_type.get(), key, amt)
                self.refresh_dashboard()
                win.destroy()
                messagebox.showinfo("Success", "Limit updated successfully.")
            except ValueError:
                messagebox.showerror("Error", "Invalid key or amount.")

        ttk.Button(win, text="Set Limit", command=submit_limit).pack(pady=15)

    def save_data(self):
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4)

    def exit_app(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
