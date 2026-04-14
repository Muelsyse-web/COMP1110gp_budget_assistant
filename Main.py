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

        # FIX 3: Added "Description" to the table header
        print("\n" + pad_text("Date", 12) + "| " + pad_text("Category", 15) + "| " + pad_text("Money", 10) + "| " + pad_text("Alarm", 10) + "| " + pad_text("Description", 20) + "| Bar Chart")
        print("-" * 110)
        
        for r in exp:
            date = f"{r['year']}-{r['month']:02d}-{r['day']:02d}"
            is_ano = Statistic.is_anomaly(r["money"], mean_v, std_v)
            alarm = f"{C_ANO}ANOMALY{C_RESET}" if is_ano else "Normal"
            bar = f"{C_BAR}{Statistic.generate_barchart(r['money'], max_v)}{C_RESET}"
            
            # Extract and truncate description to prevent breaking the table format
            desc = r.get("description", "")
            if len(desc) > 18:
                desc = desc[:15] + "..."
            
            # FIX 3: Print the description in the row
            print(f"{pad_text(date, 12)}| {pad_text(r['category'], 15)}| {pad_text(f'{r['money']:.1f}', 10)}| {pad_text(alarm, 10)}| {pad_text(desc, 20)}| {bar}")
        
        pred_recs = [r for r in self.records if (self.category_filter == "All" or r["category"] == self.category_filter)]
        pred = Statistic.predict_budget(pred_recs)
        print(f"\n{C_INC}Predicted 30-Day Budget for '{self.category_filter}': ${pred:,.2f}{C_RESET}")
        print("\nPress any key to return...")
        get_char()


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
                    
                    # FIX 1: Automatically change the dashboard Time Scale to match the limit
                    scale_map = {'d': 'Day', 'w': 'Week', 'm': 'Month', 'y': 'Year'}
                    self.scale = scale_map[scale]
                    print(f"\n[Success] Limit set! Dashboard Scale automatically changed to {self.scale}.")
                    input("Press Enter to return...") 
                    
            elif choice == '2':
                cat = input("Enter Category Name (e.g. Food): ").strip()
                amt = float(input("Enter limit amount: "))
                self.lm.set_limit("cat", cat, amt)
                
                # Automatically change the dashboard Category filter to match the limit
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
