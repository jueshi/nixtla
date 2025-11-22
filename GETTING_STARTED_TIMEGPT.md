# Getting Started with Nixtla TimeGPT

## What It Is

- Python SDK to use TimeGPT for time‑series forecasting and anomaly detection.
- Main entry point: `NixtlaClient` in `nixtla/nixtla_client.py`.

## Install

```bash
pip install nixtla>=0.7.0
```

Optional extras:

- Plotting helpers: `pip install "nixtla[plotting]"`
- Date features (holidays/calendars): `pip install "nixtla[date_extras]"`
- Distributed support (Fugue/Dask/Ray/Spark): `pip install "nixtla[distributed]"`

## Set API Key (Windows)

- Get your key at https://dashboard.nixtla.io
- Temporary (current PowerShell session):

```powershell
$env:NIXTLA_API_KEY="YOUR_API_KEY"
```

- Persistent:

```powershell
setx NIXTLA_API_KEY "YOUR_API_KEY"
```

- Or pass it directly when creating the client:

```python
from nixtla import NixtlaClient
nixtla_client = NixtlaClient(api_key="YOUR_API_KEY")
```

## Quickstart: Forecast

Using default column names (`unique_id`, `ds`, `y`):

```python
import pandas as pd
from nixtla import NixtlaClient

nixtla_client = NixtlaClient()  # reads NIXTLA_API_KEY
df = pd.read_csv(
    "https://raw.githubusercontent.com/Nixtla/transfer-learning-time-series/main/datasets/electricity-short.csv"
)
fcst_df = nixtla_client.forecast(df, h=24, level=[80, 90])
# Optional plot
nixtla_client.plot(df, fcst_df, level=[80, 90])
```

Custom columns:

```python
fcst_df = nixtla_client.forecast(
    df,
    h=24,
    id_col="series_id",
    time_col="timestamp",
    target_col="value",
)
```

## Quickstart: Anomaly Detection

```python
import pandas as pd
from nixtla import NixtlaClient

nixtla_client = NixtlaClient()
df = pd.read_csv("https://datasets-nixtla.s3.amazonaws.com/peyton-manning.csv")
anomalies_df = nixtla_client.detect_anomalies(
    df, time_col="timestamp", target_col="value", freq="D"
)
# Optional plot
nixtla_client.plot(df, anomalies_df, time_col="timestamp", target_col="value")
```

## Data Format

- Single series: provide `time_col` and `target_col`.
- Multiple series: stack rows and include `id_col` (default `unique_id`).
- Defaults: `id_col="unique_id"`, `time_col="ds"`, `target_col="y"`.
- Add exogenous regressors with `X_df` (future) or `hist_exog_list` (historical).

## Helpful Options

- `level=[80, 95]` adds prediction intervals.
- `model="timegpt-1-long-horizon"` for long horizons.
- `date_features=True` to automatically add time‑based features.
- `feature_contributions=True` to compute SHAP over exogenous features.
- `validate_api_key=True` to proactively check your key.

## Troubleshooting

- Authorization errors: ensure `NIXTLA_API_KEY` is set or passed; test with `nixtla_client.validate_api_key()`.
- Column mismatches: specify `id_col`, `time_col`, `target_col` to match your DataFrame.
- Horizon warnings: for very long `h`, consider `model="timegpt-1-long-horizon"`.

## Learn More

- Repo quickstart and examples: `README.md` in this repo.
- Notebooks: `nbs/docs/getting-started/2_quickstart.ipynb` and `nbs/docs/capabilities/forecast/01_quickstart.ipynb`.
- Docs site: https://docs.nixtla.io