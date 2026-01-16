"""
OmniPD Core - Modello matematico e funzioni di utilità
"""
import numpy as np
from scipy.optimize import curve_fit

# Costante globale
TCPMAX = 1800  # secondi


def ompd_power(t, CP, W_prime, Pmax, A):
    """Modello OmniPD completo con 4 parametri"""
    t = np.array(t, dtype=float)
    base = (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP
    P = np.where(t <= TCPMAX, base, base - A * np.log(t / TCPMAX))
    return P


def ompd_power_short(t, CP, W_prime, Pmax):
    """Curva base per t ≤ TCPmax"""
    t = np.array(t, dtype=float)
    return (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP


def w_eff(t, W_prime, CP, Pmax):
    """W' efficace nel tempo"""
    return W_prime * (1 - np.exp(-t * (Pmax - CP) / W_prime))


def _format_time_label(seconds):
    """Formatta i secondi in formato leggibile"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes >= 60:
        h = minutes // 60
        m = minutes % 60
        return f"{h}h" if m == 0 else f"{h}h{m}m"
    return f"{minutes}m" if secs == 0 else f"{minutes}m{secs}s"
