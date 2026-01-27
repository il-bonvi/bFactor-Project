# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
INSPECTION CORE - Logica per la gestione e modifica degli effort
Mantiene traccia delle modifiche e permette reset/undo
"""

from typing import List, Tuple, Dict, Any, Optional
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class InspectionManager:
    """Gestisce la modifica interattiva degli effort con traccia delle modifiche"""
    
    def __init__(self, df: pd.DataFrame, efforts: List[Tuple[int, int, float]],
                 sprints: List[Dict[str, Any]], ftp: float, weight: float):
        """
        Inizializza il manager di ispezione
        
        Args:
            df: DataFrame con i dati FIT
            efforts: Lista di tuple (start_idx, end_idx, avg_power)
            sprints: Lista di dict con dati sprint
            ftp: Soglia funzionale (W)
            weight: Peso atleta (kg)
        """
        self.df = df
        self.ftp = ftp
        self.weight = weight
        
        # Copia degli effort originali (indici per preservare integrità con il df)
        self.original_efforts: List[Tuple[int, int, float]] = [
            (s, e, avg) for s, e, avg in efforts
        ]
        
        # Effort modificati (manteniamo indici ma potrebbero essere mappati a secondi)
        self.modified_efforts: List[Tuple[int, int, float]] = [
            (s, e, avg) for s, e, avg in efforts
        ]
        
        self.sprints = sprints
        
        # Traccia modifiche per ogni effort
        self.modifications: Dict[int, bool] = {i: False for i in range(len(efforts))}
        
        # Mapping tempo_sec -> indice per interpolazione
        self.time_sec = df['time_sec'].values
        self.power = df['power'].values
        
        logger.info(
            f"InspectionManager inizializzato: {len(self.original_efforts)} efforts, "
            f"FTP={ftp}W, Weight={weight}kg"
        )
    
    def _time_to_index(self, time_sec: float) -> int:
        """Converte secondi a indice nel dataframe"""
        # Trova l'indice più vicino al tempo dato
        idx = np.searchsorted(self.time_sec, time_sec)
        idx = max(0, min(idx, len(self.time_sec) - 1))
        # Se non è esatto, controlla il valore precedente
        if idx > 0 and abs(self.time_sec[idx-1] - time_sec) < abs(self.time_sec[idx] - time_sec):
            idx -= 1
        return idx
    
    def _index_to_time(self, idx: int) -> float:
        """Converte indice a secondi"""
        return self.time_sec[idx]
    
    def _recalculate_effort_power(self, start_idx: int, end_idx: int) -> float:
        """
        Calcola la potenza media di un effort in base ai nuovi indici.
        
        Note: end_idx è ESCLUSIVO (non incluso), come da convenzione Python slicing
        """
        # Verifica che gli indici siano validi
        if start_idx < 0 or start_idx >= len(self.power):
            return 0.0
        if end_idx <= 0 or end_idx > len(self.power):
            return 0.0
        if start_idx >= end_idx:
            return 0.0
        
        # Usa slicing con end_idx esclusivo
        seg_power = self.power[start_idx:end_idx]
        return float(np.mean(seg_power[seg_power > 0])) if (seg_power > 0).any() else 0.0
    
    def modify_effort(self, effort_idx: int, start_sec: float, end_sec: float):
        """
        Modifica i bordi di un effort
        
        Args:
            effort_idx: Indice dell'effort da modificare
            start_sec: Tempo inizio in secondi
            end_sec: Tempo fine in secondi
            
        Raises:
            ValueError: Se parametri non validi
        """
        if effort_idx < 0 or effort_idx >= len(self.original_efforts):
            raise ValueError(f"Indice effort non valido: {effort_idx}")
        
        if start_sec >= end_sec:
            raise ValueError(f"Inizio ({start_sec}s) deve essere prima di fine ({end_sec}s)")
        
        if start_sec < self.time_sec[0] or end_sec > self.time_sec[-1]:
            raise ValueError(
                f"Tempo fuori range [0, {self.time_sec[-1]:.1f}]s"
            )
        
        # Converti a indici
        start_idx = self._time_to_index(start_sec)
        end_idx = self._time_to_index(end_sec)
        
        if start_idx >= end_idx:
            raise ValueError("Range di indici non valido dopo conversione")
        
        # Calcola nuova potenza media
        new_avg_power = self._recalculate_effort_power(start_idx, end_idx)
        
        # Aggiorna
        self.modified_efforts[effort_idx] = (start_idx, end_idx, new_avg_power)
        self.modifications[effort_idx] = True
        
        logger.info(
            f"Effort {effort_idx} modificato: "
            f"({start_sec:.1f}s, {end_sec:.1f}s) -> ({start_idx}, {end_idx}, {new_avg_power:.0f}W)"
        )
    
    def reset_effort(self, effort_idx: int):
        """Ripristina un effort al valore originale"""
        if effort_idx < 0 or effort_idx >= len(self.original_efforts):
            raise ValueError(f"Indice effort non valido: {effort_idx}")
        
        self.modified_efforts[effort_idx] = self.original_efforts[effort_idx]
        self.modifications[effort_idx] = False
        
        logger.info(f"Effort {effort_idx} ripristinato")
    
    def delete_effort(self, effort_idx: int):
        """Elimina un effort dalla lista"""
        if effort_idx < 0 or effort_idx >= len(self.modified_efforts):
            raise ValueError(f"Indice effort non valido: {effort_idx}")
        
        self.modified_efforts.pop(effort_idx)
        self.original_efforts.pop(effort_idx)
        
        # Ricalcola mappatura delle modifiche
        old_mods = self.modifications
        self.modifications = {}
        new_idx = 0
        for i in range(len(old_mods)):
            if i != effort_idx:
                self.modifications[new_idx] = old_mods[i]
                new_idx += 1
        
        logger.info(f"Effort {effort_idx} eliminato - rimasti {len(self.modified_efforts)}")
    
    def is_modified(self, effort_idx: int) -> bool:
        """Verifica se un effort è stato modificato"""
        if effort_idx < 0 or effort_idx >= len(self.modifications):
            return False
        return self.modifications.get(effort_idx, False)
    
    def get_modified_efforts(self) -> List[Tuple[int, int, float]]:
        """Ritorna la lista degli effort modificati"""
        return list(self.modified_efforts)
    
    def get_effort_stats(self, effort_idx: int) -> Dict[str, Any]:
        """Ritorna statistiche dettagliate di un effort
        
        Note: end_idx è esclusivo (non incluso), seguendo la convenzione Python slicing
        """
        if effort_idx < 0 or effort_idx >= len(self.modified_efforts):
            raise ValueError(f"Indice effort non valido: {effort_idx}")
        
        start_idx, end_idx, avg_power = self.modified_efforts[effort_idx]
        
        seg_power = self.power[start_idx:end_idx]
        seg_time = self.time_sec[start_idx:end_idx]
        
        start_time = seg_time[0]
        end_time = seg_time[-1]
        duration = end_time - start_time
        
        # Valori disponibili
        power_peak = float(seg_power.max()) if len(seg_power) > 0 else 0.0
        power_mean = float(avg_power)
        
        # HR se disponibile
        if 'heartrate' in self.df.columns:
            seg_hr = self.df['heartrate'].iloc[start_idx:end_idx].values
            hr_mean = float(seg_hr[seg_hr > 0].mean()) if (seg_hr > 0).any() else 0.0
            hr_max = float(seg_hr.max()) if len(seg_hr) > 0 else 0.0
        else:
            hr_mean = 0.0
            hr_max = 0.0
        
        # Altimetria se disponibile
        if 'altitude' in self.df.columns:
            seg_alt = self.df['altitude'].iloc[start_idx:end_idx].values
            elevation_gain = float(seg_alt[-1] - seg_alt[0])
            vam = elevation_gain / (duration / 3600) if duration > 0 else 0.0
        else:
            elevation_gain = 0.0
            vam = 0.0
        
        # Calcoli w/kg
        w_kg = power_mean / self.weight if self.weight > 0 else 0.0
        
        # Calcolo energia (kJ)
        energy_j = 0.0
        for i in range(start_idx, min(end_idx - 1, len(self.time_sec) - 1)):
            dt = self.time_sec[i+1] - self.time_sec[i]
            if dt > 0 and dt < 30:  # Sanità check per delta
                energy_j += self.power[i] * dt
        energy_kj = energy_j / 1000
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'power_mean': power_mean,
            'power_peak': power_peak,
            'w_kg': w_kg,
            'hr_mean': hr_mean,
            'hr_max': hr_max,
            'elevation_gain': elevation_gain,
            'vam': vam,
            'energy_kj': energy_kj,
            'is_modified': self.is_modified(effort_idx),
            'original_duration': (
                self.time_sec[self.original_efforts[effort_idx][1] - 1] -
                self.time_sec[self.original_efforts[effort_idx][0]]
            )
        }
    
    def get_all_stats(self) -> List[Dict[str, Any]]:
        """Ritorna statistiche per tutti gli effort"""
        stats = []
        for i in range(len(self.modified_efforts)):
            try:
                stats.append(self.get_effort_stats(i))
            except Exception as e:
                logger.error(f"Errore calcolo stats effort {i}: {e}")
        return stats
    
    def validate_efforts(self) -> Tuple[bool, str]:
        """
        Valida la lista di effort modificati
        
        Returns:
            Tuple (is_valid, message)
        """
        if len(self.modified_efforts) == 0:
            return False, "Nessun effort presente"
        
        for i, (start, end, avg) in enumerate(self.modified_efforts):
            if start >= end:
                return False, f"Effort {i}: inizio >= fine"
            if start < 0 or end > len(self.power):
                return False, f"Effort {i}: indici fuori range"
            if avg <= 0:
                return False, f"Effort {i}: potenza media non valida"
        
        return True, "Validazione OK"


# ============================================================================
# DATABASE FUNCTIONS - Salvataggio/Caricamento Effort
# ============================================================================

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime


def get_database_path() -> Path:
    """Ritorna il percorso della cartella Database in PEFFORT"""
    peffort_dir = Path(__file__).parent
    db_path = peffort_dir / "Database" / "JSON"
    db_path.mkdir(parents=True, exist_ok=True)
    return db_path


def hash_fit_file(fit_path: str) -> str:
    """Calcola hash MD5 di un file FIT per verificare integrità"""
    try:
        with open(fit_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Errore nel calcolo hash FIT: {e}")
        return ""


def save_efforts_to_database(fit_path: str, efforts: List[Tuple[int, int, float]]) -> bool:
    """
    Salva gli effort in un file JSON nel Database
    
    Args:
        fit_path: Percorso completo al file FIT originale
        efforts: Lista di tuple (start_idx, end_idx, avg_power)
    
    Returns:
        True se salvato con successo, False altrimenti
    """
    try:
        fit_name = Path(fit_path).stem  # Nome senza estensione
        db_path = get_database_path()
        json_path = db_path / f"{fit_name}.efforts.json"
        
        fit_hash = hash_fit_file(fit_path)
        
        data = {
            "fit_file": Path(fit_path).name,
            "fit_hash": fit_hash,
            "created": datetime.now().isoformat(),
            "efforts": [
                {"start_idx": int(s), "end_idx": int(e), "avg_power": float(avg)}
                for s, e, avg in efforts
            ]
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Effort salvati in: {json_path}")
        return True
        
    except Exception as e:
        logger.error(f"Errore nel salvataggio effort: {e}", exc_info=True)
        return False


def load_efforts_from_database(fit_path: str) -> Optional[List[Tuple[int, int, float]]]:
    """
    Carica gli effort da file JSON nel Database se esiste e hash valido
    
    Args:
        fit_path: Percorso completo al file FIT
    
    Returns:
        Lista di tuple (start_idx, end_idx, avg_power) se trovato e valido, None altrimenti
    """
    try:
        fit_name = Path(fit_path).stem
        db_path = get_database_path()
        json_path = db_path / f"{fit_name}.efforts.json"
        
        if not json_path.exists():
            logger.info(f"Nessun file di effort salvato per {fit_name}")
            return None
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Verifica hash
        stored_hash = data.get("fit_hash", "")
        current_hash = hash_fit_file(fit_path)
        
        if stored_hash and stored_hash != current_hash:
            logger.warning(f"Hash FIT non corrisponde. File potrebbe essere stato modificato.")
            return None
        
        # Estrai effort
        efforts = [
            (e["start_idx"], e["end_idx"], e["avg_power"])
            for e in data.get("efforts", [])
        ]
        
        logger.info(f"Effort caricati da: {json_path}")
        return efforts if efforts else None
        
    except Exception as e:
        logger.error(f"Errore nel caricamento effort: {e}", exc_info=True)
        return None


def get_saved_effort_info(fit_path: str) -> Optional[Dict[str, Any]]:
    """
    Ritorna info sul file effort salvato (data creazione, numero effort, ecc)
    
    Args:
        fit_path: Percorso completo al file FIT
    
    Returns:
        Dict con info o None se non esiste
    """
    try:
        fit_name = Path(fit_path).stem
        db_path = get_database_path()
        json_path = db_path / f"{fit_name}.efforts.json"
        
        if not json_path.exists():
            return None
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return {
            "path": str(json_path),
            "created": data.get("created"),
            "effort_count": len(data.get("efforts", [])),
            "fit_name": data.get("fit_file")
        }
        
    except Exception as e:
        logger.error(f"Errore nel recupero info effort: {e}")
        return None
