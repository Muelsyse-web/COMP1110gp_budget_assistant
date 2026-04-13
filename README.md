# COMP1110 Group Project: budget_assistant

**Topic:** Topic A: Personal Budget
**Tutorial Subclass:** [Insert Subclass, e.g., Group 1A]

## Group Members
* [Student Name 1] - [Student ID]
* [Student Name 2] - [Student ID]
* [Student Name 3] - [Student ID]
* [Student Name 4] - [Student ID]
* [Student Name 5] - [Student ID]
---


1. Project Overview

This project is an advanced Command Line Interface (CLI) based personal finance management system. It goes beyond basic tracking and display by integrating a powerful statistical engine. Key features include pixel-precision visual bar charts, Z-Score based anomaly spending alerts, and predictive budgeting using linear regression and momentum factors.

The entire system utilizes ANSI color rendering and a "One-Letter Trigger" interaction model, eliminating the need for tedious command typing and providing an ultra-fast, seamless user experience.

2. Core Technical Highlights

High-Precision Logarithmic Bar Charts (1/8 Block Resolution): Utilizes Unicode sub-blocks (from 1/8 to 8/8 width) to achieve high-resolution data visualization in the terminal. Combined with a logarithmic scaling algorithm, it perfectly resolves the visual issue where small expenses (e.g., $10) and large expenses (e.g., $1000) cannot be meaningfully displayed on the same chart.

Z-Score Intelligent Anomaly Warning: The system automatically calculates the mean and standard deviation of your spending based on current filters. Any expense that deviates from the mean by more than 2 standard deviations ($|Z| \ge 2.0$) is highlighted as a ⚠️ ANOMALY (impulse or irregular spending).

Clean-Data Predictive Budget: When forecasting the next month's budget, the system automatically excludes the aforementioned "anomalies" and calculates the "Daily Burn Rate" based on your regular spending habits. By integrating a "Momentum Factor" (comparing the first and second halves of your timeline), it provides a highly realistic 30-day budget prediction. It also automatically adds a 10% safety buffer if an upward spending trend is detected.

3. Environment & Execution

Environment: Python 3.x (3.8+ recommended)

Dependencies: Pure Python standard libraries (json, os, sys, math, statistics, datetime, re). No external packages are required.

How to Run: Open your terminal or command prompt in the project root directory and execute:

python Main.py


4. Interactive Operation Guide (One-Letter Trigger)

The system listens for keystrokes in real-time. You do not need to press Enter to trigger a command (compatible with both Windows and Unix).

The main control bar on the dashboard looks like this:
[T]Time:All | [C]Cat:All | [R]Range:All | [L]Limits | [I]nput | [Y]Details | [Q]uit

📊 Core Data Filters

All filters can be stacked/combined. For example, you can view bills from "February 2026" AND in the "Food" category AND with an amount "between 100 and 500".

[T] Time Scale
Cycles through the time scale: Day -> Week -> Month -> Year -> All.
When selecting a specific date/month, the system will prompt you to enter the target (e.g., 2026-02). The dashboard data and totals will update immediately.

[C] Category
Dynamically lists all existing spending categories in your database with assigned numbers. Enter the number to view only that category.

[R] Money Range
Prompts you to enter a minimum (Lower bound) and maximum (Upper bound) amount. Leave empty for no limit.

🛡️ Budgets & Limits

[L] Limits Management
Set spending caps for specific time frames (e.g., monthly) or specific categories (e.g., Food).

[1] Set Time Limit: Set an absolute time-based limit (e.g., $1000 per month).

[2] Set Category Limit: Set a limit for a specific category.

[3] Remove Limit: Set a limit to 0 to remove it.

UI Integration: Once set, the dashboard displays a real-time colored progress bar. If you exceed the limit, the bar turns Red.

📝 Data Input

[I] Input Data
Choose between two input methods:

[F]ile Batch Import:
When prompted with Enter file path:, type your txt file name (e.g., import_test.txt).
Format requirement (space-separated, one record per line):
YYYY-MM-DD Category Money Description
(Note: The system has high fault tolerance. If the file contains invalid dates like 2026-02-30 or letters in the money field, it will silently skip the invalid line to ensure the program never crashes.)

[T]erminal Manual Entry:
The system will ask if it is Income (I) or Expenditure (E), then prompt you to enter the data in the YYYY-MM-DD Category Money Description format. This mode includes strict validation and will block/reject any typos or invalid data instantly.

🔎 Details & Exit

[Y] View Details
Opens the detailed data panel. You will see a perfectly aligned table of your filtered records, including Date, Category, Money, Z-Score Alarm Flags, and High-Resolution Bar Charts.
At the bottom of the table, the system displays the predicted 30-day budget based on your current filters.

[Q] Quit
Safely exit the system. The program will automatically serialize and save all recent data to the data.json file.
(Note: Even if you force-quit the program using Ctrl+C, the underlying try...finally mechanism guarantees that your data is securely saved before termination.)

5. Data Persistence (data.json)

The system uses data.json in the root directory as the core database.

First Run: If the file does not exist, the system will start with an empty database.

Auto Load: Every time Main.py starts, it automatically loads history from this file.

Auto Save: Whether you exit manually, import a file, or encounter an unexpected interrupt, the program automatically overwrites and saves the latest data to data.json. No manual saving is required.
