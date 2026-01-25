# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
CONFIG.PY - Configurazione centralizzata per API keys e impostazioni sensibili
Carica credenziali da variabili d'ambiente per sicurezza

SECURITY CONSIDERATIONS:
- MAPTILER_KEY: Required API key for MapTiler services (3D map rendering)
  Must be set in .env file or environment variable
- MAPBOX_TOKEN: Public token for Mapbox GL JS (read-only access)
  This is a public demo token and can be safely committed to source control
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env (se presente)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Mapbox token (pubblico - può rimanere qui)
# This is a publicly available demo token provided by Plotly/Mapbox
MAPBOX_TOKEN = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

def get_maptiler_key():
    """
    Lazy-loaded getter for MapTiler API key.
    Validates key is present when called, not at import time.
    
    Returns:
        str: MapTiler API key
        
    Raises:
        ValueError: If MAPTILER_KEY is not configured
    """
    key = os.getenv("MAPTILER_KEY")
    if not key:
        raise ValueError(
            "MAPTILER_KEY non configurata!\n"
            "1. Copia .env.example a .env\n"
            "2. Aggiungi la tua API key di MapTiler a .env\n"
            "3. Visita https://cloud.maptiler.com/ per ottenere una chiave gratuita"
        )
    return key

def get_mapbox_token():
    """
    Getter for Mapbox token (for consistency with get_maptiler_key).
    
    Returns:
        str: Mapbox public token
    """
    return MAPBOX_TOKEN
