from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple, cast

import pandas as pd

from src.extraction import extract_modes_from_dataframe, normalize_mode_columns
from src.optimizer import fit_resonant_modes
from src.preprocess.loader import (
    dataset_to_dataframe,
    find_dataset,
    load_component_record,
)
from src.preprocess.schema import ParameterFamily, ParameterRepresentation
from src.types import AnalysisEntry, FitResultsByMode, ModeFitResult
from src.utils import PREPROCESSED_DATA_DIR
from src.visualization import plot_json_results, print_dataframe_table

# ---------------------------------------------------------------------------
# User configuration
# ---------------------------------------------------------------------------

# Component IDs stored under data/preprocessed/<component_id>.json
DEFAULT_COMPONENT_IDS: Sequence[str] = [
    "LJPAL658_v1",
    "LJPAL658_v2",
    "LJPAL658_v3",
    # "LJPAL658_v1_No_Pump_Line",
    # "LJPAL658_v2_No_Pump_Line",
    # "LJPAL658_v3_No_Pump_Line",
    # "LJPAL6574_B46D1",
    # "LJPAL6572_B46D2",
]

# Specify which extracted modes should be plotted/highlighted.
# Use None/empty to plot every available mode.
DEFAULT_MODES_TO_PLOT: Sequence[str] = ["Mode 1"]

# Default parameter bounds (None indicates no bound).
DEFAULT_FIT_BOUNDS: dict[str, tuple[float | None, float | None]] = {
    "Ls_nH": (0.0, None),
    "C_pF": (0.0, None),
}


class AdmittanceFitArgs(NamedTuple):
    components: list[str]
    modes: list[str] | None
    title: str
    ls_min: float | None
    ls_max: float | None
    c_min: float | None
    c_max: float | None
    matplotlib: bool


def parse_args() -> AdmittanceFitArgs:
    parser = argparse.ArgumentParser(
        description=("Batch analysis of admittance datasets stored under data/preprocessed/.")
    )
    _ = parser.add_argument(
        "components",
        nargs="*",
        help="Component IDs or JSON paths under data/preprocessed/ (defaults provided).",
    )
    _ = parser.add_argument(
        "--modes",
        nargs="+",
        help="Subset of modes to fit/plot (e.g., --modes 'Mode 1' 'Mode 2').",
    )
    _ = parser.add_argument(
        "--title",
        default="SQUID JPA Mode Fits",
        help="Custom title for the plot window.",
    )
    _ = parser.add_argument("--ls-min", type=float, default=None, help="Lower bound for Ls (nH).")
    _ = parser.add_argument("--ls-max", type=float, default=None, help="Upper bound for Ls (nH).")
    _ = parser.add_argument("--c-min", type=float, default=None, help="Lower bound for C (pF).")
    _ = parser.add_argument("--c-max", type=float, default=None, help="Upper bound for C (pF).")
    _ = parser.add_argument(
        "--matplotlib",
        action="store_true",
        help="Render plots with Matplotlib instead of the default Plotly view.",
    )
    args = cast(AdmittanceFitArgs, cast(object, parser.parse_args()))
    return args


def _build_bounds(
    args: AdmittanceFitArgs,
) -> dict[str, tuple[float | None, float | None]]:
    def resolve(
        key: str,
        override_min: float | None,
        override_max: float | None,
    ) -> tuple[float | None, float | None]:
        default_min, default_max = DEFAULT_FIT_BOUNDS[key]
        bound_min = override_min if override_min is not None else default_min
        bound_max = override_max if override_max is not None else default_max
        return (bound_min, bound_max)

    return {
        "Ls_nH": resolve("Ls_nH", args.ls_min, args.ls_max),
        "C_pF": resolve("C_pF", args.c_min, args.c_max),
    }


def resolve_component_path(candidate: str) -> Path | None:
    """Resolve a component identifier or explicit JSON path."""
    path = Path(candidate)
    if path.exists():
        return path

    fallback = PREPROCESSED_DATA_DIR / f"{candidate}.json"
    if fallback.exists():
        return fallback

    print(f"[Warning] Component record not found: {candidate}")
    return None


def extract_modes(component_path: Path) -> pd.DataFrame | None:
    record = load_component_record(component_path)
    dataset = find_dataset(
        record,
        family=ParameterFamily.y_parameters,
        parameter="Y11",
        representation=ParameterRepresentation.imaginary,
    )
    df_raw = dataset_to_dataframe(dataset, value_label="im(Y) []")
    df_modes = extract_modes_from_dataframe(df_raw)
    if df_modes is None:
        return None
    df_modes = normalize_mode_columns(df_modes)
    return df_modes


def print_fit_summary(
    name: str,
    fit_results: FitResultsByMode,
    target_modes: Sequence[str] | None,
) -> None:
    if not fit_results:
        print(f"[Warning] {name}: no fit results to summarize.")
        return

    print(f"\n--- Mode fit summary for {name} ---")
    for mode_name in sorted(fit_results.keys()):
        if target_modes and mode_name not in target_modes:
            continue

        result: ModeFitResult = fit_results[mode_name]
        if result["status"] != "success":
            print(f"  > {mode_name}: failed ({result['reason']})")
            continue

        params = result["params"]
        metrics = result["metrics"]
        print(
            f"  > {mode_name}: "
            + f"Ls={params['Ls_nH']:.4f} nH, "
            + f"C={params['C_eff_pF']:.4f} pF, "
            + f"RMSE={metrics['RMSE']:.4f}"
        )
    print()


def analyze_file(
    component_path: Path,
    modes_to_highlight: Sequence[str] | None,
    parameter_bounds: dict[str, tuple[float | None, float | None]],
) -> AnalysisEntry | None:
    print(f"\n=== Processing {component_path.stem} ===")
    df_modes = extract_modes(component_path)
    if df_modes is None or df_modes.empty:
        print(f"  > Extraction failed or returned empty results for {component_path.stem}")
        return None

    print_dataframe_table("Extracted Resonant Modes", df_modes)

    fit_results = fit_resonant_modes(df_modes, parameter_bounds=parameter_bounds)
    print_fit_summary(component_path.stem, fit_results, modes_to_highlight)

    entry: AnalysisEntry = {"filename": component_path.stem, "fits": fit_results}
    return entry


def run() -> None:
    args = parse_args()

    file_list: Sequence[str] = args.components if args.components else DEFAULT_COMPONENT_IDS
    modes_to_plot: Sequence[str] | None = args.modes if args.modes else DEFAULT_MODES_TO_PLOT
    parameter_bounds = _build_bounds(args)
    plot_title = args.title
    use_matplotlib = args.matplotlib
    analysis_entries: list[AnalysisEntry] = []

    for identifier in file_list:
        component_path = resolve_component_path(identifier)
        if component_path is None:
            continue
        entry = analyze_file(component_path, modes_to_plot, parameter_bounds)
        if entry:
            analysis_entries.append(entry)

    if not analysis_entries:
        print("[Error] No datasets were processed successfully.")
        return

    plot_modes: list[str] | None = list(modes_to_plot) if modes_to_plot else None
    plot_json_results(
        analysis_entries,
        target_modes=plot_modes,
        title=plot_title,
        use_matplotlib=use_matplotlib,
    )


if __name__ == "__main__":
    run()
