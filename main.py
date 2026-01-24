# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
MAIN.PY - Launcher principale per bFactor Project
Punto di ingresso per accedere a tutti i moduli della suite
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QGridLayout, QMessageBox, QComboBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from PEFFORT import EffortAnalyzer
from omniPD_calculator import OmniPDAnalyzer
from MetaboPower import MetaboPowerApp
from bTeam import BTeamApp
from RaceReport import RaceReportGUI
from shared.styles import get_style, TEMI


class BfactorLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("bFactor Project")
        self.setMinimumSize(1000, 850)
        self.current_theme = "Forest Green"
        self.setStyleSheet(get_style(self.current_theme))
        
        self.peffort_window = None
        self.omnipd_window = None
        self.omniselector_window = None
        self.metabopower_window = None
        self.bteam_window = None
        self.racereport_window = None
        
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

        # THEME SELECTOR
        theme_layout = QHBoxLayout()
        theme_layout.setAlignment(Qt.AlignRight)
        theme_label = QLabel("Tema")
        theme_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(list(TEMI.keys()))
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.apply_theme)
        self.theme_selector.setFixedHeight(34)
        self.theme_selector.setMaximumWidth(220)
        self.theme_selector.setToolTip("Seleziona tema UI")
        self.theme_selector.setStyleSheet("""
        QComboBox {
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 12px;
        }
        QComboBox:hover {
            border: 1px solid #4ade80;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #1e293b;
        }
        """)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_selector)

        main_layout.addLayout(theme_layout)

        # GRIGLIA PULSANTI
        grid_main = QGridLayout()
        grid_main.setSpacing(25)

        # --- PULSANTE 1: PEFFORT ANALYZER ---
        self.btn_peffort = self.create_main_button(
            "📊 PEFFORT Analyzer",
            "Analisi avanzata file FIT\nSprint, sforzi sostenuti e metriche",
            "#16a34a"
        )
        self.btn_peffort.clicked.connect(self.open_peffort)
        grid_main.addWidget(self.btn_peffort, 0, 0)

        # --- PULSANTE 2: OMNISELECTOR ---
        self.btn_omniselector = self.create_main_button(
            "🧮 Omniselector",
            "Selezione e validazione dati\nIn fase di sviluppo",
            "#2563eb"
        )
        self.btn_omniselector.clicked.connect(self.open_omniselector)
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
            "🫁 MetaboPower",
            "Confronto Metabolimetro - Power Meter",
            "#b9531d"
        )
        self.btn_nuovo.clicked.connect(self.open_metabopower)
        grid_main.addWidget(self.btn_nuovo, 1, 1)

        # --- PULSANTE 5: WORK IN PROGRESS 1 ---
        self.btn_bteam = self.create_main_button(
            "👥 bTeam",
            "Prossima app in sviluppo (LENTO)",
            "#f59e0b"
        )
        self.btn_bteam.clicked.connect(self.open_bteam)
        grid_main.addWidget(self.btn_bteam, 2, 0)

        # --- PULSANTE 6: RACE REPORT ---
        self.btn_racereport = self.create_main_button(
            "📋 Race Report",
            "Generatore report gare\nAnalisi e confronto performance",
            "#0891b2"
        )
        self.btn_racereport.clicked.connect(self.open_racereport)
        grid_main.addWidget(self.btn_racereport, 2, 1)

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
            self.peffort_window = EffortAnalyzer(theme=self.current_theme)
            self.peffort_window.showMaximized()

    def open_omnipd(self):
        """Apre il calcolatore OmniPD"""
        if self.omnipd_window is not None and self.omnipd_window.isVisible():
            self.omnipd_window.raise_()
            self.omnipd_window.activateWindow()
        else:
            self.omnipd_window = OmniPDAnalyzer(theme=self.current_theme)
            self.omnipd_window.showMaximized()

    def open_omniselector(self):
        """Apre la finestra Omniselector"""
        if self.omniselector_window is not None and self.omniselector_window.isVisible():
            self.omniselector_window.raise_()
            self.omniselector_window.activateWindow()
        else:
            from omniselector import omniselector
            self.omniselector_window = omniselector(theme=self.current_theme)
            self.omniselector_window.showMaximized()

    def open_metabopower(self):
        """Apre la finestra MetaboPower"""
        if self.metabopower_window is not None and self.metabopower_window.isVisible():
            self.metabopower_window.raise_()
            self.metabopower_window.activateWindow()
        else:
            app = MetaboPowerApp(theme=self.current_theme)
            self.metabopower_window = app.run()
            self.metabopower_window.showMaximized()

    def open_bteam(self):
        if self.bteam_window is not None and self.bteam_window.isVisible():
            self.bteam_window.raise_()
            self.bteam_window.activateWindow()
        else:
            self.bteam_window = BTeamApp(theme=self.current_theme)
            self.bteam_window.showMaximized()

    def open_racereport(self):
        """Apre la finestra Race Report"""
        if self.racereport_window is not None and self.racereport_window.isVisible():
            self.racereport_window.raise_()
            self.racereport_window.activateWindow()
        else:
            self.racereport_window = RaceReportGUI()
            self.racereport_window.showMaximized()

    def apply_theme(self, tema_nome):
        """Applica il tema selezionato al launcher e lo salva"""
        self.current_theme = tema_nome
        self.setStyleSheet(get_style(tema_nome))

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