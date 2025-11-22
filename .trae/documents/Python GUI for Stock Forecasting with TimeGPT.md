## Overview
- Build a desktop Python GUI to load a stock `.tsv` file, select a training data range and prediction length, run TimeGPT forecasting, and plot forecasts alongside actuals to the end of the prediction period.
- Expose all relevant TimeGPT forecasting parameters with sensible defaults and an Advanced panel.

## Tech Stack
- GUI: Tkinter (builtin), ttk widgets.
- Data: pandas for TSV loading (`sep='\t'`).
- Plotting: matplotlib embedded in Tkinter (`FigureCanvasTkAgg`).
- Forecasting: `nixtla.NixtlaClient` using `NIXTLA_API_KEY` (env) or user input field.

## Data Assumptions
- Minimal columns: time, target; optional id for multi-series.
- Configurable column mapping: `id_col`, `time_col`, `target_col` with defaults (`unique_id`, `ds`, `y`).
- Date parsing: auto via pandas `parse_dates` when time column is detected; manual format input optional.

## UI Layout
- Top bar: API key (text, prefilled from env), Base URL (optional), Load File button (TSV), Column selectors (comboboxes for time/target/id).
- Training range: From/To inputs (date/time strings) with quick-fill buttons (min/max), plus frequency dropdown.
- Prediction settings: Horizon `h` (int), Model dropdown (`timegpt-1`, `timegpt-1-long-horizon`).
- Confidence/Quantiles: `level` multi-select (80, 90, 95), or quantile list.
- Advanced panel (collapsible): finetune steps/depth/loss, finetuned model id, `date_features`, `date_features_to_one_hot`, `add_history`, `clean_ex_first`, `feature_contributions`, `multivariate`, `model_parameters` (JSON), `num_partitions`.
- Actions: Run Forecast, Clear Plot.
- Plot area: matplotlib canvas; legend toggle.
- Status bar: validation messages, API key check result.

## Workflow
1. Read TSV via file dialog: `pd.read_csv(path, sep='\t')`.
2. Let user choose columns; validate presence and types.
3. Optional: infer frequency automatically; allow override.
4. Training window: filter DataFrame between From/To; ensure sorted by time and continuous frequency where feasible.
5. Create `NixtlaClient(api_key=... or env)`; optionally validate key.
6. Call `forecast(df=filtered_df, h=..., freq=..., id_col=..., time_col=..., target_col=..., level=..., quantiles=..., finetune_steps=..., finetune_depth=..., finetune_loss=..., finetuned_model_id=..., clean_ex_first=..., hist_exog_list=None, validate_api_key=False, add_history=..., date_features=..., date_features_to_one_hot=..., model=..., num_partitions=None, feature_contributions=..., model_parameters=..., multivariate=...)`.
7. Receive forecast DataFrame; merge with actuals to construct plotting frame through the end of prediction horizon.
8. Plot lines:
   - Actuals: full dataset up to max available (if available beyond training window, include for comparison).
   - Forecast: predicted mean line.
   - Intervals: shaded regions for `level` (if provided).
9. Show tabular summary (optional): last N actuals and first N forecasts.

## Adjustable Parameters (UI)
- Basic:
  - `h` (horizon), `freq` (auto/explicit), `model` (`timegpt-1`, `timegpt-1-long-horizon`).
  - `level` (e.g., 80/90/95), `quantiles` (mutually exclusive with level).
- Data mapping:
  - `id_col`, `time_col`, `target_col` comboboxes.
- Fine-tuning:
  - `finetune_steps`, `finetune_depth` (1–5), `finetune_loss` (`default`, `mae`, `mse`, `rmse`, `mape`, `smape`).
  - `finetuned_model_id`.
- Features & history:
  - `date_features` (True/list/function), `date_features_to_one_hot`.
  - `add_history` (include fitted values), `clean_ex_first`.
- Explainability & multivariate:
  - `feature_contributions` (requires exogenous X), `multivariate`.
- Advanced:
  - `model_parameters` (JSON dict), `num_partitions`.
- Connectivity:
  - `api_key` (defaults to env), `base_url` (optional).

## Plotting & Comparison
- Extend actuals line to the end of the forecast horizon when ground truth exists; otherwise show actuals up to last known timestamp and forecasts beyond.
- Display prediction intervals bands for each `level`.
- Provide toggles to hide/show intervals and series.

## Validation & Errors
- Input validation: required columns, non-empty training window, numeric horizon, mutually exclusive `level` vs `quantiles`.
- API errors surfaced in status bar (HTTP status and brief body).
- Safe defaults: auto frequency, `model=timegpt-1`, omit advanced unless toggled.

## Implementation Plan
- Single script: `stock_forecast_gui.py` under project root or `tools/`.
- Structure:
  - `App` class (Tk root, state, widget wiring).
  - `DataLoader` functions (TSV load, type inference, window filter).
  - `ForecastRunner` (client creation, call, response handling).
  - `Plotter` (matplotlib canvas, draw/update).
- No secrets persisted; read API key from env or transient input.

## Next Steps
- Confirm the plan and preferred location for the script.
- Implement, test with a sample `.tsv`, and deliver the runnable GUI with usage notes.
