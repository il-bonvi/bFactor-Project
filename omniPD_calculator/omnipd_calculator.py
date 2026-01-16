import sys
import os
from pathlib import Path

if __name__ == "__main__":
    root_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(root_path))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QScrollArea,
                             QApplication)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from shared.styles import get_style

class MmpRow(QHBoxLayout):
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

class OmniPDAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmniPD - Analyzer")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet(get_style("Forest Green"))
        
        self.rows = []
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)

        # --- SIDEBAR SINISTRA (Come prima) ---
        self.sidebar = QVBoxLayout()
        
        lbl_title = QLabel("OMNIPD INPUT")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ade80;")
        self.sidebar.addWidget(lbl_title)

        # NUOVO: Messaggio informativo sopra le celle
        self.info_lbl = QLabel("One must be sprint power (best 1-10s)\nMinimum 4 points!!")
        self.info_lbl.setStyleSheet("color: #94a3b8; font-style: italic; font-size: 11px;")
        self.info_lbl.setAlignment(Qt.AlignCenter)
        self.sidebar.addWidget(self.info_lbl)

        # Area Input Scrollabile
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.container = QWidget()
        self.scroll_layout = QVBoxLayout(self.container)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.container)
        self.sidebar.addWidget(self.scroll)

        # Pulsanti gestione righe
        btn_row_layout = QHBoxLayout()
        self.btn_add = QPushButton("+")
        self.btn_add.clicked.connect(self.add_empty_row)
        self.btn_remove = QPushButton("-")
        self.btn_remove.clicked.connect(self.remove_last_row)
        btn_row_layout.addWidget(self.btn_add)
        btn_row_layout.addWidget(self.btn_remove)
        self.sidebar.addLayout(btn_row_layout)

        # CONVERTITORE (Ripristinato come lo volevi)
        self.conv_box = QFrame()
        self.conv_box.setStyleSheet("background-color: #0b2e24; border: 1px solid #16a34a; border-radius: 10px; padding: 5px;")
        conv_l = QVBoxLayout(self.conv_box)
        conv_l.addWidget(QLabel("⚡ Quick Converter"))
        
        input_h = QHBoxLayout()
        self.min_in = QLineEdit()
        self.min_in.setPlaceholderText("Minuti")
        self.min_in.textChanged.connect(self.convert_time)
        self.sec_out = QLabel("= 0 s")
        self.sec_out.setStyleSheet("font-weight: bold; color: white; font-size: 14px;")
        
        input_h.addWidget(self.min_in)
        input_h.addWidget(self.sec_out)
        conv_l.addLayout(input_h)
        self.sidebar.addWidget(self.conv_box)

        # Bottone Calcola e Risultati
        self.btn_calc = QPushButton("ELABORA MODELLO")
        self.btn_calc.setStyleSheet("background-color: #7c3aed; padding: 15px; font-weight: bold;")
        self.sidebar.addWidget(self.btn_calc)

        self.res_box = QFrame()
        self.res_box.setStyleSheet("background-color: #1e293b; border-radius: 10px; padding: 10px;")
        res_l = QVBoxLayout(self.res_box)
        self.lbl_cp = QLabel("CP: -- W")
        self.lbl_wprime = QLabel("W': -- J")
        res_l.addWidget(self.lbl_cp)
        res_l.addWidget(self.lbl_wprime)
        self.sidebar.addWidget(self.res_box)

        # --- AREA DESTRA (Grafico) ---
        self.figure = Figure(facecolor='#061f17')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.format_plot()

        self.main_layout.addLayout(self.sidebar, 1)
        self.main_layout.addWidget(self.canvas, 3)

        # Inizializzazione con 4 righe obbligatorie
        self.load_initial_points()

    def format_plot(self):
        self.ax.set_facecolor('#061f17')
        self.ax.tick_params(colors='white')
        for s in self.ax.spines.values(): s.set_color('#334155')
        self.ax.grid(True, alpha=0.1)

    def add_empty_row(self, t="", w=""):
        row = MmpRow(t, w)
        self.rows.append(row)
        self.scroll_layout.addLayout(row)

    def remove_last_row(self):
        if len(self.rows) > 4:
            row = self.rows.pop()
            # Rimuoviamo i widget dal layout e li distruggiamo
            for i in reversed(range(row.count())):
                widget = row.itemAt(i).widget()
                if widget: widget.deleteLater()
            self.scroll_layout.removeItem(row)

    def load_initial_points(self):
        points = [(5, 900), (60, 560), (300, 410), (1200, 335)]
        for t, w in points:
            self.add_empty_row(t, w)

    def convert_time(self, text):
        try:
            val = float(text.replace(',', '.'))
            self.sec_out.setText(f"= {int(val * 60)} s")
        except:
            self.sec_out.setText("= 0 s")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OmniPDAnalyzer()
    window.show()
    sys.exit(app.exec())