# COMP1110 Group Project: budget_assistant

**Topic:** Topic A: Personal Budget  
**Tutorial Subclass:** [Insert Subclass, e.g., Group 1A]  

## Group Members
* Xu Mohan - 3036601604
* Ma Xiaoyu - 3036481664
* Wu Chung Hin Hugo - 3036582602
* Li Xingwei - 3036452821
* Zhang Jiaqi - 3036588979

---

## 1. Project Overview

This project is an advanced Command Line Interface (CLI) based personal finance management system. It goes beyond basic tracking and display by integrating a powerful statistical engine. Key features include pixel-precision visual bar charts, Z-Score based anomaly spending alerts, and predictive budgeting using linear regression and momentum factors.

The entire system utilizes ANSI color rendering and a "One-Letter Trigger" interaction model, eliminating the need for tedious command typing and providing an ultra-fast, seamless user experience.

## 2. File Structure and Purpose

* **`Main.py`**: The core application entry point. It manages the main event loop, handles the "One-Letter Trigger" UI interactions, and renders the live dashboard.
* **`Input.py`**: Manages all data ingestion. It safely reads batch data from `.txt` files and handles manual terminal inputs with strict format validation to prevent crashes.
* **`Limit.py`**: The logic handler for budget caps. It stores, updates, and calculates the progress ratios for both time-based limits (e.g., daily, monthly) and category-based limits.
* **`Statistic.py`**: The mathematical engine of the app. It calculates Z-scores for anomaly detection, generates the high-precision logarithmic bar charts, and computes the trend-based budget predictions.
* **`data.json`**: The persistent local database where all transaction records are safely serialized and stored.

## 3. Environment & Execution

* **Language:** Python 3.x (3.8+ recommended)
* **Dependencies:** Pure Python standard libraries (`json`, `os`, `sys`, `math`, `statistics`, `datetime`, `re`). No external third-party packages are required.
* **Execution Environment:** Compatible with Windows, macOS, and Linux terminals.
* **How to Run:** Open your terminal or command prompt in the project root directory and execute:
    ```bash
    python Main.py
    ```

## 4. Interactive Operation Guide

The system listens for keystrokes in real-time. You do not need to press `Enter` to trigger a command. The main control bar looks like this:
`[T]Time:All | [C]Cat:All | [R]Range:All | [L]Limits | [I]nput | [Y]Details | [Q]uit`

### 📊 Core Data Filters
* **`[T]` Time Scale**: Cycles through the time scale: Day -> Week -> Month -> Year -> All.
* **`[C]` Category**: Dynamically lists all existing spending categories. Enter the corresponding number to filter.
* **`[R]` Money Range**: Prompts you to enter a minimum and maximum amount.

### 🛡️ Budgets & Limits
* **`[L]` Limits Management**: Set spending caps for specific time frames (e.g., $1000/month) or specific categories. The dashboard displays a real-time colored progress bar that turns red if you overspend.

### 📝 Data Input
* **`[I]` Input Data**: Choose between two input methods:
    * **`[F]`ile Batch Import**: Reads space-separated text files. Format: `YYYY-MM-DD Category Money Description`
    * **`[T]`erminal Manual Entry**: Step-by-step strict validation for manual logging.

### 🔎 Details & Exit
* **`[Y]` View Details**: Opens the detailed data panel showing a perfectly aligned table with Date, Category, Money, Z-Score Alarm Flags, and High-Resolution Bar Charts.
* **`[Q]` Quit**: Safely exit the system. Auto-saves to `data.json`.

## 5. Sample Test Cases & Scenarios

To demonstrate the system's capabilities, we have designed three realistic case studies. You can test these by importing the corresponding text files using the `[I]nput` -> `[F]ile` command. 

*Note: Ensure you create these sample `.txt` files in your directory to follow along.*

### Scenario 1: Daily Food Budget Cap (HK$50)
* **Goal:** Track small, frequent food purchases and alert the user if they exceed a daily budget of $50.
* **Test Data (`test_food.txt`):**
    ```text
    2026-03-01 Food 30.5 Breakfast
    2026-03-01 Food 25.0 Lunch
    2026-03-02 Food 45.0 Dinner
    ```
* **How to test:** Import the file. Press `[L]` to set a daily time limit of `50`. Press `[T]` to filter by Day (`2026-03-01`). The dashboard will highlight that the limit is exceeded (111%).

### Scenario 2: Monthly Transport Tracking
* **Goal:** Evaluate transport spending over a month to see if a monthly pass is worth buying.
* **Test Data (`test_transport.txt`):**
    ```text
    2026-03-01 Transport 12.0 MTR_to_HKU
    2026-03-02 Transport 12.0 MTR_to_HKU
    2026-03-05 Transport 85.0 Taxi_Home
    ```
* **How to test:** Import the file. Press `[C]` to filter by `Transport`. Press `[Y]` to view details. The $85 Taxi trip will be automatically flagged as an `ANOMALY` by the Z-score engine. 

### Scenario 3: Subscription Creep Detection
* **Goal:** Detect hidden or forgotten recurring expenses over a year.
* **Test Data (`test_subs.txt`):**
    ```text
    2026-01-15 Subscription 78.0 Netflix
    2026-02-15 Subscription 78.0 Netflix
    2026-03-15 Subscription 118.0 Netflix_Premium_Upgrade
    ```
* **How to test:** Import the file. Press `[C]` to filter by `Subscription`. The system's predictive budgeting will automatically forecast next month's expected subscription cost, factoring in the recent upward trend.

## 6. Data Persistence

The system uses `data.json` in the root directory as the core database.
* **First Run:** If the file does not exist, the system starts with an empty database.
* **Auto Load & Save:** Every time `Main.py` starts, it loads the history. Whether you exit manually or encounter an unexpected interrupt, the program securely overwrites and saves the latest data to `data.json`.
