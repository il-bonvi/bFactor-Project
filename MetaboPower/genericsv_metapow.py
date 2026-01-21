# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
GENERICSV_METAPOW.PY - Parser per CSV generico
Gestisce l'importazione di file CSV con autodetection dell'intestazione
Supporta vari formati di decimali e separatori
"""

import pandas as pd
from typing import Dict, Optional


class GenericCSVParser:
    """Parser generico per file CSV da qualsiasi fonte"""
    
    def __init__(self):
        self.data = None
        self.metadata = {}
        self.file_path = None
    
    def load(self, file_path: str, settings: Dict) -> Dict:
        """Carica file CSV generico con autodetection"""
        try:
            self.file_path = file_path
            self.metadata = {}
            
            # ===== LEGGI IL CSV =====
            df = self._read_csv(file_path, settings)
            
            if df is None or df.empty:
                return {
                    "success": False,
                    "error": "File CSV vuoto o non leggibile"
                }
            
            # ===== NORMALIZZA DECIMALI =====
            df = self._normalize_decimals(df)
            
            # ===== POSTPROCESSING METADATI =====
            self._postprocess_metadata(df)
            
            self.data = df
            
            return {
                "success": True,
                "file_type": "CSV (Generico)",
                "rows": len(df),
                "columns": list(df.columns),
                "metadata": self.metadata
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Errore parsing CSV generico: {str(e)}"
            }
    
    def _read_csv(self, file_path: str, settings: Dict) -> Optional[pd.DataFrame]:
        """Legge CSV con autodetection di separatore e header
        
        Prova diversi separatori e strategie di rilevamento header.
        """
        separators = [',', ';', '\t']
        header_strategies = [0, None, 'infer']
        
        # Prova ogni combinazione di separatore e header
        for sep in separators:
            for header in header_strategies:
                try:
                    if header is None:
                        df = pd.read_csv(file_path, sep=sep, header=None)
                    else:
                        df = pd.read_csv(file_path, sep=sep, header=header)
                    
                    # Controlla se il DataFrame è valido
                    if not df.empty and len(df.columns) > 0:
                        # Se non ha header, genera nomi colonna generici
                        if header is None:
                            df.columns = [f"Col_{i}" for i in range(len(df.columns))]
                        
                        return df
                except Exception:
                    continue
        
        return None
    
    def _postprocess_metadata(self, df: pd.DataFrame) -> None:
        """Arricchisce metadati con info utili estratte dai dati:
        - time_column: nome della colonna tempo
        - power_column: nome della colonna potenza
        - numeric_columns: lista delle colonne numeriche disponibili
        """
        # Identifica colonne tempo e potenza
        time_col = self._find_column(df, keywords=["time", "tempo", "t (", "hh:mm:ss"])
        if time_col:
            self.metadata["time_column"] = time_col
        
        power_col = self._find_column(df, keywords=["power", "watt", "potenza", "wr", "w"])
        if power_col:
            self.metadata["power_column"] = power_col
        
        # Lista colonne numeriche per future analisi
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        self.metadata["numeric_columns"] = numeric_cols
    
    @staticmethod
    def _find_column(df: pd.DataFrame, keywords: list) -> Optional[str]:
        """Trova una colonna per keyword"""
        for col in df.columns:
            name = str(col).lower()
            if any(k.lower() in name for k in keywords):
                return col
        return None
    
    @staticmethod
    def _normalize_decimals(df: pd.DataFrame) -> pd.DataFrame:
        """Normalizza decimali: sostituisce ',' con '.' e converte colonne numeriche
        
        Rileva automaticamente il formato di decimale (virgola o punto) e normalizza.
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
                except:
                    pass  # Rimane stringa se conversione fallisce
        
        return df
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Ritorna il DataFrame caricato"""
        return self.data
    
    def get_metadata(self) -> Dict:
        """Ritorna i metadati estratti"""
        return self.metadata
    
    def get_summary(self) -> Dict:
        """Ritorna riassunto dei dati caricati"""
        if self.data is None:
            return {"error": "Nessun dato caricato"}
        
        return {
            "parser": "Generic CSV",
            "file_path": self.file_path,
            "rows": len(self.data),
            "columns": len(self.data.columns),
            "column_names": list(self.data.columns),
            "metadata": self.metadata,
            "numeric_columns": self.data.select_dtypes(include=['number']).columns.tolist()
        }
