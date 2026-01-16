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


def calculate_omnipd_model(t_data, p_data):
    """
    Calcola i parametri del modello OmniPD con gli errori
    
    Args:
        t_data: array di tempi (secondi)
        p_data: array di potenze (Watt)
    
    Returns:
        dict con chiavi:
        - params: [CP, W_prime, Pmax, A]
        - CP, W_prime, Pmax, A: parametri individuali
        - P_pred: potenze predette
        - residuals: residui
        - RMSE: errore quadratico medio
        - MAE: errore medio assoluto
    
    Raises:
        ValueError: se dati insufficienti o fitting fallisce
    """
    t_data = np.array(t_data, dtype=float)
    p_data = np.array(p_data, dtype=float)
    
    if len(t_data) < 4:
        raise ValueError("Dati insufficienti: servono almeno 4 punti")
    
    # Guess iniziale
    initial_guess = [
        np.percentile(p_data, 30),
        20000,
        p_data.max(),
        5
    ]
    
    # Fitting del modello COMPLETO
    try:
        popt, _ = curve_fit(
            ompd_power, 
            t_data, 
            p_data, 
            p0=initial_guess, 
            maxfev=20000,
            bounds=([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf])
        )
    except Exception as e:
        raise ValueError(f"Fitting fallito: {str(e)}")
    
    CP, W_prime, Pmax, A = popt
    
    # Calcolo errori
    P_pred = ompd_power(t_data, CP, W_prime, Pmax, A)
    residuals = p_data - P_pred
    RMSE = np.sqrt(np.mean(residuals**2))
    MAE = np.mean(np.abs(residuals))
    
    return {
        'params': popt,
        'CP': CP,
        'W_prime': W_prime,
        'Pmax': Pmax,
        'A': A,
        'P_pred': P_pred,
        'residuals': residuals,
        'RMSE': RMSE,
        'MAE': MAE
    }
