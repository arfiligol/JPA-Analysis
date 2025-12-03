from __future__ import annotations

from typing import Dict, List, Literal, TypedDict, Union


class ModeFitSeries(TypedDict):
    L_jun: List[float]
    Freq: List[float]


class ModeFitParams(TypedDict):
    Ls_nH: float
    C_eff_pF: float


class ModeFitMetrics(TypedDict):
    RMSE: float


class ModeFitSuccess(TypedDict):
    status: Literal["success"]
    params: ModeFitParams
    metrics: ModeFitMetrics
    raw_data: ModeFitSeries
    fit_curve: ModeFitSeries


class ModeFitFailure(TypedDict):
    status: Literal["failed"]
    reason: str


ModeFitResult = Union[ModeFitSuccess, ModeFitFailure]


FitResultsByMode = Dict[str, ModeFitResult]


class AnalysisEntry(TypedDict):
    filename: str
    fits: FitResultsByMode


class Y11FitParams(TypedDict):
    Ls1_nH: float
    Ls2_nH: float
    C_pF: float


class Y11FitMetrics(TypedDict):
    RMSE: float


class Y11FitSeries(TypedDict):
    freq_ghz: List[float]
    imag_y: List[float]
    L_jun: List[float]


class Y11FitSuccess(TypedDict):
    status: Literal["success"]
    params: Y11FitParams
    metrics: Y11FitMetrics
    raw_data: Y11FitSeries
    fit_curve: Y11FitSeries


class Y11FitFailure(TypedDict):
    status: Literal["failed"]
    reason: str


Y11FitResult = Union[Y11FitSuccess, Y11FitFailure]


__all__ = [
    "AnalysisEntry",
    "FitResultsByMode",
    "ModeFitFailure",
    "ModeFitMetrics",
    "ModeFitParams",
    "ModeFitResult",
    "ModeFitSeries",
    "ModeFitSuccess",
    "Y11FitFailure",
    "Y11FitMetrics",
    "Y11FitParams",
    "Y11FitSeries",
    "Y11FitResult",
    "Y11FitSuccess",
]
