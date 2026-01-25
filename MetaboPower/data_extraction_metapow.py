# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
DATA_EXTRACTION_METAPOW.PY - Estrazione e conversione dati
Funzioni per estrarre serie temporali da metabolimetro e FIT, conversioni formato
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def find_column(df: pd.DataFrame, keywords: list) -> Optional[str]:
    """Trova una colonna per keyword.
    
    Utility condivisa da cortex_metapow.py e genericsv_metapow.py
    
    Args:
        df: DataFrame con colonne da cercare
        keywords: Lista di keyword da cercare (case-insensitive)
    
    Returns:
        Nome della colonna trovata o None
    """
    for col in df.columns:
        name = str(col).lower()
        if any(k.lower() in name for k in keywords):
            return col
    return None


def normalize_decimals(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizza decimali: sostituisce ',' con '.' e converte colonne numeriche.
    
    Utility condivisa da cortex_metapow.py e genericsv_metapow.py
    Rileva automaticamente il formato di decimale (virgola o punto) e normalizza.
    
    Args:
        df: DataFrame con eventuali decimali in formato virgola
    
    Returns:
        DataFrame con decimali normalizzati a punto
    """
    for col in df.columns:
        if df[col].dtype == 'object':  # Colonne stringa
            try:
                # Converte a stringa e rimpiazza virgola con punto
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                # Prova conversione numerica
                converted = pd.to_numeric(df[col], errors='coerce')
                # Se >50% numerico, converti la colonna
                if converted.notna().sum() / len(df) > 0.5:
                    df[col] = converted
            except (ValueError, TypeError, KeyError):
                pass  # Rimane stringa se conversione fallisce
    
    return df


def hmsms_to_seconds(series: pd.Series) -> np.ndarray:
    """Converte h:mm:ss,ms (con virgola come decimale) in secondi totali.
    
    Esempi: 
        '0:00:06,840' -> 6.84s
        '0:01:30,500' -> 90.5s
        '1:15:30,250' -> 4530.25s
    
    Args:
        series: Serie pandas con valori temporali in formato h:mm:ss,ms
    
    Returns:
        Array numpy con i valori in secondi totali
    """
    result = []
    for val in series:
        try:
            s = str(val).strip()
            if not s:
                result.append(0.0)
                continue
            
            # Split su ':' per separare h, mm, ss,ms
            parts = s.split(":")
            if len(parts) == 3:
                hh_str = parts[0]
                mm_str = parts[1]
                ss_ms_str = parts[2]  # 'ss,ms' formato
                
                hours = int(hh_str)
                minutes = int(mm_str)
                
                # Converti ss,ms (sostituisci virgola con punto)
                ss_ms_str = ss_ms_str.replace(",", ".")
                seconds = float(ss_ms_str)
                
                total_seconds = hours * 3600 + minutes * 60 + seconds
                result.append(total_seconds)
            else:
                result.append(0.0)
        except Exception:
            result.append(0.0)
    
    return np.array(result)


def extract_metabolimeter_series(df: pd.DataFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Estrae serie (tempo in secondi, potenza) dal DataFrame metabolimetro.
    
    Cerca colonne:
        - Tempo: h:mm:ss.ms (già convertito da virgola a punto dal parser)
        - Potenza: colonna 'WR' o simili
    
    Args:
        df: DataFrame con dati metabolimetro
    
    Returns:
        Tuple (time_series, power_series) - entrambi np.ndarray o None se non trovate
    """
    if df is None or df.empty:
        return None, None

    # ===== COLONNA TEMPO =====
    time_col = None
    
    # Cerca colonna tempo con formato h:mm:ss
    for col in df.columns:
        col_lower = str(col).lower()
        if col_lower.startswith('t') and 'h:mm:ss' in col_lower:
            time_col = col
            break
    
    # Fallback: cerca colonna tempo generica
    if time_col is None:
        for col in df.columns:
            name = str(col).lower()
            if "time" in name or "tempo" in name:
                time_col = col
                break
    
    # Converti tempo in secondi
    if time_col:
        time_series = hmsms_to_seconds(df[time_col])
    else:
        # Fallback: usa indice come tempo
        time_series = np.arange(len(df), dtype=float)

    # ===== COLONNA POTENZA =====
    power_col = None
    
    # Cerca colonna WR (work rate)
    for col in df.columns:
        col_lower = str(col).lower().split('(')[0].strip()  # Rimuovi unità
        if col_lower == 'wr':
            power_col = col
            break
    
    # Fallback: cerca altre colonne di potenza
    if power_col is None:
        for col in df.columns:
            name = str(col).lower()
            if "power" in name or "watt" in name or "potenza" in name:
                power_col = col
                break
    
    # Ultima spiaggia: prima colonna numerica (escluso tempo)
    if power_col is None:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            power_col = numeric_cols[0]
    
    if power_col is None:
        return time_series, None

    power_series = pd.to_numeric(df[power_col], errors='coerce').fillna(0).values
    return time_series, power_series


def extract_fit_series(df: pd.DataFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Estrae serie (tempo in secondi, potenza) dal DataFrame FIT.
    
    Convenzione FIT:
        - Tempo: ogni riga = 1 secondo (usa indice come tempo)
        - Potenza: colonna 'power'
    
    Args:
        df: DataFrame con dati FIT
    
    Returns:
        Tuple (time_series, power_series) - entrambi np.ndarray o None se non trovate
    """
    if df is None or df.empty:
        return None, None

    # ===== TEMPO =====
    # FIT: ogni riga è 1 secondo
    time_series = np.arange(len(df), dtype=float)

    # ===== POTENZA =====
    power_col = None
    
    # Cerca colonna 'power'
    for col in df.columns:
        if str(col).lower() == "power":
            power_col = col
            break
    
    # Fallback: prima colonna numerica
    if power_col is None:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            power_col = numeric_cols[0]
    
    if power_col is None:
        return time_series, None

    power_series = pd.to_numeric(df[power_col], errors='coerce').fillna(0).values
    return time_series, power_series


def find_ramp_start(power_series: np.ndarray) -> int:
    """Trova l'indice di inizio rampa (primo punto con potenza > 0).
    
    Args:
        power_series: Array numpy con valori di potenza
    
    Returns:
        Indice di inizio rampa (0 se non trovato)
    """
    try:
        start_idx = int(np.argmax(power_series > 0))
        return max(0, start_idx)
    except Exception:
        return 0


def find_vt_intersections(time_aligned: np.ndarray, power_data: np.ndarray, 
                         vt1: Optional[float], vt2: Optional[float], 
                         map_power: Optional[float]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Trova i tempi di intersezione delle soglie VT con la curva di potenza.
    
    Args:
        time_aligned: Array numpy con tempi allineati (relativi alla fine)
        power_data: Array numpy con dati di potenza
        vt1: Soglia VT1 in Watt (o None)
        vt2: Soglia VT2 in Watt (o None)
        map_power: Soglia MAP in Watt (o None)
    
    Returns:
        Tuple (vt1_time, vt2_time, map_time) - tempi di intersezione o None se non trovati
    """
    vt1_time = None
    vt2_time = None
    map_time = None
    
    if vt1 is not None:
        vt1_idx = np.where(power_data >= vt1)[0]
        if len(vt1_idx) > 0:
            vt1_time = time_aligned[vt1_idx[0]]
    
    if vt2 is not None:
        vt2_idx = np.where(power_data >= vt2)[0]
        if len(vt2_idx) > 0:
            vt2_time = time_aligned[vt2_idx[0]]
    
    if map_power is not None:
        map_idx = np.where(power_data >= map_power)[0]
        if len(map_idx) > 0:
            map_time = time_aligned[map_idx[0]]
    
    return vt1_time, vt2_time, map_time


def calculate_rolling_averages(power_data: np.ndarray, 
                               windows: list = [15, 30]) -> dict:
    """Calcola medie mobili della potenza su finestre temporali specifiche.
    
    Convenzione FIT: 1 campione = 1 secondo, quindi window size = secondi
    Consolidata da vtcomparison_metapow.py per evitare duplicazione.
    
    Args:
        power_data: Array numpy con dati di potenza
        windows: Lista di finestre in secondi (default: [15, 30])
    
    Returns:
        Dictionary con chiavi f"{window}s" e valori array numpy delle medie mobili
    """
    result = {}
    
    for window in windows:
        if len(power_data) < window:
            # Se i dati sono più corti della finestra, usa media totale
            result[f"{window}s"] = np.full_like(power_data, np.mean(power_data), dtype=float)
        else:
            # Calcola media mobile con pandas (più efficiente)
            rolling_avg = pd.Series(power_data).rolling(window=window, center=False, min_periods=1).mean().values
            result[f"{window}s"] = rolling_avg
    
    return result


def calculate_rolling_centered15_fit(fit_data: np.ndarray) -> np.ndarray:
    """Calcola l'array di medie mobili centrate su 15 secondi (7 prima + 7 dopo).
    
    Args:
        fit_data: Array potenza FIT
    
    Returns:
        Array medie mobili centrate 15s (stessa lunghezza di fit_data)
    """
    if fit_data is None or len(fit_data) == 0:
        return fit_data
    
    result = np.zeros_like(fit_data, dtype=float)
    for i in range(len(fit_data)):
        start_idx = max(0, i - 7)
        end_idx = min(len(fit_data), i + 8)
        result[i] = np.mean(fit_data[start_idx:end_idx])
    return result


def calculate_rolling_centered30_fit(fit_data: np.ndarray) -> np.ndarray:
    """Calcola l'array di medie mobili centrate su 30 secondi (15 prima + 15 dopo).
    
    Args:
        fit_data: Array potenza FIT
    
    Returns:
        Array medie mobili centrate 30s (stessa lunghezza di fit_data)
    """
    if fit_data is None or len(fit_data) == 0:
        return fit_data
    
    result = np.zeros_like(fit_data, dtype=float)
    for i in range(len(fit_data)):
        start_idx = max(0, i - 15)
        end_idx = min(len(fit_data), i + 16)
        result[i] = np.mean(fit_data[start_idx:end_idx])
    return result


def calculate_rolling_avg5_fit(fit_data: np.ndarray) -> np.ndarray:
    """Calcola l'array di medie mobili non centrate su 5 secondi.
    
    Args:
        fit_data: Array potenza FIT
    
    Returns:
        Array medie mobili 5s (stessa lunghezza di fit_data)
    """
    if fit_data is None or len(fit_data) == 0:
        return fit_data
    
    result = np.zeros_like(fit_data, dtype=float)
    for i in range(len(fit_data)):
        start_idx = max(0, i - 5)
        result[i] = np.mean(fit_data[start_idx:i + 1])
    return result
