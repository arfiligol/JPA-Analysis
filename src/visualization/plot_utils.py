from __future__ import annotations

import re
from typing import List, Optional, Sequence, Tuple, cast

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from src.types import AnalysisEntry, ModeFitSuccess
from src.utils import (
    MATPLOTLIB_FONT_SIZE,
    MATPLOTLIB_TITLE_SIZE,
    apply_plotly_layout,
    plotly_default_config,
)


def plot_json_results(
    results_list: Sequence[AnalysisEntry],
    target_modes: Optional[List[str]] = None,
    title: str = "SQUID JPA Fitting Results",
    use_matplotlib: bool = False,
) -> None:
    sorted_results = sorted(results_list, key=_analysis_sort_key)
    if use_matplotlib:
        _plot_json_results_matplotlib(sorted_results, target_modes, title)
    else:
        _plot_json_results_plotly(sorted_results, target_modes, title)


def _plot_json_results_plotly(
    results_list: Sequence[AnalysisEntry],
    target_modes: Optional[List[str]],
    title: str,
) -> None:
    traces: List[go.Scatter] = []
    colors: List[str] = [
        "#1f77b4",
        "#d62728",
        "#2ca02c",
        "#9467bd",
        "#ff7f0e",
        "#17becf",
        "#8c564b",
    ]
    color_idx = 0
    for res_obj in results_list:
        file_label = res_obj["filename"]
        for mode_name, mode_data in res_obj["fits"].items():
            if target_modes and mode_name not in target_modes:
                continue
            if mode_data["status"] != "success":
                continue
            success_data = cast(ModeFitSuccess, mode_data)
            raw = success_data["raw_data"]
            fit = success_data["fit_curve"]
            params = success_data["params"]
            color = colors[color_idx % len(colors)]
            color_idx += 1
            traces.append(
                go.Scatter(
                    x=raw["L_jun"],
                    y=raw["Freq"],
                    mode="markers",
                    name=f"{file_label} - {mode_name}",
                    marker=dict(color=color, size=8),
                )
            )
            traces.append(
                go.Scatter(
                    x=fit["L_jun"],
                    y=fit["Freq"],
                    mode="lines",
                    name=(
                        f"Fit {mode_name} "
                        f"(Ls={params['Ls_nH']:.3f} nH, C={params['C_eff_pF']:.3f} pF)"
                    ),
                    line=dict(color=color, dash="dash", width=3),
                )
            )
    fig = go.Figure(data=traces)
    apply_plotly_layout(
        fig,
        title=title,
        xaxis_title="Junction Inductance L_jun [nH]",
        yaxis_title="Frequency [GHz]",
        legend_title="Datasets",
    )
    fig.show(config=plotly_default_config(title))


def _plot_json_results_matplotlib(
    results_list: Sequence[AnalysisEntry],
    target_modes: Optional[List[str]],
    title: str,
) -> None:
    plt.figure(figsize=(10, 6))
    colors: List[str] = ["blue", "red", "green", "purple", "orange", "cyan", "magenta"]
    color_idx = 0
    for res_obj in results_list:
        file_label = res_obj["filename"]
        for mode_name, mode_data in res_obj["fits"].items():
            if target_modes and mode_name not in target_modes:
                continue
            if mode_data["status"] != "success":
                continue
            success_data = cast(ModeFitSuccess, mode_data)
            raw = success_data["raw_data"]
            fit = success_data["fit_curve"]
            params = success_data["params"]
            color = colors[color_idx % len(colors)]
            plt.scatter(
                raw["L_jun"],
                raw["Freq"],
                color=color,
                s=50,
                alpha=0.6,
                label=f"{file_label} - {mode_name}",
            )
            plt.plot(
                fit["L_jun"],
                fit["Freq"],
                color=color,
                linestyle="--",
                linewidth=2,
                label=f"Fit: Ls={params['Ls_nH']:.3f}n, C={params['C_eff_pF']:.2f}p",
            )
            color_idx += 1
    plt.xlabel(r"Junction Inductance $L_{jun}$ [nH]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.ylabel("Frequency [GHz]", fontsize=MATPLOTLIB_FONT_SIZE)
    plt.title(title, fontsize=MATPLOTLIB_TITLE_SIZE)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()


def _version_key(filename: str) -> Tuple[int, str]:
    match = re.search(r"_v(\d+)", filename, flags=re.IGNORECASE)
    version = int(match.group(1)) if match else 10_000
    return (version, filename)


def _analysis_sort_key(entry: AnalysisEntry) -> Tuple[int, str]:
    return _version_key(entry["filename"])
