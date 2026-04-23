import os
import json
import math
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

import Input
import Limit
import Statistic

# --- MODERN WEB-INSPIRED THEME ---
C_BG = '#0f172a'       # Deep Slate Background
C_PANEL = '#1e293b'    # Card/Panel Background
C_FG = '#f8fafc'       # Main Text
C_MUTED = '#94a3b8'    # Muted/Subtext
C_INC = '#10b981'      # Emerald Green
C_EXP = '#ef4444'      # Rose Red
C_ANO = '#f59e0b'      # Amber (Anomaly)
C_BAR = '#3b82f6'      # Blue (Charts/Bars)
C_PUR = '#8b5cf6'      # Purple (Predictions)
C_HEAD = '#0f172a'     # Table Header

PIE_COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']

def create_round_rectangle(canvas, x1, y1, x2, y2, radius=15, **kwargs):
    points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class RangeSliderDialog(tk.Toplevel):
    def __init__(self, parent, current_min, current_max, absolute_max):
        super().__init__(parent)
        self.title("Set Amount Range")
        self.geometry("450x220")
        self.configure(bg=C_PANEL)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.abs_max = max(100.0, absolute_max)
        
        tk.Label(self, text="Adjust Amount Range", bg=C_PANEL, fg=C_FG, font=("Segoe UI", 12, "bold")).pack(pady=10)
        frame = tk.Frame(self, bg=C_PANEL)
        frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        tk.Label(frame, text="Minimum:", bg=C_PANEL, fg=C_FG).grid(row=0, column=0, sticky='w')
        self.var_min = tk.DoubleVar(value=current_min)
        self.scl_min = ttk.Scale(frame, from_=0, to=self.abs_max, variable=self.var_min, command=self._on_slider_min)
        self.scl_min.grid(row=0, column=1, sticky='ew', padx=10, pady=10)
        
        self.var_min_str = tk.StringVar(value=f"{current_min:.0f}")
        self.entry_min = tk.Entry(frame, textvariable=self.var_min_str, width=10, bg=C_HEAD, fg=C_FG, insertbackground=C_FG, justify='center')
        self.entry_min.grid(row=0, column=2)
        self.entry_min.bind('<KeyRelease>', self._on_entry_min)
        
        cur_max_val = self.abs_max if current_max == float('inf') else current_max
        tk.Label(frame, text="Maximum:", bg=C_PANEL, fg=C_FG).grid(row=1, column=0, sticky='w')
        self.var_max = tk.DoubleVar(value=cur_max_val)
        self.scl_max = ttk.Scale(frame, from_=0, to=self.abs_max, variable=self.var_max, command=self._on_slider_max)
        self.scl_max.grid(row=1, column=1, sticky='ew', padx=10, pady=10)
        
        self.var_max_str = tk.StringVar(value="INF" if current_max == float('inf') else f"{current_max:.0f}")
        self.entry_max = tk.Entry(frame, textvariable=self.var_max_str, width=10, bg=C_HEAD, fg=C_FG, insertbackground=C_FG, justify='center')
        self.entry_max.grid(row=1, column=2)
        self.entry_max.bind('<KeyRelease>', self._on_entry_max)
        
        frame.columnconfigure(1, weight=1)
        btn_frame = tk.Frame(self, bg=C_PANEL)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Save", command=self._save, bg=C_INC, fg='black', relief=tk.FLAT, width=10, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Set Max to INF", command=self._set_inf, bg=C_BAR, fg='black', relief=tk.FLAT, width=15, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)

    def _on_slider_min(self, *args):
        v = self.var_min.get()
        if v > self.var_max.get() and self.var_max_str.get() != "INF":
            self.var_max.set(v)
            self.var_max_str.set(f"{v:.0f}")
        self.var_min_str.set(f"{v:.0f}")

    def _on_slider_max(self, *args):
        v = self.var_max.get()
        if v < self.var_min.get():
            self.var_min.set(v)
            self.var_min_str.set(f"{v:.0f}")
        if self.var_max_str.get() != "INF":
            self.var_max_str.set(f"{v:.0f}")

    def _on_entry_min(self, event):
        try:
            val = float(self.var_min_str.get())
            if 0 <= val <= self.abs_max:
                self.var_min.set(val)
                if val > self.var_max.get() and self.var_max_str.get() != "INF":
                    self.var_max.set(val)
                    self.var_max_str.set(f"{val:.0f}")
        except ValueError: pass

    def _on_entry_max(self, event):
        if self.var_max_str.get().upper() == "INF": return
        try:
            val = float(self.var_max_str.get())
            if 0 <= val <= self.abs_max:
                self.var_max.set(val)
                if val < self.var_min.get():
                    self.var_min.set(val)
                    self.var_min_str.set(f"{val:.0f}")
        except ValueError: pass

    def _set_inf(self):
        self.result = (self.var_min.get(), float('inf'))
        self.destroy()

    def _save(self):
        try:
            m_val = float('inf') if self.var_max_str.get().upper() == "INF" else float(self.var_max_str.get())
            self.result = (float(self.var_min_str.get()), m_val)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers entered.", parent=self)

