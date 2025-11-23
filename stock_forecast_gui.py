import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from nixtla import NixtlaClient
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        self.id = None
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)
    def enter(self, event=None):
        self.schedule()
    def leave(self, event=None):
        self.unschedule()
        self.hide()
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.show)
    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
    def show(self):
        if self.tip or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=6, ipady=4)
    def hide(self):
        if self.tip:
            self.tip.destroy()
            self.tip = None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("TimeGPT Stock Forecast GUI")
        self.df = None
        self.filtered_df = None
        self._tooltips = []
        self.api_key_var = tk.StringVar(value=os.getenv("NIXTLA_API_KEY", ""))
        self.base_url_var = tk.StringVar(value=os.getenv("NIXTLA_BASE_URL", ""))
        self.file_path_var = tk.StringVar()
        self.id_col_var = tk.StringVar(value="unique_id")
        self.time_col_var = tk.StringVar(value="ds")
        self.target_col_var = tk.StringVar(value="y")
        self.series_id_var = tk.StringVar()
        self.freq_var = tk.StringVar(value="")
        self.h_var = tk.IntVar(value=24)
        self.model_var = tk.StringVar(value="timegpt-1")
        self.level_var = tk.StringVar(value="80,90")
        self.quantiles_var = tk.StringVar(value="")
        self.start_var = tk.StringVar(value="")
        self.end_var = tk.StringVar(value="")
        self.add_history_var = tk.BooleanVar(value=False)
        self.date_features_var = tk.BooleanVar(value=False)
        self.date_features_oh_var = tk.BooleanVar(value=False)
        self.clean_ex_first_var = tk.BooleanVar(value=True)
        self.feature_contrib_var = tk.BooleanVar(value=False)
        self.multivariate_var = tk.BooleanVar(value=False)
        self.auto_fix_ts_var = tk.BooleanVar(value=True)
        self.impute_target_var = tk.BooleanVar(value=True)
        self.impute_method_var = tk.StringVar(value="ffill_bfill")
        self.auto_fix_ts_var = tk.BooleanVar(value=True)
        self.finetune_steps_var = tk.IntVar(value=0)
        self.finetune_depth_var = tk.IntVar(value=1)
        self.finetune_loss_var = tk.StringVar(value="default")
        self.finetuned_model_id_var = tk.StringVar(value="")
        self.model_params_var = tk.StringVar(value="")
        self.advanced_visible = False
        self.figure = None
        self.canvas = None
        self.display_start_var = tk.StringVar(value="")
        self.display_end_var = tk.StringVar(value="")
        self.last_fcst_df = None
        self.last_id_col = None
        self.last_time_col = None
        self.last_target_col = None
        self.last_levels = None
        self.last_quantiles = None
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=8, pady=8)
        ttk.Label(top, text="API Key").grid(row=0, column=0, sticky=tk.W)
        self.api_key_entry = ttk.Entry(top, textvariable=self.api_key_var, width=40)
        self.api_key_entry.grid(row=0, column=1, sticky=tk.W)
        ttk.Label(top, text="Base URL").grid(row=0, column=2, sticky=tk.W)
        self.base_url_entry = ttk.Entry(top, textvariable=self.base_url_var, width=40)
        self.base_url_entry.grid(row=0, column=3, sticky=tk.W)
        self.load_btn = ttk.Button(top, text="Load Data", command=self.load_file)
        self.load_btn.grid(row=0, column=4, padx=6)

        cols = ttk.Frame(self.root)
        cols.pack(fill=tk.X, padx=8)
        ttk.Label(cols, text="Time Col").grid(row=0, column=0, sticky=tk.W)
        self.time_col_cb = ttk.Combobox(cols, textvariable=self.time_col_var, values=[], width=20)
        self.time_col_cb.grid(row=0, column=1)
        ttk.Label(cols, text="Target Col").grid(row=0, column=2, sticky=tk.W)
        self.target_col_cb = ttk.Combobox(cols, textvariable=self.target_col_var, values=[], width=20)
        self.target_col_cb.grid(row=0, column=3)
        ttk.Label(cols, text="ID Col").grid(row=0, column=4, sticky=tk.W)
        self.id_col_cb = ttk.Combobox(cols, textvariable=self.id_col_var, values=[], width=20)
        self.id_col_cb.grid(row=0, column=5)
        ttk.Label(cols, text="Series ID").grid(row=0, column=6, sticky=tk.W)
        self.series_id_cb = ttk.Combobox(cols, textvariable=self.series_id_var, values=[], width=20)
        self.series_id_cb.grid(row=0, column=7)

        rng = ttk.Frame(self.root)
        rng.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(rng, text="Train From").grid(row=0, column=0)
        self.start_entry = ttk.Entry(rng, textvariable=self.start_var, width=20)
        self.start_entry.grid(row=0, column=1)
        ttk.Label(rng, text="Train To").grid(row=0, column=2)
        self.end_entry = ttk.Entry(rng, textvariable=self.end_var, width=20)
        self.end_entry.grid(row=0, column=3)
        ttk.Label(rng, text="Freq").grid(row=0, column=4)
        self.freq_entry = ttk.Entry(rng, textvariable=self.freq_var, width=10)
        self.freq_entry.grid(row=0, column=5)
        ttk.Button(rng, text="Use Full Range", command=self.use_full_range).grid(row=0, column=6, padx=6)

        pred = ttk.Frame(self.root)
        pred.pack(fill=tk.X, padx=8)
        ttk.Label(pred, text="Horizon").grid(row=0, column=0)
        self.h_entry = ttk.Entry(pred, textvariable=self.h_var, width=8)
        self.h_entry.grid(row=0, column=1)
        ttk.Label(pred, text="Model").grid(row=0, column=2)
        self.model_cb = ttk.Combobox(pred, textvariable=self.model_var, values=["timegpt-1", "timegpt-1-long-horizon"], width=24)
        self.model_cb.grid(row=0, column=3)
        self.model_cb.bind("<<ComboboxSelected>>", lambda e: self.on_model_change())
        self.on_model_change()
        ttk.Label(pred, text="Level").grid(row=0, column=4)
        self.level_entry = ttk.Entry(pred, textvariable=self.level_var, width=16)
        self.level_entry.grid(row=0, column=5)
        ttk.Label(pred, text="Quantiles").grid(row=0, column=6)
        self.quantiles_entry = ttk.Entry(pred, textvariable=self.quantiles_var, width=16)
        self.quantiles_entry.grid(row=0, column=7)

        disp = ttk.Frame(self.root)
        disp.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(disp, text="Display From").grid(row=0, column=0)
        self.display_start_entry = ttk.Entry(disp, textvariable=self.display_start_var, width=20)
        self.display_start_entry.grid(row=0, column=1)
        ttk.Label(disp, text="Display To").grid(row=0, column=2)
        self.display_end_entry = ttk.Entry(disp, textvariable=self.display_end_var, width=20)
        self.display_end_entry.grid(row=0, column=3)

        adv_toggle = ttk.Button(self.root, text="Show Advanced", command=self.toggle_advanced)
        adv_toggle.pack(padx=8, pady=6, anchor=tk.W)

        self.adv = ttk.Frame(self.root)
        self._build_advanced(self.adv)

        actions = ttk.Frame(self.root)
        actions.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(actions, text="Run Forecast", command=self.run_forecast).pack(side=tk.LEFT)
        ttk.Button(actions, text="Visualize Data", command=self.visualize_data).pack(side=tk.LEFT, padx=6)
        ttk.Button(actions, text="Clear Plot", command=self.clear_plot).pack(side=tk.LEFT)
        ttk.Button(actions, text="Update Plot", command=self.update_plot).pack(side=tk.LEFT, padx=6)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var).pack(fill=tk.X, padx=8, pady=4)

        plotf = ttk.Frame(self.root)
        plotf.pack(fill=tk.BOTH, expand=True)
        self.plot_frame = plotf
        self.load_default_file()

    def _build_advanced(self, frame):
        g1 = ttk.Frame(frame)
        g1.pack(fill=tk.X, padx=8)
        self.add_history_cb = ttk.Checkbutton(g1, text="Add History", variable=self.add_history_var)
        self.add_history_cb.grid(row=0, column=0, sticky=tk.W)
        self.date_features_cb = ttk.Checkbutton(g1, text="Date Features", variable=self.date_features_var)
        self.date_features_cb.grid(row=0, column=1, sticky=tk.W)
        self.date_features_oh_cb = ttk.Checkbutton(g1, text="One-Hot Date Features", variable=self.date_features_oh_var)
        self.date_features_oh_cb.grid(row=0, column=2, sticky=tk.W)
        self.clean_ex_first_cb = ttk.Checkbutton(g1, text="Clean Exogenous First", variable=self.clean_ex_first_var)
        self.clean_ex_first_cb.grid(row=0, column=3, sticky=tk.W)
        self.feature_contrib_cb = ttk.Checkbutton(g1, text="Feature Contributions", variable=self.feature_contrib_var)
        self.feature_contrib_cb.grid(row=0, column=4, sticky=tk.W)
        self.multivariate_cb = ttk.Checkbutton(g1, text="Multivariate", variable=self.multivariate_var)
        self.multivariate_cb.grid(row=0, column=5, sticky=tk.W)
        self.auto_fix_ts_cb = ttk.Checkbutton(g1, text="Auto-fix timestamps (dedupe & fill gaps)", variable=self.auto_fix_ts_var)
        self.auto_fix_ts_cb.grid(row=0, column=6, sticky=tk.W)

        g1b = ttk.Frame(frame)
        g1b.pack(fill=tk.X, padx=8)
        self.impute_target_cb = ttk.Checkbutton(g1b, text="Impute Missing Target", variable=self.impute_target_var)
        self.impute_target_cb.grid(row=0, column=0, sticky=tk.W)
        ttk.Label(g1b, text="Method").grid(row=0, column=1, sticky=tk.W)
        self.impute_method_cb = ttk.Combobox(g1b, textvariable=self.impute_method_var, values=["ffill","bfill","ffill_bfill","interpolate","interpolate_ffill_bfill"], width=12)
        self.impute_method_cb.grid(row=0, column=2, sticky=tk.W)
        self.auto_fix_ts_cb = ttk.Checkbutton(g1, text="Auto-fix timestamps (dedupe & fill gaps)", variable=self.auto_fix_ts_var)
        self.auto_fix_ts_cb.grid(row=0, column=6, sticky=tk.W)

        g2 = ttk.Frame(frame)
        g2.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(g2, text="Finetune Steps").grid(row=0, column=0)
        self.finetune_steps_entry = ttk.Entry(g2, textvariable=self.finetune_steps_var, width=8)
        self.finetune_steps_entry.grid(row=0, column=1)
        ttk.Label(g2, text="Finetune Depth").grid(row=0, column=2)
        self.finetune_depth_entry = ttk.Entry(g2, textvariable=self.finetune_depth_var, width=8)
        self.finetune_depth_entry.grid(row=0, column=3)
        ttk.Label(g2, text="Finetune Loss").grid(row=0, column=4)
        self.finetune_loss_cb = ttk.Combobox(g2, textvariable=self.finetune_loss_var, values=["default","mae","mse","rmse","mape","smape"], width=12)
        self.finetune_loss_cb.grid(row=0, column=5)
        ttk.Label(g2, text="Finetuned Model ID").grid(row=0, column=6)
        self.finetuned_model_id_entry = ttk.Entry(g2, textvariable=self.finetuned_model_id_var, width=18)
        self.finetuned_model_id_entry.grid(row=0, column=7)

        g3 = ttk.Frame(frame)
        g3.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(g3, text="Model Parameters (JSON)").grid(row=0, column=0, sticky=tk.W)
        self.model_params_entry = ttk.Entry(g3, textvariable=self.model_params_var, width=80)
        self.model_params_entry.grid(row=0, column=1, sticky=tk.W)
        self.add_tooltips()

    def add_tooltip(self, widget, text):
        t = Tooltip(widget, text)
        self._tooltips.append(t)

    def add_tooltips(self):
        self.add_tooltip(self.api_key_entry, "API key for TimeGPT. Leave blank to use NIXTLA_API_KEY env.")
        self.add_tooltip(self.base_url_entry, "Optional custom base URL, e.g., https://api.nixtla.io")
        self.add_tooltip(self.load_btn, "Load TSV or CSV data file")
        self.add_tooltip(self.time_col_cb, "Time column name. Parsed as datetime.")
        self.add_tooltip(self.target_col_cb, "Target value column name.")
        self.add_tooltip(self.id_col_cb, "ID column for multiple series. Leave empty for single series.")
        self.add_tooltip(self.series_id_cb, "Select specific series when ID column exists.")
        self.add_tooltip(self.start_entry, "Training start time. Leave empty to use earliest.")
        self.add_tooltip(self.end_entry, "Training end time. Leave empty to use latest.")
        self.add_tooltip(self.freq_entry, "Frequency, e.g., D, H, 15T. Leave empty to infer. For daily stocks, prefer B (Business Day).")
        self.add_tooltip(self.auto_fix_ts_cb, "Ensures continuous timestamps by de-duplicating and filling missing dates.")
        self.add_tooltip(self.impute_target_cb, "Fill missing target values created by the time grid.")
        self.add_tooltip(self.impute_method_cb, "Choose ffill/bfill/ffill_bfill/interpolate for imputation.")
        self.add_tooltip(self.h_entry, "Forecast horizon h (integer).")
        self.add_tooltip(self.model_cb, "Model: timegpt-1 or timegpt-1-long-horizon.")
        self.add_tooltip(self.level_entry, "Confidence levels comma-separated, e.g., 80,90. Not with quantiles.")
        self.add_tooltip(self.quantiles_entry, "Quantiles comma-separated in 0-1, e.g., 0.1,0.5,0.9. Not with levels.")
        self.add_tooltip(self.add_history_cb, "Return fitted values of the model.")
        self.add_tooltip(self.date_features_cb, "Add date-based features.")
        self.add_tooltip(self.date_features_oh_cb, "One-hot encode date features.")
        self.add_tooltip(self.clean_ex_first_cb, "Clean exogenous signals before forecasting.")
        self.add_tooltip(self.feature_contrib_cb, "Compute feature contributions (SHAP). Requires exogenous X.")
        self.add_tooltip(self.multivariate_cb, "Enable multivariate predictions.")
        self.add_tooltip(self.finetune_steps_entry, "Finetune steps. 0 to disable.")
        self.add_tooltip(self.finetune_depth_entry, "Finetune depth 1-5.")
        self.add_tooltip(self.finetune_loss_cb, "Finetune loss function.")
        self.add_tooltip(self.finetuned_model_id_entry, "Use a previously finetuned model ID.")
        self.add_tooltip(self.model_params_entry, "JSON dict for model parameters.")
        self.add_tooltip(self.display_start_entry, "Plot start time. Leave empty to auto.")
        self.add_tooltip(self.display_end_entry, "Plot end time. Leave empty to auto.")

    def toggle_advanced(self):
        if self.advanced_visible:
            self.adv.pack_forget()
            self.advanced_visible = False
        else:
            self.adv.pack(fill=tk.X)
            self.advanced_visible = True

    def load_file(self, path=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("TSV files","*.tsv"), ("CSV files","*.csv"), ("All files","*.*")])
        if not path:
            return
        try:
            ext = os.path.splitext(path)[1].lower()
            sep = "\t" if ext == ".tsv" else ","
            df = pd.read_csv(path, sep=sep)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.df = df
        self.file_path_var.set(path)
        self.update_columns()
        self.status_var.set(f"Loaded {os.path.basename(path)} ({len(df)} rows)")

    def load_default_file(self):
        default_path = r"C:\Users\JueShi\Downloads\QQQ_stock_data.tsv"
        if os.path.exists(default_path):
            try:
                self.load_file(default_path)
            except Exception:
                pass

    def update_columns(self):
        if self.df is None:
            return
        cols = list(self.df.columns)
        self.time_col_cb["values"] = cols
        self.target_col_cb["values"] = cols
        self.id_col_cb["values"] = [""] + cols
        if self.id_col_var.get() in cols:
            ids = sorted(self.df[self.id_col_var.get()].dropna().unique().tolist())
        else:
            ids = []
        self.series_id_cb["values"] = ids
        if len(ids) > 0:
            self.series_id_var.set(ids[0])
        if self.time_col_var.get() in cols:
            try:
                s = pd.to_datetime(self.df[self.time_col_var.get()], errors="coerce")
                s_valid = s.dropna()
                if not s_valid.empty:
                    self.start_var.set(str(s_valid.min()))
                    self.end_var.set(str(s_valid.max()))
                    sf = self._suggest_freq(s_valid)
                    if sf:
                        self.freq_var.set(sf)
            except Exception:
                pass

    def use_full_range(self):
        if self.df is None or self.time_col_var.get() == "":
            return
        try:
            s = pd.to_datetime(self.df[self.time_col_var.get()], errors="coerce")
            s_valid = s.dropna()
            if not s_valid.empty:
                self.start_var.set(str(s_valid.min()))
                self.end_var.set(str(s_valid.max()))
        except Exception:
            pass

    def _suggest_freq(self, s: pd.Series):
        try:
            s_sorted = s.sort_values()
            inf = pd.infer_freq(s_sorted)
            if inf:
                return inf
            diffs = s_sorted.diff().dropna()
            if not diffs.empty:
                mode = diffs.mode().iloc[0]
                days = getattr(mode, 'days', None)
                if days == 1:
                    weekday_counts = s_sorted.dt.weekday.value_counts()
                    if weekday_counts.get(5, 0) == 0 and weekday_counts.get(6, 0) == 0:
                        return 'B'
                    return 'D'
            return None
        except Exception:
            return None

    def _auto_fix_timestamps(self, df: pd.DataFrame, id_col: str | None, time_col: str, target_col: str, freq: str | None) -> pd.DataFrame:
        if id_col and id_col in df.columns:
            df = df.drop_duplicates(subset=[id_col, time_col], keep='last')
        else:
            df = df.drop_duplicates(subset=[time_col], keep='last')
        if not freq:
            return df
        def grid_group(g: pd.DataFrame) -> pd.DataFrame:
            idx = pd.date_range(start=g[time_col].min(), end=g[time_col].max(), freq=freq)
            g2 = g.set_index(time_col).reindex(idx)
            g2.index.name = time_col
            g2 = g2.reset_index()
            if id_col and id_col in g.columns:
                g2[id_col] = g[id_col].iloc[0]
            return g2
        if id_col and id_col in df.columns:
            out = (
                df.groupby(id_col, observed=True, sort=False)
                .apply(grid_group, include_groups=False)
                .reset_index(drop=True)
            )
        else:
            out = grid_group(df)
        return out

    def _supports_multivariate(self, model: str) -> bool:
        # Default TimeGPT models in this GUI do not support multivariate.
        return False

    def on_model_change(self):
        model = self.model_var.get()
        if not self._supports_multivariate(model):
            try:
                self.multivariate_var.set(False)
                self.multivariate_cb.state(["disabled"])
            except Exception:
                pass
        else:
            try:
                self.multivariate_cb.state(["!disabled"])
            except Exception:
                pass

    def _impute_target(self, df: pd.DataFrame, id_col: str | None, time_col: str, target_col: str, method: str) -> pd.DataFrame:
        if method == "ffill":
            if id_col and id_col in df.columns:
                df[target_col] = df.groupby(id_col, observed=True)[target_col].transform(lambda s: s.ffill())
            else:
                df[target_col] = df[target_col].ffill()
        elif method == "bfill":
            if id_col and id_col in df.columns:
                df[target_col] = df.groupby(id_col, observed=True)[target_col].transform(lambda s: s.bfill())
            else:
                df[target_col] = df[target_col].bfill()
        elif method == "ffill_bfill":
            if id_col and id_col in df.columns:
                df[target_col] = df.groupby(id_col, observed=True)[target_col].transform(lambda s: s.ffill().bfill())
            else:
                df[target_col] = df[target_col].ffill().bfill()
        elif method == "interpolate" or method == "interpolate_ffill_bfill":
            if id_col and id_col in df.columns:
                interp = df.groupby(id_col, observed=True).apply(lambda g: g.set_index(time_col)[target_col].interpolate(method="time")).reset_index(level=0, drop=True)
                df[target_col] = interp
            else:
                df = df.set_index(time_col)
                df[target_col] = df[target_col].interpolate(method="time")
                df = df.reset_index()
            if method == "interpolate_ffill_bfill":
                if id_col and id_col in df.columns:
                    df[target_col] = df.groupby(id_col, observed=True)[target_col].transform(lambda s: s.ffill().bfill())
                else:
                    df[target_col] = df[target_col].ffill().bfill()
        return df

    def _parse_levels(self):
        txt = self.level_var.get().strip()
        if not txt:
            return None
        try:
            return [float(x) for x in txt.split(",") if x.strip()]
        except Exception:
            return None

    def _parse_quantiles(self):
        txt = self.quantiles_var.get().strip()
        if not txt:
            return None
        try:
            return [float(x) for x in txt.split(",") if x.strip()]
        except Exception:
            return None

    def visualize_data(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Load a TSV file first")
            return
        id_col = self.id_col_var.get() if self.id_col_var.get() else None
        time_col = self.time_col_var.get()
        target_col = self.target_col_var.get()
        if not time_col or not target_col:
            messagebox.showwarning("Warning", "Select time and target columns")
            return

        try:
            import matplotlib
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception as e:
            messagebox.showerror("Error", "matplotlib is required: " + str(e))
            return

        self.clear_plot()
        fig = Figure(figsize=(9, 5), dpi=100)
        ax = fig.add_subplot(111)

        # Prepare actual data
        act_df = self.df.copy()
        act_df[time_col] = pd.to_datetime(act_df[time_col], errors="coerce")
        act_df[target_col] = pd.to_numeric(act_df[target_col], errors="coerce")
        act_df = act_df.dropna(subset=[time_col, target_col])

        if id_col in act_df.columns and self.series_id_var.get():
            act_df = act_df[act_df[id_col] == self.series_id_var.get()]

        act_df = act_df.sort_values(time_col)

        # Apply Display filters
        disp_start = self.display_start_var.get().strip()
        disp_end = self.display_end_var.get().strip()

        if disp_start:
            ds = pd.to_datetime(disp_start, errors="coerce")
            if pd.notna(ds):
                act_df = act_df[act_df[time_col] >= ds]
        if disp_end:
            de = pd.to_datetime(disp_end, errors="coerce")
            if pd.notna(de):
                act_df = act_df[act_df[time_col] <= de]

        if act_df.empty:
             messagebox.showinfo("Info", "No data to display in the selected range")
             return

        ax.plot(act_df[time_col], act_df[target_col], label="Actual", color="#1f77b4")

        ax.legend(loc="best")
        ax.set_title(f"Data Visualization: {self.series_id_var.get() if self.series_id_var.get() else 'All Series'}")
        ax.set_xlabel(time_col)
        ax.set_ylabel(target_col)

        self.figure = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.status_var.set("Data visualization complete")

    def run_forecast(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Load a TSV file first")
            return
        id_col = self.id_col_var.get() if self.id_col_var.get() else None
        time_col = self.time_col_var.get()
        target_col = self.target_col_var.get()
        if not time_col or not target_col:
            messagebox.showwarning("Warning", "Select time and target columns")
            return
        try:
            df = self.df.copy()
            df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
            df[target_col] = pd.to_numeric(df[target_col], errors="coerce")
            df = df.dropna(subset=[time_col, target_col])
            if id_col and id_col in df.columns and self.series_id_var.get():
                df = df[df[id_col] == self.series_id_var.get()]
            s = df[time_col]
            start = self.start_var.get().strip()
            end = self.end_var.get().strip()
            if start:
                df = df[s >= pd.to_datetime(start)]
            if end:
                df = df[s <= pd.to_datetime(end)]
            df = df.sort_values(time_col)
            freq = self.freq_var.get().strip() or None
            if self.auto_fix_ts_var.get():
                df = self._auto_fix_timestamps(df, id_col, time_col, target_col, freq)
            if self.impute_target_var.get():
                df = self._impute_target(df, id_col, time_col, target_col, self.impute_method_var.get())
            if df[target_col].isna().any():
                messagebox.showerror("Error", f"Target column ({target_col}) cannot contain missing values.")
                return
            self.filtered_df = df
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        levels = self._parse_levels()
        quantiles = self._parse_quantiles()
        try:
            if id_col and id_col in self.filtered_df.columns:
                min_len = int(self.filtered_df.groupby(id_col)[time_col].count().min())
            else:
                min_len = int(len(self.filtered_df))
        except Exception:
            min_len = None
        if levels and min_len is not None and min_len < 25:
            messagebox.showinfo("Info", "Series too short for prediction intervals (need >=25). Proceeding without intervals.")
            levels = None
        if levels and quantiles:
            messagebox.showerror("Error", "Use level or quantiles, not both")
            return
        api_key = self.api_key_var.get().strip() or os.getenv("NIXTLA_API_KEY", "")
        if not api_key:
            messagebox.showerror("Error", "API key is required")
            return
        try:
            client = NixtlaClient(api_key=api_key, base_url=self.base_url_var.get().strip() or None)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        try:
            freq = self.freq_var.get().strip() or None
            mp = None
            if self.model_params_var.get().strip():
                mp = json.loads(self.model_params_var.get().strip())
            if self.multivariate_var.get() and not self._supports_multivariate(self.model_var.get()):
                messagebox.showinfo("Info", "Selected model does not support multivariate; proceeding univariate.")
                self.multivariate_var.set(False)
            res = client.forecast(
                df=self.filtered_df,
                h=int(self.h_var.get()),
                freq=freq,
                id_col=id_col or "unique_id",
                time_col=time_col,
                target_col=target_col,
                level=levels,
                quantiles=quantiles,
                finetune_steps=int(self.finetune_steps_var.get()),
                finetune_depth=int(self.finetune_depth_var.get()),
                finetune_loss=self.finetune_loss_var.get(),
                finetuned_model_id=self.finetuned_model_id_var.get().strip() or None,
                clean_ex_first=bool(self.clean_ex_first_var.get()),
                validate_api_key=False,
                add_history=bool(self.add_history_var.get()),
                date_features=bool(self.date_features_var.get()),
                date_features_to_one_hot=bool(self.date_features_oh_var.get()),
                model=self.model_var.get(),
                num_partitions=None,
                feature_contributions=bool(self.feature_contrib_var.get()),
                model_parameters=mp,
                multivariate=bool(self.multivariate_var.get()) and self._supports_multivariate(self.model_var.get()),
            )
            if hasattr(res, "to_pandas"):
                fcst_df = res.to_pandas()
            elif isinstance(res, pd.DataFrame):
                fcst_df = res
            else:
                try:
                    import fugue.api as fa
                    fcst_df = fa.as_pandas(res)
                except Exception:
                    fcst_df = pd.DataFrame(res)
            self.last_fcst_df = fcst_df
            self.last_id_col = id_col or "unique_id"
            self.last_time_col = time_col
            self.last_target_col = target_col
            self.last_levels = levels
            self.last_quantiles = quantiles
            self.plot_results(fcst_df, self.last_id_col, self.last_time_col, self.last_target_col, levels, quantiles)
            self.status_var.set("Forecast complete")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

    def clear_plot(self):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        self.figure = None

    def plot_results(self, fcst_df, id_col, time_col, target_col, levels, quantiles):
        try:
            import matplotlib
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception as e:
            messagebox.showerror("Error", "matplotlib is required: " + str(e))
            return
        self.clear_plot()
        fig = Figure(figsize=(9, 5), dpi=100)
        ax = fig.add_subplot(111)
        act_df = self.df.copy()
        act_df[time_col] = pd.to_datetime(act_df[time_col], errors="coerce")
        act_df = act_df.dropna(subset=[time_col, target_col])
        if id_col in act_df.columns and self.series_id_var.get():
            act_df = act_df[act_df[id_col] == self.series_id_var.get()]
        fcst_df = fcst_df.copy()
        fcst_df[time_col] = pd.to_datetime(fcst_df[time_col], errors="coerce")
        disp_start = self.display_start_var.get().strip()
        disp_end = self.display_end_var.get().strip()
        fcst_end = fcst_df[time_col].max()
        act_ext = act_df[act_df[time_col] <= fcst_end]
        if disp_start:
            ds = pd.to_datetime(disp_start, errors="coerce")
            if pd.notna(ds):
                act_ext = act_ext[act_ext[time_col] >= ds]
                fcst_df = fcst_df[fcst_df[time_col] >= ds]
        if disp_end:
            de = pd.to_datetime(disp_end, errors="coerce")
            if pd.notna(de):
                act_ext = act_ext[act_ext[time_col] <= de]
                fcst_df = fcst_df[fcst_df[time_col] <= de]
        ax.plot(act_ext[time_col], act_ext[target_col], label="Actual", color="#1f77b4")
        if "TimeGPT" in fcst_df.columns:
            train_end = None
            if self.filtered_df is not None and time_col in self.filtered_df.columns:
                train_end = pd.to_datetime(self.filtered_df[time_col], errors="coerce").max()
            if pd.isna(train_end):
                train_end = pd.to_datetime(act_df[time_col], errors="coerce").max()
            hist_mask = fcst_df[time_col] <= train_end
            fut_mask = fcst_df[time_col] > train_end
            if hist_mask.any():
                ax.plot(fcst_df.loc[hist_mask, time_col], fcst_df.loc[hist_mask, "TimeGPT"], linestyle="--", color="#ff7f0e", label="Forecast (history)")
            if fut_mask.any():
                ax.plot(fcst_df.loc[fut_mask, time_col], fcst_df.loc[fut_mask, "TimeGPT"], linestyle="-", color="#ff7f0e", label="Forecast")
        if levels:
            lv_sorted = sorted(levels)
            for lv in lv_sorted:
                lo = f"TimeGPT-lo-{lv}"
                hi = f"TimeGPT-hi-{lv}"
                if lo in fcst_df.columns and hi in fcst_df.columns:
                    if "train_end" in locals():
                        fut_mask = fcst_df[time_col] > train_end
                        x = fcst_df.loc[fut_mask, time_col]
                        ylo = fcst_df.loc[fut_mask, lo]
                        yhi = fcst_df.loc[fut_mask, hi]
                        ax.fill_between(x, ylo, yhi, alpha=0.15, label=f"PI {lv}%")
                    else:
                        ax.fill_between(fcst_df[time_col], fcst_df[lo], fcst_df[hi], alpha=0.15, label=f"PI {lv}%")
        if quantiles:
            for q in quantiles:
                qc = f"TimeGPT-q-{int(100*q)}"
                if qc in fcst_df.columns:
                    if "train_end" in locals():
                        fut_mask = fcst_df[time_col] > train_end
                        ax.plot(fcst_df.loc[fut_mask, time_col], fcst_df.loc[fut_mask, qc], linestyle="--", alpha=0.5, label=qc)
                    else:
                        ax.plot(fcst_df[time_col], fcst_df[qc], linestyle="--", alpha=0.5, label=qc)
        ax.legend(loc="best")
        ax.set_title("TimeGPT Forecast")
        ax.set_xlabel(time_col)
        ax.set_ylabel(target_col)
        self.figure = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plot(self):
        if self.last_fcst_df is None:
            messagebox.showinfo("Info", "Run a forecast first")
            return
        self.plot_results(self.last_fcst_df, self.last_id_col, self.last_time_col, self.last_target_col, self.last_levels, self.last_quantiles)

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()