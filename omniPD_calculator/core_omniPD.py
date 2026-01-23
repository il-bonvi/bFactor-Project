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
import logging
from typing import Dict, List, Tuple, Any, Optional, Iterable
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from numpy.typing import NDArray

# Setup logging
logger = logging.getLogger(__name__)

# Costante globale
TCPMAX = 1800  # secondi


def ompd_power(t: NDArray[np.float64] | float, CP: float, W_prime: float, Pmax: float, A: float) -> NDArray[np.float64] | float:
    """
    Modello OmniPD completo con 4 parametri.
    
    Args:
        t: Tempo in secondi (scalare o array)
        CP: Potenza Critica (Watt)
        W_prime: Capacità anaerobica (Joule)
        Pmax: Potenza massima sprint (Watt)
        A: Coefficiente di fatica long-term
    
    Returns:
        Potenza predetta dal modello (Watt)
    """
    t = np.array(t, dtype=float)
    base = (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP
    P = np.where(t <= TCPMAX, base, base - A * np.log(t / TCPMAX))
    return P


def ompd_power_short(t: NDArray[np.float64] | float, CP: float, W_prime: float, Pmax: float) -> NDArray[np.float64] | float:
    """Curva base per t ≤ TCPmax (senza termine fatica long-term)."""
    t = np.array(t, dtype=float)
    return (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP


def w_eff(t: NDArray[np.float64] | float, W_prime: float, CP: float, Pmax: float) -> NDArray[np.float64] | float:
    """W' efficace utilizzato nel tempo."""
    return W_prime * (1 - np.exp(-t * (Pmax - CP) / W_prime))


def _format_time_label(seconds: float) -> str:
    """
    Formatta i secondi in formato leggibile.
    
    Args:
        seconds: Tempo in secondi
    
    Returns:
        Stringa formattata (es. "5s", "3m30s", "1h15m")
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes >= 60:
        h = minutes // 60
        m = minutes % 60
        return f"{h}h" if m == 0 else f"{h}h{m}m"
    return f"{minutes}m" if secs == 0 else f"{minutes}m{secs}s"


def calculate_omnipd_model(t_data: NDArray[np.float64], p_data: NDArray[np.float64]) -> Dict[str, Any]:
    """
    Calcola i parametri del modello OmniPD con gli errori.
    
    Args:
        t_data: Array di tempi (secondi)
        p_data: Array di potenze (Watt)
    
    Returns:
        Dict con chiavi:
        - params: [CP, W_prime, Pmax, A]
        - CP, W_prime, Pmax, A: parametri individuali
        - P_pred: potenze predette
        - residuals: residui
        - RMSE: errore quadratico medio
        - MAE: errore medio assoluto
    
    Raises:
        ValueError: se dati insufficienti o fitting fallisce
    """
    logger.info(f"Fitting OmniPD model con {len(t_data)} punti dati")
    
    t_data = np.array(t_data, dtype=float)
    p_data = np.array(p_data, dtype=float)
    
    if len(t_data) < 4:
        logger.error("Dati insufficienti: servono almeno 4 punti")
        raise ValueError("Dati insufficienti: servono almeno 4 punti")
    
    # Guess iniziale con bounds realistici
    CP_guess = np.percentile(p_data, 30)
    W_prime_guess = 20000
    Pmax_guess = p_data.max()
    A_guess = 5
    
    initial_guess = [CP_guess, W_prime_guess, Pmax_guess, A_guess]
    
    # Bounds fisici realistici
    pmax_max = p_data.max() * 1.5
    w_prime_max = p_data.max() * 1000
    bounds = (
        [0, 0, p_data.max(), 0],
        [p_data.max() * 0.95, w_prime_max, pmax_max, 10]
    )
    
    logger.debug(f"Initial guess: CP={CP_guess:.0f}, W'={W_prime_guess:.0f}, Pmax={Pmax_guess:.0f}, A={A_guess:.2f}")
    
    # Fitting del modello COMPLETO - ottimizzato per performance
    try:
        popt, _ = curve_fit(
            ompd_power, 
            t_data, 
            p_data, 
            p0=initial_guess, 
            maxfev=5000,  # Ridotto da 20000 per migliore performance (equilibrio accuracy/speed)
            bounds=bounds,
            ftol=1e-5,  # Tolleranza funzione
            xtol=1e-5,  # Tolleranza parametri
            gtol=1e-5   # Tolleranza gradiente
        )
        logger.debug(f"Curve_fit converged with params: {popt}")
    except Exception as e:
        logger.error(f"Fitting fallito: {str(e)}", exc_info=True)
        raise ValueError(f"Fitting fallito: {str(e)}")
    
    CP, W_prime, Pmax, A = popt
    
    # Calcolo errori
    P_pred = ompd_power(t_data, CP, W_prime, Pmax, A)
    residuals = p_data - P_pred
    RMSE = np.sqrt(np.mean(residuals**2))
    MAE = np.mean(np.abs(residuals))
    
    logger.info(f"Fitting successo: CP={CP:.0f}W, W'={W_prime:.0f}J, Pmax={Pmax:.0f}W, A={A:.2f}, RMSE={RMSE:.2f}W, MAE={MAE:.2f}W")
    
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

def convert_time_minutes_to_seconds(minutes_str: str) -> int:
    """
    Converte minuti (input da UI) a secondi.
    
    Args:
        minutes_str: Stringa rappresentante minuti (accetta virgola come separatore)
    
    Returns:
        Secondi (int)
    
    Raises:
        ValueError: se la stringa non è un numero valido
    """
    try:
        val = float(minutes_str.replace(',', '.'))
        return int(val * 60)
    except (ValueError, AttributeError) as e:
        logger.warning(f"Conversione tempo non valida per '{minutes_str}': {e}")
        raise ValueError(f"Conversione tempo non valida: {str(e)}")


def extract_data_from_rows(rows: List[Any]) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Estrae e valida dati (tempo, potenza) dalle righe di input UI.
    
    Args:
        rows: Lista di oggetti MmpRow con attributi t_input, w_input (QLineEdit)
    
    Returns:
        Tuple di array numpy: (t_data, p_data)
    
    Raises:
        ValueError: se dati insufficienti o non validi
    """
    t_data = []
    p_data = []
    
    for i, row in enumerate(rows):
        t_val = row.t_input.text().strip()
        w_val = row.w_input.text().strip()
        
        if t_val and w_val:
            try:
                t_data.append(float(t_val))
                p_data.append(float(w_val))
            except ValueError as e:
                logger.error(f"Valore numerico non valido in riga {i}: {str(e)}")
                raise ValueError(f"Valore numerico non valido: {str(e)}")
    
    if len(t_data) < 4:
        logger.warning(f"Inserisci almeno 4 punti validi (trovati {len(t_data)})")
        raise ValueError("Inserisci almeno 4 punti validi!")
    
    logger.info(f"Estratti {len(t_data)} punti validi dalle righe UI")
    return np.array(t_data), np.array(p_data)


def load_data_from_file(file_path: str | Path, time_col_idx: int = 0, power_col_idx: int = 1) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Carica dati da file CSV, XLSX o XLSM.
    
    Args:
        file_path: Percorso del file
        time_col_idx: Indice della colonna tempo (default: 0)
        power_col_idx: Indice della colonna potenza (default: 1)
    
    Returns:
        Tuple di array numpy: (t_data, p_data)
    
    Raises:
        ValueError: se file non valido o dati insufficienti
    """
    file_path = str(file_path)
    logger.info(f"Caricamento file: {file_path}")
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
            logger.error(f"Formato file non supportato: {ext}")
            raise ValueError(f"Formato file non supportato: {ext}")
        
        # Estrai le colonne selezionate
        df_selected = df.iloc[:, [time_col_idx, power_col_idx]]
        
        # Pulizia e conversione dati
        df_selected.columns = ["t", "P"]
        df_selected["t"] = pd.to_numeric(df_selected["t"], errors="coerce")
        df_selected["P"] = pd.to_numeric(df_selected["P"], errors="coerce")
        df_selected = df_selected.dropna()
        
        if df_selected.empty:
            logger.error("File non contiene dati numerici validi")
            raise ValueError("File non contiene dati numerici validi")
        
        if len(df_selected) < 4:
            logger.error(f"Insufficienti punti dati: {len(df_selected)} (minimo 4)")
            raise ValueError(f"Insufficienti punti dati: {len(df_selected)} (minimo 4)")
        
        logger.info(f"File caricato: {len(df_selected)} punti estratti")
        return df_selected["t"].values, df_selected["P"].values
    
    except Exception as e:
        logger.error(f"Errore durante il caricamento file: {str(e)}", exc_info=True)
        raise ValueError(f"Errore durante il caricamento file: {str(e)}")
