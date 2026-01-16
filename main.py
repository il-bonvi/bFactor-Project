"""
MAIN.PY - Launcher principale per bFactor Performance Suite
Punto di ingresso per accedere a tutti i moduli della suite
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QGridLayout, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from PEFFORT.gui_interface import EffortAnalyzer
from shared.styles import get_style


# =====================
# LAUNCHER PRINCIPALE
# =====================
class BfactorLauncher(QWidget):
    """
    Launcher per la suite bFactor
    Interfaccia principale per accedere ai vari moduli
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("bFactor Project")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(get_style("Forest Green"))
        
        # Variabile per mantenere riferimento alla finestra di PEFFORT
        self.peffort_window = None
        
        self.setup_ui()

    def setup_ui(self):
        """Configura l'interfaccia utente"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # =====================
        # HEADER
        # =====================
        header = QLabel("bFactor Project")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        main_layout.addWidget(header)

        # Sottotitolo
        subtitle = QLabel("Seleziona uno strumento per iniziare")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)

        # =====================
        # GRIGLIA PULSANTI PRINCIPALI
        # =====================
        grid_main = QGridLayout()
        grid_main.setSpacing(25)
        grid_main.setContentsMargins(0, 0, 0, 0)

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
        self.btn_omnipd.clicked.connect(self.show_in_development)
        grid_main.addWidget(self.btn_omnipd, 1, 0)

        # --- PULSANTE 4: NUOVA FUNZIONALITÀ ---
        self.btn_nuovo = self.create_main_button(
            "💦 Amalia allenati",      # Titolo
            "Fa allenare Amalia", # Sottotitolo
            "#ea580c"                    # Colore (Arancione in questo caso)
        )
        self.btn_nuovo.clicked.connect(self.show_in_development)
        grid_main.addWidget(self.btn_nuovo, 1, 1) # <--- Riga 1, Colonna 1

        main_layout.addLayout(grid_main)
        main_layout.addStretch()

        # =====================
        # FOOTER
        # =====================
        footer = QLabel("© 2026 bFactor Project | Developed by Andrea Bonvicin")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #64748b; font-size: 11px; margin-top: 20px;")
        main_layout.addWidget(footer)

    def create_main_button(self, title, description, accent_color):
        """
        Crea un pulsante principale stilizzato
        
        Args:
            title: Titolo del pulsante
            description: Descrizione dettagliata
            accent_color: Colore di accento (hex)
        """
        button = QPushButton(f"{title}\n\n{description}")
        button.setMinimumHeight(180)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Font personalizzato
        font = QFont("Segoe UI", 14)
        font.setBold(True)
        button.setFont(font)
        
        # Stile dinamico
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border-radius: 15px;
                padding: 25px;
                border: none;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
                transition: all 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(accent_color)};
                border: 3px solid #4ade80;
                padding: 22px;
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(accent_color)};
                padding: 27px;
            }}
        """)
        
        return button

    @staticmethod
    def lighten_color(hex_color):
        """Schiarisce un colore hex"""
        # Semplice algoritmo di schiarimento
        h = hex_color.lstrip('#')
        r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.2))
        g = min(255, int(g * 1.2))
        b = min(255, int(b * 1.2))
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def darken_color(hex_color):
        """Scurisce un colore hex"""
        h = hex_color.lstrip('#')
        r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def open_peffort(self):
        """Apre l'Effort Analyzer in una nuova finestra massimizzata"""
        if self.peffort_window is not None and self.peffort_window.isVisible():
            # Se la finestra è già aperta, portala in primo piano
            self.peffort_window.raise_()
            self.peffort_window.activateWindow()
        else:
            # Crea una nuova finestra
            self.peffort_window = EffortAnalyzer()
            self.peffort_window.showMaximized()

    def show_in_development(self):
        """Mostra un messaggio di avviso per i moduli in sviluppo"""
        QMessageBox.information(
            self,
            "UOOOPS NON FUNZ",
            "Amalia non vuole allenarsi.\n\n"
            "Riprova un altro giorno",
            QMessageBox.StandardButton.Ok
        )


# =====================
# PUNTO DI INGRESSO
# =====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = BfactorLauncher()
    launcher.show()
    sys.exit(app.exec())