import sys
import os
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit

# --- LOGICA PER LANCIO STANDALONE ---
if __name__ == "__main__":
    root_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(root_path))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QScrollArea,
                             QApplication, QMessageBox)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

try:
    from shared.styles import get_style
except ImportError:
    def get_style(x): return "background-color: #061f17; color: white;"

# =========================================================
# MODELLO OMNIPD COMPLETO (da script Tkinter)
# =========================================================
TCPMAX = 1800  # secondi

def ompd_power(t, CP, W_prime, Pmax, A):
    """Modello OmniPD completo con 4 parametri"""
    t = np.array(t, dtype=float)
    base = (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP
    P = np.where(t <= TCPMAX, base, base - A * np.log(t / TCPMAX))
    return P

def ompd_power_short(t, CP, W_prime, Pmax):
    """Curva base per t ≤ TCPmax"""
    t = np.array(t, dtype=float)
    return (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP

def w_eff(t, W_prime, CP, Pmax):
    """W' efficace nel tempo"""
    return W_prime * (1 - np.exp(-t * (Pmax - CP) / W_prime))

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
        self.params = None  # Parametri stimati [CP, W_prime, Pmax, A]
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)

        # --- SIDEBAR SINISTRA ---
        self.sidebar = QVBoxLayout()
        
        lbl_title = QLabel("OMNIPD INPUT")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ade80;")
        self.sidebar.addWidget(lbl_title)

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

        # CONVERTITORE
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

        # Bottone Calcola
        self.btn_calc = QPushButton("ELABORA MODELLO")
        self.btn_calc.setStyleSheet("background-color: #7c3aed; padding: 15px; font-weight: bold;")
        self.btn_calc.clicked.connect(self.run_calculation)
        self.sidebar.addWidget(self.btn_calc)

        # Risultati (Tutti i 4 parametri + metriche)
        self.res_box = QFrame()
        self.res_box.setStyleSheet("background-color: #1e293b; border-radius: 10px; padding: 10px;")
        res_l = QVBoxLayout(self.res_box)
        
        self.lbl_cp = QLabel("CP: -- W")
        self.lbl_wprime = QLabel("W': -- J")
        self.lbl_pmax = QLabel("Pmax: -- W")
        self.lbl_a = QLabel("A: --")
        self.lbl_rmse = QLabel("RMSE: -- W")
        self.lbl_mae = QLabel("MAE: -- W")
        
        res_l.addWidget(self.lbl_cp)
        res_l.addWidget(self.lbl_wprime)
        res_l.addWidget(self.lbl_pmax)
        res_l.addWidget(self.lbl_a)
        res_l.addWidget(QLabel("---"))  # Separatore
        res_l.addWidget(self.lbl_rmse)
        res_l.addWidget(self.lbl_mae)
        
        self.sidebar.addWidget(self.res_box)

        # --- AREA DESTRA (Grafico) ---
        self.figure = Figure(facecolor='#061f17')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.format_plot()

        self.main_layout.addLayout(self.sidebar, 1)
        self.main_layout.addWidget(self.canvas, 3)

        self.load_initial_points()

    def format_plot(self):
        self.ax.set_facecolor('#061f17')
        self.ax.tick_params(colors='white')
        for s in self.ax.spines.values(): 
            s.set_color('#334155')
        self.ax.grid(True, alpha=0.1)
        self.ax.set_xlabel("Time (s)", color='white')
        self.ax.set_ylabel("Power (W)", color='white')

    def add_empty_row(self, t="", w=""):
        row = MmpRow(t, w)
        self.rows.append(row)
        self.scroll_layout.addLayout(row)

    def remove_last_row(self):
        if len(self.rows) > 4:
            row = self.rows.pop()
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

    # =========================================================
    # ESECUZIONE CALCOLI - MODELLO COMPLETO
    # =========================================================
    def run_calculation(self):
        try:
            t_data = []
            p_data = []
            
            for row in self.rows:
                t_val = row.t_input.text().strip()
                w_val = row.w_input.text().strip()
                if t_val and w_val:
                    t_data.append(float(t_val))
                    p_data.append(float(w_val))

            if len(t_data) < 4:
                raise ValueError("Inserisci almeno 4 punti!")

            # Conversione in NumPy arrays
            x_data = np.array(t_data)
            y_data = np.array(p_data)

            # Fitting del modello COMPLETO a 4 parametri
            # p0: [CP, W', Pmax, A]
            initial_guess = [
                np.percentile(y_data, 30),  # CP stimato
                20000,                       # W' stimato
                y_data.max(),               # Pmax = massima potenza
                5                            # A coefficiente
            ]
            
            popt, _ = curve_fit(
                ompd_power, 
                x_data, 
                y_data, 
                p0=initial_guess, 
                maxfev=20000
            )
            
            CP, W_prime, Pmax, A = popt
            self.params = popt

            # Calcolo errori
            P_pred = ompd_power(x_data, CP, W_prime, Pmax, A)
            residuals = y_data - P_pred
            RMSE = np.sqrt(np.mean(residuals**2))
            MAE = np.mean(np.abs(residuals))

            # Aggiornamento Label Risultati
            self.lbl_cp.setText(f"CP: {CP:.2f} W")
            self.lbl_wprime.setText(f"W': {W_prime:.0f} J")
            self.lbl_pmax.setText(f"Pmax: {Pmax:.0f} W")
            self.lbl_a.setText(f"A: {A:.2f}")
            self.lbl_rmse.setText(f"RMSE: {RMSE:.2f} W")
            self.lbl_mae.setText(f"MAE: {MAE:.2f} W")

            # Aggiornamento Grafico
            self.update_plot(x_data, y_data, CP, W_prime, Pmax, A)

        except Exception as e:
            QMessageBox.critical(self, "Errore Calcolo", str(e))

    def update_plot(self, x_data, y_data, CP, W_prime, Pmax, A):
        self.ax.clear()
        self.format_plot()

        # Dati inseriti (Punti)
        self.ax.scatter(x_data, y_data, color='#4ade80', label='MMP Data', 
                       zorder=5, s=60, edgecolors='white', linewidths=1)

        # Range di tempo per le curve
        t_max = max(max(x_data) * 1.2, 1800)  # Almeno fino a TCPMAX
        t_model = np.linspace(1, t_max, 500)
        
        # Curva del modello completo
        p_model = ompd_power(t_model, CP, W_prime, Pmax, A)
        self.ax.plot(t_model, p_model, color='#7c3aed', linewidth=2.5, 
                    label='OmniPD Full Model')
        
        # Curva base (t ≤ TCPMAX)
        t_short = t_model[t_model <= TCPMAX]
        p_short = ompd_power_short(t_short, CP, W_prime, Pmax)
        self.ax.plot(t_short, p_short, color='#3b82f6', linewidth=1.5, 
                    linestyle='--', alpha=0.7, label='Base curve (t ≤ 30m)')
        
        # Linea asintotica CP
        self.ax.axhline(y=CP, color='#ef4444', linestyle='--', alpha=0.6, 
                       linewidth=1.5, label=f'CP: {CP:.1f}W')
        
        # Linea verticale TCPMAX
        self.ax.axvline(x=TCPMAX, color='#3b82f6', linestyle=':', 
                       alpha=0.5, linewidth=1.5, label='TCPmax (30m)')

        self.ax.legend(facecolor='#1e293b', edgecolor='none', 
                      labelcolor='white', loc='upper right')
        self.ax.set_title("OmniPD Power-Duration Model", color='white', fontsize=14)
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OmniPDAnalyzer()
    window.show()
    sys.exit(app.exec())