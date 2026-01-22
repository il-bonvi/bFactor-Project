# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
CONFIG_METAPOW.PY - Configurazioni e profili di importazione
Profili predefiniti per diversi metabolimetri e formati
"""

from typing import Dict, Optional

# Configurazioni profili di importazione
IMPORT_PROFILES = {
    "cortex_xlsx": {
        "name": "Cortex XLSX",
        "description": "File XLSX esportato direttamente da Cortex",
        "file_extensions": ["xlsx"],
        "settings": {
            "format": "xlsx",
            "metabolimeter": "cortex",
            "header_row": 117,
            "subheader_row": 118,
            "data_start_row": 119,
            "metadata_cells": {
                "cognome": "C27",
                "nome": "C28",
                "genere": "C30",
                "data_nascita": "C31",
                "altezza": "C35",
                "peso": "C36",
                "vt1": "C110",
                "vt2": "E110",
                "map": "G110",
            },
            "decimal_separator": ",",
            "turn_column_index": 2,  # Colonna C (0-based)
            "time_column_candidates": ["Time", "Time (s)", "Tempo", "Tempo (s)", "tempo", "time"],
            "power_column_candidates": ["Power", "Watt", "Watt (W)", "W"],
        }
    },
    "generic_csv": {
        "name": "CSV Generico",
        "description": "File CSV con legenda colonne",
        "file_extensions": ["csv"],
        "settings": {
            "format": "csv",
            "metabolimeter": "generic",
            "auto_detect_header": True,
            "decimal_separator": "auto",  # Rileva automaticamente
            "metadata": None,  # Nessun metadato disponibile
        }
    }
}


class ImportProfileManager:
    """Gestisce i profili di importazione"""
    
    def __init__(self):
        """Inizializza il manager"""
        pass
    
    def get_all_profiles(self) -> Dict:
        """Ritorna tutti i profili disponibili"""
        return IMPORT_PROFILES.copy()
    
    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """Ritorna un profilo specifico"""
        return IMPORT_PROFILES.get(profile_name)
    
    def get_profile_by_extension(self, extension: str) -> Optional[Dict]:
        """Ritorna il profilo predefinito per un'estensione"""
        ext = extension.lower().lstrip('.')
        
        # Priorità: cortex per xlsx, generic per csv
        if ext == "xlsx":
            return self.get_profile("cortex_xlsx")
        elif ext == "csv":
            return self.get_profile("generic_csv")
        
        return None


# Istanza globale manager
_profile_manager = None


def get_profile_manager() -> ImportProfileManager:
    """Ritorna l'istanza globale del profile manager"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ImportProfileManager()
    return _profile_manager
