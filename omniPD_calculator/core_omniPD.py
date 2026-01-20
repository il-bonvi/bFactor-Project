# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
OmniPD Core - Modello matematico e funzioni di utilità
"""
import os
import numpy as np
import pandas as pd
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


def extract_data_from_rows(rows):
    """
    Estrae dati (tempo, potenza) dalle righe di input UI
    
    Args:
        rows: lista di oggetti MmpRow (hanno attributi t_input, w_input)
    
    Returns:
        tuple: (t_data, p_data) come array numpy
    
    Raises:
        ValueError: se dati insufficienti o non validi
    """
    t_data = []
    p_data = []
    
    for row in rows:
        t_val = row.t_input.text().strip()
        w_val = row.w_input.text().strip()
        
        if t_val and w_val:
            try:
                t_data.append(float(t_val))
                p_data.append(float(w_val))
            except ValueError as e:
                raise ValueError(f"Valore numerico non valido: {str(e)}")
    
    if len(t_data) < 4:
        raise ValueError("Inserisci almeno 4 punti validi!")
    
    return np.array(t_data), np.array(p_data)


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
