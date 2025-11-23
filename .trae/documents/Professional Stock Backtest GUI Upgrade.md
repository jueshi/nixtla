## Overview
- Build a polished Streamlit app (`stock_forecast_gui.py`) for TimeGPT stock backtesting with professional layout, robust validations, and exportable results.
- Keep core forecasting via `NixtlaClient.forecast` (nixtla/nixtla_client.py:1446) and use Plotly visuals.

## Dependencies
- Add `streamlit` (and use existing `pandas`, `plotly` if available; fallback to `matplotlib` for charts if Plotly missing).
- Optional: `python -m pip install streamlit plotly` if not already present.

## App Structure
- Sidebar: API Key (masked), TSV file picker/uploader, target column, frequency (`B`, `D`, `W`, `MS`, `H`), model selection, date range, horizon.
- Main:
  - Metrics cards: MAE, RMSE, MAPE, coverage (% of forecast points with actuals).
  - Interactive Plotly chart with Actual (training), Forecast, Actual (future), Delta bars.
  - Data table of forecast results.
  - Export buttons (CSV of forecasts, PNG of chart).

## Defaults
- Pre-fill Start `2024-08-15`, End `2025-08-15`.
- Horizon auto-computed as business days from `2025-08-16` to `2025-10-16`.
- Default `Freq='B'` for business-day stock data.

## Data & Validation
- Read TSV with `pandas.read_csv(sep='\t')`.
- Detect time and target columns with reasonable defaults; allow override.
- Clean training slice to match selected frequency (dedupe, reindex, fill) before forecasting.
- Evaluation uses the full dataset for the forecast window to compute metrics and delta.
- Clear error messages for missing API key, bad dates, invalid horizon, frequency mismatches (point to docs when needed).

## Forecast Logic
- Use `NixtlaClient` with `freq` from UI; model options: `timegpt-1`, `timegpt-1-long-horizon`.
- Optional intervals: toggle `level=[80, 95]` to show prediction bands.

## Visuals
- Plotly theme with readable labels and legend toggles.
- Hover tooltips for timestamp, actual, forecast, delta.
- Responsive layout; cards styled using Streamlit containers/columns.

## Performance
- Cache parsed TSV and column detection (`st.cache_data`) keyed by file path and timestamp to keep UI snappy.
- Spinner during API calls; concise error banners.

## Delivery & Run
- Implement `stock_forecast_gui.py` in repo root.
- Run with `streamlit run stock_forecast_gui.py`.
- No changes to core client code; app confined to the new file and minimal dependency.

## Next
- After approval, I will implement the Streamlit app, wire forecasting and visuals, and test with your QQQ TSV.