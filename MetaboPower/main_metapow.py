# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
MAIN_METAPOW.PY - Entry point per MetaboPower
Confronto metabolimetro e power meter per trasposizione VT1/VT2
"""

from PySide6.QtWidgets import QApplication
import sys
from .gui_metapow import MetaboPowerGUI


class MetaboPowerApp:
    """Classe principale per MetaboPower"""
    
    def __init__(self, theme="Forest Green"):
        self.theme = theme
        self.gui = None
    
    def run(self):
        """Avvia l'applicazione"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        self.gui = MetaboPowerGUI(theme=self.theme)
        self.gui.show()
        
        if not QApplication.instance():
            sys.exit(app.exec())
        
        return self.gui


def main():
    """Entry point per esecuzione standalone"""
    app = QApplication(sys.argv)
    window = MetaboPowerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
