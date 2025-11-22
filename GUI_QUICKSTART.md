# Stock Price Backtest GUI - Quick Start Guide

This guide will help you get up and running with the Stock Price Backtest GUI, a tool designed to easily backtest TimeGPT forecasts on stock data.

## 1. Prerequisites

Before you begin, ensure you have the following:

*   **Python 3.9+** installed on your system.
*   A **Nixtla API Key**. You can obtain one by signing up at [dashboard.nixtla.io](https://dashboard.nixtla.io).

## 2. Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/Nixtla/nixtla.git
    cd nixtla
    ```

2.  **Install Dependencies**:
    The GUI requires specific libraries (`streamlit`, `yfinance`, `plotly`, and the `nixtla` SDK). You can install them using pip:

    ```bash
    pip install streamlit yfinance plotly nixtla utilsforecast
    ```

    *Note: If you are developing within the `nixtla` repo environment, these may already be installed or available via `pip install -e .[dev]`.*

## 3. Running the Application

To launch the GUI, run the following command in your terminal:

```bash
streamlit run stock_app.py
```

This will start a local web server and automatically open the application in your default web browser (usually at `http://localhost:8501`).

## 4. Usage Guide

Once the app is running, follow these steps to perform a backtest:

### Step 1: Configuration
*   **Nixtla API Key**: Enter your API key in the sidebar.
    *   *Tip*: You can also set the `NIXTLA_API_KEY` environment variable before running the app to skip this step.

### Step 2: Data Input
You have two options for loading data:
*   **Ticker Symbol**: Enter a valid stock ticker (e.g., `AAPL`, `MSFT`, `TSLA`). Select the **Start Date** and **End Date**, then click **Fetch Data**.
*   **CSV Upload**: Select "CSV Upload" and drop a CSV file containing your time series. Map the columns to "Date" (`ds`) and "Value" (`y`).

### Step 3: Model Parameters
*   **Model**: Choose between `timegpt-1` (standard) or `timegpt-1-long-horizon` (optimized for longer forecasts).
*   **Frequency**: Select the frequency of your data (e.g., `D` for daily, `h` for hourly).

### Step 4: Backtest Parameters
Configure how the backtest should run:
*   **Horizon (h)**: How many steps into the future to forecast for each window.
*   **Number of Windows**: How many historical points to test backwards.
*   **Step Size**: The stride between each backtest window.
*   **Confidence Levels**: Enter desired prediction intervals (e.g., `80, 90`).

### Step 5: Run & Analyze
1.  Click the **Run Backtest** button.
2.  Wait for the progress spinner to complete.
3.  **View Results**:
    *   **Dataframe**: Inspect the raw forecast numbers.
    *   **Metrics**: Check the `MAE`, `RMSE`, and `MAPE` scores to evaluate performance.
    *   **Visualization**: Interact with the plot to compare the Forecasts (colored lines) against the Actual history (black line) and view confidence intervals.
