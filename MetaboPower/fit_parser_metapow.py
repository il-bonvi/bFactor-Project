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
