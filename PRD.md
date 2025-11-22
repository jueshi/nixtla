# Product Requirements Document: Stock Price Backtest GUI

## 1. Overview
The Stock Price Backtest GUI is a web-based application designed to allow users to backtest stock price forecasting models using TimeGPT (via the Nixtla SDK). The tool aims to simplify the process of evaluating forecasting performance on historical stock data without writing code.

## 2. Goals
- **Accessibility**: Enable users without coding skills to leverage TimeGPT for stock analysis.
- **Efficiency**: Provide a quick way to iterate on backtesting parameters.
- **Visualization**: Offer clear, interactive visualizations of backtest results and performance metrics.

## 3. User Personas
- **Quantitative Analyst**: Wants to quickly test TimeGPT on various tickers before integrating it into a pipeline.
- **Trader**: Wants to see how well the model would have predicted past price movements.
- **Data Scientist**: Needs a visual tool to demonstrate model performance to stakeholders.

## 4. Functional Requirements

### 4.1 Data Input
- **Stock Ticker Integration**:
  - Users can enter a stock ticker symbol (e.g., "AAPL", "MSFT").
  - The application fetches historical data using a library like `yfinance`.
- **CSV Upload (Fallback)**:
  - Users can upload a CSV file containing time series data (columns: `timestamp`, `value`).
- **Date Range**:
  - Users can select the start and end dates for the historical data to be used.

### 4.2 Configuration
- **API Credentials**:
  - Input field for Nixtla API Key (masked).
  - Option to save/cache the key for the session.
- **Model Parameters**:
  - **Model Selection**: Dropdown to choose between `timegpt-1` and `timegpt-1-long-horizon`.
  - **Frequency**: Auto-inferred or manually selectable (e.g., Daily, Hourly).
- **Backtest Parameters**:
  - **Horizon (`h`)**: The forecast horizon (e.g., 7 days).
  - **Number of Windows (`n_windows`)**: How many historical windows to test.
  - **Step Size (`step_size`)**: The gap between each window.
  - **Confidence Levels**: Input for prediction intervals (e.g., 80, 90).
  - **Quantiles**: Alternative to levels, allowing specific quantile inputs.

### 4.3 Execution
- **Run Backtest**: A prominent button to initiate the backtesting process (calls `NixtlaClient.cross_validation`).
- **Progress Indicator**: Visual feedback while data is being fetched and the API is being queried.

### 4.4 Visualization & Reporting
- **Interactive Chart**:
  - A multi-line chart using Plotly.
  - Shows:
    - Historical "Truth" data.
    - Forecasted values for each backtest window.
    - Prediction intervals (confidence bands).
    - Anomalies (optional, if `detect_anomalies` is integrated).
- **Performance Metrics**:
  - Display a table of aggregated error metrics:
    - MAE (Mean Absolute Error)
    - RMSE (Root Mean Squared Error)
    - MAPE (Mean Absolute Percentage Error)
  - Option to view metrics per backtest window.

## 5. Non-Functional Requirements
- **Performance**: The GUI should remain responsive. Long-running API calls should not freeze the interface.
- **Security**: API keys must not be logged or exposed in the UI (beyond the input field).
- **Usability**: Clean, intuitive interface with tooltips explaining parameters.

## 6. Technical Stack (Proposed)
- **Frontend/App Framework**: [Streamlit](https://streamlit.io/) (Python).
- **Data Handling**: `pandas`, `yfinance`.
- **Forecasting Engine**: `nixtla` SDK.
- **Visualization**: `plotly`.

## 7. Future Scope
- **Portfolio Backtesting**: Backtest multiple stocks simultaneously.
- **Exogenous Variables**: Allow adding external features (e.g., interest rates, oil prices) to the model.
- **Anomaly Detection Mode**: A dedicated view for `detect_anomalies`.
