# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
OmniPD Widgets - Componenti custom per la GUI
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QDialogButtonBox)


class CSVColumnDialog(QDialog):
    """Dialog per selezionare colonne CSV"""
    def __init__(self, parent, columns):
        super().__init__(parent)
        self.setWindowTitle("Seleziona colonne CSV")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Colonna Tempo
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Colonna Tempo (s):"))
        self.cb_time = QComboBox()
        self.cb_time.addItems(columns)
        time_layout.addWidget(self.cb_time)
        layout.addLayout(time_layout)
        
        # Colonna Potenza
        power_layout = QHBoxLayout()
        power_layout.addWidget(QLabel("Colonna Potenza (W):"))
        self.cb_power = QComboBox()
        self.cb_power.addItems(columns)
        if len(columns) > 1:
            self.cb_power.setCurrentIndex(1)
        power_layout.addWidget(self.cb_power)
        layout.addLayout(power_layout)
        
        # Pulsanti
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_selection(self):
        """Restituisce gli indici delle colonne selezionate"""
        return self.cb_time.currentIndex(), self.cb_power.currentIndex()


class MmpRow(QHBoxLayout):
    """Widget per input di una riga MMP (Tempo, Potenza)"""
    def __init__(self, t="", w=""):
        super().__init__()
        self.t_input = QLineEdit(str(t))
        self.t_input.setPlaceholderText("Sec")
        self.w_input = QLineEdit(str(w))
        self.w_input.setPlaceholderText("Watt")
        
        self.addWidget(QLabel("T:"))
        self.addWidget(self.t_input)
        self.addWidget(QLabel("W:"))
        self.addWidget(self.w_input)
