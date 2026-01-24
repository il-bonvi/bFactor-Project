# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
MAIN.PY - Supporto per lancio standalone di PEFFORT
Nota: Questo file è opzionale. Per il launcher usa root/main.py
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from .gui_PEFFORT import EffortAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('peffort.log')
    ]
)
logger = logging.getLogger(__name__)


def launch_peffort():
    """Funzione per lanciare PEFFORT come applicazione standalone"""
    logger.info("Avvio PEFFORT...")
    
    # Gestisci QApplication istanza unica
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        logger.info("Nuova QApplication creata")
    else:
        logger.info("QApplication già presente")
    
    window = EffortAnalyzer()
    window.showMaximized()
    logger.info("EffortAnalyzer window shown")
    
    sys.exit(app.exec())

