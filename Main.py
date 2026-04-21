import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import math
from datetime import datetime
from Limit import LimitManager
import Input
import Statistic

class FinanceGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Budget Assistant GUI (Tkinter)")
        self.geometry("1000x700")
        self.configure(padx=10, pady=10)
        
        # State Data
        self.records = Input.read_input("data.json", "json")
        self.lm = LimitManager()
        self.target_date_str = tk.StringVar(value="")
        self.category_filter = tk.StringVar(value="All")
        self.range_min = tk.DoubleVar(value=0.0)
        self.range_max = tk.DoubleVar(value=0.0) 
        self.auto_suggest = tk.BooleanVar(value=True)

        # Style
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10, 'bold'))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Treeview', rowheight=25)
        
        # Main Notebook structure
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Setup Tabs
        self.frame_dash = ttk.Frame(self.notebook, padding=10)
        self.frame_records = ttk.Frame(self.notebook, padding=10)
        self.frame_input = ttk.Frame(self.notebook, padding=10)
        self.frame_limits = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.frame_dash, text="Dashboard")
        self.notebook.add(self.frame_records, text="Records & Details")
        self.notebook.add(self.frame_input, text="Input Data")
        self.notebook.add(self.frame_limits, text="Limits Config")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.build_dashboard()
        self.build_records()
        self.build_input()
        self.build_limits()
        
        # Intercept window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def save(self):
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4)

    def get_current_scale(self):
        """Auto-detects the scale based strictly on the Date input structure"""
        t_date = self.target_date_str.get().strip()
        if not t_date: 
            return "All", None
        
        parts = t_date.split('-')
        try:
            if len(parts) == 1 and parts[0].isdigit():
                return "Year", {"year": int(parts[0])}
            elif len(parts) == 2 and all(p.isdigit() for p in parts):
                return "Month", {"year": int(parts[0]), "month": int(parts[1])}
            elif len(parts) == 3 and all(p.isdigit() for p in parts):
                return "Day", {"year": int(parts[0]), "month": int(parts[1]), "day": int(parts[2])}
        except ValueError:
            pass
        return "All", None

    def get_filtered_records(self):
        filtered = []
        c_scale, target_dict = self.get_current_scale()
        c_cat = self.category_filter.get()
        rmin = self.range_min.get()
        rmax = self.range_max.get() if self.range_max.get() > 0 else float('inf')

        for r in self.records:
            if target_dict:
                if "year" in target_dict and r["year"] != target_dict["year"]: continue
                if "month" in target_dict and r["month"] != target_dict["month"]: continue
                if "day" in target_dict and r["day"] != target_dict["day"]: continue
            
            if c_cat != "All" and r["category"] != c_cat: continue
            if not (rmin <= r["money"] <= rmax): continue
                
            filtered.append(r)
        return filtered

    # ================= UI BUILDERS =================
    def build_dashboard(self):
        # Filters Header
        f_frame = ttk.LabelFrame(self.frame_dash, text="Global Filters", padding=10)
        f_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(f_frame, text="Target Date (YYYY / YYYY-MM / YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(f_frame, textvariable=self.target_date_str, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(f_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5)
        self.cat_cb = ttk.Combobox(f_frame, textvariable=self.category_filter, values=["All"], state="readonly", width=15)
        self.cat_cb.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(f_frame, text="Apply Filters", command=self.refresh_all).grid(row=0, column=4, padx=15)

        # Overview Stats
        stats_frame = ttk.Frame(self.frame_dash)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_exp = ttk.Label(stats_frame, text="Total Expenses: $0.00", font=('Segoe UI', 16, 'bold'), foreground="darkred")
        self.lbl_exp.pack(side=tk.LEFT, padx=20)
        
        self.lbl_inc = ttk.Label(stats_frame, text="Total Income: $0.00", font=('Segoe UI', 16, 'bold'), foreground="darkgreen")
        self.lbl_inc.pack(side=tk.LEFT, padx=20)

        # Limits Display
        limit_frame = ttk.LabelFrame(self.frame_dash, text="Real-Time Limit Progress", padding=10)
        limit_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_limit_info = ttk.Label(limit_frame, text="", font=('Segoe UI', 10))
        self.lbl_limit_info.pack(anchor="w")
        
        self.prog_limit = ttk.Progressbar(limit_frame, orient="horizontal", length=400, mode="determinate")
        self.prog_limit.pack(fill=tk.X, pady=5)

        # Predictions
        pred_frame = ttk.LabelFrame(self.frame_dash, text="Statistical Engine", padding=10)
        pred_frame.pack(fill=tk.X, pady=10)
        self.lbl_prediction = ttk.Label(pred_frame, text="Predicted Budget: N/A", font=('Segoe UI', 12))
        self.lbl_prediction.pack(anchor="w")

    def build_records(self):
        ctrl_frame = ttk.Frame(self.frame_records)
        ctrl_frame.pack(fill=tk.X, pady=5)
        ttk.Button(ctrl_frame, text="Edit Selected", command=self.edit_selected_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="Delete Selected", command=self.delete_selected_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="Toggle Anomaly Ignore", command=self.toggle_anomaly).pack(side=tk.LEFT, padx=5)
        
        self.tree = ttk.Treeview(self.frame_records, columns=("Idx", "Date", "Type", "Cat", "Money", "Desc", "Alarm", "Bar"), show='headings')
        self.tree.heading("Idx", text="Idx")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Cat", text="Category")
        self.tree.heading("Money", text="Money")
        self.tree.heading("Desc", text="Description")
        self.tree.heading("Alarm", text="Alarm Status")
        self.tree.heading("Bar", text="Relative Bar Chart")
        
        self.tree.column("Idx", width=40, anchor="center")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Type", width=70, anchor="center")
        self.tree.column("Cat", width=120)
        self.tree.column("Money", width=100, anchor="e")
        self.tree.column("Desc", width=200)
        self.tree.column("Alarm", width=100, anchor="center")
        self.tree.column("Bar", width=250)

        # Tags for colors
        self.tree.tag_configure('income', foreground='darkgreen')
        self.tree.tag_configure('expense', foreground='black')
        self.tree.tag_configure('anomaly', foreground='red', font=('Segoe UI', 9, 'bold'))

        vsb = ttk.Scrollbar(self.frame_records, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def build_input(self):
        f1 = ttk.LabelFrame(self.frame_input, text="Manual Entry", padding=15)
        f1.pack(fill=tk.X, pady=10)
        
        tk.Label(f1, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        self.e_date = ttk.Entry(f1)
        self.e_date.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(f1, text="Type:").grid(row=0, column=2, padx=5, pady=5)
        self.e_type = ttk.Combobox(f1, values=["Expense", "Income"], state="readonly", width=10)
        self.e_type.set("Expense")
        self.e_type.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(f1, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.e_cat = ttk.Entry(f1)
        self.e_cat.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(f1, text="Money:").grid(row=1, column=2, padx=5, pady=5)
        self.e_money = ttk.Entry(f1)
        self.e_money.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(f1, text="Desc:").grid(row=2, column=0, padx=5, pady=5)
        self.e_desc = ttk.Entry(f1, width=35)
        self.e_desc.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        
        ttk.Button(f1, text="Add Record", command=self.add_manual_record).grid(row=3, column=0, columnspan=4, pady=10)

        f2 = ttk.LabelFrame(self.frame_input, text="Batch Import", padding=15)
        f2.pack(fill=tk.X, pady=10)
        ttk.Button(f2, text="Select .txt File", command=self.import_file).pack()

    def build_limits(self):
        f = ttk.LabelFrame(self.frame_limits, text="Set Time Scale Limit", padding=10)
        f.pack(fill=tk.X, pady=10)
        
        tk.Label(f, text="Scale:").grid(row=0, column=0, padx=5)
        self.lim_scale = ttk.Combobox(f, values=["d (Daily)", "w (Weekly)", "m (Monthly)", "y (Yearly)"], state="readonly")
        self.lim_scale.set("m (Monthly)")
        self.lim_scale.grid(row=0, column=1, padx=5)
        
        tk.Label(f, text="Amount:").grid(row=0, column=2, padx=5)
        self.lim_amt = ttk.Entry(f)
        self.lim_amt.grid(row=0, column=3, padx=5)
        
        ttk.Button(f, text="Set Time Limit", command=self.set_time_limit).grid(row=0, column=4, padx=10)

        c = ttk.LabelFrame(self.frame_limits, text="Set Category Limit", padding=10)
        c.pack(fill=tk.X, pady=10)
        
        tk.Label(c, text="Category:").grid(row=0, column=0, padx=5)
        self.lim_cat = ttk.Entry(c)
        self.lim_cat.grid(row=0, column=1, padx=5)
        
        tk.Label(c, text="Amount:").grid(row=0, column=2, padx=5)
        self.lim_cat_amt = ttk.Entry(c)
        self.lim_cat_amt.grid(row=0, column=3, padx=5)
        
        ttk.Button(c, text="Set Cat Limit", command=self.set_cat_limit).grid(row=0, column=4, padx=10)

        a = ttk.Frame(self.frame_limits, padding=10)
        a.pack(fill=tk.X)
        ttk.Checkbutton(a, text="Enable Auto-Suggested Limits (Machine Learning)", variable=self.auto_suggest, command=self.refresh_all).pack(anchor="w")

    # ================= LOGIC & REFRESH =================
    def on_tab_change(self, event):
        self.refresh_all()

    def refresh_all(self):
        filtered = self.get_filtered_records()
        exp = [r for r in filtered if not r.get("is_income", False)]
        inc = [r for r in filtered if r.get("is_income", False)]
        
        t_exp = sum(r["money"] for r in exp)
        t_inc = sum(r["money"] for r in inc)

        # Update categories list in combobox
        cats = ["All"] + sorted(list(set(r["category"] for r in self.records)))
        self.cat_cb['values'] = cats

        # Dashboard refresh
        self.lbl_exp.config(text=f"Total Expenses: ${t_exp:,.2f}")
        self.lbl_inc.config(text=f"Total Income: ${t_inc:,.2f}")

        c_scale, _ = self.get_current_scale()
        is_exc, ratio, rem, limit_name, limit_val = self.lm.check_limit(exp, c_scale, self.category_filter.get())
        
        if c_scale == "All" and limit_val <= 1e-9:
            self.lbl_limit_info.config(text="Limit: N/A in 'All' Time Scale. Enter a Date to view limits.")
            self.prog_limit['value'] = 0
        elif limit_val <= 1e-9:
            if self.auto_suggest.get():
                scale_str, target_days = Statistic.determine_scale(exp, c_scale)
                sug_limit = Statistic.predict_budget(exp, target_days)
                if sug_limit > 1e-9:
                    r = t_exp / sug_limit
                    self.lbl_limit_info.config(text=f"Auto-Suggested Limit ({scale_str}): ${sug_limit:,.2f} | Usage: {r*100:.1f}%")
                    self.prog_limit['value'] = min(100, r * 100)
                else:
                    self.lbl_limit_info.config(text="Auto-Suggest: Need more data to predict limit.")
                    self.prog_limit['value'] = 0
            else:
                self.lbl_limit_info.config(text="Limit: Not Set")
                self.prog_limit['value'] = 0
        else:
            self.lbl_limit_info.config(text=f"Limit ({limit_name}): ${limit_val:,.2f} | Rem: ${rem:,.2f} | Usage: {ratio*100:.1f}%")
            self.prog_limit['value'] = min(100, ratio * 100)

        # Predict Budget
        if c_scale != "All":
            scale_str, target_days = Statistic.determine_scale(exp, c_scale)
            pred_val = Statistic.predict_budget(exp, target_days)
            if pred_val > 1e-9:
                self.lbl_prediction.config(text=f"Predicted {scale_str} Budget: ${pred_val:,.2f}")
            else:
                self.lbl_prediction.config(text=f"Predicted {scale_str} Budget: Awaiting more data")
        else:
            self.lbl_prediction.config(text="Predicted Budget: N/A in 'All' scale.")

        # Records Table Refresh
        for row in self.tree.get_children():
            self.tree.delete(row)

        all_records = inc + exp
        log_stats, raw_stats = Statistic.get_both_stats(all_records)
        m_list = [r["money"] for r in all_records if r["money"] > 0]
        max_v = max(m_list) if m_list else 0

        for i, r in enumerate(all_records):
            date_str = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            t_str = "Income" if r.get("is_income", False) else "Expense"
            bar = Statistic.generate_barchart(r['money'], max_v)
            
            alarm = "Normal"
            tag = 'income' if r.get("is_income", False) else 'expense'
            
            if not r.get("is_income", False):
                if r.get("ignore_anomaly", False):
                    alarm = "Ignored"
                elif Statistic.is_hybrid_anomaly(r["money"], log_stats, raw_stats, ignore_flag=False):
                    alarm = "ANOMALY"
                    tag = 'anomaly'

            self.tree.insert("", tk.END, iid=str(self.records.index(r)), values=(
                i+1, date_str, t_str, r["category"], f"${r['money']:.2f}", r.get("description", ""), alarm, bar
            ), tags=(tag,))

    # ================= ACTIONS =================
    def add_manual_record(self):
        d = self.e_date.get()
        t = self.e_type.get()
        c = self.e_cat.get()
        m = self.e_money.get()
        desc = self.e_desc.get()
        
        t_char = 'I' if t == "Income" else 'E'
        raw = f"{t_char} {d} {c} {m} {desc}"
        
        parsed = Input.parse_staged_line(raw)
        if parsed["valid"]:
            self.records.append(parsed["record"])
            self.records.sort(key=lambda x: (x["year"], x["month"], x["day"]))
            self.save()
            messagebox.showinfo("Success", "Record added securely.")
            self.e_date.delete(0, tk.END)
            self.e_cat.delete(0, tk.END)
            self.e_money.delete(0, tk.END)
            self.e_desc.delete(0, tk.END)
            self.refresh_all()
        else:
            messagebox.showerror("Validation Error", parsed["error"])

    def import_file(self):
        fpath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if fpath:
            recs = Input.read_input(fpath, "txt")
            if recs:
                self.records.extend(recs)
                self.records.sort(key=lambda x: (x["year"], x["month"], x["day"]))
                self.save()
                messagebox.showinfo("Success", f"Imported {len(recs)} records.")
                self.refresh_all()
            else:
                messagebox.showwarning("Warning", "No valid records found in file.")

    def edit_selected_record(self):
        sel = self.tree.selection()
        if not sel: 
            messagebox.showwarning("Warning", "Please select a record to edit first.")
            return
            
        idx = int(sel[0]) # IID tracks the global index in self.records
        r = self.records[idx]
        
        edit_win = tk.Toplevel(self)
        edit_win.title("Edit Record")
        edit_win.geometry("350x260")
        edit_win.grab_set() # Block main window interactions
        
        ttk.Label(edit_win, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        e_date = ttk.Entry(edit_win)
        e_date.insert(0, f"{r['year']}-{r['month']:02d}-{r['day']:02d}")
        e_date.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(edit_win, text="Type:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        e_type = ttk.Combobox(edit_win, values=["Expense", "Income"], state="readonly")
        e_type.set("Income" if r.get("is_income") else "Expense")
        e_type.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(edit_win, text="Category:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        e_cat = ttk.Entry(edit_win)
        e_cat.insert(0, r["category"])
        e_cat.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(edit_win, text="Money:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        e_money = ttk.Entry(edit_win)
        e_money.insert(0, str(r["money"]))
        e_money.grid(row=3, column=1, padx=10, pady=10)
        
        ttk.Label(edit_win, text="Description:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        e_desc = ttk.Entry(edit_win)
        e_desc.insert(0, r.get("description", ""))
        e_desc.grid(row=4, column=1, padx=10, pady=10)
        
        def save_edit():
            raw = f"{'I' if e_type.get() == 'Income' else 'E'} {e_date.get()} {e_cat.get()} {e_money.get()} {e_desc.get()}"
            parsed = Input.parse_staged_line(raw)
            if parsed["valid"]:
                new_rec = parsed["record"]
                # Retain the anomaly bypass status if it remained an expense
                if not new_rec["is_income"]:
                    new_rec["ignore_anomaly"] = r.get("ignore_anomaly", False)
                
                self.records[idx] = new_rec
                self.records.sort(key=lambda x: (x["year"], x["month"], x["day"]))
                self.save()
                self.refresh_all()
                edit_win.destroy()
                messagebox.showinfo("Success", "Record updated successfully.")
            else:
                messagebox.showerror("Error", parsed["error"])
                
        ttk.Button(edit_win, text="Save Changes", command=save_edit).grid(row=5, column=0, columnspan=2, pady=15)

    def set_time_limit(self):
        val = self.lim_scale.get()[0] # gets 'd', 'w', 'm', 'y'
        try:
            amt = float(self.lim_amt.get())
            self.lm.set_limit("time", val, amt)
            messagebox.showinfo("Success", f"Time limit set for '{val}' to ${amt}")
            self.refresh_all()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")

    def set_cat_limit(self):
        cat = self.lim_cat.get().strip()
        try:
            amt = float(self.lim_cat_amt.get())
            if cat:
                self.lm.set_limit("cat", cat, amt)
                messagebox.showinfo("Success", f"Category limit set for '{cat}' to ${amt}")
                self.refresh_all()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")

    def delete_selected_record(self):
        sel = self.tree.selection()
        if not sel: return
        idx = int(sel[0]) # IID is the actual index in self.records
        if messagebox.askyesno("Confirm", "Delete this record?"):
            self.records.pop(idx)
            self.save()
            self.refresh_all()

    def toggle_anomaly(self):
        sel = self.tree.selection()
        if not sel: return
        idx = int(sel[0])
        r = self.records[idx]
        if not r.get("is_income", False):
            r["ignore_anomaly"] = not r.get("ignore_anomaly", False)
            self.save()
            self.refresh_all()
        else:
            messagebox.showinfo("Info", "Income records don't trigger anomaly checks.")

    def on_close(self):
        self.save()
        self.destroy()

if __name__ == "__main__":
    app = FinanceGUI()
    app.mainloop()
