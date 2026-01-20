# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
Omniselector Widgets - Componenti custom per la GUI
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QDialogButtonBox, QTextEdit)


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


class TimeWindowsDialog(QDialog):
    """Dialog per inserire finestre temporali come 'tmin,tmax' per riga"""
    
    def __init__(self, parent, defaults=None):
        super().__init__(parent)
        self.setWindowTitle("Finestre temporali (secondi)")
        self.result = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Una finestra per riga, formato: tmin,tmax"))
        
        self.text = QTextEdit()
        layout.addWidget(self.text)
        
        # Popola con valori di default
        if defaults:
            lines = [f"{int(tmin)},{int(tmax)}" for tmin, tmax in defaults]
            self.text.setPlainText("\n".join(lines))
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_windows(self):
        """Restituisce la lista di finestre temporali (tmin, tmax)"""
        text = self.text.toPlainText()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        windows = []
        for line in lines:
            try:
                if ',' in line:
                    tmin_str, tmax_str = line.split(',')
                    tmin = float(tmin_str.strip())
                    tmax = float(tmax_str.strip())
                    if tmax <= tmin:
                        raise ValueError("tmax deve essere > tmin")
                    windows.append((tmin, tmax))
                else:
                    raise ValueError(f"Riga non valida: '{line}' (usa tmin,tmax)")
            except Exception as e:
                raise ValueError(f"Errore nella riga '{line}': {str(e)}")
        
        if not windows:
            raise ValueError("Inserisci almeno una finestra valida")
        return windows
