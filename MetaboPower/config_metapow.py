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

import json
import os
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
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Inizializza il manager
        
        Args:
            config_dir: Directory per salvare configurazioni custom. 
                       Se None, usa directory home progetto.
        """
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), ".import_configs")
        
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        self.custom_profiles = self._load_custom_profiles()
        self.preferences_file = os.path.join(config_dir, "preferences.json")
        self.preferences = self._load_preferences()
    
    def get_all_profiles(self) -> Dict:
        """Ritorna tutti i profili (built-in + custom)"""
        profiles = IMPORT_PROFILES.copy()
        profiles.update(self.custom_profiles)
        return profiles
    
    def get_profile(self, profile_name: str) -> Optional[Dict]:
        """Ritorna un profilo specifico"""
        profiles = self.get_all_profiles()
        return profiles.get(profile_name)
    
    def get_profile_by_extension(self, extension: str) -> Optional[Dict]:
        """Ritorna il profilo predefinito per un'estensione"""
        ext = extension.lower().lstrip('.')
        
        # Priorità: cortex per xlsx, generic per csv
        if ext == "xlsx":
            return self.get_profile("cortex_xlsx")
        elif ext == "csv":
            return self.get_profile("generic_csv")
        
        return None
    
    def save_custom_profile(self, profile_name: str, profile_config: Dict) -> bool:
        """Salva un profilo custom"""
        try:
            config_file = os.path.join(self.config_dir, f"{profile_name}.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(profile_config, f, indent=2, ensure_ascii=False)
            
            self.custom_profiles[profile_name] = profile_config
            return True
        except Exception as e:
            print(f"Errore salvataggio profilo: {e}")
            return False
    
    def _load_custom_profiles(self) -> Dict:
        """Carica profili custom salvati"""
        profiles = {}
        try:
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    profile_name = filename[:-5]
                    filepath = os.path.join(self.config_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        profiles[profile_name] = json.load(f)
        except Exception as e:
            print(f"Errore caricamento profili custom: {e}")
        
        return profiles
    
    def _load_preferences(self) -> Dict:
        """Carica preferenze salvate"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Errore caricamento preferenze: {e}")
        
        return {
            "default_profile_xlsx": "cortex_xlsx",
            "default_profile_csv": "generic_csv",
            "last_used_profile": None
        }
    
    def save_preferences(self) -> bool:
        """Salva preferenze"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Errore salvataggio preferenze: {e}")
            return False
    
    def set_default_profile(self, file_extension: str, profile_name: str) -> bool:
        """Imposta il profilo di default per un'estensione"""
        ext = file_extension.lower().lstrip('.')
        
        if ext == "xlsx":
            self.preferences["default_profile_xlsx"] = profile_name
        elif ext == "csv":
            self.preferences["default_profile_csv"] = profile_name
        else:
            return False
        
        return self.save_preferences()
    
    def get_default_profile(self, file_extension: str) -> Optional[str]:
        """Ottiene il profilo di default per un'estensione"""
        ext = file_extension.lower().lstrip('.')
        
        if ext == "xlsx":
            return self.preferences.get("default_profile_xlsx")
        elif ext == "csv":
            return self.preferences.get("default_profile_csv")
        
        return None
    
    def set_last_used_profile(self, profile_name: str) -> bool:
        """Salva il profilo usato più di recente"""
        self.preferences["last_used_profile"] = profile_name
        return self.save_preferences()
    
    def get_last_used_profile(self) -> Optional[str]:
        """Ottiene il profilo usato più di recente"""
        return self.preferences.get("last_used_profile")


# Istanza globale manager
_profile_manager = None


def get_profile_manager() -> ImportProfileManager:
    """Ritorna l'istanza globale del profile manager"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ImportProfileManager()
    return _profile_manager
