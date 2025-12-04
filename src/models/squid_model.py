import numpy as np


def squid_lc_frequency(L_jun: float | np.ndarray, Ls_nH: float, C_pF: float) -> float | np.ndarray:
    """
    Calculates the resonant frequency of a SQUID JPA LC circuit.
    
    Formula: f = 1 / (2*pi * sqrt( (L_jun/2 + Ls) * C ))
    
    Args:
        L_jun (float | np.ndarray): Junction Inductance in nH.
        Ls_nH (float): Series Inductance in nH.
        C_pF (float): Effective Capacitance in pF.
        
    Returns:
        float | np.ndarray: Resonant frequency in GHz.
    """
    L_sq = L_jun / 2.0
    L_tot_nH = L_sq + Ls_nH
    
    # Avoid negative or zero inductance during fitting
    L_tot_nH = np.maximum(L_tot_nH, 1e-15)
    
    L_tot_H = L_tot_nH * 1e-9
    C_tot_F = C_pF * 1e-12
    
    f_Hz = 1 / (2 * np.pi * np.sqrt(L_tot_H * C_tot_F))
    return f_Hz / 1e9
