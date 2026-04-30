#COMP1110 Group Project: Personal Budget and Spending Assistant (PFMS)

**Topic: Topic A:** Personal Budget and Spending Assistant

**Tutorial Subclass:** B08

**Group Members**

Xu Mohan - 3036601604

Ma Xiaoyu - 3036481664

Wu Chung Hin Hugo - 3036582602

Li Xingwei - 3036452821

Zhang Jiaqi - 3036588979

**1. Project Overview & Problem Modeling**

Managing personal finances is a daily challenge characterized by frequent, fragmented spending across multiple categories. In this project, we modeled everyday spending as a computational problem.

Our modeling approach:

Transactions: Every transaction is modeled with discrete attributes: Date (YYYY-MM-DD), Amount (Money > 0), Category, Description, and Type (Income/Expense).

Budget Rules: Budgets are modeled as threshold values dynamically mapped to specific time scales (Daily, Weekly, Monthly, Yearly) and specific categories.

Analysis: We transcended simple aggregations by introducing statistical modeling (Hybrid Z-scores) to detect spending anomalies and linear momentum forecasting to predict future budget needs.

While the project guidelines specify text-based interactions as a baseline, we took a step further to implement a hybrid Graphical User Interface (GUI) driven by a "One-Letter Trigger" keyboard system. This maximizes data entry efficiency while providing highly readable visual analytics.

**2. Execution Environment & Setup**

Programming Language: Python 3.x (3.8+ recommended)

Dependencies: Pure Python standard libraries (json, os, sys, math, statistics, datetime, tkinter). No external third-party packages (like pandas, numpy, or matplotlib) are required.

Execution Environment: Compatible with Windows, macOS, and Linux desktop environments.

How to Run: Open your terminal or command prompt in the project root directory and execute:

python3 Main.py


(Note: Since this utilizes tkinter, ensure you are running it in an environment with display support).

**3. File Structure & Purpose**

Our codebase is strictly modularized to separate data input, logic, statistics, and UI rendering:

Main.py (User Interface & Orchestrator): Manages the main event loop, handles the keystrokes, renders the live dashboard (tables, native canvas charts, budget progress bars), and orchestrates data persistence.

Input.py (File I/O & Error Handling): Handles data ingestion. Safely reads batch data from .txt files and parses manual inputs. Error Handling: It strictly validates date formats (YYYY-MM-DD) and ensures money is a positive float, preventing system crashes from corrupted files.

Limit.py (Budget Guard): The logic handler for rule-based alerts. It stores, updates, and calculates the progress ratios for time-based and category-based limits.

Statistic.py (Mathematical Engine): Computes summary statistics. Features our custom Hybrid Z-score anomaly detection and generates predictive budgets using historical momentum.

data.json (Data Model Storage): The persistent local database where all transaction records are safely serialized.

Data Model Design (Schema)

Transactions are stored as dictionaries in a JSON array:

{
  "year": 2026, "month": 3, "day": 1, 
  "category": "Food", "money": 30.5, 
  "description": "Breakfast", 
  "is_income": false, "ignore_anomaly": false
}


**4. Key Features (Aligned with Topic A Requirements)**

Menu Interface (One-Letter Triggers): Navigated purely via hotkeys:

[T]ime, [C]ategory, [R]ange, [S]ort, [L]imits, [I]nput, [Y] Details, [Q]uit & Save.

Interactive Data Management (CRUD): * Import transactions from space-separated .txt files or manual input via a staging area.

Double-click any record in the tables to instantly Edit or Delete it.

Advanced Summary Statistics & Visualization: * Dynamically computes total spending and time-based totals.

Native Canvas Charts: The Details window ([Y]) renders custom Expense Distribution (Pie Chart) and Cashflow Trends (Line Chart) dynamically based on active filters.

Rule-based Alerts: Visual warning systems (progress bars turning red) when daily/weekly/monthly limits for specific categories are exceeded.

Hybrid Anomaly Detection: Instead of basic thresholding, our algorithm uses a hybrid approach: Log-Normal distribution for everyday small expenses, and Standard Normal distribution for outliers > $1000, ensuring highly accurate flagging of irregular expenses.

**5. Sample Test Cases & Scenarios**

To demonstrate the system's capabilities in realistic spending situations, we have designed three case studies.

(Preparation: Ensure test_food.txt, test_transport.txt, and test_subs.txt are in the project root directory).

Case Study 1: Daily Food Budget Cap & Editing

Purpose: Test rule-based alerts, daily time-based summaries, and CRUD functionality.

Scenario: A student wants to cap their daily food spending at HK$50 and needs an alert if they overspend.

Test Data (test_food.txt):

E 2026-03-01 Food 30.5 Breakfast
E 2026-03-01 Food 25.0 Lunch
E 2026-03-02 Food 45.0 Dinner


Execution: 1. Press [I], type F test_food.txt and press Enter, then type DONE.
2. Press [L] to open Limits, set a Daily limit for Food at 50.
3. Press [T], select Day and enter 2026-03-01.

Expected Output: The dashboard progress bar will turn red, showing $55 / $50 (110%), successfully generating an overspend warning. (You can double-click the Lunch record to change it to $10, and watch the bar turn green instantly).

Case Study 2: Monthly Transport Tracking & Hybrid Anomaly Detection

Purpose: Test category filtering, multi-dimensional sorting, and the Hybrid Z-Score engine.

Scenario: Evaluating regular transport spending versus irregular, expensive taxi rides.

Test Data (test_transport.txt):

E 2026-03-01 Transport 12.0 MTR_to_HKU
E 2026-03-02 Transport 12.0 MTR_to_HKU
E 2026-03-03 Transport 12.0 MTR_to_HKU
E 2026-03-05 Transport 85.0 Taxi_Home


Execution:

Press [I], import F test_transport.txt, and type DONE.

Press [C] and select only Transport. Press [S] to sort by "Amount".

Press [Y] to open Detailed Analytics.

Expected Output: In the Full Data Table, the $85 Taxi trip will be automatically flagged as ANOMALY by the statistical engine. The Line Chart will also clearly show a spike on March 5th.

Case Study 3: Subscription Creep Forecasting

Purpose: Test the predictive budgeting system based on historical spending trends.

Scenario: Detecting hidden or increasing recurring expenses over several months.

Test Data (test_subs.txt):

E 2026-01-15 Subscription 78.0 Netflix
E 2026-02-15 Subscription 78.0 Netflix
E 2026-03-15 Subscription 118.0 Netflix_Premium


Execution:

Press [I], import F test_subs.txt, and type DONE.

Press [C] and select only Subscription.

Observe the "Predictive Budget" indicator on the main dashboard.

Expected Output: The statistical engine will calculate a momentum factor based on the recent price hike. It will automatically forecast next month's expected cost to be significantly higher than the simple historical average, actively warning the user of the upward subscription creep.
