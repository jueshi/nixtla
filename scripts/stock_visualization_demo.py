import os
import pandas as pd
import yfinance as yf
from nixtla import NixtlaClient
import matplotlib.pyplot as plt

# 1. Data Acquisition
def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches stock data from yfinance and preprocesses it for Nixtla.
    """
    print(f"Fetching data for {ticker}...")
    try:
        # Fetch data
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if df.empty:
            raise ValueError("No data fetched.")

        # Reset index to get 'Date' as a column
        df = df.reset_index()

        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        # Select and rename columns
        date_col = [c for c in df.columns if 'Date' in str(c)][0]
        target_col = 'Close'

        df = df[[date_col, target_col]].copy()
        df.columns = ['ds', 'y']
        df['unique_id'] = ticker

        # Ensure correct types and handle timezone
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)

        # Resample to fill missing dates (weekends/holidays) to ensure regular frequency
        # This is crucial for TimeGPT if not using 'B' frequency which can be strict about holidays
        print("Resampling data to Daily frequency (forward filling)...")
        df = df.set_index('ds').asfreq('D').ffill().reset_index()
        df['unique_id'] = ticker # unique_id might become NaN after resampling

        print(f"Data fetched and resampled successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Generating dummy data for demonstration...")
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        import numpy as np
        y = np.linspace(100, 150, len(dates)) + np.random.normal(0, 2, len(dates))
        df = pd.DataFrame({'ds': dates, 'y': y, 'unique_id': ticker})
        return df

# 2. Nixtla Functions
def run_nixtla_demo(df: pd.DataFrame):
    api_key = os.environ.get("NIXTLA_API_KEY")
    if not api_key:
        print("WARNING: NIXTLA_API_KEY not found in environment variables.")
        print("Please set it to run the actual TimeGPT model.")
        return

    client = NixtlaClient(api_key=api_key)

    # 2.1 Forecast
    print("\n--- Running Forecast ---")
    try:
        forecast_horizon = 14
        # We pass freq='D' explicitly since we resampled to Daily
        fcst_df = client.forecast(df, h=forecast_horizon, level=[80, 90], freq='D')
        print("Forecast generated successfully.")
        print(fcst_df.head())

        # Plot Forecast
        client.plot(df, fcst_df, level=[80, 90])
        plt.savefig("stock_forecast.png")
        print("Forecast plot saved to 'stock_forecast.png'")
    except Exception as e:
        print(f"Forecast failed: {e}")

    # 2.2 Anomaly Detection
    print("\n--- Running Anomaly Detection ---")
    try:
        anomalies_df = client.detect_anomalies(df, time_col='ds', target_col='y', level=99, freq='D')
        print("Anomaly detection complete.")
        print(anomalies_df.head())

        # Plot Anomalies
        client.plot(df, anomalies_df, time_col='ds', target_col='y', plot_anomalies=True)
        plt.savefig("stock_anomalies.png")
        print("Anomaly plot saved to 'stock_anomalies.png'")
    except Exception as e:
        print(f"Anomaly detection failed: {e}")

    # 2.3 Cross Validation
    print("\n--- Running Cross Validation ---")
    try:
        cv_df = client.cross_validation(
            df,
            h=7,
            n_windows=3,
            step_size=7,
            level=[80, 90],
            freq='D'
        )
        print("Cross validation complete.")
        print(cv_df.head())

        # Plot CV
        client.plot(df, cv_df, level=[80, 90])
        plt.savefig("stock_cv.png")
        print("Cross validation plot saved to 'stock_cv.png'")
    except Exception as e:
        print(f"Cross validation failed: {e}")

if __name__ == "__main__":
    # Parameters
    TICKER = "AAPL"
    START = "2023-01-01"
    END = "2024-01-01"

    # Run
    df = fetch_stock_data(TICKER, START, END)
    run_nixtla_demo(df)
