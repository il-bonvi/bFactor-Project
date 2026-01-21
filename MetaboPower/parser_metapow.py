# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
PARSER_METAPOW.PY - Orchestrator parser per dati metabolimetro
Deleghe a parser specifici per ogni tipo di metabolimetro (Cortex, Generic CSV, etc.)
Questa classe funge da dispatcher che dirotta verso il parser appropriato in base al profilo.
"""

import pandas as pd
from typing import Dict, Optional
from .config_metapow import get_profile_manager, IMPORT_PROFILES
from .cortex_metapow import CortexMetabolitParser
from .genericsv_metapow import GenericCSVParser


class MetabolitDataParser:
    """Parser orchestrator per dati metabolimetro
    
    Delega a parser specifici in base al profilo selezionato:
    - cortex_metapow.CortexMetabolitParser per XLSX Cortex
    - genericsv_metapow.GenericCSVParser per CSV generici
    
    Metodi principali:
    - load_file_with_profile(): Caricamento con profilo esplicito
    - get_data(): Ritorna DataFrame caricato
    - get_metadata(): Ritorna metadati paziente
    """
    
    def __init__(self):
        self.data = None
        self.metadata = {}
        self.file_type = None
        self.profile_used = None
        self.profile_manager = get_profile_manager()
        
        # Parsers delegati
        self.cortex_parser = CortexMetabolitParser()
        self.generic_csv_parser = GenericCSVParser()
    
    def load_file_with_profile(self, file_path: str, profile_name: str) -> Dict:
        """Carica file usando un profilo specifico"""
        try:
            profile = self.profile_manager.get_profile(profile_name)
            if not profile:
                return {
                    "success": False,
                    "error": f"Profilo '{profile_name}' non trovato"
                }
            
            self.profile_used = profile_name
            settings = profile.get("settings", {})
            file_format = settings.get("format")
            
            # Delega al parser appropriato in base al profilo
            if file_format == "xlsx":
                result = self.cortex_parser.load(file_path, settings)
                if result["success"]:
                    self.data = self.cortex_parser.get_data()
                    self.metadata = self.cortex_parser.get_metadata()
                    self.file_type = result.get("file_type")
            elif file_format == "csv":
                result = self.generic_csv_parser.load(file_path, settings)
                if result["success"]:
                    self.data = self.generic_csv_parser.get_data()
                    self.metadata = self.generic_csv_parser.get_metadata()
                    self.file_type = result.get("file_type")
            else:
                return {
                    "success": False,
                    "error": f"Formato non supportato nel profilo: {file_format}"
                }
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Errore caricamento con profilo: {str(e)}"
            }
    
    def get_data(self) -> Optional[pd.DataFrame]:
        """Ritorna il DataFrame caricato"""
        return self.data
    
    def get_metadata(self) -> Dict:
        """Ritorna i metadati paziente"""
        return self.metadata
    
    def get_summary(self) -> Dict:
        """Ritorna un riassunto dei dati"""
        if self.data is None:
            return {"error": "Nessun dato caricato"}
        
        return {
            "file_type": self.file_type,
            "profile_used": self.profile_used,
            "rows": len(self.data),
            "columns": len(self.data.columns),
            "column_names": list(self.data.columns),
            "metadata": self.metadata,
            "numeric_columns": self.data.select_dtypes(include=['number']).columns.tolist()
        }
