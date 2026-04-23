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

def create_round_rectangle(canvas, x1, y1, x2, y2, radius=15, **kwargs):
    """Custom algorithm to draw smooth rounded rectangles in standard Tkinter."""
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
        
        # Min Controls
        tk.Label(frame, text="Minimum:", bg=C_PANEL, fg=C_FG).grid(row=0, column=0, sticky='w')
        self.var_min = tk.DoubleVar(value=current_min)
        self.scl_min = ttk.Scale(frame, from_=0, to=self.abs_max, variable=self.var_min, command=self._on_slider_min)
        self.scl_min.grid(row=0, column=1, sticky='ew', padx=10, pady=10)
        
        self.var_min_str = tk.StringVar(value=f"{current_min:.0f}")
        self.entry_min = tk.Entry(frame, textvariable=self.var_min_str, width=10, bg=C_HEAD, fg=C_FG, insertbackground=C_FG, justify='center')
        self.entry_min.grid(row=0, column=2)
        self.entry_min.bind('<KeyRelease>', self._on_entry_min)
        
        # Max Controls
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
        tk.Button(btn_frame, text="Save", command=self._save, bg=C_INC, fg='#fff', relief=tk.FLAT, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Set Max to INF", command=self._set_inf, bg=C_BAR, fg='#fff', relief=tk.FLAT, width=15).pack(side=tk.LEFT, padx=10)

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
    """High-Performance Canvas-based Table with flat, modern styling."""
    def __init__(self, parent, headers, widths, sort_callback, edit_callback):
        super().__init__(parent, bg=C_PANEL)
        self.headers = headers
        self.widths = widths
        self.sort_callback = sort_callback
        self.edit_callback = edit_callback
        self.row_height = 35
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
        
        # Headers
        for i, h in enumerate(self.headers):
            self.head_canvas.create_text(coords[i], 20, text=h.upper(), fill=C_MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
            
        total_height = len(self.data) * self.row_height
        self.body_canvas.configure(scrollregion=(0, 0, sum(self.widths)+20, total_height))
        
        # Body Rows
        for r_idx, row in enumerate(self.data):
            y_top = r_idx * self.row_height
            y_mid = y_top + (self.row_height // 2)
            
            is_ano = row.get("is_anomaly") and not row["record_ref"].get("ignore_anomaly")
            
            bg_color = C_PANEL if r_idx % 2 == 0 else '#233044'
            if is_ano: bg_color = '#3b2f19'
                
            self.body_canvas.create_rectangle(0, y_top, sum(self.widths)+20, y_top+self.row_height, fill=bg_color, outline="")
            self.body_canvas.create_line(0, y_top+self.row_height, sum(self.widths)+20, y_top+self.row_height, fill='#334155')
            
            fg = C_INC if self.is_income else (C_FG if not is_ano else C_ANO)
            
            for c_idx, val in enumerate(row["values"][:-1]):
                text_col = C_FG
                if c_idx == 4: text_col = fg
                elif c_idx == 3 and is_ano: text_col = C_ANO
                elif c_idx == 3 and self.is_income: text_col = C_INC
                
                self.body_canvas.create_text(coords[c_idx], y_mid, text=str(val), fill=text_col, font=("Segoe UI", 10), anchor="w")
                
            money = row["record_ref"]["money"]
            c_idx = len(row["values"]) - 1
            bar_x = coords[c_idx]
            bar_w = self.widths[c_idx] - 20
            
            if self.max_money > 1e-9 and money > 1e-9:
                length = (math.log(money + 1) / math.log(self.max_money + 1)) * bar_w
                length = max(4, length)
                create_round_rectangle(self.body_canvas, bar_x, y_mid-5, bar_x+length, y_mid+5, radius=4, fill=C_BAR, outline="")

class CollapsibleSection(tk.Frame):
    def __init__(self, parent, title, color, headers, widths, sort_cb, edit_cb, toggle_cb=None):
        super().__init__(parent, bg=C_BG)
        self.is_open = True
        self.toggle_cb = toggle_cb
        
        self.head_frame = tk.Frame(self, bg=C_PANEL, pady=8, padx=15)
        self.head_frame.pack(fill=tk.X)
        
        self.lbl_title = tk.Label(self.head_frame, text=title, bg=C_PANEL, fg=color, font=("Segoe UI", 12, "bold"))
        self.lbl_title.pack(side=tk.LEFT)
        
        self.btn_toggle = tk.Button(self.head_frame, text="[-] Hide", bg=C_BG, fg=C_FG, relief=tk.FLAT, command=self.toggle)
        self.btn_toggle.pack(side=tk.RIGHT)
        
        self.table = VirtualTable(self, headers, widths, sort_cb, edit_cb)
        self.table.pack(fill=tk.BOTH, expand=True)

    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self.table.pack(fill=tk.BOTH, expand=True)
            self.btn_toggle.config(text="[-] Hide")
        else:
            self.table.pack_forget()
            self.btn_toggle.config(text="[+] Show")
            
        if self.toggle_cb:
            self.toggle_cb(self, self.is_open)

class FinanceSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 8 Project - PFMS Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg=C_BG)
        
        self.records = Input.read_input("data.json", "json")
        self.lm = Limit.LimitManager()
        
        self.scale = "All"
        self.target_date = None
        self.category_filter = "All"
        self.range_filter = (0.0, float('inf'))
        self.auto_suggest = True
        self.sort_mode = "time"
        self.sort_desc = False
        self.details_visible = True
        
        self._setup_styles()
        self._build_ui()
        self._bind_keys()
        self.update_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), background=C_PANEL, foreground=C_FG, borderwidth=0)

    def _build_ui(self):
        # 1. TOP HEADER BAR
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
            b = tk.Button(ctrl_frame, text=text, command=cmd, bg=C_PANEL, fg=C_FG, relief=tk.FLAT, padx=8, pady=5)
            b.pack(side=tk.LEFT, padx=3)
            
        btn("[T] Time", self._handle_time_menu)
        btn("[C] Cat", self._handle_category)
        btn("[R] Range", self._handle_range)
        btn("[L] Limits", self._handle_limit_menu)
        btn("[S] Sort", self._handle_sort_menu)
        btn("[I] Input", self._handle_input)
        btn("[Y] Details", self._toggle_details)

        # 2. MIDDLE DASHBOARD CARDS
        self.card_canvas = tk.Canvas(self.root, height=130, bg=C_BG, highlightthickness=0)
        self.card_canvas.pack(fill=tk.X, padx=15, pady=5)

        # 3. BOTTOM TABLES CONTAINER
        self.tables_container = tk.Frame(self.root, bg=C_BG)
        self.tables_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Secure PanedWindow implementation that prevents widgets from leaving the manager
        self.paned_window = tk.PanedWindow(self.tables_container, orient=tk.VERTICAL, bg='#334155', bd=0, sashwidth=6, sashpad=4)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        headers = ["Idx", "Date", "Category", "Status", "Amount", "Description", "Bar Chart"]
        widths = [40, 90, 120, 100, 90, 200, 250]
        
        self.inc_section = CollapsibleSection(self.paned_window, "Recent Income", C_INC, headers, widths, self._handle_sort, self.edit_record, self._on_section_toggle)
        self.exp_section = CollapsibleSection(self.paned_window, "Recent Expenses", C_EXP, headers, widths, self._handle_sort, self.edit_record, self._on_section_toggle)
        
        self.paned_window.add(self.inc_section, stretch="always", minsize=45)
        self.paned_window.add(self.exp_section, stretch="always", minsize=45)
        
        self.card_canvas.bind('<Configure>', self._on_canvas_resize)

    def _on_section_toggle(self, section, is_open):
        """Robust toggle logic using sash placement to close gaps without removing widgets."""
        if section == self.inc_section:
            if not is_open:
                self.paned_window.paneconfigure(self.inc_section, stretch="never")
                self.paned_window.sash_place(0, 0, 45) # Force sash to the top
            else:
                self.paned_window.paneconfigure(self.inc_section, stretch="always")
                self.paned_window.sash_place(0, 0, self.paned_window.winfo_height() // 2)
        else:
            if not is_open:
                self.paned_window.paneconfigure(self.exp_section, stretch="never")
                self.paned_window.sash_place(0, 0, self.paned_window.winfo_height() - 45) # Force sash to bottom
            else:
                self.paned_window.paneconfigure(self.exp_section, stretch="always")
                self.paned_window.sash_place(0, 0, self.paned_window.winfo_height() // 2)

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
        elif char == 'Y': self._toggle_details()

    def _toggle_details(self):
        self.details_visible = not self.details_visible
        if self.details_visible:
            self.tables_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        else:
            self.tables_container.pack_forget()

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
            top.destroy()
            
        tk.Button(top, text="Apply Sort", command=apply_sort, bg=C_BAR, fg='#fff', relief=tk.FLAT).pack(pady=20)

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

    def _handle_time_menu(self):
        """Upgraded Interactive Time Selection Menu"""
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

        tk.Button(top, text="Apply Filter", command=apply_time, bg=C_BAR, fg='#fff', relief=tk.FLAT).pack(pady=15)

    def _handle_category(self):
        cats = ["All Categories"] + list(set(r["category"] for r in self.records))
        top = tk.Toplevel(self.root)
        top.title("Select Category")
        top.geometry("300x400")
        top.configure(bg=C_PANEL)
        top.transient(self.root)
        top.grab_set()
        tk.Label(top, text="Click or Select Category:", bg=C_PANEL, fg=C_FG, font=("Segoe UI", 11)).pack(pady=5)
        listbox = tk.Listbox(top, bg=C_HEAD, fg=C_FG, font=("Segoe UI", 11), selectbackground=C_BAR, borderwidth=0)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        for i, c in enumerate(cats): listbox.insert(tk.END, f"{i}: {c}")
        def on_select(event=None):
            if listbox.curselection():
                self.category_filter = "All" if listbox.curselection()[0] == 0 else cats[listbox.curselection()[0]]
                self.update_ui()
                top.destroy()
        listbox.bind("<Double-Button-1>", on_select)
        listbox.bind("<Return>", on_select)

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
        top.geometry("600x500")
        top.configure(bg=C_PANEL)
        top.transient(self.root)
        top.grab_set()
        
        all_exp = sum(r["money"] for r in self.records if not r.get("is_income", False))
        all_inc = sum(r["money"] for r in self.records if r.get("is_income", False))
        
        tk.Label(top, text="LIMIT MANAGEMENT DASHBOARD", bg=C_PANEL, fg=C_FG, font=("Segoe UI", 14, "bold")).pack(pady=10)
        tk.Label(top, text=f"Lifetime Exp: ${all_exp:,.2f}  |  Lifetime Inc: ${all_inc:,.2f}", bg=C_PANEL, fg=C_BAR, font=("Segoe UI", 12)).pack()
        
        grid_frame = tk.Frame(top, bg=C_PANEL)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        t_frame = tk.Frame(grid_frame, bg=C_BG, padx=15, pady=15)
        t_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        tk.Label(t_frame, text="ACTIVE TIME LIMITS", bg=C_BG, fg=C_BAR, font=("Segoe UI", 11, "bold")).pack(anchor='w', pady=(0,10))
        
        scale_map = {'d':'Daily', 'w':'Weekly', 'm':'Monthly', 'y':'Yearly'}
        act_t = False
        for k, v in self.lm.time_limits.items():
            if v > 1e-9:
                tk.Label(t_frame, text=f"- {scale_map.get(k, k)}: ${v:,.2f}", bg=C_BG, fg=C_FG).pack(anchor='w')
                act_t = True
        if not act_t:
            if self.auto_suggest:
                s_str, t_days = Statistic.determine_scale([r for r in self.records if not r.get("is_income", False)], "All")
                sug = Statistic.predict_budget([r for r in self.records if not r.get("is_income", False)], t_days)
                tk.Label(t_frame, text=f">> Auto-Suggested {s_str}:\n${sug:,.0f}", bg=C_BG, fg=C_PUR, justify=tk.LEFT).pack(anchor='w')
            else:
                tk.Label(t_frame, text="(None set)", bg=C_BG, fg=C_MUTED).pack(anchor='w')

        c_frame = tk.Frame(grid_frame, bg=C_BG, padx=15, pady=15)
        c_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10,0))
        tk.Label(c_frame, text="ACTIVE CATEGORY LIMITS", bg=C_BG, fg=C_BAR, font=("Segoe UI", 11, "bold")).pack(anchor='w', pady=(0,10))
        act_c = False
        for k, v in self.lm.category_limits.items():
            if v > 1e-9:
                tk.Label(c_frame, text=f"- {k}: ${v:,.2f}", bg=C_BG, fg=C_FG).pack(anchor='w')
                act_c = True
        if not act_c:
            tk.Label(c_frame, text="(None set)", bg=C_BG, fg=C_MUTED).pack(anchor='w')
            
        btn_f = tk.Frame(top, bg=C_PANEL)
        btn_f.pack(pady=10)
        
        def _add_time():
            s = simpledialog.askstring("Time", "Scale [d/w/m/y]:", parent=top)
            if s and s.lower() in ['d','w','m','y']:
                a = simpledialog.askfloat("Amount", "Limit:", parent=top)
                if a is not None: self.lm.set_limit("time", s.lower(), a); self.update_ui(); top.destroy(); self._handle_limit_menu()
                
        def _add_cat():
            c = simpledialog.askstring("Category", "Name:", parent=top)
            if c:
                a = simpledialog.askfloat("Amount", "Limit:", parent=top)
                if a is not None: self.lm.set_limit("cat", c, a); self.update_ui(); top.destroy(); self._handle_limit_menu()
                
        def _rem():
            ch = simpledialog.askstring("Remove", "[T]ime or [C]ategory?", parent=top)
            if ch and ch.upper() == 'T':
                s = simpledialog.askstring("Scale", "[d/w/m/y]:", parent=top)
                if s: self.lm.set_limit("time", s.lower(), 0.0); self.update_ui(); top.destroy(); self._handle_limit_menu()
            elif ch and ch.upper() == 'C':
                c = simpledialog.askstring("Category", "Name:", parent=top)
                if c: self.lm.set_limit("cat", c, 0.0); self.update_ui(); top.destroy(); self._handle_limit_menu()
                
        def _tog():
            self.auto_suggest = not self.auto_suggest; self.update_ui(); top.destroy(); self._handle_limit_menu()

        tk.Button(btn_f, text="Add Time Limit", command=_add_time, bg=C_BG, fg=C_FG, relief=tk.FLAT, width=15).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_f, text="Add Cat Limit", command=_add_cat, bg=C_BG, fg=C_FG, relief=tk.FLAT, width=15).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_f, text="Remove Limit", command=_rem, bg=C_BG, fg=C_FG, relief=tk.FLAT, width=15).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(btn_f, text=f"Auto-Suggest: {'ON' if self.auto_suggest else 'OFF'}", command=_tog, bg=C_PUR, fg='#fff', relief=tk.FLAT, width=20).grid(row=1, column=0, columnspan=3, pady=10)

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
                for item in staging_buffer: self.records.append(item["record"])
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
        tk.Button(top, text="Submit/Add (or type DONE to save)", command=process_cmd, bg=C_BAR, fg='#fff', relief=tk.FLAT).pack(pady=10)

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
        tk.Button(btn_f, text="Save", command=save_edits, bg=C_INC, fg='#fff', relief=tk.FLAT).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_f, text="Delete", command=del_record, bg=C_EXP, fg='#fff', relief=tk.FLAT).pack(side=tk.LEFT, padx=10)

    def get_filtered(self):
        f = []
        for r in self.records:
            if self.scale == "Year" and self.target_date and r["year"] != self.target_date["year"]: continue
            elif self.scale == "Month" and self.target_date and (r["year"] != self.target_date["year"] or r["month"] != self.target_date["month"]): continue
            elif self.scale == "Day" and self.target_date and (r["year"] != self.target_date["year"] or r["month"] != self.target_date["month"] or r["day"] != self.target_date["day"]): continue
            if self.category_filter != "All" and r["category"] != self.category_filter: continue
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
        
        upper_bound_str = "INF" if self.range_filter[1] == float('inf') else f"{self.range_filter[1]:.0f}"
        self.lbl_filters.config(text=f"Time: {td_str}   |   Category: {self.category_filter}   |   Range: ${self.range_filter[0]:.0f} - ${upper_bound_str}")

        # --- DRAW DASHBOARD CARDS ON CANVAS ---
        self.card_canvas.delete("all")
        width = self.card_canvas.winfo_width()
        if width < 100: width = 1160 
        
        card_w = (width - 15) // 2
        
        # Draw Card 1: Overview
        create_round_rectangle(self.card_canvas, 0, 0, card_w, 120, radius=12, fill=C_PANEL, outline="")
        self.card_canvas.create_text(20, 20, text="FINANCIAL OVERVIEW", fill=C_MUTED, font=("Segoe UI", 9, "bold"), anchor="w")
        
        self.card_canvas.create_text(20, 55, text="Total Income", fill=C_MUTED, font=("Segoe UI", 10), anchor="w")
        self.card_canvas.create_text(20, 85, text=f"${t_inc:,.2f}", fill=C_INC, font=("Segoe UI", 20, "bold"), anchor="w")
        
        self.card_canvas.create_text(card_w//2 + 20, 55, text="Total Expense", fill=C_MUTED, font=("Segoe UI", 10), anchor="w")
        self.card_canvas.create_text(card_w//2 + 20, 85, text=f"${t_exp:,.2f}", fill=C_EXP, font=("Segoe UI", 20, "bold"), anchor="w")
        
        # Draw Card 2: Limits & Predictions
        x_offset = card_w + 15
        create_round_rectangle(self.card_canvas, x_offset, 0, x_offset+card_w, 120, radius=12, fill=C_PANEL, outline="")
        
        is_exc, ratio, rem, limit_name, limit_val = self.lm.check_limit(exp, self.scale, self.category_filter)
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

        # --- UPDATE TABLES ---
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
        for i, r in enumerate(inc, 1):
            date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            inc_data.append({"values": [i, date, r["category"], "Income", f"${r['money']:.2f}", r.get("description", ""), ""], "is_anomaly": False, "record_ref": r})
            
        for i, r in enumerate(exp, 1):
            date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            is_ano = Statistic.is_hybrid_anomaly(r["money"], log_stats, raw_stats, pivot=1000.0, ignore_flag=r.get("ignore_anomaly", False))
            stat = "Ignored" if r.get("ignore_anomaly") else ("ANOMALY" if is_ano else "Normal")
            exp_data.append({"values": [i, date, r["category"], stat, f"${r['money']:.2f}", r.get("description", ""), ""], "is_anomaly": is_ano, "record_ref": r})

        self.inc_section.table.update_data(inc_data, True, max_v)
        self.exp_section.table.update_data(exp_data, False, max_v)

    def quit_app(self):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceSystemGUI(root)
    root.mainloop()
