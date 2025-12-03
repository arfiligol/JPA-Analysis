from __future__ import annotations

import numpy as np
import pandas as pd
from lmfit import Model
from typing import Dict, List, Optional, Tuple

from src.models.squid_model import squid_lc_frequency
from src.types import FitResultsByMode, ModeFitFailure, ModeFitSuccess

ParameterBounds = Dict[str, Tuple[Optional[float], Optional[float]]]


def fit_resonant_modes(
    df_modes: pd.DataFrame,
    parameter_bounds: Optional[ParameterBounds] = None,
) -> FitResultsByMode:
    """
    Fits the SQUID LC model to each Mode column in the DataFrame.
    """
    return _fit_resonant_modes(
        df_modes,
        fixed_capacitance_pf=None,
        parameter_bounds=parameter_bounds,
    )


def fit_resonant_modes_fixed_capacitance(
    df_modes: pd.DataFrame,
    capacitance_pf: float,
    parameter_bounds: Optional[ParameterBounds] = None,
) -> FitResultsByMode:
    """
    Fit modes while holding the capacitance parameter fixed.
    """
    return _fit_resonant_modes(
        df_modes,
        fixed_capacitance_pf=capacitance_pf,
        parameter_bounds=parameter_bounds,
    )


def _fit_resonant_modes(
    df_modes: pd.DataFrame,
    fixed_capacitance_pf: Optional[float],
    parameter_bounds: Optional[ParameterBounds],
) -> FitResultsByMode:
    if df_modes is None or df_modes.empty:
        print("[Error] Input DataFrame is empty.")
        return {}

    results: FitResultsByMode = {}
    mode_cols: List[str] = [c for c in df_modes.columns if "Mode" in c]

    if not mode_cols:
        print("[Warning] No Mode columns found.")
        return {}

    x_data_all: np.ndarray = df_modes["L_jun"].values

    suffix = "" if fixed_capacitance_pf is None else f" (C fixed at {fixed_capacitance_pf:.4f} pF)"
    print(f"Starting fitting analysis for {len(mode_cols)} modes{suffix}...")

    for mode_name in mode_cols:
        df_clean = df_modes[["L_jun", mode_name]].dropna()
        df_clean = df_clean[df_clean[mode_name] > 0.001]

        if len(df_clean) < 3:
            failure_result: ModeFitFailure = {
                "status": "failed",
                "reason": "Not enough points",
            }
            results[mode_name] = failure_result
            continue

        x_fit: np.ndarray = df_clean["L_jun"].values
        y_fit: np.ndarray = df_clean[mode_name].values

        model = Model(squid_lc_frequency, independent_vars=["L_jun"])
        params = model.make_params(Ls_nH=0.1, C_pF=1.0)
        params["Ls_nH"].min = 0.0
        params["C_pF"].min = 0.0
        _apply_bounds(params["Ls_nH"], parameter_bounds, "Ls_nH")
        _apply_bounds(params["C_pF"], parameter_bounds, "C_pF")
        if fixed_capacitance_pf is not None:
            params["C_pF"].set(value=fixed_capacitance_pf, vary=False)

        try:
            result = model.fit(y_fit, params=params, L_jun=x_fit)
            if not result.success:
                raise RuntimeError(result.message)

            Ls_fit = result.params["Ls_nH"].value
            C_fit = result.params["C_pF"].value

            # Evaluate at the raw sample points for reporting.
            y_pred_all = result.eval(params=result.params, L_jun=x_data_all)

            # Generate a dense grid for plotting so the curve looks smooth.
            if len(x_data_all) >= 2:
                l_min = float(np.min(x_data_all))
                l_max = float(np.max(x_data_all))
                x_curve = np.linspace(l_min, l_max, 200)
            else:
                x_curve = x_data_all
            y_curve = result.eval(params=result.params, L_jun=x_curve)

            y_fit_pred = result.best_fit
            rmse = np.sqrt(np.mean((y_fit - y_fit_pred) ** 2))

            success_result: ModeFitSuccess = {
                "status": "success",
                "params": {"Ls_nH": float(Ls_fit), "C_eff_pF": float(C_fit)},
                "metrics": {"RMSE": float(rmse)},
                "raw_data": {
                    "L_jun": df_clean["L_jun"].tolist(),
                    "Freq": df_clean[mode_name].tolist(),
                },
                "fit_curve": {
                    "L_jun": x_curve.tolist(),
                    "Freq": y_curve.tolist(),
                },
            }
            results[mode_name] = success_result

            caption = (
                f"  > {mode_name}: Ls={Ls_fit:.4f} nH, C={C_fit:.4f} pF, RMSE={rmse:.4f}"
            )
            if fixed_capacitance_pf is not None:
                caption += " (C fixed)"
            print(caption)
        except Exception as exc:
            failure_result = ModeFitFailure(status="failed", reason=str(exc))
            results[mode_name] = failure_result
            print(f"  > {mode_name}: Fitting failed ({exc})")

    return results


def _apply_bounds(param, bounds: Optional[ParameterBounds], name: str) -> None:
    if not bounds:
        return
    if name not in bounds:
        return
    lower, upper = bounds[name]
    if lower is not None:
        param.min = lower
    if upper is not None:
        param.max = upper
