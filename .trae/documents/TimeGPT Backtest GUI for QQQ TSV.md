## Overview
- Build an interactive GUI (Jupyter notebook with ipywidgets) to backtest TimeGPT on `C:\Users\juesh\OneDrive\Documents\windsurf\stock_data\QQQ_stock_data.tsv`.
- User selects the training period (date range) and forecast horizon; app calls TimeGPT, overlays forecasts with actuals, and displays the point-by-point delta and summary error metrics.

## UX & Controls
- `API Key` input: secure text box; sets `NIXTLA_API_KEY` for the session.
- `Date range` selectors: start and end date for the training window.
- `Horizon (steps)` input: integer number of future timesteps to predict.
- `Target column` dropdown: auto-detected from TSV (defaults to typical stock columns like `Close`).
- `Model` dropdown: `timegpt-1` or `timegpt-1-long-horizon`.
- `Run` button: triggers forecasting; `Reset` clears selections.

## Data Ingest
- Load TSV with `pandas.read_csv(sep='\t')`.
- Normalize schema to TimeGPT format: `unique_id` (constant `QQQ`), `ds` (parsed datetime), `y` (selected target column).
- Infer frequency automatically; handle timezone-naive/aware timestamps.
- Robust column handling: try common date columns (`Date`, `Datetime`, `ds`) and target columns (`Close`, `Adj Close`, `y`); allow manual override via dropdown.

## Forecast Logic
- Use `NixtlaClient.forecast` (`nixtla/nixtla_client.py:1446`) with selected `h`, inferred `freq`, `id_col='unique_id'`, `time_col='ds'`, `target_col='y'`.
- Restrict input to the chosen training date range; horizon forecasts extend forward from the last training timestamp.
- Warn if `h` exceeds model horizon and suggest switching to `timegpt-1-long-horizon`.
- Optional: allow `level=[80, 95]` toggle to show prediction intervals (off by default).

## Visualization
- Overlay plot: actual vs. forecast using `plotly` if available, else `matplotlib`.
- Delta series: plot `actual - forecast` for the forecast window; color code positive/negative deltas.
- Metrics: display MAE, RMSE, MAPE over the forecast window; show last value delta.
- Tooltips with timestamps and values; legend to toggle series.

## Error Handling
- Missing API key: show inline message and disable `Run` until set.
- Invalid dates/horizon: validate and show concise errors.
- Data gaps/irregular timestamps: surface friendly guidance if frequency cannot be inferred.

## File Placement & Run
- Deliver as `nbs/timegpt_backtest_gui.ipynb` to run inside the already-active Jupyter Lab.
- No external servers or new dependencies required; relies on `pandas` and repo’s `nixtla` client. Falls back to `matplotlib` if `plotly` is unavailable.

## Verification
- Use the provided TSV to run at least two scenarios:
  - Short horizon (e.g., 10 steps) with a recent training window.
  - Longer horizon (e.g., 60 steps) using `timegpt-1-long-horizon`.
- Confirm overlays, deltas, and metrics, and validate frequency inference.

## Acceptance
- After approval, I will implement the notebook, wire up widgets, integrate TimeGPT calls, and test end-to-end in the current Jupyter session.

Please confirm this plan so I can proceed with implementation.