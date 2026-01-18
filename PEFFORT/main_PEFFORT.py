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
from PySide6.QtWidgets import QApplication
from .gui_PEFFORT import EffortAnalyzer


def launch_peffort():
    """Funzione per lanciare PEFFORT come applicazione standalone"""
    app = QApplication(sys.argv)
    window = EffortAnalyzer()
    window.showMaximized()
    sys.exit(app.exec())
