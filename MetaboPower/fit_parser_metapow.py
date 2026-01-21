# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
FIT_PARSER_METAPOW.PY - Parser per file FIT da power meter
Estrae dati di potenza e sincronizza con metabolimetro
"""

import pandas as pd
from typing import Dict, Optional, Tuple, List
import numpy as np

try:
    import fitparse
except ImportError:
    fitparse = None


class FitFileParser:
    """Parser per file FIT da power meter"""
    
    def __init__(self):
        self.data = None
        self.metadata = {}
        self.file_path = None
    
    def load_file(self, file_path: str) -> Dict:
        """Carica file FIT"""
        if fitparse is None:
            return {
                "success": False,
                "error": "Libreria 'fitparse' non installata. Esegui: pip install fitparse"
            }
        
        try:
            self.file_path = file_path
            fitfile = fitparse.FitFile(file_path)
            
            # Estrai i record dai file FIT
            records = []
            device_info = {}
            file_id = {}
            
            # Itera sui messaggi del file FIT
            for message in fitfile.messages:
                if message.name == 'record':
                    record_data = {}
                    for field in message.fields:
                        record_data[field.name] = field.value
                    records.append(record_data)
                
                elif message.name == 'device_info':
                    for field in message.fields:
                        device_info[field.name] = field.value
                
                elif message.name == 'file_id':
                    for field in message.fields:
                        file_id[field.name] = field.value
            
            if not records:
                return {
                    "success": False,
                    "error": "Nessun dato 'record' trovato nel file FIT"
                }
            
            # Crea DataFrame
            df = pd.DataFrame(records)
            
            # Estrai metadati
            self.metadata = {
                "device": device_info.get('manufacturer', 'Unknown'),
                "device_model": device_info.get('product', 'Unknown'),
                "serial_number": device_info.get('serial_number'),
                "file_type": file_id.get('type'),
            }
            
            self.data = df
            
            return {
                "success": True,
                "rows": len(df),
                "columns": list(df.columns),
                "metadata": self.metadata,
                "power_column_found": 'power' in df.columns,
                "timestamp_column_found": 'timestamp' in df.columns
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Errore parsing FIT: {str(e)}"
            }
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Ritorna il DataFrame caricato"""
        return self.data
    
    def get_metadata(self) -> Dict:
        """Ritorna i metadati del file FIT"""
        return self.metadata
    
    def detect_effort_segments(self) -> Dict:
        """
        Rileva i segmenti di sforzo (rampa) nel file FIT
        Distingue tra warmup, rampa, cooldown
        """
        if self.data is None:
            return {"success": False, "error": "Nessun dato caricato"}
        
        if 'power' not in self.data.columns:
            return {"success": False, "error": "Colonna 'power' non trovata"}
        
        # Calcola media mobile della potenza per rilevare i segmenti
        df = self.data.copy()
        df['power'] = pd.to_numeric(df['power'], errors='coerce')
        
        # Rimuovi NaN
        df = df.dropna(subset=['power'])
        
        if len(df) == 0:
            return {"success": False, "error": "Nessun dato di potenza valido"}
        
        # Calcola la media mobile su 30 secondi (circa)
        window_size = max(1, len(df) // 20)  # Adatta la finestra
        df['power_smooth'] = df['power'].rolling(window=window_size, center=True).mean()
        
        # Rileva soglie
        min_power = df['power'].min()
        max_power = df['power'].max()
        mean_power = df['power'].mean()
        
        # Soglia: considerare "sforzo" quando power > media + 20%
        threshold_effort = mean_power + (max_power - mean_power) * 0.2
        threshold_zero = mean_power * 0.1  # Soglia per considerare zero
        
        # Identifica i segmenti
        df['is_effort'] = df['power_smooth'] > threshold_effort
        
        # Rileva i cambi di stato
        df['state_change'] = df['is_effort'].astype(int).diff().fillna(0)
        
        segments = []
        current_segment = None
        
        for idx, row in df.iterrows():
            if row['state_change'] == 1:  # Inizio sforzo
                if current_segment and current_segment['type'] == 'warmup':
                    segments.append(current_segment)
                current_segment = {
                    'start_idx': idx,
                    'start_power': row['power'],
                    'type': 'effort',
                    'data_indices': [idx]
                }
            elif row['state_change'] == -1:  # Fine sforzo
                if current_segment:
                    current_segment['end_idx'] = idx
                    current_segment['end_power'] = row['power']
                    current_segment['length'] = idx - current_segment['start_idx']
                    segments.append(current_segment)
                current_segment = None
            elif current_segment and row['is_effort']:
                current_segment['data_indices'].append(idx)
        
        # Chiudi ultimo segmento se ancora aperto
        if current_segment:
            current_segment['end_idx'] = len(df) - 1
            current_segment['end_power'] = df.iloc[-1]['power']
            current_segment['length'] = current_segment['end_idx'] - current_segment['start_idx']
            segments.append(current_segment)
        
        # Classifica i segmenti
        if len(segments) > 0:
            # Il segmento più lungo è probabilmente la rampa
            max_segment_idx = max(range(len(segments)), key=lambda i: segments[i]['length'])
            
            classified_segments = []
            for i, seg in enumerate(segments):
                if i < max_segment_idx:
                    seg['type'] = 'warmup'
                elif i == max_segment_idx:
                    seg['type'] = 'ramp'
                else:
                    seg['type'] = 'cooldown'
                
                classified_segments.append({
                    'type': seg['type'],
                    'start_idx': seg['start_idx'],
                    'end_idx': seg['end_idx'],
                    'start_power': seg['start_power'],
                    'end_power': seg['end_power'],
                    'duration': seg['length'],
                    'mean_power': df.iloc[seg['data_indices']]['power'].mean()
                })
            
            return {
                "success": True,
                "segments": classified_segments,
                "recommended_ramp": classified_segments[max_segment_idx] if max_segment_idx < len(classified_segments) else None
            }
        
        return {
            "success": False,
            "error": "Nessun segmento di sforzo rilevato",
            "segments": []
        }
    
    def extract_ramp_data(self, start_idx: int, end_idx: int) -> Optional[pd.DataFrame]:
        """Estrae i dati della rampa tra gli indici specificati"""
        if self.data is None:
            return None
        
        return self.data.iloc[start_idx:end_idx+1].copy()
    
    def get_summary(self) -> Dict:
        """Ritorna un riassunto dei dati FIT"""
        if self.data is None:
            return {"error": "Nessun dato caricato"}
        
        summary = {
            "total_records": len(self.data),
            "columns": list(self.data.columns),
            "metadata": self.metadata,
        }
        
        if 'power' in self.data.columns:
            power_data = pd.to_numeric(self.data['power'], errors='coerce').dropna()
            summary.update({
                "power_available": True,
                "power_min": float(power_data.min()),
                "power_max": float(power_data.max()),
                "power_mean": float(power_data.mean()),
                "power_std": float(power_data.std())
            })
        
        if 'timestamp' in self.data.columns:
            summary["timestamp_available"] = True
        
        return summary
