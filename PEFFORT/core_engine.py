# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
CORE ENGINE - Logica pura per analisi efforts e sprints
Contiene: parsing FIT, calcoli VAM, filtraggio, analisi sprint
"""

import numpy as np
import pandas as pd
from fitparse import FitFile

# =====================
# CONFIGURAZIONE DEFAULT
# =====================
WINDOW_SECONDS = 60
MERGE_POWER_DIFF_PERCENT = 15
MIN_EFFORT_INTENSITY_FTP = 100
TRIM_WINDOW_SECONDS = 10
TRIM_LOW_PERCENT = 85
EXTEND_WINDOW_SECONDS = 15
EXTEND_LOW_PERCENT = 80

# Sprint defaults
SPRINT_WINDOW_SECONDS = 5
MIN_SPRINT_POWER = 500

ZONE_COLORS = [
    (106, "#1f77b4", "CP–just above"),
    (116, "#3eb33e", "Threshold+"),
    (126, "#ff7f0e", "VO₂max"),
    (136, "#da2fbd", "High VO₂max / MAP"),
    (999, "#7315ca", "Supra-MAP"),
]
ZONE_DEFAULT = ("Anaerobico", "#6B3C3C73")


# =====================
# FUNZIONI UTILITY
# =====================

def format_time_hhmmss(seconds):
    """Formatta secondi in HH:MM:SS"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_time_mmss(seconds):
    """Formatta secondi in MM:SS"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


# =====================
# FUNZIONI CORE - PARSING & DATA
# =====================

def parse_fit(file_path):
    """Estrae dati FIT in DataFrame"""
    fit = FitFile(file_path)
    data = {
        "time": [], "power": [], "altitude": [], "distance": [], 
        "heartrate": [], "grade": [], "cadence": []
    }
    
    for record in fit.get_messages("record"):
        vals = {f.name: f.value for f in record}
        data["time"].append(vals.get("timestamp"))
        data["power"].append(vals.get("power") or 0)
        data["altitude"].append(vals.get("enhanced_altitude") or 0)
        data["distance"].append(vals.get("distance") or 0)
        data["heartrate"].append(vals.get("heart_rate") or 0)
        data["grade"].append(vals.get("grade") or 0)
        data["cadence"].append(vals.get("cadence") or 0)
    
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"])
    df["time_sec"] = (df["time"] - df["time"].iloc[0]).dt.total_seconds()
    df["distance_km"] = df["distance"] / 1000
    df = df.fillna(0)
    
    # Fix initial altitude
    first_nonzero = df[df["altitude"] != 0]["altitude"].iloc[0] if len(df[df["altitude"] != 0]) > 0 else 0
    for i in range(len(df)):
        if df.loc[i, "altitude"] == 0:
            df.loc[i, "altitude"] = first_nonzero
        else:
            break
    
    return df


def get_zone_color(avg_power, ftp):
    """Determina colore zona in base alla potenza"""
    if ftp <= 0:
        return "grey"
    perc = avg_power / ftp * 100
    for th, color, _ in ZONE_COLORS:
        if perc < th:
            return color
    return ZONE_DEFAULT[1]


# =====================
# FUNZIONI CORE - EFFORTS
# =====================

def trim_segment(power, start, end, trim_win, trim_pct):
    """Limatura inizio/fine"""
    while True:
        changed = False
        if end - start < trim_win * 2:
            break
        seg = power[start:end]
        avg = seg.mean() if len(seg) > 0 else 0

        head_avg = power[start:start+trim_win].mean()
        if head_avg < avg * trim_pct / 100:
            start += trim_win
            changed = True

        tail_avg = power[end-trim_win:end].mean()
        if tail_avg < avg * trim_pct / 100:
            end -= trim_win
            changed = True

        if not changed:
            break
    return start, end


def create_efforts(df, ftp, window_sec=60, merge_pct=15, min_ftp_pct=100, trim_win=10, trim_low=85):
    """Crea finestre, merge, trim, filtro FTP"""
    power = df["power"].values
    n = len(power)
    windows = []
    i = 0
    
    while i + window_sec <= n:
        seg = power[i:i+window_sec]
        windows.append((i, i+window_sec, seg.mean()))
        i += window_sec

    merged = []
    idx = 0
    
    while idx < len(windows):
        s, e, avg = windows[idx]
        tot = avg * window_sec
        length = window_sec
        j = idx + 1
        
        while j < len(windows):
            s2, e2, avg2 = windows[j]
            diff = abs(avg2 - avg) / avg * 100 if avg > 0 else 0
            if diff <= merge_pct:
                tot += avg2 * window_sec
                length += window_sec
                avg = tot / length
                e = e2
                j += 1
            else:
                break
        
        s_trim, e_trim = trim_segment(power, s, e, trim_win, trim_low)
        avg_trim = power[s_trim:e_trim].mean() if e_trim > s_trim else 0
        
        if avg_trim > ftp * min_ftp_pct / 100:
            merged.append((s_trim, e_trim, avg_trim))
        
        idx = j
    
    return merged


def merge_extend(df, efforts, merge_pct=15, trim_win=10, trim_low=85, extend_win=15, extend_low=80):
    """Merge + estensione iterativa"""
    power = df["power"].values
    changed = True
    
    while changed:
        changed = False
        new_eff = []
        efforts.sort(key=lambda x: x[0])
        i = 0
        
        while i < len(efforts):
            s, e, avg = efforts[i]
            j = i + 1
            
            while j < len(efforts) and efforts[j][0] < e:
                s2, e2, avg2 = efforts[j]
                diff = abs(avg2 - avg) / ((avg + avg2) / 2) * 100 if avg > 0 else 0
                if diff <= merge_pct:
                    s = min(s, s2)
                    e = max(e, e2)
                    avg = power[s:e].mean()
                    j += 1
                else:
                    break
            
            # Extend front
            while s - extend_win >= 0:
                ext = power[s-extend_win:s].mean()
                if ext >= avg * extend_low / 100:
                    s -= extend_win
                    avg = power[s:e].mean()
                else:
                    break
            
            # Extend back
            while e + extend_win <= len(power):
                ext = power[e:e+extend_win].mean()
                if ext >= avg * extend_low / 100:
                    e += extend_win
                    avg = power[s:e].mean()
                else:
                    break
            
            s_trim, e_trim = trim_segment(power, s, e, trim_win, trim_low)
            avg_trim = power[s_trim:e_trim].mean() if e_trim > s_trim else 0
            new_eff.append((s_trim, e_trim, avg_trim))
            i = j
        
        if new_eff != efforts:
            changed = True
        efforts = new_eff
    
    return efforts


def split_included(df, efforts):
    """Split se un effort è contenuto in un altro"""
    power = df["power"].values
    efforts.sort(key=lambda x: x[0])
    changed = True
    
    while changed:
        changed = False
        for i in range(len(efforts)):
            for j in range(len(efforts)):
                if i == j:
                    continue
                
                s, e, avg = efforts[i]
                s2, e2, avg2 = efforts[j]
                
                # j completamente dentro i
                if s < s2 and e2 < e:
                    new_efforts = []
                    
                    # Prima di j
                    if s2 > s:
                        pow1 = power[s:s2]
                        if len(pow1) > 0:
                            new_efforts.append((s, s2, pow1.mean()))
                    
                    # j stesso
                    new_efforts.append((s2, e2, avg2))
                    
                    # Dopo j
                    if e2 < e:
                        pow2 = power[e2:e]
                        if len(pow2) > 0:
                            new_efforts.append((e2, e, pow2.mean()))
                    
                    # Rimuovi i e j, aggiungi nuovi
                    efforts = [eff for k, eff in enumerate(efforts) if k != i and k != j]
                    efforts.extend(new_efforts)
                    efforts.sort(key=lambda x: x[0])
                    changed = True
                    break
            
            if changed:
                break
    
    return efforts


# =====================
# FUNZIONI CORE - SPRINTS
# =====================

def detect_sprints(df, min_power, min_duration_sec, merge_gap_sec=1):
    """
    Rilevamento sprint dinamici (stile JS Surges):
    Rileva blocchi di potenza sopra min_power e li unisce se vicini.
    """
    power = df["power"].values
    time_sec = df["time_sec"].values
    
    # Trova i segmenti dove la potenza è costantemente sopra la soglia
    above_threshold = power >= min_power
    sprints = []
    i = 0
    
    while i < len(above_threshold):
        if above_threshold[i]:
            start = i
            while i < len(above_threshold) and above_threshold[i]:
                i += 1
            end = i  # fine del blocco
            
            durata = time_sec[end-1] - time_sec[start] + 1
            if durata >= min_duration_sec:
                sprints.append({
                    'start': start, 
                    'end': end, 
                    'avg': np.mean(power[start:end])
                })
        else:
            i += 1
    
    if not sprints:
        return []

    # Unisce sprint che hanno un gap temporale piccolo
    merged = []
    curr = sprints[0]
    
    for nxt in sprints[1:]:
        gap = time_sec[nxt['start']] - time_sec[curr['end']-1]
        if gap <= merge_gap_sec:
            new_start = curr['start']
            new_end = nxt['end']
            curr = {
                'start': new_start, 
                'end': new_end, 
                'avg': np.mean(power[new_start:new_end])
            }
        else:
            merged.append(curr)
            curr = nxt
    
    merged.append(curr)
    return merged
