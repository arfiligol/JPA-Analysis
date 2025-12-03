from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

CsvPath = Union[str, Path]


def extract_from_admittance(csv_file_path: CsvPath) -> Optional[pd.DataFrame]:
    """
    Extracts resonant frequencies from HFSS CSV data based on Imaginary Admittance (Im(Y)=0).
    
    Args:
        csv_file_path (Union[str, Path]): Path to the CSV file.
        
    Returns:
        Optional[pd.DataFrame]: DataFrame containing 'L_jun' and corresponding Mode frequencies (Mode 1, Mode 2...),
                                or None if extraction fails.
    """
    try:
        csv_path = Path(csv_file_path)
        df: pd.DataFrame = pd.read_csv(csv_path)
    except Exception as e:
        print(f"[Error] Failed to read file {csv_file_path}: {e}")
        return None

    return extract_modes_from_dataframe(df)


def extract_modes_from_dataframe(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Extract resonant frequencies from a pre-loaded DataFrame.
    """
    # --- 1. Identify Columns ---
    l_cols: List[str] = [c for c in df.columns if 'L_jun' in c or 'L_ind' in c]
    l_col: Optional[str] = l_cols[0] if l_cols else None

    freq_cols: List[str] = [c for c in df.columns if 'Freq' in c]
    if not freq_cols:
        print("[Error] Frequency column (Freq) not found.")
        return None
    freq_col: str = freq_cols[0]

    y_cols: List[str] = [c for c in df.columns if 'im(' in c.lower() and ('Y' in c or 'Z' in c)]
    if not y_cols:
        print("[Error] Admittance/Impedance Imaginary part column (Im(Y) or Im(Z)) not found.")
        return None
    y_col: str = y_cols[0]

    # --- 2. Process Data ---
    results: List[Dict[str, float]] = []
    
    unique_Ls: List[float]
    if l_col:
        unique_Ls = sorted(float(value) for value in df[l_col].unique())
    else:
        unique_Ls = [0.0] # Dummy L value

    for l_val in unique_Ls:
        # Filter data
        if l_col:
            subset = df[df[l_col] == l_val].sort_values(freq_col)
        else:
            subset = df.sort_values(freq_col)
            
        freqs: np.ndarray = subset[freq_col].to_numpy(dtype=float)
        ys: np.ndarray = subset[y_col].to_numpy(dtype=float)
        
        crossings: List[float] = []
        
        # Find Zero Crossings
        for i in range(len(ys) - 1):
            y1, y2 = ys[i], ys[i+1]
            if y1 == 0:
                crossings.append(freqs[i])
            elif y1 * y2 < 0: # Sign change indicates crossing
                # Linear interpolation
                x_zero = freqs[i] - y1 * (freqs[i+1] - freqs[i]) / (y2 - y1)
                crossings.append(x_zero)
        
        # Store results
        entry: Dict[str, float] = {'L_jun': float(l_val)}
        for idx, f in enumerate(crossings):
            entry[f'Mode {idx+1}'] = f
        results.append(entry)

    return pd.DataFrame(results)
