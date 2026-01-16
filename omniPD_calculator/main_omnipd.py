# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Performance Suite
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
OmniPD Standalone Launcher
Permette l'esecuzione diretta: python omniPD_calculator/main_omnipd.py
"""
import sys
from pathlib import Path

# --- Gestione sys.path per accesso a shared module e package recognition ---
if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    root_path = current_dir.parent
    
    # Aggiungi root alla sys.path se non presente
    root_str = str(root_path)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    
    # Aggiungi package directory per consentire import relativi
    pkg_str = str(current_dir)
    if pkg_str not in sys.path:
        sys.path.insert(0, pkg_str)

from PySide6.QtWidgets import QApplication

# Import della GUI - se viene eseguito come script, usa import assoluto
try:
    from .gui_omnipd import OmniPDAnalyzer
except ImportError:
    # Fallback per esecuzione diretta come script
    from gui_omnipd import OmniPDAnalyzer


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OmniPDAnalyzer()
    window.show()
    sys.exit(app.exec())
