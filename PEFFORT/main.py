# Copyright (c) 2026 Andrea Bonvicin
# Released under the MIT License (see LICENSE file for details)

"""
MAIN.PY - Supporto per lancio standalone di PEFFORT
Nota: Questo file è opzionale. Per il launcher usa root/main.py
"""

import sys
from PySide6.QtWidgets import QApplication
from .gui_interface import EffortAnalyzer


def launch_peffort():
    """Funzione per lanciare PEFFORT come applicazione standalone"""
    app = QApplication(sys.argv)
    window = EffortAnalyzer()
    window.showMaximized()
    sys.exit(app.exec())
