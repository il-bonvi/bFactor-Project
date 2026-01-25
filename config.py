# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
CONFIG.PY - Configurazione centralizzata per API keys e impostazioni sensibili
Carica credenziali da variabili d'ambiente per sicurezza
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carica variabili d'ambiente dal file .env (se presente)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# MapTiler API Key - Carica da variabile d'ambiente
MAPTILER_KEY = os.getenv(
    "MAPTILER_KEY",
    None
)

# Mapbox token (pubblico - può rimanere qui)
MAPBOX_TOKEN = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"


def validate_maptiler_key():
    """
    Valida la presenza della chiave MapTiler.
    Da chiamare solo quando effettivamente necessaria (quando si usano le mappe 3D).
    """
    if not MAPTILER_KEY:
        raise ValueError(
            "MAPTILER_KEY non configurata!\n"
            "1. Copia .env.example a .env\n"
            "2. Aggiungi la tua API key di MapTiler a .env\n"
            "3. Visita https://cloud.maptiler.com/ per ottenere una chiave gratuita"
        )
