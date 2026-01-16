import sys
import os
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

# =========================================================================
# GESTIONE PERCORSI PER IMPORT SHARED 💦
# =========================================================================
# Saliamo di un livello per trovare la cartella 'shared'
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

try:
    from shared.styles import get_style
except ImportError:
    # Fallback se non trova lo stile durante lo sviluppo
    def get_style(x): return "background-color: #061f17; color: white;"

class OmniPDAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("bFactor - OmniPD Calculator ⚡")
        self.setMinimumSize(1100, 700)
        
        # Applichiamo lo stile centralizzato
        self.setStyleSheet(get_style("Forest Green"))
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =====================
        # SIDEBAR SINISTRA (Input Dati)
        # =====================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(320)
        sidebar_layout = QVBoxLayout(sidebar)

        title = QLabel("⚡ OMNI-PD INPUT")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ade80; margin-bottom: 15px;")
        sidebar_layout.addWidget(title)

        # Tabella per inserimento punti
        label_tab = QLabel("Inserisci punti test (Tempo | Watt):")
        label_tab.setStyleSheet("font-weight: bold; color: #94a3b8;")
        sidebar_layout.addWidget(label_tab)
        
        self.data_table = QTableWidget(8, 2)
        self.data_table.setHorizontalHeaderLabels(["Tempo (s)", "Potenza (W)"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Placeholder con qualche valore di esempio per test rapidi
        self.seed_example_data()
        sidebar_layout.addWidget(self.data_table)

        # Input Atleta
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(QLabel("Peso Atleta (kg):"))
        self.weight_input = QLineEdit("75")
        sidebar_layout.addWidget(self.weight_input)

        # Pulsante Calcola con testo personalizzato
        self.btn_calculate = QPushButton("🚀 CALCOLA POWER-DURATION")
        self.btn_calculate.setObjectName("ActionBtn")
        self.btn_calculate.setMinimumHeight(50)
        self.btn_calculate.clicked.connect(self.run_calculations)
        sidebar_layout.addWidget(self.btn_calculate)

        sidebar_layout.addStretch()
        
        # Footer Sidebar
        footer_sb = QLabel("© 2026 bFactor Engine | Andrea Bonvicin 💦")
        footer_sb.setStyleSheet("font-size: 10px; color: #64748b;")
        sidebar_layout.addWidget(footer_sb)

        # =====================
        # AREA CENTRALE (Grafico)
        # =====================
        content_area = QVBoxLayout()
        self.web_view = QWebEngineView()
        self.web_view.setHtml(f"""
            <body style='background-color:#061f17; color:#94a3b8; display:flex; 
            flex-direction:column; justify-content:center; align-items:center; height:90vh; font-family:sans-serif;'>
                <h1 style='color:#4ade80;'>⚡ OmniPD Ready</h1>
                <p>Inserisci i dati dei test nella tabella a sinistra.</p>
                <p style='font-size: 0.8em;'>Esempio: 15s, 60s, 300s, 720s</p>
            </body>
        """)
        
        content_area.addWidget(self.web_view)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(content_area)

    def seed_example_data(self):
        """Dati di esempio per non doverli scrivere ogni volta durante il test"""
        examples = [("15", "850"), ("60", "550"), ("300", "380"), ("720", "320")]
        for i, (t, p) in enumerate(examples):
            self.data_table.setItem(i, 0, QTableWidgetItem(t))
            self.data_table.setItem(i, 1, QTableWidgetItem(p))

    def run_calculations(self):
        """Logica di calcolo e messaggio personalizzato"""
        try:
            points = []
            for r in range(self.data_table.rowCount()):
                t_item = self.data_table.item(r, 0)
                p_item = self.data_table.item(r, 1)
                if t_item and p_item and t_item.text() and p_item.text():
                    points.append((float(t_item.text()), float(p_item.text())))

            if len(points) < 3:
                msg = QMessageBox(self)
                msg.setWindowTitle("Dati Insufficienti")
                msg.setText("<b>Servono più dati!</b>")
                msg.setInformativeText("Inserisci almeno 3 punti (es: sprint, 5 min, 12 min) per una curva affidabile.")
                msg.setStyleSheet(get_style("Forest Green"))
                msg.addButton("Capito, aggiungo! 💦", QMessageBox.ButtonRole.AcceptRole)
                msg.exec()
                return

            # Qui integreremo la logica matematica di omniPD_standalone
            QMessageBox.information(self, "OmniPD", "Dati pronti per il calcolo dei modelli Monod e Ward-Smith! 💦")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Controlla i numeri inseriti: {str(e)}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = OmniPDAnalyzer()
    window.showMaximized()
    sys.exit(app.exec())