class VirtualTable(tk.Frame):
    def __init__(self, parent, headers, widths, sort_callback, edit_callback):
        super().__init__(parent, bg=C_PANEL)
        self.headers = headers
        self.widths = widths
        self.sort_callback = sort_callback
        self.edit_callback = edit_callback
        self.row_height = 40 
        self.data = []
        self.is_income = False
        self.max_money = 0
        
        self.head_canvas = tk.Canvas(self, height=40, bg=C_HEAD, highlightthickness=0)
        self.head_canvas.pack(fill=tk.X)
        self.head_canvas.bind("<Button-1>", self._on_header_click)
        
        self.body_canvas = tk.Canvas(self, bg=C_PANEL, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.body_canvas.yview)
        self.body_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.body_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.body_canvas.bind("<Double-Button-1>", self._on_body_dblclick)
        self.body_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.body_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _get_x_coords(self):
        x = 15
        coords = []
        for w in self.widths:
            coords.append(x)
            x += w
        return coords

    def _on_header_click(self, event):
        coords = self._get_x_coords()
        for i, x in enumerate(coords):
            if x <= event.x <= (x + self.widths[i]):
                self.sort_callback(self.headers[i])
                break

    def _on_body_dblclick(self, event):
        canvas_y = self.body_canvas.canvasy(event.y)
        row_idx = int(canvas_y // self.row_height)
        if 0 <= row_idx < len(self.data):
            self.edit_callback(self.data[row_idx]["record_ref"])

    def update_data(self, processed_data, is_income, max_money):
        self.data = processed_data
        self.is_income = is_income
        self.max_money = max_money
        self._redraw()

    def _redraw(self):
        self.head_canvas.delete("all")
        self.body_canvas.delete("all")
        coords = self._get_x_coords()
        
        for i, h in enumerate(self.headers):
            self.head_canvas.create_text(coords[i], 20, text=h.upper(), fill=C_MUTED, font=("Segoe UI", 11, "bold"), anchor="w")
            
        total_height = len(self.data) * self.row_height
        self.body_canvas.configure(scrollregion=(0, 0, sum(self.widths)+20, total_height))
        
        has_chart = "Bar Chart" in self.headers
        has_status = "Status" in self.headers
        
        for r_idx, row in enumerate(self.data):
            y_top = r_idx * self.row_height
            y_mid = y_top + (self.row_height // 2)
            
            is_ano = row.get("is_anomaly") and not row["record_ref"].get("ignore_anomaly")
            bg_color = C_PANEL if r_idx % 2 == 0 else '#233044'
            if is_ano: bg_color = '#3b2f19'
                
            self.body_canvas.create_rectangle(0, y_top, sum(self.widths)+20, y_top+self.row_height, fill=bg_color, outline="")
            self.body_canvas.create_line(0, y_top+self.row_height, sum(self.widths)+20, y_top+self.row_height, fill='#334155')
            
            fg = C_INC if self.is_income else (C_FG if not is_ano else C_ANO)
            
            limit = len(self.headers) - 1 if has_chart else len(self.headers)
            for c_idx in range(limit):
                val = row["values"][c_idx]
                text_col = C_FG
                
                if "Amount" in self.headers and c_idx == self.headers.index("Amount"): text_col = fg
                elif has_status and c_idx == self.headers.index("Status") and is_ano: text_col = C_ANO
                elif has_status and c_idx == self.headers.index("Status") and self.is_income: text_col = C_INC
                
                self.body_canvas.create_text(coords[c_idx], y_mid, text=str(val), fill=text_col, font=("Segoe UI", 12), anchor="w")
                
            if has_chart:
                money = row["record_ref"]["money"]
                c_idx = len(self.headers) - 1
                bar_x = coords[c_idx]
                bar_w = self.widths[c_idx] - 20
                
                if self.max_money > 1e-9 and money > 1e-9:
                    length = (math.log(money + 1) / math.log(self.max_money + 1)) * bar_w
                    length = max(4, length)
                    create_round_rectangle(self.body_canvas, bar_x, y_mid-5, bar_x+length, y_mid+5, radius=4, fill=C_BAR, outline="")

class CollapsibleSection(tk.Frame):
    def __init__(self, parent, title, color, headers, widths, sort_cb, edit_cb):
        super().__init__(parent, bg=C_BG)
        self.head_frame = tk.Frame(self, bg=C_PANEL, pady=8, padx=15)
        self.head_frame.pack(fill=tk.X, pady=(0,2))
        self.lbl_title = tk.Label(self.head_frame, text=title, bg=C_PANEL, fg=color, font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(side=tk.LEFT)
        self.table = VirtualTable(self, headers, widths, sort_cb, edit_cb)
        self.table.pack(fill=tk.BOTH, expand=True)

class FinanceSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 8 Project - PFMS Dashboard")
        self.root.geometry("1300x800")
        self.root.configure(bg=C_BG)
        
        self.records = Input.read_input("data.json", "json")
        self.lm = Limit.LimitManager()
        
        self.scale = "All"
        self.target_date = None
        self.range_filter = (0.0, float('inf'))
        self.auto_suggest = True
        self.sort_mode = "time"
        self.sort_desc = False
        
        all_cats = set(r["category"] for r in self.records)
        self.active_categories = all_cats.copy()
        
        self.update_full_tables_cb = None
        
        self._setup_styles()
        self._build_ui()
        self._bind_keys()
        self.update_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), background=C_PANEL, foreground=C_FG, borderwidth=0)
        style.configure("TNotebook", background=C_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=C_PANEL, foreground=C_FG, font=("Segoe UI", 11, "bold"), padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", C_BAR)])

    def _build_ui(self):
        header_frame = tk.Frame(self.root, bg=C_BG, pady=15, padx=20)
        header_frame.pack(fill=tk.X)
        
        title_frame = tk.Frame(header_frame, bg=C_BG)
        title_frame.pack(side=tk.LEFT)
        tk.Label(title_frame, text="Group 8 Project", bg=C_BG, fg=C_BAR, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        self.lbl_filters = tk.Label(title_frame, bg=C_BG, fg=C_MUTED, font=("Segoe UI", 10), anchor="w")
        self.lbl_filters.pack(anchor="w")
        
        ctrl_frame = tk.Frame(header_frame, bg=C_BG)
        ctrl_frame.pack(side=tk.RIGHT, pady=10)
        
        def btn(text, cmd):
            b = tk.Button(ctrl_frame, text=text, command=cmd, bg=C_PANEL, fg='black', relief=tk.FLAT, padx=8, pady=5, font=("Segoe UI", 10, "bold"))
            b.pack(side=tk.LEFT, padx=3)
            
        btn("Time", self._handle_time_menu)
        btn("Categories", self._handle_category)
        btn("Range", self._handle_range)
        btn("Limits", self._handle_limit_menu)
        btn("Sort", self._handle_sort_menu)
        btn("Input", self._handle_input)
        btn("Details & Graphs", self._show_details_window)

        self.card_canvas = tk.Canvas(self.root, height=130, bg=C_BG, highlightthickness=0)
        self.card_canvas.pack(fill=tk.X, padx=15, pady=5)

        self.tables_container = tk.Frame(self.root, bg=C_BG)
        self.tables_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        s_headers = ["Date", "Category", "Amount"]
        s_widths = [180, 250, 180]
        
        self.inc_frame = tk.Frame(self.tables_container, bg=C_BG)
        self.inc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.inc_section = CollapsibleSection(self.inc_frame, "Recent Income (Simplified)", C_INC, s_headers, s_widths, self._handle_sort, self.edit_record)
        self.inc_section.pack(fill=tk.BOTH, expand=True)
        
        self.exp_frame = tk.Frame(self.tables_container, bg=C_BG)
        self.exp_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        self.exp_section = CollapsibleSection(self.exp_frame, "Recent Expenses (Simplified)", C_EXP, s_headers, s_widths, self._handle_sort, self.edit_record)
        self.exp_section.pack(fill=tk.BOTH, expand=True)
        
        self.card_canvas.bind('<Configure>', self._on_canvas_resize)

    def _on_canvas_resize(self, event):
        if hasattr(self, '_resize_timer'): self.root.after_cancel(self._resize_timer)
        self._resize_timer = self.root.after(150, self.update_ui)

    def _bind_keys(self):
        self.root.bind('<Key>', self.handle_keypress)

    def handle_keypress(self, event):
        if isinstance(event.widget, (tk.Entry, tk.Text, tk.Listbox)): return
        if not event.char: return
        char = event.char.upper()
        
        if char == 'Q': self.quit_app()
        elif char == 'T': self._handle_time_menu()
        elif char == 'C': self._handle_category()
        elif char == 'R': self._handle_range()
        elif char == 'S': self._handle_sort_menu()
        elif char == 'I': self._handle_input()
        elif char == 'L': self._handle_limit_menu()
        elif char == 'Y': self._show_details_window()

    def _show_details_window(self):
        top = tk.Toplevel(self.root)
        top.title("Detailed Analytics & Full Records")
        top.geometry("1150x700")
        top.configure(bg=C_BG)
        top.transient(self.root)
        
        notebook = ttk.Notebook(top)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tab_tables = tk.Frame(notebook, bg=C_BG)
        notebook.add(tab_tables, text="Full Data Tables")
        
        t_frame = tk.Frame(tab_tables, bg=C_BG)
        t_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ctrl_f = tk.Frame(t_frame, bg=C_BG)
        ctrl_f.pack(fill=tk.X, pady=(0, 10))
        tk.Label(ctrl_f, text="Sort Mode:", bg=C_BG, fg=C_FG).pack(side=tk.LEFT)
        v_mode = tk.StringVar(value=self.sort_mode)
        tk.Radiobutton(ctrl_f, text="Date", variable=v_mode, value="time", bg=C_BG, fg=C_FG, selectcolor=C_PANEL, command=lambda: [setattr(self, 'sort_mode', v_mode.get()), self.update_ui(), update_full_tables()]).pack(side=tk.LEFT)
        tk.Radiobutton(ctrl_f, text="Amount", variable=v_mode, value="money", bg=C_BG, fg=C_FG, selectcolor=C_PANEL, command=lambda: [setattr(self, 'sort_mode', v_mode.get()), self.update_ui(), update_full_tables()]).pack(side=tk.LEFT)
        
        paned = tk.PanedWindow(t_frame, orient=tk.VERTICAL, bg='#334155', bd=0, sashwidth=6, sashpad=4)
        paned.pack(fill=tk.BOTH, expand=True)
        
        f_headers = ["Idx", "Date", "Category", "Status", "Amount", "Description", "Bar Chart"]
        f_widths = [40, 110, 150, 100, 110, 220, 250]
        
        full_inc = CollapsibleSection(paned, "Income Records (Full)", C_INC, f_headers, f_widths, self._handle_sort, self.edit_record)
        full_exp = CollapsibleSection(paned, "Expense Records (Full)", C_EXP, f_headers, f_widths, self._handle_sort, self.edit_record)
        
        paned.add(full_inc, stretch="always", minsize=100)
        paned.add(full_exp, stretch="always", minsize=100)

        tab_pie = tk.Frame(notebook, bg=C_PANEL)
        notebook.add(tab_pie, text="Expense Distribution")
        c_pie = tk.Canvas(tab_pie, bg=C_PANEL, highlightthickness=0)
        c_pie.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tab_line = tk.Frame(notebook, bg=C_PANEL)
        notebook.add(tab_line, text="Cashflow Trends")
        c_line = tk.Canvas(tab_line, bg=C_PANEL, highlightthickness=0)
        c_line.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        def update_full_tables():
            if not tk.Toplevel.winfo_exists(top):
                self.update_full_tables_cb = None
                return
                
            filtered = self.get_filtered()
            exp = [r for r in filtered if not r.get("is_income", False)]
            inc = [r for r in filtered if r.get("is_income", False)]
            
            if self.sort_mode == "time":
                exp.sort(key=lambda x: (x["year"], x["month"], x["day"]), reverse=self.sort_desc)
                inc.sort(key=lambda x: (x["year"], x["month"], x["day"]), reverse=self.sort_desc)
            elif self.sort_mode == "money":
                exp.sort(key=lambda x: x["money"], reverse=self.sort_desc)
                inc.sort(key=lambda x: x["money"], reverse=self.sort_desc)
            elif self.sort_mode == "alphabet":
                exp.sort(key=lambda x: x["category"].lower(), reverse=self.sort_desc)
                inc.sort(key=lambda x: x["category"].lower(), reverse=self.sort_desc)
            
            m_list = [r["money"] for r in filtered if r["money"] > 0]
            max_v = max(m_list) if m_list else 0
            log_stats, raw_stats = Statistic.get_both_stats(exp)
            
            full_inc_data, full_exp_data = [], []
            for i, r in enumerate(inc, 1):
                date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
                full_inc_data.append({"values": [i, date, r["category"], "Income", f"${r['money']:.2f}", r.get("description", ""), ""], "is_anomaly": False, "record_ref": r})
                
            for i, r in enumerate(exp, 1):
                date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
                is_ano = Statistic.is_hybrid_anomaly(r["money"], log_stats, raw_stats, pivot=1000.0, ignore_flag=r.get("ignore_anomaly", False))
                stat = "Ignored" if r.get("ignore_anomaly") else ("ANOMALY" if is_ano else "Normal")
                full_exp_data.append({"values": [i, date, r["category"], stat, f"${r['money']:.2f}", r.get("description", ""), ""], "is_anomaly": is_ano, "record_ref": r})

            full_inc.table.update_data(full_inc_data, True, max_v)
            full_exp.table.update_data(full_exp_data, False, max_v)
            draw_graphs()

        self.update_full_tables_cb = update_full_tables

        def draw_graphs():
            if not tk.Toplevel.winfo_exists(top): return
            c_pie.delete("all")
            c_line.delete("all")
            
            filtered = self.get_filtered()
            exp_records = [r for r in filtered if not r.get("is_income", False)]
            inc_records = [r for r in filtered if r.get("is_income", False)]
            
            w_p, h_p = c_pie.winfo_width(), c_pie.winfo_height()
            if w_p < 100: w_p, h_p = 1000, 600
            
            if exp_records:
                cat_sums = {}
                for r in exp_records: cat_sums[r["category"]] = cat_sums.get(r["category"], 0.0) + r["money"]
                total = sum(cat_sums.values())
                
                if total > 1e-9:
                    start_angle = 0
                    legend_y = 60
                    c_pie.create_text(w_p//2 - 150, 30, text=f"Expense Distribution (Total: ${total:,.2f})", fill=C_FG, font=("Segoe UI", 16, "bold"))
                    
                    cx, cy, r_size = w_p//2 - 200, h_p//2, min(w_p, h_p)//2 - 60
                    if r_size > 20:
                        sorted_cats = sorted(cat_sums.items(), key=lambda x: x[1], reverse=True)
                        
                        for i, (cat, val) in enumerate(sorted_cats):
                            if val <= 0: continue
                            extent = (val / total) * 360
                            color = PIE_COLORS[i % len(PIE_COLORS)]
                            c_pie.create_arc(cx-r_size, cy-r_size, cx+r_size, cy+r_size, start=start_angle, extent=extent, fill=color, outline=C_BG, width=3)
                            
                            lx = w_p//2 + 100
                            c_pie.create_rectangle(lx, legend_y, lx+20, legend_y+20, fill=color, outline="")
                            c_pie.create_text(lx+35, legend_y+10, text=f"{cat}: ${val:,.2f} ({(val/total)*100:.1f}%)", fill=C_FG, anchor="w", font=("Segoe UI", 12))
                            
                            start_angle += extent
                            legend_y += 35
                else: c_pie.create_text(w_p//2, h_p//2, text="Total expenses are zero.", fill=C_MUTED, font=("Segoe UI", 14))
            else: c_pie.create_text(w_p//2, h_p//2, text="No expense data for selected filters.", fill=C_MUTED, font=("Segoe UI", 14))

            if filtered:
                date_sums = {}
                for r in filtered:
                    d_str = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
                    if d_str not in date_sums: date_sums[d_str] = {"inc": 0.0, "exp": 0.0}
                    if r.get("is_income"): date_sums[d_str]["inc"] += r["money"]
                    else: date_sums[d_str]["exp"] += r["money"]
                    
                sorted_dates = sorted(date_sums.keys())
                if len(sorted_dates) > 1:
                    max_val = max(max(v["inc"], v["exp"]) for v in date_sums.values())
                    max_val = max(1.0, max_val * 1.1) 
                    
                    pad_x, pad_y = 80, 60
                    w_l, h_l = c_line.winfo_width(), c_line.winfo_height()
                    if w_l < 100: w_l, h_l = 1000, 600
                    
                    c_line.create_text(w_l//2, 30, text="Income vs Expense Trend", fill=C_FG, font=("Segoe UI", 16, "bold"))
                    
                    c_line.create_line(pad_x, h_l-pad_y, w_l-pad_x, h_l-pad_y, fill=C_MUTED, width=2) 
                    c_line.create_line(pad_x, pad_y, pad_x, h_l-pad_y, fill=C_MUTED, width=2) 
                    c_line.create_text(pad_x-10, pad_y, text=f"${max_val:,.0f}", fill=C_MUTED, anchor="e", font=("Segoe UI", 10))
                    c_line.create_text(pad_x-10, h_l-pad_y, text="$0", fill=C_MUTED, anchor="e", font=("Segoe UI", 10))
                    
                    x_step = (w_l - 2*pad_x) / (len(sorted_dates) - 1)
                    prev_x, prev_inc_y, prev_exp_y = None, None, None
                    
                    for i, d in enumerate(sorted_dates):
                        x = pad_x + i * x_step
                        inc_y = (h_l - pad_y) - (date_sums[d]["inc"] / max_val) * (h_l - 2*pad_y)
                        exp_y = (h_l - pad_y) - (date_sums[d]["exp"] / max_val) * (h_l - 2*pad_y)
                        
                        if prev_x is not None:
                            c_line.create_line(prev_x, prev_inc_y, x, inc_y, fill=C_INC, width=3, smooth=True)
                            c_line.create_line(prev_x, prev_exp_y, x, exp_y, fill=C_EXP, width=3, smooth=True)
                        
                        c_line.create_oval(x-4, inc_y-4, x+4, inc_y+4, fill=C_INC, outline=C_PANEL)
                        c_line.create_oval(x-4, exp_y-4, x+4, exp_y+4, fill=C_EXP, outline=C_PANEL)
                        
                        if len(sorted_dates) <= 15 or i % max(1, len(sorted_dates)//10) == 0:
                            c_line.create_text(x, h_l-pad_y+20, text=d[5:], fill=C_MUTED, font=("Segoe UI", 9), angle=45)
                            
                        prev_x, prev_inc_y, prev_exp_y = x, inc_y, exp_y
                    
                    c_line.create_text(w_l-pad_x-100, 40, text="■ Income", fill=C_INC, anchor="w", font=("Segoe UI", 12))
                    c_line.create_text(w_l-pad_x-100, 65, text="■ Expense", fill=C_EXP, anchor="w", font=("Segoe UI", 12))
                else: c_line.create_text(w_l//2, h_l//2, text="Need at least 2 active days to draw a trend line.", fill=C_MUTED, font=("Segoe UI", 14))

        def safe_draw_manager(event=None):
            if not tk.Toplevel.winfo_exists(top): return
            if hasattr(top, '_graph_timer'): top.after_cancel(top._graph_timer)
            top._graph_timer = top.after(100, draw_graphs)

        top.after(200, update_full_tables)
        c_pie.bind('<Configure>', safe_draw_manager)
        c_line.bind('<Configure>', safe_draw_manager)

    def _handle_sort_menu(self):
        top = tk.Toplevel(self.root)
        top.title("Sort Options")
        top.geometry("250x300")
        top.configure(bg=C_PANEL)
        top.transient(self.root)
        top.grab_set()
        
        tk.Label(top, text="Sort Mode", bg=C_PANEL, fg=C_FG, font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        var_mode = tk.StringVar(value=self.sort_mode)
        modes = [("Time / Date", "time"), ("Amount / Money", "money"), ("Category (Alphabet)", "alphabet")]
        
        for text, mode in modes:
            tk.Radiobutton(top, text=text, variable=var_mode, value=mode, bg=C_PANEL, fg=C_FG, selectcolor=C_BG, activebackground=C_PANEL, activeforeground=C_FG).pack(anchor='w', padx=40, pady=2)
            
        tk.Label(top, text="Order", bg=C_PANEL, fg=C_FG, font=("Segoe UI", 12, "bold")).pack(pady=10)
        var_desc = tk.BooleanVar(value=self.sort_desc)
        tk.Radiobutton(top, text="Ascending", variable=var_desc, value=False, bg=C_PANEL, fg=C_FG, selectcolor=C_BG, activebackground=C_PANEL, activeforeground=C_FG).pack(anchor='w', padx=40, pady=2)
        tk.Radiobutton(top, text="Descending", variable=var_desc, value=True, bg=C_PANEL, fg=C_FG, selectcolor=C_BG, activebackground=C_PANEL, activeforeground=C_FG).pack(anchor='w', padx=40, pady=2)
        
        def apply_sort():
            self.sort_mode = var_mode.get()
            self.sort_desc = var_desc.get()
            self.update_ui()
            if hasattr(self, 'update_full_tables_cb') and self.update_full_tables_cb:
                try: self.update_full_tables_cb()
                except Exception: pass
            top.destroy()
            
        tk.Button(top, text="Apply Sort", command=apply_sort, bg=C_BAR, fg='black', relief=tk.FLAT, font=("Segoe UI", 10, "bold")).pack(pady=20)

    def _handle_sort(self, col_name):
        if col_name == "Amount": new_mode = "money"
        elif col_name == "Date": new_mode = "time"
        elif col_name == "Category": new_mode = "alphabet"
        else: return
        
        if self.sort_mode == new_mode: self.sort_desc = not self.sort_desc
        else:
            self.sort_mode = new_mode
            self.sort_desc = False
        self.update_ui()
        if hasattr(self, 'update_full_tables_cb') and self.update_full_tables_cb:
            try: self.update_full_tables_cb()
            except Exception: pass

    def _handle_time_menu(self):
        top = tk.Toplevel(self.root)
        top.title("Time Scale Options")
        top.geometry("300x360")
        top.configure(bg=C_PANEL)
        top.transient(self.root)
        top.grab_set()

        tk.Label(top, text="Select Time Filter", bg=C_PANEL, fg=C_FG, font=("Segoe UI", 12, "bold")).pack(pady=10)

        var_scale = tk.StringVar(value=self.scale)

        def on_scale_change(*args):
            s = var_scale.get()
            if s == "All":
                entry_date.config(state='disabled')
                var_date.set("")
                lbl_hint.config(text="(No text input needed)")
            else:
                entry_date.config(state='normal')
                if s == "Year":
                    lbl_hint.config(text="Enter Year (YYYY):")
                    var_date.set(str(self.target_date["year"]) if self.scale == "Year" and self.target_date else str(datetime.now().year))
                elif s == "Month":
                    lbl_hint.config(text="Enter Month (YYYY-MM):")
                    var_date.set(f"{self.target_date['year']}-{self.target_date['month']:02d}" if self.scale == "Month" and self.target_date else datetime.now().strftime("%Y-%m"))
                elif s == "Day":
                    lbl_hint.config(text="Enter Day (YYYY-MM-DD):")
                    var_date.set(f"{self.target_date['year']}-{self.target_date['month']:02d}-{self.target_date['day']:02d}" if self.scale == "Day" and self.target_date else datetime.now().strftime("%Y-%m-%d"))

        scales = [("All Time", "All"), ("Yearly", "Year"), ("Monthly", "Month"), ("Daily", "Day")]
        for text, val in scales:
            tk.Radiobutton(top, text=text, variable=var_scale, value=val, bg=C_PANEL, fg=C_FG, selectcolor=C_BG, activebackground=C_PANEL, activeforeground=C_FG, command=on_scale_change).pack(anchor='w', padx=40, pady=2)

        lbl_hint = tk.Label(top, text="", bg=C_PANEL, fg=C_MUTED, font=("Segoe UI", 10))
        lbl_hint.pack(pady=(15, 5))

        var_date = tk.StringVar()
        entry_date = tk.Entry(top, textvariable=var_date, bg=C_BG, fg=C_FG, insertbackground=C_FG, justify='center', font=("Consolas", 12))
        entry_date.pack(pady=5, padx=40, fill=tk.X, ipady=3)

        on_scale_change()

        def apply_time():
            s = var_scale.get()
            d_val = var_date.get().strip()
            if s == "All":
                self.scale = "All"
                self.target_date = None
            elif s == "Year":
                if d_val.isdigit() and len(d_val) == 4:
                    self.scale = "Year"
                    self.target_date = {"year": int(d_val)}
                else: messagebox.showerror("Error", "Invalid Year format (YYYY).", parent=top); return
            elif s == "Month":
                parts = d_val.split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    self.scale = "Month"
                    self.target_date = {"year": int(parts[0]), "month": int(parts[1])}
                else: messagebox.showerror("Error", "Invalid Month format (YYYY-MM).", parent=top); return
            elif s == "Day":
                dp = Input.validate_date(d_val)
                if dp:
                    self.scale = "Day"
                    self.target_date = {"year": dp[0], "month": dp[1], "day": dp[2]}
                else: messagebox.showerror("Error", "Invalid Day format (YYYY-MM-DD).", parent=top); return
            self.update_ui()
            top.destroy()

        tk.Button(top, text="Apply Filter", command=apply_time, bg=C_BAR, fg='black', relief=tk.FLAT, font=("Segoe UI", 10, "bold")).pack(pady=15)

    def _handle_category(self):
        all_cats = list(set(r["category"] for r in self.records))
        for c in all_cats:
            if c not in self.active_categories and c not in [r["category"] for r in self.records if r["category"] not in self.active_categories]:
                self.active_categories.add(c)
                
        top = tk.Toplevel(self.root)
        top.title("Manage Categories")
        top.geometry("350x500")
        top.configure(bg=C_PANEL)
        top.transient(self.root)
        top.grab_set()
        
        tk.Label(top, text="Filter Active Categories", bg=C_PANEL, fg=C_FG, font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        f_container = tk.Frame(top, bg=C_HEAD)
        f_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        canvas = tk.Canvas(f_container, bg=C_HEAD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(f_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=C_HEAD)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        var_dict = {}
        for c in all_cats:
            var = tk.BooleanVar(value=(c in self.active_categories))
            var_dict[c] = var
            tk.Checkbutton(scrollable_frame, text=c, variable=var, bg=C_HEAD, fg=C_FG, selectcolor=C_PANEL, activebackground=C_HEAD, activeforeground=C_FG).pack(anchor="w", padx=10, pady=2)
            
        def select_all():
            for v in var_dict.values(): v.set(True)
            
        def clear_all():
            for v in var_dict.values(): v.set(False)
            
        def save():
            self.active_categories = {c for c, var in var_dict.items() if var.get()}
            if not self.active_categories:
                messagebox.showwarning("Warning", "You hid all categories. Tables will be empty.", parent=top)
            self.update_ui()
            top.destroy()

        btn_f1 = tk.Frame(top, bg=C_PANEL)
        btn_f1.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_f1, text="Select All", command=select_all, bg=C_BG, fg=C_FG, relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(btn_f1, text="Clear All", command=clear_all, bg=C_BG, fg=C_FG, relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(top, text="Apply Category Filters", command=save, bg=C_BAR, fg='black', relief=tk.FLAT, font=("Segoe UI", 10, "bold")).pack(fill=tk.X, padx=20, pady=10)

    def _handle_range(self):
        max_val = max([r["money"] for r in self.records] + [100.0]) if self.records else 100.0
        dialog = RangeSliderDialog(self.root, self.range_filter[0], self.range_filter[1], max_val)
        self.root.wait_window(dialog)
        if dialog.result:
            self.range_filter = dialog.result
            self.update_ui()

    def _handle_limit_menu(self):
        top = tk.Toplevel(self.root)
        top.title("Limit Management Dashboard")
        top.geometry("650x550")
        top.configure(bg=C_PANEL)
        top.transient(self.root)
        top.grab_set()
        
        all_exp = sum(r["money"] for r in self.records if not r.get("is_income", False))
        all_inc = sum(r["money"] for r in self.records if r.get("is_income", False))
        
        tk.Label(top, text="LIMIT MANAGEMENT DASHBOARD", bg=C_PANEL, fg=C_FG, font=("Segoe UI", 14, "bold")).pack(pady=10)
        tk.Label(top, text=f"Lifetime Exp: ${all_exp:,.2f}  |  Lifetime Inc: ${all_inc:,.2f}", bg=C_PANEL, fg=C_BAR, font=("Segoe UI", 12)).pack()
        
        grid_frame = tk.Frame(top, bg=C_PANEL)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        list_frame = tk.Frame(grid_frame, bg=C_BG, padx=15, pady=15)
        list_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(list_frame, text="ACTIVE LIMITS", bg=C_BG, fg=C_BAR, font=("Segoe UI", 11, "bold")).pack(anchor='w', pady=(0,10))
        
        limits_container = tk.Frame(list_frame, bg=C_BG)
        limits_container.pack(fill=tk.BOTH, expand=True)
        
        def _refresh_limits():
            for widget in limits_container.winfo_children():
                widget.destroy()
            
            scale_map_rev = {'d':'Daily', 'w':'Weekly', 'm':'Monthly', 'y':'Yearly', 'all': 'All Time'}
            act_t = False
            for k, v in self.lm.combined_limits.items():
                if v > 1e-9:
                    parts = k.split("_", 1)
                    s_name = scale_map_rev.get(parts[0], parts[0])
                    c_name = parts[1]
                    tk.Label(limits_container, text=f"- {s_name} limit for '{c_name}': ${v:,.2f}", bg=C_BG, fg=C_FG, font=("Segoe UI", 11)).pack(anchor='w', pady=2)
                    act_t = True
            if not act_t:
                tk.Label(limits_container, text="(None set)", bg=C_BG, fg=C_MUTED, font=("Segoe UI", 11)).pack(anchor='w')
                
        _refresh_limits()
        
        form_frame = tk.Frame(top, bg=C_BG, padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(form_frame, text="Set Limit:", bg=C_BG, fg=C_FG, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=5, pady=5)
        
        scale_var = tk.StringVar(value="Monthly")
        scale_cb = ttk.Combobox(form_frame, textvariable=scale_var, values=["Daily", "Weekly", "Monthly", "Yearly", "All Time"], width=10, state="readonly", font=("Segoe UI", 10))
        scale_cb.grid(row=0, column=1, padx=5, pady=5)
        
        cat_var = tk.StringVar(value="All")
        cats = ["All"] + list(set(r["category"] for r in self.records))
        cat_cb = ttk.Combobox(form_frame, textvariable=cat_var, values=cats, width=15, font=("Segoe UI", 10))
        cat_cb.grid(row=0, column=2, padx=5, pady=5)
        
        amt_var = tk.StringVar()
        amt_entry = tk.Entry(form_frame, textvariable=amt_var, width=10, font=("Segoe UI", 10))
        amt_entry.grid(row=0, column=3, padx=5, pady=5)
        
        def _apply_limit():
            s = scale_var.get()
            c = cat_var.get()
            try:
                val = float(amt_var.get())
                if val >= 0:
                    sm = {"Daily": "d", "Weekly": "w", "Monthly": "m", "Yearly": "y", "All Time": "all"}
                    self.lm.set_limit(sm[s], c, val)
                    self.update_ui()
                    _refresh_limits()
                    amt_var.set("")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount", parent=top)
                
        def _remove_limit():
            s = scale_var.get()
            c = cat_var.get()
            sm = {"Daily": "d", "Weekly": "w", "Monthly": "m", "Yearly": "y", "All Time": "all"}
            self.lm.set_limit(sm[s], c, 0.0)
            self.update_ui()
            _refresh_limits()

        tk.Button(form_frame, text="Set", command=_apply_limit, bg=C_INC, fg='black', relief=tk.FLAT, width=8, font=("Segoe UI", 10, "bold")).grid(row=0, column=4, padx=5, pady=5)
        tk.Button(form_frame, text="Remove", command=_remove_limit, bg=C_EXP, fg='black', relief=tk.FLAT, width=8, font=("Segoe UI", 10, "bold")).grid(row=0, column=5, padx=5, pady=5)

    def _handle_input(self):
        top = tk.Toplevel(self.root)
        top.title("Data Input Staging Area")
        top.geometry("800x500")
        top.configure(bg=C_PANEL)
        top.transient(self.root)
        top.grab_set()
        
        staging_buffer = []
        lbl_text = "Manual Format: [I/E] [YYYY-MM-DD] [Category] [Amount] [Description]\n(I = Income, E = Expense)\nFile Format: F filename.txt"
        tk.Label(top, text=lbl_text, bg=C_PANEL, fg=C_MUTED, font=("Segoe UI", 10), justify=tk.LEFT).pack(anchor='w', padx=15, pady=10)
        
        entry = tk.Entry(top, font=("Consolas", 12), bg=C_BG, fg=C_FG, insertbackground=C_FG, relief=tk.FLAT)
        entry.pack(fill=tk.X, padx=15, pady=5, ipady=5)
        entry.focus_set()
        
        tree = ttk.Treeview(top, columns=("raw", "status"), show="headings", height=10)
        tree.heading("raw", text="Parsed Record")
        tree.heading("status", text="Status")
        tree.column("raw", width=600)
        tree.column("status", width=150)
        tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        def process_cmd(event=None):
            raw = entry.get().strip()
            if not raw: return
            entry.delete(0, tk.END)
            
            if raw.upper() == 'DONE':
                for item in staging_buffer: 
                    self.records.append(item["record"])
                    self.active_categories.add(item["record"]["category"])
                self.records.sort(key=lambda x: (x["year"], x["month"], x["day"]))
                with open("data.json", "w", encoding="utf-8") as f: json.dump(self.records, f, indent=4)
                self.update_ui()
                top.destroy()
                return
                
            if raw.upper().startswith('F '):
                try:
                    with open(raw[2:].strip(), 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                parsed = Input.parse_staged_line(line.strip() if line.strip()[0].upper() in ['I','E'] else "E " + line.strip())
                                if parsed["valid"]:
                                    staging_buffer.append(parsed)
                                    tree.insert("", tk.END, values=(parsed['raw'], "Valid"))
                except Exception as e: messagebox.showerror("Error", str(e), parent=top)
            else:
                parsed = Input.parse_staged_line(raw)
                if parsed["valid"]:
                    staging_buffer.append(parsed)
                    tree.insert("", tk.END, values=(parsed['raw'], "Valid"))
                else:
                    messagebox.showerror("Error", parsed["error"], parent=top)
                    
        entry.bind("<Return>", process_cmd)
        tk.Button(top, text="Submit/Add (or type DONE to save)", command=process_cmd, bg=C_BAR, fg='black', relief=tk.FLAT, font=("Segoe UI", 10, "bold")).pack(pady=10)

    def edit_record(self, record):
        top = tk.Toplevel(self.root)
        top.title("Edit Record")
        top.geometry("400x350")
        top.configure(bg=C_PANEL)
        
        def save_edits():
            record["category"] = e_cat.get().strip()
            record["description"] = e_desc.get().strip()
            try: record["money"] = float(e_money.get().strip())
            except: pass
            dp = Input.validate_date(e_date.get().strip())
            if dp: record["year"], record["month"], record["day"] = dp
            record["ignore_anomaly"] = bool(var_ignore.get())
            self.active_categories.add(record["category"])
            with open("data.json", "w", encoding="utf-8") as f: json.dump(self.records, f, indent=4)
            self.update_ui()
            top.destroy()
            
        def del_record():
            self.records.remove(record)
            with open("data.json", "w", encoding="utf-8") as f: json.dump(self.records, f, indent=4)
            self.update_ui()
            top.destroy()

        tk.Label(top, text="Date (YYYY-MM-DD):", bg=C_PANEL, fg=C_FG).pack(pady=2)
        e_date = tk.Entry(top); e_date.insert(0, f"{record['year']}-{record['month']:02d}-{record['day']:02d}"); e_date.pack()
        tk.Label(top, text="Category:", bg=C_PANEL, fg=C_FG).pack(pady=2)
        e_cat = tk.Entry(top); e_cat.insert(0, record['category']); e_cat.pack()
        tk.Label(top, text="Amount:", bg=C_PANEL, fg=C_FG).pack(pady=2)
        e_money = tk.Entry(top); e_money.insert(0, str(record['money'])); e_money.pack()
        tk.Label(top, text="Description:", bg=C_PANEL, fg=C_FG).pack(pady=2)
        e_desc = tk.Entry(top); e_desc.insert(0, record.get('description','')); e_desc.pack()
        
        var_ignore = tk.IntVar(value=int(record.get('ignore_anomaly', False)))
        if not record.get("is_income", False):
            tk.Checkbutton(top, text="Ignore Anomaly", variable=var_ignore, bg=C_PANEL, fg=C_ANO, selectcolor=C_BG, activebackground=C_PANEL, activeforeground=C_ANO).pack(pady=10)
            
        btn_f = tk.Frame(top, bg=C_PANEL)
        btn_f.pack(pady=15)
        tk.Button(btn_f, text="Save", command=save_edits, bg=C_INC, fg='black', relief=tk.FLAT, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_f, text="Delete", command=del_record, bg=C_EXP, fg='black', relief=tk.FLAT, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)

    def get_filtered(self):
        f = []
        for r in self.records:
            if self.scale == "Year" and self.target_date and r["year"] != self.target_date["year"]: continue
            elif self.scale == "Month" and self.target_date and (r["year"] != self.target_date["year"] or r["month"] != self.target_date["month"]): continue
            elif self.scale == "Day" and self.target_date and (r["year"] != self.target_date["year"] or r["month"] != self.target_date["month"] or r["day"] != self.target_date["day"]): continue
            if r["category"] not in self.active_categories: continue
            if not (self.range_filter[0] <= r["money"] <= self.range_filter[1]): continue
            f.append(r)
        return f

    def update_ui(self):
        recs = self.get_filtered()
        exp = [r for r in recs if not r.get("is_income", False)]
        inc = [r for r in recs if r.get("is_income", False)]
        t_exp, t_inc = sum(r["money"] for r in exp), sum(r["money"] for r in inc)

        td_str = "All Time"
        if self.scale == "Year" and self.target_date: td_str = f"{self.target_date['year']}"
        elif self.scale == "Month" and self.target_date: td_str = f"{self.target_date['year']}-{self.target_date['month']:02d}"
        elif self.scale == "Day" and self.target_date: td_str = f"{self.target_date['year']}-{self.target_date['month']:02d}-{self.target_date['day']:02d}"
        
        cat_str = "Custom" if len(self.active_categories) != len(set(r["category"] for r in self.records)) else "All"
        upper_bound_str = "INF" if self.range_filter[1] == float('inf') else f"{self.range_filter[1]:.0f}"
        self.lbl_filters.config(text=f"Time: {td_str}   |   Categories: {cat_str}   |   Range: ${self.range_filter[0]:.0f} - ${upper_bound_str}")

        self.card_canvas.delete("all")
        width = self.card_canvas.winfo_width()
        if width < 100: width = 1160 
        card_w = (width - 15) // 2
        
        create_round_rectangle(self.card_canvas, 0, 0, card_w, 120, radius=12, fill=C_PANEL, outline="")
        self.card_canvas.create_text(20, 20, text="FINANCIAL OVERVIEW", fill=C_MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        self.card_canvas.create_text(20, 55, text="Total Income", fill=C_MUTED, font=("Segoe UI", 10), anchor="w")
        self.card_canvas.create_text(20, 85, text=f"${t_inc:,.2f}", fill=C_INC, font=("Segoe UI", 20, "bold"), anchor="w")
        self.card_canvas.create_text(card_w//2 + 20, 55, text="Total Expense", fill=C_MUTED, font=("Segoe UI", 10), anchor="w")
        self.card_canvas.create_text(card_w//2 + 20, 85, text=f"${t_exp:,.2f}", fill=C_EXP, font=("Segoe UI", 20, "bold"), anchor="w")
        
        x_offset = card_w + 15
        create_round_rectangle(self.card_canvas, x_offset, 0, x_offset+card_w, 120, radius=12, fill=C_PANEL, outline="")
        
        is_exc, ratio, rem, limit_name, limit_val = self.lm.check_limit(exp, self.scale, self.category_filter if self.category_filter != "All" else "All")
        scale_str, target_days = Statistic.determine_scale(exp, self.scale)
        
        title_str = f"LIMIT PROGRESS ({limit_name})" if limit_val > 0 else "LIMIT PROGRESS"
        self.card_canvas.create_text(x_offset+20, 20, text=title_str, fill=C_MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        
        bar_y = 65
        bar_max_w = card_w - 40
        create_round_rectangle(self.card_canvas, x_offset+20, bar_y, x_offset+20+bar_max_w, bar_y+10, radius=5, fill=C_BG, outline="")
        
        if self.scale == "All":
            self.card_canvas.create_text(x_offset+20, 45, text="[ N/A in 'All' Time Scale ]", fill=C_FG, font=("Segoe UI", 11), anchor="w")
        elif limit_val <= 1e-9:
            if self.auto_suggest:
                sug = Statistic.predict_budget(exp, target_days)
                
                if sug > 0:
                    s_rat = min(1.0, t_exp / sug)
                    self.card_canvas.create_text(x_offset+20, 45, text=f"Auto-Suggested: ${t_exp:,.0f} / ${sug:,.0f} ({(t_exp/sug)*100:.0f}%)", fill=C_FG, font=("Segoe UI", 11), anchor="w")
                    c_color = C_EXP if s_rat >= 1.0 else (C_ANO if s_rat >= 0.75 else C_BAR)
                    create_round_rectangle(self.card_canvas, x_offset+20, bar_y, x_offset+20+(bar_max_w*s_rat), bar_y+10, radius=5, fill=c_color, outline="")
                else:
                    self.card_canvas.create_text(x_offset+20, 45, text="[ Log data to unlock suggestions ]", fill=C_MUTED, font=("Segoe UI", 11), anchor="w")
            else:
                self.card_canvas.create_text(x_offset+20, 45, text="[ Not Set ]", fill=C_MUTED, font=("Segoe UI", 11), anchor="w")
        else:
            self.card_canvas.create_text(x_offset+20, 45, text=f"${t_exp:,.0f} / ${limit_val:,.0f} ({ratio*100:.0f}%)", fill=C_FG, font=("Segoe UI", 11), anchor="w")
            c_color = C_EXP if is_exc else C_BAR
            create_round_rectangle(self.card_canvas, x_offset+20, bar_y, x_offset+20+min(bar_max_w, bar_max_w*ratio), bar_y+10, radius=5, fill=c_color, outline="")

        pred = Statistic.predict_budget(exp, target_days)
        pred_text = f"${round(pred):,.0f}" if pred > 1e-9 and self.scale != "All" else "N/A"
        self.card_canvas.create_text(x_offset+20, 95, text=f"Predictive Budget: ", fill=C_MUTED, font=("Segoe UI", 10), anchor="w")
        self.card_canvas.create_text(x_offset+130, 95, text=pred_text, fill=C_PUR, font=("Segoe UI", 11, "bold"), anchor="w")

        if self.sort_mode == "time":
            exp.sort(key=lambda x: (x["year"], x["month"], x["day"]), reverse=self.sort_desc)
            inc.sort(key=lambda x: (x["year"], x["month"], x["day"]), reverse=self.sort_desc)
        elif self.sort_mode == "money":
            exp.sort(key=lambda x: x["money"], reverse=self.sort_desc)
            inc.sort(key=lambda x: x["money"], reverse=self.sort_desc)
        elif self.sort_mode == "alphabet":
            exp.sort(key=lambda x: x["category"].lower(), reverse=self.sort_desc)
            inc.sort(key=lambda x: x["category"].lower(), reverse=self.sort_desc)

        m_list = [r["money"] for r in recs if r["money"] > 0]
        max_v = max(m_list) if m_list else 0
        log_stats, raw_stats = Statistic.get_both_stats(exp)
        
        inc_data, exp_data = [], []
        for r in inc:
            date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            inc_data.append({"values": [date, r["category"], f"${r['money']:.2f}"], "is_anomaly": False, "record_ref": r})
            
        for r in exp:
            date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            is_ano = Statistic.is_hybrid_anomaly(r["money"], log_stats, raw_stats, pivot=1000.0, ignore_flag=r.get("ignore_anomaly", False))
            exp_data.append({"values": [date, r["category"], f"${r['money']:.2f}"], "is_anomaly": is_ano, "record_ref": r})

        self.inc_section.table.update_data(inc_data, True, max_v)
        self.exp_section.table.update_data(exp_data, False, max_v)
        
        if hasattr(self, 'update_full_tables_cb') and self.update_full_tables_cb:
            try: self.update_full_tables_cb()
            except Exception: pass

    def quit_app(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceSystemGUI(root)
    root.mainloop()
