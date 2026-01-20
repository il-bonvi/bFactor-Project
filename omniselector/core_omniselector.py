# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
Omniselector Core - Modello matematico e funzioni di utilità
"""
import os
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# Costante globale
TCPMAX = 1800  # secondi


def ompd_power(t, CP, W_prime, Pmax, A):
    """Modello Omniselector completo con 4 parametri"""
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
    Calcola i parametri del modello Omniselector con gli errori
    
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


# ============================================================================
# DATA HANDLING - Funzioni per I/O file e gestione dati
# ============================================================================

def convert_time_minutes_to_seconds(minutes_str):
    """
    Converte minuti (input da UI) a secondi
    
    Args:
        minutes_str: stringa rappresentante minuti (accetta virgola come separatore)
    
    Returns:
        int: secondi
    
    Raises:
        ValueError: se la stringa non è un numero valido
    """
    try:
        val = float(minutes_str.replace(',', '.'))
        return int(val * 60)
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Conversione tempo non valida: {str(e)}")


def load_data_from_file(file_path, time_col_idx=0, power_col_idx=1):
    """
    Carica dati da file CSV, XLSX o XLSM
    
    Args:
        file_path: percorso del file
        time_col_idx: indice della colonna tempo (default: 0)
        power_col_idx: indice della colonna potenza (default: 1)
    
    Returns:
        tuple: (t_data, p_data) come array numpy
    
    Raises:
        ValueError: se file non valido o dati insufficienti
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == ".xlsm":
            try:
                df = pd.read_excel(file_path, sheet_name="Summary Sheet", 
                                 usecols="A:B", header=None)
            except ValueError:
                df = pd.read_excel(file_path, sheet_name=0, 
                                 usecols="A:B", header=None)
        elif ext == ".xlsx":
            df = pd.read_excel(file_path, usecols="A:B", header=None)
        elif ext == ".csv":
            df = pd.read_csv(file_path, sep=None, engine="python")
        else:
            raise ValueError(f"Formato file non supportato: {ext}")
        
        # Estrai le colonne selezionate
        df_selected = df.iloc[:, [time_col_idx, power_col_idx]]
        
        # Pulizia e conversione dati
        df_selected.columns = ["t", "P"]
        df_selected["t"] = pd.to_numeric(df_selected["t"], errors="coerce")
        df_selected["P"] = pd.to_numeric(df_selected["P"], errors="coerce")
        df_selected = df_selected.dropna()
        
        if df_selected.empty:
            raise ValueError("File non contiene dati numerici validi")
        
        if len(df_selected) < 4:
            raise ValueError(f"Insufficienti punti dati: {len(df_selected)} (minimo 4)")
        
        return df_selected["t"].values, df_selected["P"].values
    
    except Exception as e:
        raise ValueError(f"Errore durante il caricamento file: {str(e)}")


# ============================================================================
# FILTERING - Funzioni per filtraggio e selezione dati
# ============================================================================

def apply_data_filters(x_data, y_data, time_windows, percentile_min, values_per_window, sprint_value, current_params=None):
    """
    Applica filtri ai dati basati su finestre temporali, percentile e sprint
    
    Args:
        x_data: array di tempi (s)
        y_data: array di potenze (W)
        time_windows: lista di tuple (tmin, tmax) in secondi
        percentile_min: percentile minimo per selezione (0-100)
        values_per_window: numero massimo di valori per finestra
        sprint_value: tempo del valore sprint da includere sempre (s)
        current_params: parametri modello esistenti [CP, Wp, Pmax, A] o None
    
    Returns:
        tuple: (x_filtered, y_filtered, selected_mask)
            - x_filtered: array tempi selezionati
            - y_filtered: array potenze selezionate
            - selected_mask: maschera booleana per i dati originali
    """
    x_arr = np.array(x_data, dtype=float)
    y_arr = np.array(y_data, dtype=float)
    selected_mask = np.zeros_like(x_arr, dtype=bool)
    
    if not time_windows:
        selected_mask[:] = True
        return x_arr, y_arr, selected_mask

    # Fit model to all data to get residuals
    try:
        if current_params is not None:
            CP, Wp, Pmax, A = current_params
        else:
            # Fallback: rough initial fit
            p0 = [np.percentile(y_arr, 30), 20000, np.max(y_arr), 5]
            params, _ = curve_fit(ompd_power, x_arr, y_arr, p0=p0, maxfev=20000)
            CP, Wp, Pmax, A = params
    except Exception:
        # If fit fails, fallback to no filtering
        selected_mask[:] = True
        return x_arr, y_arr, selected_mask

    # Calculate residuals
    pred = (Wp / x_arr) * (1 - np.exp(-x_arr * (Pmax - CP) / Wp)) + CP
    pred = np.where(x_arr <= TCPMAX, pred, pred - A * np.log(x_arr / TCPMAX))
    residuals = y_arr - pred

    # Global percentile threshold (only for t > 120)
    mask_gt_120 = x_arr > 120
    if np.any(mask_gt_120):
        cut_global = np.percentile(residuals[mask_gt_120], percentile_min)
    else:
        cut_global = np.percentile(residuals, percentile_min)

    selected_x = []
    selected_y = []
    
    # Window selection
    for (tmin, tmax) in time_windows:
        mask = (x_arr >= tmin) & (x_arr <= tmax)
        idx = np.where(mask)[0]
        if idx.size == 0:
            continue
        res_window = residuals[idx]
        # Select top N residuals above global percentile threshold
        sorted_idx = idx[np.argsort(res_window)[::-1]]
        count = 0
        for i in sorted_idx:
            if residuals[i] >= cut_global:
                selected_x.append(x_arr[i])
                selected_y.append(y_arr[i])
                selected_mask[i] = True
                count += 1
            if count >= max(1, values_per_window):
                break
    
    # Sprint selection - always add closest point to sprint value if not already selected
    if sprint_value > 0 and len(x_arr) > 0:
        sprint_idx = int(np.argmin(np.abs(x_arr - sprint_value)))
        if 0 <= sprint_idx < len(selected_mask) and not selected_mask[sprint_idx]:
            selected_x.append(x_arr[sprint_idx])
            selected_y.append(y_arr[sprint_idx])
            selected_mask[sprint_idx] = True
    
    if not selected_x:
        raise ValueError("Nessun dato selezionato dalle finestre")
    
    return np.array(selected_x), np.array(selected_y), selected_mask
