# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
OmniPD GUI - Interfaccia grafica completa
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QScrollArea,
                             QMessageBox, QTabWidget, QFileDialog,
                             QDialog, QComboBox, QDialogButtonBox, QGridLayout)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import FixedLocator, FuncFormatter

# Gestione import relativi/assoluti per compatibility
try:
    from .core_omniPD import (ompd_power, ompd_power_short, w_eff, 
                              _format_time_label, TCPMAX, calculate_omnipd_model)
except ImportError:
    # Fallback per esecuzione diretta
    from omniPD_calculator.core_omniPD import (ompd_power, ompd_power_short, w_eff, 
                             _format_time_label, TCPMAX, calculate_omnipd_model)

try:
    from shared.styles import get_style, TEMI
except ImportError:
    from shared.styles import get_style
    TEMI = {"Forest Green": {}}
    def get_style(x):
        return "background-color: #061f17; color: white;"


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
        return self.cb_time.currentIndex(), self.cb_power.currentIndex()


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
    def __init__(self, theme=None):
        super().__init__()
        self.setWindowTitle("OmniPD - Analyzer")
        self.setMinimumSize(1200, 800)
        if theme is None:
            theme = "Forest Green"
        self.current_theme = theme
        self.setStyleSheet(get_style(theme))
        
        self.rows = []
        self.params = None
        self.x_data = None
        self.y_data = None
        self.residuals = None
        self.RMSE = None
        self.MAE = None
        
        # Variabili per hover
        self.hover_ann_points = None
        self.ann_curve = None
        self.cursor_point = None
        self.hover_ann_residuals = None
        self.marker_line = None
        self.marker_text = None
        
        # Connection IDs per eventi
        self.cid_ompd = None
        self.cid_residuals = None
        self.cid_weff = None
        
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)

        # --- SIDEBAR SINISTRA ---
        self.sidebar = QVBoxLayout()
        
        lbl_title = QLabel("OMNIPD INPUT")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ade80;")
        self.sidebar.addWidget(lbl_title)

        # Theme Selector
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(list(TEMI.keys()))
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.apply_selected_theme)
        self.sidebar.addWidget(self.theme_selector)

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
        self.conv_box.setObjectName("converter_box")
        conv_l = QVBoxLayout(self.conv_box)
        conv_l.setContentsMargins(12, 10, 12, 10)
        conv_l.setSpacing(8)
        # Titolo converter
        self.conv_title = QLabel("⚡ Quick Converter")
        self.conv_title.setAlignment(Qt.AlignCenter)
        self.conv_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #4ade80;") ##<<<--- DA METTERE COLORE TEMA!!!!
        conv_l.addWidget(self.conv_title)
        # Input/Output layout
        input_h = QHBoxLayout()
        input_h.setSpacing(10)
        self.min_in = QLineEdit()
        self.min_in.setPlaceholderText("Minuti")
        self.min_in.setMinimumHeight(32)
        self.min_in.textChanged.connect(self.convert_time)
        self.sec_out = QLabel("= 0 s")
        self.sec_out.setAlignment(Qt.AlignCenter)
        self.sec_out.setMinimumWidth(80)
        self.sec_out.setStyleSheet("font-weight: bold; color: white; font-size: 14px; padding: 6px;")
        input_h.addWidget(self.min_in, 1)
        input_h.addWidget(self.sec_out, 1)
        conv_l.addLayout(input_h)
        self.sidebar.addWidget(self.conv_box)

        # Bottone Calcola
        self.btn_calc = QPushButton("ELABORA MODELLO")
        self.btn_calc.setStyleSheet("background-color: #7c3aed; padding: 15px; font-weight: bold;")
        self.btn_calc.clicked.connect(self.run_calculation)
        self.sidebar.addWidget(self.btn_calc)

        # Bottone Import CSV/Excel
        self.btn_import = QPushButton("📁 IMPORT CSV/EXCEL")
        self.btn_import.setStyleSheet("background-color: #059669; padding: 12px; font-weight: bold;")
        self.btn_import.clicked.connect(self.import_file)
        self.sidebar.addWidget(self.btn_import)

        # Risultati
        self.res_box = QFrame()
        self.res_box.setStyleSheet("background-color: #1e293b; border-radius: 10px; padding: 10px;")
        res_l = QGridLayout(self.res_box)
        res_l.setSpacing(8)
        
        self.lbl_cp = QLabel("CP: -- W")
        self.lbl_wprime = QLabel("W': -- J")
        self.lbl_pmax = QLabel("Pmax: -- W")
        self.lbl_a = QLabel("A: --")
        self.lbl_rmse = QLabel("RMSE: -- W")
        self.lbl_mae = QLabel("MAE: -- W")
        
        # Colonna 1 (sinistra): CP, W', Pmax, A
        res_l.addWidget(self.lbl_cp, 0, 0)
        res_l.addWidget(self.lbl_wprime, 1, 0)
        res_l.addWidget(self.lbl_pmax, 2, 0)
        res_l.addWidget(self.lbl_a, 3, 0)
        
        # Colonna 2 (destra): RMSE, MAE
        res_l.addWidget(self.lbl_rmse, 0, 1)
        res_l.addWidget(self.lbl_mae, 1, 1)
        
        self.sidebar.addWidget(self.res_box)

        # --- AREA DESTRA (TabWidget) ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #334155;
                background: #061f17;
            }
            QTabBar::tab {
                background: #1e293b;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #7c3aed;
            }
        """)
        
        # Tab 1: OmPD Curve
        self.create_ompd_tab()
        
        # Tab 2: Residuals
        self.create_residuals_tab()
        
        # Tab 3: W'eff
        self.create_weff_tab()

        self.main_layout.addLayout(self.sidebar, 1)
        self.main_layout.addWidget(self.tab_widget, 3)

        self.load_initial_points()

    def create_ompd_tab(self):
        """Crea il tab principale OmPD"""
        tab1 = QWidget()
        layout1 = QVBoxLayout(tab1)
        
        self.figure1 = Figure(facecolor='#061f17')
        self.canvas1 = FigureCanvas(self.figure1)
        self.ax1 = self.figure1.add_subplot(111)
        self.format_plot(self.ax1)
        
        # Toolbar
        toolbar1 = NavigationToolbar(self.canvas1, tab1)
        
        layout1.addWidget(toolbar1)
        layout1.addWidget(self.canvas1)
        
        self.tab_widget.addTab(tab1, "OmPD Curve")

    def create_residuals_tab(self):
        """Crea il tab dei residui"""
        tab2 = QWidget()
        layout2 = QVBoxLayout(tab2)
        
        self.figure2 = Figure(facecolor='#061f17')
        self.canvas2 = FigureCanvas(self.figure2)
        self.ax2 = self.figure2.add_subplot(111)
        self.format_plot(self.ax2)
        
        # Toolbar
        toolbar2 = NavigationToolbar(self.canvas2, tab2)
        
        layout2.addWidget(toolbar2)
        layout2.addWidget(self.canvas2)
        
        self.tab_widget.addTab(tab2, "Residuals")

    def create_weff_tab(self):
        """Crea il tab W'eff"""
        tab3 = QWidget()
        layout3 = QVBoxLayout(tab3)
        
        self.figure3 = Figure(facecolor='#061f17')
        self.canvas3 = FigureCanvas(self.figure3)
        self.ax3 = self.figure3.add_subplot(111)
        self.format_plot(self.ax3)
        
        # Toolbar
        toolbar3 = NavigationToolbar(self.canvas3, tab3)
        
        layout3.addWidget(toolbar3)
        layout3.addWidget(self.canvas3)
        
        self.tab_widget.addTab(tab3, "W'eff")

    def format_plot(self, ax):
        """Formattazione comune per tutti i plot"""
        ax.set_facecolor('#061f17')
        ax.tick_params(colors='white')
        for s in ax.spines.values(): 
            s.set_color('#334155')
        ax.grid(True, alpha=0.1)

    def apply_selected_theme(self, tema_nome):
        """Cambia il tema dell'interfaccia"""
        self.current_theme = tema_nome
        self.setStyleSheet(get_style(tema_nome))

    def add_empty_row(self, t="", w=""):
        row = MmpRow(t, w)
        self.rows.append(row)
        self.scroll_layout.addLayout(row)

    def remove_last_row(self):
        if len(self.rows) > 0:
            row = self.rows.pop()
            for i in reversed(range(row.count())):
                widget = row.itemAt(i).widget()
                if widget: widget.deleteLater()
            self.scroll_layout.removeItem(row)

    def load_initial_points(self):
        points = [(5, 850), (180, 330), (360, 290), (750, 270)]
        for t, w in points:
            self.add_empty_row(t, w)

    def convert_time(self, text):
        try:
            val = float(text.replace(',', '.'))
            self.sec_out.setText(f"= {int(val * 60)} s")
        except:
            self.sec_out.setText("= 0 s")

    def import_file(self):
        """Importa dati da file CSV o Excel ed elabora direttamente"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona file",
            "",
            "Excel/CSV files (*.xlsm *.xlsx *.csv);;All Files (*)"
        )
        
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == ".xlsm":
                try:
                    df = pd.read_excel(file_path, sheet_name="Summary Sheet", 
                                     usecols="A:B", header=None)
                except ValueError:
                    df = pd.read_excel(file_path, sheet_name=0, 
                                     usecols="A:B", header=None)
            elif ext == ".xlsx":
                df = pd.read_excel(file_path, usecols="A:B", header=None)
            elif ext == ".csv":
                df_csv = pd.read_csv(file_path, sep=None, engine="python")
                
                # Dialog per selezionare colonne
                col_dialog = CSVColumnDialog(self, df_csv.columns.tolist())
                if col_dialog.exec() == QDialog.Accepted:
                    col_time_idx, col_power_idx = col_dialog.get_selection()
                    df = df_csv.iloc[:, [col_time_idx, col_power_idx]]
                else:
                    return
            else:
                QMessageBox.critical(self, "Errore", "Formato file non supportato")
                return
                
            # Pulizia dati
            df.columns = ["t", "P"]
            df["t"] = pd.to_numeric(df["t"], errors="coerce")
            df["P"] = pd.to_numeric(df["P"], errors="coerce")
            df = df.dropna()
            
            if df.empty:
                QMessageBox.critical(self, "Errore", "File senza dati numerici validi")
                return
            
            # Carica direttamente i dati e calcola senza visualizzare nelle righe
            self.x_data = df["t"].values
            self.y_data = df["P"].values
            
            if len(self.x_data) < 4:
                QMessageBox.critical(self, "Errore", "Hai bisogno di almeno 4 punti!")
                return
            
            # Esegui il calcolo direttamente
            self._calculate_model()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'importazione:\n{str(e)}")
    
    def _calculate_model(self):
        """Calcola il modello OmniPD usando la logica core"""
        try:
            if self.x_data is None or len(self.x_data) < 4:
                raise ValueError("Dati insufficienti")
            
            # Usa la logica di calcolo dal core
            result = calculate_omnipd_model(self.x_data, self.y_data)
            
            # Estrai i risultati
            self.params = result['params']
            self.residuals = result['residuals']
            self.RMSE = result['RMSE']
            self.MAE = result['MAE']
            
            CP = result['CP']
            W_prime = result['W_prime']
            Pmax = result['Pmax']
            A = result['A']

            # Aggiornamento Label
            self.lbl_cp.setText(f"CP: {CP:.0f} W")
            self.lbl_wprime.setText(f"W': {W_prime:.0f} J")
            self.lbl_pmax.setText(f"Pmax: {Pmax:.0f} W")
            self.lbl_a.setText(f"A: {A:.2f}")
            self.lbl_rmse.setText(f"RMSE: {self.RMSE:.2f} W")
            self.lbl_mae.setText(f"MAE: {self.MAE:.2f} W")

            # Aggiornamento Grafici
            self.update_ompd_plot()
            self.update_residuals_plot()
            self.update_weff_plot()

        except Exception as e:
            QMessageBox.critical(self, "Errore Calcolo", str(e))

    def run_calculation(self):
        # Pulisci vecchie connessioni di hover
        if self.cid_ompd is not None:
            self.canvas1.mpl_disconnect(self.cid_ompd)
            self.cid_ompd = None
        if self.cid_residuals is not None:
            self.canvas2.mpl_disconnect(self.cid_residuals)
            self.cid_residuals = None
        
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

            self.x_data = np.array(t_data)
            self.y_data = np.array(p_data)

            # Usa la logica di calcolo condivisa
            self._calculate_model()

        except Exception as e:
            QMessageBox.critical(self, "Errore Calcolo", str(e))

    def update_ompd_plot(self):
        """Aggiorna il grafico OmPD principale"""
        if self.params is None:
            return
            
        CP, W_prime, Pmax, A = self.params
        
        self.ax1.clear()
        self.format_plot(self.ax1)

        # Dati inseriti
        self.ax1.scatter(self.x_data, self.y_data, color='#4ade80', 
                        label='MMP Data', zorder=5, s=80, marker='x',
                        linewidths=1)

        # Range di tempo
        t_max = max(max(self.x_data) * 1.2, 3600)
        t_model = np.logspace(np.log10(1.0), np.log10(t_max), 500)
        
        # Curva completa
        p_model = ompd_power(t_model, CP, W_prime, Pmax, A)
        self.ax1.plot(t_model, p_model, color='#7c3aed', 
                     linewidth=2.5, label='OmniPD')
        
        # Curva base
        t_short = t_model[t_model <= TCPMAX]
        p_short = ompd_power_short(t_short, CP, W_prime, Pmax)
        self.ax1.plot(t_short, p_short, color='#3b82f6', 
                     linewidth=1.5, linestyle='--', alpha=0.7, 
                     label='Base curve (t ≤ TCPmax)')
        
        # Linee di riferimento
        self.ax1.axhline(y=CP, color='red', linestyle='--', 
                        linewidth=1.0, alpha=0.8, zorder=1)
        self.ax1.axvline(x=TCPMAX, color='blue', linestyle=':', 
                        linewidth=1.0, alpha=0.7, zorder=1)

        # Assi
        self.ax1.set_xscale("log")
        self.ax1.set_xlim(left=1, right=t_max)
        
        xticks = [5, 3*60, 5*60, 12*60, 20*60, 30*60, 40*60, 60*60]
        self.ax1.xaxis.set_major_locator(FixedLocator(xticks))
        self.ax1.xaxis.set_minor_locator(plt.NullLocator())  # Rimuove tick minori
        self.ax1.set_xticklabels([_format_time_label(t) for t in xticks])
        
        self.ax1.set_xlabel("Time", color='white')
        self.ax1.set_ylabel("Power (W)", color='white')
        self.ax1.set_title("OmniPD Curve", color='white', fontsize=14)
        
        # Griglia solo sui tick maggiori
        self.ax1.grid(which='major', linestyle='-', linewidth=0.8, alpha=0.5)
        self.ax1.grid(which='minor', visible=False)
        
        # Parametri nel grafico
        textstr = f"CP={int(round(CP))} W\nW'={int(round(W_prime))} J\nPmax={int(round(Pmax))} W\nA={A:.2f}"
        self.ax1.text(0.98, 0.98, textstr, transform=self.ax1.transAxes, 
                     fontsize=9, verticalalignment='top', horizontalalignment='right',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        self.ax1.legend(facecolor='#1e293b', edgecolor='none', 
                       labelcolor='white', loc='lower left', fontsize=9)
        
        self.canvas1.draw()
        
        # Connetti event hover al grafico OmPD
        self._connect_ompd_hover()

    def _connect_ompd_hover(self):
        """Connette gli eventi di hover per il grafico OmPD"""
        # Disconnetti vecchi eventi se presenti
        if self.cid_ompd is not None:
            self.canvas1.mpl_disconnect(self.cid_ompd)
        
        # Connetti nuovo evento
        self.cid_ompd = self.canvas1.mpl_connect('motion_notify_event', self._on_ompd_hover)
    
    def _on_ompd_hover(self, event):
        """Gestisce il movimento del mouse sul grafico OmPD"""
        if event.inaxes != self.ax1 or self.params is None:
            # Rimuovi annotazioni se fuori dall'asse
            if self.hover_ann_points is not None:
                self.hover_ann_points.remove()
                self.hover_ann_points = None
            if self.ann_curve is not None:
                self.ann_curve.remove()
                self.ann_curve = None
            self.canvas1.draw_idle()
            return
        
        # Ottieni coordinate mouse
        x_mouse = event.xdata
        if x_mouse is None:
            return
        
        CP, W_prime, Pmax, A = self.params
        
        # Rimuovi vecchia annotazione sulla curva
        if self.ann_curve is not None:
            self.ann_curve.remove()
            self.ann_curve = None
        
        # Aggiungi annotazione per la curva nel punto x_mouse
        try:
            y_curve = ompd_power(x_mouse, CP, W_prime, Pmax, A)
            self.ann_curve = self.ax1.annotate(
                f"{_format_time_label(x_mouse)}\n{int(y_curve)}W",
                xy=(x_mouse, y_curve),
                xytext=(5, 5),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#7c3aed', alpha=0.8, edgecolor='white', linewidth=1),
                fontsize=8,
                color='white',
                weight='bold'
            )
        except:
            pass
        
        # Hover sui punti inseriti
        if self.hover_ann_points is not None:
            self.hover_ann_points.remove()
            self.hover_ann_points = None
        
        # Trova il punto più vicino al mouse
        distances = np.abs(self.x_data - x_mouse)
        closest_idx = np.argmin(distances)
        closest_dist = distances[closest_idx]
        
        # Se abbastanza vicino, mostra annotazione
        if closest_dist < max(self.x_data) * 0.05:  # 5% della scala
            x_point = self.x_data[closest_idx]
            y_point = self.y_data[closest_idx]
            self.hover_ann_points = self.ax1.annotate(
                f"MMP: {_format_time_label(x_point)} @ {int(y_point)}W",
                xy=(x_point, y_point),
                xytext=(5, -20),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#4ade80', alpha=0.8, edgecolor='white', linewidth=1),
                fontsize=8,
                color='black',
                weight='bold'
            )
        
        self.canvas1.draw_idle()

    def update_residuals_plot(self):
        """Aggiorna il grafico dei residui"""
        if self.residuals is None:
            return
            
        self.ax2.clear()
        self.format_plot(self.ax2)
        
        # Linea zero
        self.ax2.axhline(0, color='white', linestyle='--', linewidth=1, alpha=0.5)
        
        # Residui
        self.ax2.plot(self.x_data, self.residuals, linestyle='-', 
                     color='red', linewidth=1, marker='x', 
                     markerfacecolor='black', markeredgecolor='black', 
                     markersize=5)
        
        # Assi
        self.ax2.set_xscale("log")
        xticks = [5, 30, 60, 3*60, 5*60, 6*60, 10*60, 12*60, 15*60, 20*60, 30*60, 60*60]
        self.ax2.xaxis.set_major_locator(FixedLocator(xticks))
        self.ax2.xaxis.set_minor_locator(plt.NullLocator())  # Rimuove tick minori
        self.ax2.xaxis.set_major_formatter(FuncFormatter(lambda x,pos: _format_time_label(x)))
        
        self.ax2.set_xlabel("Time", color='white')
        self.ax2.set_ylabel("Residuals (W)", color='white')
        self.ax2.set_title("OmPD Residuals", color='white', fontsize=14)
        
        # Griglia solo sui tick maggiori
        self.ax2.grid(which='major', linestyle='-', linewidth=0.7, alpha=0.5)
        self.ax2.grid(which='minor', visible=False)
        
        # Metriche
        metrics_text = f"RMSE = {self.RMSE:.2f} W\nMAE  = {self.MAE:.2f} W"
        self.ax2.text(0.98, 0.98, metrics_text, transform=self.ax2.transAxes,
                     fontsize=9, verticalalignment='top', horizontalalignment='right',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        self.canvas2.draw()
        
        # Connetti event hover al grafico residui
        self._connect_residuals_hover()
    
    def _connect_residuals_hover(self):
        """Connette gli eventi di hover per il grafico residui"""
        # Disconnetti vecchi eventi se presenti
        if self.cid_residuals is not None:
            self.canvas2.mpl_disconnect(self.cid_residuals)
        
        # Connetti nuovo evento
        self.cid_residuals = self.canvas2.mpl_connect('motion_notify_event', self._on_residuals_hover)
    
    def _on_residuals_hover(self, event):
        """Gestisce il movimento del mouse sul grafico residui"""
        if event.inaxes != self.ax2:
            if self.hover_ann_residuals is not None:
                self.hover_ann_residuals.remove()
                self.hover_ann_residuals = None
            self.canvas2.draw_idle()
            return
        
        x_mouse = event.xdata
        if x_mouse is None:
            return
        
        if self.hover_ann_residuals is not None:
            self.hover_ann_residuals.remove()
            self.hover_ann_residuals = None
        
        # Trova il punto più vicino
        distances = np.abs(self.x_data - x_mouse)
        closest_idx = np.argmin(distances)
        closest_dist = distances[closest_idx]
        
        if closest_dist < max(self.x_data) * 0.05:
            x_point = self.x_data[closest_idx]
            y_residual = self.residuals[closest_idx]
            self.hover_ann_residuals = self.ax2.annotate(
                f"{_format_time_label(x_point)}\nResidual: {int(y_residual)}W",
                xy=(x_point, y_residual),
                xytext=(5, 10),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='red', alpha=0.8, edgecolor='white', linewidth=1),
                fontsize=8,
                color='white',
                weight='bold'
            )
        
        self.canvas2.draw_idle()

    def update_weff_plot(self):
        """Aggiorna il grafico W'eff"""
        if self.params is None:
            return
            
        CP, W_prime, Pmax, A = self.params
        
        self.ax3.clear()
        self.format_plot(self.ax3)
        
        # Range di tempo per W'eff
        T_plot_w = np.linspace(1, 3*60, 500)
        Weff_plot = w_eff(T_plot_w, W_prime, CP, Pmax)
        
        # Curva W'eff
        self.ax3.plot(T_plot_w, Weff_plot, color='#4ade80', linewidth=2.5)
        
        # Punto 99% W'
        W_99 = 0.99 * W_prime
        t_99_idx = np.argmin(np.abs(Weff_plot - W_99))
        t_99 = T_plot_w[t_99_idx]
        w_99 = Weff_plot[t_99_idx]
        
        self.ax3.axhline(y=w_99, color='blue', linestyle='--', linewidth=1, alpha=0.8)
        self.ax3.axvline(x=t_99, color='blue', linestyle='--', linewidth=1, alpha=0.8)
        
        minutes = int(t_99 // 60)
        seconds = int(t_99 % 60)
        self.ax3.annotate(f"99% W'eff at {minutes}m{seconds}s ({int(t_99)}s)",
                         xy=(t_99, W_99), xytext=(10, -18), 
                         textcoords='offset points',
                         bbox=dict(boxstyle='round', facecolor='blue', alpha=0.2),
                         fontsize=10, color='white')
        
        # Assi
        self.ax3.set_xlim(0, 3*60)
        self.ax3.set_ylim(0, np.max(Weff_plot) * 1.1)
        self.ax3.set_xlabel("Time", color='white')
        self.ax3.set_ylabel("W'eff (J)", color='white')
        self.ax3.set_title("OmPD Effective W'", color='white', fontsize=14)
        
        x_ticks = list(range(0, 181, 30))
        self.ax3.set_xticks(x_ticks)
        self.ax3.set_xticklabels([_format_time_label(t) for t in x_ticks])
        self.ax3.set_xticks([], minor=True)  # Rimuove tick minori
        
        # Griglia pulita
        self.ax3.grid(which='major', linestyle='-', linewidth=0.8, alpha=0.5)
        self.ax3.grid(which='minor', visible=False)
        
        # Info W'
        self.ax3.text(0.98, 0.98, f"W' = {int(W_prime)} J", 
                     transform=self.ax3.transAxes, fontsize=10,
                     verticalalignment='top', horizontalalignment='right',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
        
        self.canvas3.draw()
