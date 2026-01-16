import sys
import os
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, 
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

# Gestione percorsi per trovare 'shared'
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

try:
    from shared.styles import get_style
except ImportError:
    def get_style(x): return "background-color: #061f17; color: white;"

class OmniPDAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("bFactor - OmniPD Calculator ⚡")
        self.setMinimumSize(1100, 800)
        self.setStyleSheet(get_style("Forest Green"))
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # =====================
        # SIDEBAR SINISTRA
        # =====================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(320)
        sidebar_layout = QVBoxLayout(sidebar)

        title = QLabel("⚡ OMNI-PD INPUT")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ade80; margin-bottom: 5px;")
        sidebar_layout.addWidget(title)

        # Messaggio di avviso (Requisiti dati)
        warning_label = QLabel("⚠️ Minimum 4 points,\n1 must be sprint power (1-10s).")
        warning_label.setStyleSheet("color: #fbbf24; font-size: 11px; font-weight: bold; background: #2d2613; padding: 8px; border-radius: 5px;")
        warning_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(warning_label)

        # Pulsante Importa (PIÙ PICCOLO)
        self.btn_import = QPushButton("📂 Importa CSV/Excel")
        self.btn_import.setStyleSheet("background-color: #1e293b; color: #94a3b8; height: 30px; font-size: 11px; margin-top: 10px;")
        self.btn_import.clicked.connect(self.import_csv)
        sidebar_layout.addWidget(self.btn_import)

        # Tabella
        sidebar_layout.addWidget(QLabel("Dati Test (Tempo s | Watt):"))
        self.data_table = QTableWidget(6, 2)
        self.data_table.setHorizontalHeaderLabels(["Tempo (s)", "Potenza (W)"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.seed_example_data()
        sidebar_layout.addWidget(self.data_table)

        # Controlli Righe (+ / -)
        row_controls = QHBoxLayout()
        self.btn_add_row = QPushButton("+ Riga")
        self.btn_del_row = QPushButton("- Riga")
        row_btn_style = "font-size: 10px; padding: 4px; background-color: #0d3a2f; color: #94a3b8;"
        self.btn_add_row.setStyleSheet(row_btn_style)
        self.btn_del_row.setStyleSheet(row_btn_style)
        self.btn_add_row.clicked.connect(lambda: self.data_table.insertRow(self.data_table.rowCount()))
        self.btn_del_row.clicked.connect(lambda: self.data_table.removeRow(self.data_table.rowCount() - 1))
        row_controls.addWidget(self.btn_add_row)
        row_controls.addWidget(self.btn_del_row)
        sidebar_layout.addLayout(row_controls)

        # --- CONVERTITORE RAPIDO MINUTI -> SECONDI ---
        conv_frame = QFrame()
        conv_frame.setStyleSheet("background-color: #0d3a2f; border-radius: 5px; margin-top: 10px;")
        conv_layout = QVBoxLayout(conv_frame)
        conv_layout.addWidget(QLabel("⏱ Convertitore rapido (min → sec):"))
        
        conv_input_layout = QHBoxLayout()
        self.min_input = QLineEdit()
        self.min_input.setPlaceholderText("min")
        self.min_input.setFixedWidth(60)
        self.min_input.textChanged.connect(self.convert_min_to_sec)
        
        self.sec_output = QLabel("0 s")
        self.sec_output.setStyleSheet("color: #4ade80; font-weight: bold; font-size: 14px;")
        
        conv_input_layout.addWidget(self.min_input)
        conv_input_layout.addWidget(QLabel("➔"))
        conv_input_layout.addWidget(self.sec_output)
        conv_input_layout.addStretch()
        
        conv_layout.addLayout(conv_input_layout)
        sidebar_layout.addWidget(conv_frame)

        # Input Peso Atleta
        sidebar_layout.addSpacing(15)
        sidebar_layout.addWidget(QLabel("Peso Atleta (kg):"))
        self.weight_input = QLineEdit("75")
        sidebar_layout.addWidget(self.weight_input)

        # Pulsante Calcola Finale
        self.btn_calculate = QPushButton("🚀 CALCOLA MODELLI")
        self.btn_calculate.setObjectName("ActionBtn")
        self.btn_calculate.setMinimumHeight(50)
        sidebar_layout.addWidget(self.btn_calculate)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(QLabel("© 2026 bFactor Engine 💦"), alignment=Qt.AlignCenter)

        # =====================
        # AREA CENTRALE
        # =====================
        content_area = QVBoxLayout()
        self.web_view = QWebEngineView()
        self.web_view.setHtml("<body style='background-color:#061f17; color:#94a3b8; display:flex; justify-content:center; align-items:center; height:100vh; font-family:sans-serif;'><h2>Pronto per l'analisi...</h2></body>")
        content_area.addWidget(self.web_view)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(content_area)

    # =====================
    # LOGICA GUI
    # =====================
    def convert_min_to_sec(self, text):
        """Calcolo veloce minuti -> secondi mentre scrivi"""
        try:
            if text:
                val = float(text.replace(',', '.'))
                self.sec_output.setText(f"{int(val * 60)} s")
            else:
                self.sec_output.setText("0 s")
        except ValueError:
            self.sec_output.setText("err")

    def seed_example_data(self):
        examples = [("15", "850"), ("60", "550"), ("300", "380"), ("720", "320")]
        for i, (t, p) in enumerate(examples):
            self.data_table.setItem(i, 0, QTableWidgetItem(t))
            self.data_table.setItem(i, 1, QTableWidgetItem(p))

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Apri file test", "", "Dati (*.csv *.xlsx *.xls)")
        if file_path:
            try:
                df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
                self.data_table.setRowCount(0)
                for i, row in df.iterrows():
                    self.data_table.insertRow(i)
                    self.data_table.setItem(i, 0, QTableWidgetItem(str(row.iloc[0])))
                    self.data_table.setItem(i, 1, QTableWidgetItem(str(row.iloc[1])))
                self.web_view.setHtml(f"<body style='background-color:#061f17; color:#4ade80; display:flex; justify-content:center; align-items:center; height:100vh;'><h2>✅ {os.path.basename(file_path)} caricato!</h2></body>")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile caricare il file:\n{str(e)}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = OmniPDAnalyzer()
    window.showMaximized()
    sys.exit(app.exec())