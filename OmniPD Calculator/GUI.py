import sys
import numpy as np
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

# Se vuoi mantenere lo stile Forest Green di PEFFORT
from ..PEFFORT.gui_interface import get_style  # Assicurati che il percorso sia corretto

class OmniPDAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("bFactor - OmniPD Calculator ⚡")
        self.setMinimumSize(1100, 700)
        
        # Applichiamo lo stile
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
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ade80; margin-bottom: 10px;")
        sidebar_layout.addWidget(title)

        # Tabella per inserimento punti (Tempo vs Potenza)
        sidebar_layout.addWidget(QLabel("Inserisci punti test (es. 15s, 3m, 12m):"))
        self.data_table = QTableWidget(6, 2)
        self.data_table.setHorizontalHeaderLabels(["Tempo (s)", "Potenza (W)"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setStyleSheet("background-color: #0d3a2f; color: white;")
        sidebar_layout.addWidget(self.data_table)

        # Input Atleta
        sidebar_layout.addWidget(QLabel("Peso Atleta (kg):"))
        self.weight_input = QLineEdit("75")
        sidebar_layout.addWidget(self.weight_input)

        # Pulsanti Azione
        self.btn_calculate = QPushButton("🚀 CALCOLA MODELLI")
        self.btn_calculate.setObjectName("ActionBtn")
        self.btn_calculate.clicked.connect(self.run_calculations)
        sidebar_layout.addWidget(self.btn_calculate)

        sidebar_layout.addStretch()
        
        # Footer Sidebar
        footer_sb = QLabel("© 2026 bFactor Engine 💦")
        footer_sb.setStyleSheet("font-size: 10px; color: #64748b;")
        sidebar_layout.addWidget(footer_sb)

        # =====================
        # AREA CENTRALE (Grafico)
        # =====================
        content_area = QVBoxLayout()
        self.web_view = QWebEngineView()
        # Placeholder iniziale
        self.web_view.setHtml("<body style='background-color:#061f17; color:white; display:flex; justify-content:center; align-items:center; height:100vh;'><h2>Inserisci i dati e clicca su Calcola</h2></body>")
        
        content_area.addWidget(self.web_view)

        # Layout finale
        main_layout.addWidget(sidebar)
        main_layout.addLayout(content_area)

    def run_calculations(self):
        """Qui andrà la logica presa dal tuo script standalone"""
        try:
            # 1. Recupero dati dalla tabella
            test_points = []
            for r in range(self.data_table.rowCount()):
                t_item = self.data_table.item(r, 0)
                p_item = self.data_table.item(r, 1)
                if t_item and p_item and t_item.text() and p_item.text():
                    test_points.append({
                        'time': float(t_item.text()),
                        'power': float(p_item.text())
                    })

            if len(test_points) < 2:
                QMessageBox.warning(self, "Dati Insufficienti", "Inserisci almeno 2 punti per il calcolo.")
                return

            # 2. Esecuzione calcoli (Monod, etc.)
            # TODO: Integrare qui le funzioni curve_fit del tuo script originale
            
            # 3. Aggiornamento grafico Plotly
            # Per ora mostriamo un messaggio di successo
            QMessageBox.information(self, "Calcolo", "Modelli calcolati con successo! Generazione grafico...")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nel calcolo: {str(e)}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = OmniPDAnalyzer()
    window.showMaximized()
    sys.exit(app.exec())