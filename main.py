# Copyright (c) 2026 Andrea Bonvicin
# Released under the MIT License (see LICENSE file for details)

"""
MAIN.PY - Launcher principale per bFactor Performance Suite
Punto di ingresso per accedere a tutti i moduli della suite
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QGridLayout, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from PEFFORT.gui_interface import EffortAnalyzer
from omniPD_calculator import OmniPDAnalyzer
from shared.styles import get_style


class BfactorLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("bFactor Project")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(get_style("Forest Green"))
        
        self.peffort_window = None
        self.omnipd_window = None # Riferimento per OmniPD
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # HEADER
        header = QLabel("bFactor Project")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        main_layout.addWidget(header)

        subtitle = QLabel("Seleziona uno strumento per iniziare")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)

        # GRIGLIA PULSANTI
        grid_main = QGridLayout()
        grid_main.setSpacing(25)

        # --- PULSANTE 1: PEFFORT ANALYZER ---
        self.btn_peffort = self.create_main_button(
            "📈 PEFFORT Analyzer",
            "Analisi avanzata file FIT\nSprint, sforzi sostenuti e metriche",
            "#16a34a"
        )
        self.btn_peffort.clicked.connect(self.open_peffort)
        grid_main.addWidget(self.btn_peffort, 0, 0)

        # --- PULSANTE 2: OMNISELECTOR ---
        self.btn_omniselector = self.create_main_button(
            "🎯 Omniselector",
            "Selezione e validazione dati\nIn fase di sviluppo",
            "#2563eb"
        )
        self.btn_omniselector.clicked.connect(self.show_in_development)
        grid_main.addWidget(self.btn_omniselector, 0, 1)

        # --- PULSANTE 3: OmniPD CALCULATOR ---
        self.btn_omnipd = self.create_main_button(
            "⚡ OmniPD Calculator",
            "Calcoli potenza-durata\nIn fase di sviluppo",
            "#7c3aed"
        )
        # Collegato alla funzione reale
        self.btn_omnipd.clicked.connect(self.open_omnipd)
        grid_main.addWidget(self.btn_omnipd, 1, 0)

        # --- PULSANTE 4: ALTRO ---
        self.btn_nuovo = self.create_main_button(
            "Prossimo",
            "Prossimo strumento in sviluppo",
            "#ea580c"
        )
        self.btn_nuovo.clicked.connect(self.show_in_development)
        grid_main.addWidget(self.btn_nuovo, 1, 1)

        main_layout.addLayout(grid_main)
        main_layout.addStretch()

        footer = QLabel("© 2026 bFactor Project | Developed by Andrea Bonvicin")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #64748b; font-size: 11px; margin-top: 20px;")
        main_layout.addWidget(footer)

    def open_peffort(self):
        if self.peffort_window is not None and self.peffort_window.isVisible():
            self.peffort_window.raise_()
            self.peffort_window.activateWindow()
        else:
            self.peffort_window = EffortAnalyzer()
            self.peffort_window.showMaximized()

    def open_omnipd(self):
        """Apre il calcolatore OmniPD"""
        if self.omnipd_window is not None and self.omnipd_window.isVisible():
            self.omnipd_window.raise_()
            self.omnipd_window.activateWindow()
        else:
            self.omnipd_window = OmniPDAnalyzer()
            self.omnipd_window.showMaximized()

    def create_main_button(self, title, description, accent_color):
        button = QPushButton(f"{title}\n\n{description}")
        button.setMinimumHeight(180)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        button.setFont(font)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border-radius: 15px;
                padding: 25px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(accent_color)};
                border: 3px solid #4ade80;
            }}
        """)
        return button

    @staticmethod
    def lighten_color(hex_color):
        h = hex_color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        return f"#{min(255, int(rgb[0]*1.2)):02x}{min(255, int(rgb[1]*1.2)):02x}{min(255, int(rgb[2]*1.2)):02x}"

    def show_in_development(self):
        QMessageBox.information(
            self,
            "UOOOPS NON FUNZ",
            "Mona. Non c'è niente",
            QMessageBox.StandardButton.Ok
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = BfactorLauncher()
    launcher.show()
    sys.exit(app.exec())