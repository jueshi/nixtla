import os
import streamlit as st
import pandas as pd
import yfinance as yf
from nixtla import NixtlaClient
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty:
            return None
        df = df.reset_index()
        # Ensure we have date and close
        if 'Date' in df.columns:
            df = df.rename(columns={'Date': 'ds', 'Close': 'y'})
        elif 'Datetime' in df.columns: # For hourly data
            df = df.rename(columns={'Datetime': 'ds', 'Close': 'y'})
        elif 'index' in df.columns:
             # In some pandas versions/mocks, reset_index defaults to 'index'
            df = df.rename(columns={'index': 'ds', 'Close': 'y'})

        # yfinance might return MultiIndex columns if multiple tickers (not the case here but good to be safe)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Simple check for 'y'
        if 'y' not in df.columns:
             # Try to find 'Close'
             if 'Close' in df.columns:
                 df['y'] = df['Close']

        # Filter to just ds and y, and add unique_id
        df['unique_id'] = ticker

        # Check if we have required columns
        if 'ds' not in df.columns or 'y' not in df.columns:
             # Fallback: maybe columns are different.
             # Let's try to grab first column as date (if datetime) and 'Close' or 'Adj Close' as y
             pass

        df = df[['ds', 'y', 'unique_id']]

        # Ensure ds is datetime
        df['ds'] = pd.to_datetime(df['ds'])
        if df['ds'].dt.tz is not None:
             df['ds'] = df['ds'].dt.tz_convert(None) # Remove timezone for simplicity with TimeGPT checks sometimes

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    # Page configuration
    st.set_page_config(
        page_title="Stock Price Backtest GUI",
        page_icon="📈",
        layout="wide",
    )

    st.title("📈 Stock Price Backtest GUI with TimeGPT")
    st.markdown("""
    This tool allows you to backtest stock price forecasts using **TimeGPT**.
    Simply enter a ticker, configure your backtest parameters, and analyze the results.
    """)

    # Sidebar Configuration
    st.sidebar.header("Configuration")

    # API Key
    api_key = st.sidebar.text_input("Nixtla API Key", type="password", help="Enter your Nixtla API Key.")
    if not api_key:
        # Try getting from env
        api_key = os.environ.get("NIXTLA_API_KEY")
        if api_key:
            st.sidebar.success("API Key found in environment.")
        else:
            st.sidebar.warning("Please enter your API Key to proceed.")

    # Data Input
    st.sidebar.subheader("Data Input")

    input_method = st.sidebar.radio("Input Method", ["Ticker Symbol", "CSV Upload"])

    ticker = "Stock" # Default name

    if input_method == "Ticker Symbol":
        ticker = st.sidebar.text_input("Stock Ticker", value="AAPL", help="e.g., AAPL, MSFT, GOOG").upper()
        start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
        end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

        if st.sidebar.button("Fetch Data"):
            with st.spinner("Fetching data..."):
                df = load_data(ticker, start_date, end_date)
                if df is not None:
                    st.session_state['df'] = df
                    st.session_state['ticker'] = ticker
                    st.success(f"Loaded {len(df)} rows for {ticker}")
                else:
                    st.error("No data found.")
    else:
        uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                # Auto-detect columns
                # We need ds and y
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())

                # Column mapping if needed
                cols = df.columns.tolist()
                ds_col = st.sidebar.selectbox("Date Column", cols, index=0)
                y_col = st.sidebar.selectbox("Value Column", cols, index=1 if len(cols)>1 else 0)

                if st.sidebar.button("Process CSV"):
                    df = df.rename(columns={ds_col: 'ds', y_col: 'y'})
                    df['ds'] = pd.to_datetime(df['ds'])
                    if df['ds'].dt.tz is not None:
                        df['ds'] = df['ds'].dt.tz_convert(None)

                    df['unique_id'] = ticker
                    df = df[['ds', 'y', 'unique_id']]
                    st.session_state['df'] = df
                    st.session_state['ticker'] = ticker
                    st.success(f"Processed {len(df)} rows.")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")


    # Model Parameters
    st.sidebar.subheader("Model Parameters")
    model = st.sidebar.selectbox("Model", ["timegpt-1", "timegpt-1-long-horizon"], index=0)
    freq = st.sidebar.selectbox("Frequency", ["D", "h", "W", "M"], index=0, help="Frequency of the data. D=Daily, h=Hourly, etc.")

    # Backtest Parameters
    st.sidebar.subheader("Backtest Parameters")
    h = st.sidebar.number_input("Horizon (h)", min_value=1, value=7, help="Forecast horizon steps.")
    n_windows = st.sidebar.number_input("Number of Windows", min_value=1, value=1, help="Number of backtest windows.")
    step_size = st.sidebar.number_input("Step Size", min_value=1, value=7, help="Step size between windows.")
    level_input = st.sidebar.text_input("Confidence Levels (comma separated)", value="80, 90", help="e.g., 80, 90")

    try:
        # Convert to integers if possible (e.g. 80.0 -> 80), otherwise float
        level = []
        for x in level_input.split(","):
            if x.strip():
                val = float(x.strip())
                if val.is_integer():
                    level.append(int(val))
                else:
                    level.append(val)
    except ValueError:
        st.sidebar.error("Invalid format for Confidence Levels.")
        level = [80, 90]

    if 'df' in st.session_state:
        df = st.session_state['df']
        current_ticker = st.session_state.get('ticker', ticker)

        st.subheader(f"Historical Data: {current_ticker}")
        st.dataframe(df.tail())

        st.line_chart(df.set_index('ds')['y'])

        if st.button("Run Backtest"):
            if not api_key:
                st.error("API Key is missing.")
            else:
                try:
                    nixtla_client = NixtlaClient(api_key=api_key)
                    with st.spinner("Running Backtest with TimeGPT..."):
                        cv_df = nixtla_client.cross_validation(
                            df=df,
                            h=h,
                            n_windows=n_windows,
                            step_size=step_size,
                            level=level,
                            freq=freq,
                            model=model
                        )

                    st.subheader("Backtest Results")
                    st.dataframe(cv_df.head())

                    # Metrics
                    st.markdown("### Performance Metrics")
                    from utilsforecast.losses import mae, rmse, mape
                    from utilsforecast.evaluation import evaluate

                    eval_df = evaluate(
                        cv_df,
                        metrics=[mae, rmse, mape],
                        target_col='y',
                        models=['TimeGPT']
                    )
                    st.table(eval_df)

                    # Visualization using Plotly
                    st.markdown("### Visualization")

                    fig = go.Figure()

                    # Actuals
                    fig.add_trace(go.Scatter(
                        x=df['ds'],
                        y=df['y'],
                        mode='lines',
                        name='Actual',
                        line=dict(color='black')
                    ))

                    # Forecasts
                    unique_cutoffs = cv_df['cutoff'].unique()
                    colors = ['blue', 'red', 'green', 'orange', 'purple']

                    for i, cutoff in enumerate(unique_cutoffs):
                        cutoff_df = cv_df[cv_df['cutoff'] == cutoff]
                        color = colors[i % len(colors)]

                        fig.add_trace(go.Scatter(
                            x=cutoff_df['ds'],
                            y=cutoff_df['TimeGPT'],
                            mode='lines',
                            name=f'Forecast (Cutoff {pd.to_datetime(cutoff).date()})',
                            line=dict(color=color)
                        ))

                        # Plot intervals
                        if level:
                            # Use level[0]
                            lv = level[0]
                            # Handle both int and float formatting in column names if needed
                            # Nixtla SDK standardizes to integers if passed as such, or floats.
                            # We check for existence.
                            lo_col = f"TimeGPT-lo-{lv}"
                            hi_col = f"TimeGPT-hi-{lv}"

                            # Fallback if column not found (maybe it was 80.0)
                            if lo_col not in cutoff_df.columns:
                                lo_col = f"TimeGPT-lo-{float(lv)}"
                                hi_col = f"TimeGPT-hi-{float(lv)}"

                            if lo_col in cutoff_df.columns and hi_col in cutoff_df.columns:
                                fig.add_trace(go.Scatter(
                                    x=cutoff_df['ds'],
                                    y=cutoff_df[hi_col],
                                    mode='lines',
                                    line=dict(width=0),
                                    showlegend=False,
                                    hoverinfo='skip'
                                ))
                                fig.add_trace(go.Scatter(
                                    x=cutoff_df['ds'],
                                    y=cutoff_df[lo_col],
                                    mode='lines',
                                    line=dict(width=0),
                                    fill='tonexty',
                                    fillcolor=f"rgba(0,0,255,0.1)",
                                    name=f'{lv}% Interval',
                                    showlegend=False,
                                    hoverinfo='skip'
                                ))

                    fig.update_layout(title=f"Backtest Results for {current_ticker}", xaxis_title="Date", yaxis_title="Price")
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"An error occurred during backtest: {e}")

if __name__ == "__main__":
    main()
