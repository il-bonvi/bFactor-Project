# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
Omniselector GUI - Interfaccia grafica (pura presentazione)
"""
import pandas as pd

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QScrollArea,
                             QMessageBox, QTabWidget, QFileDialog,
                             QDialog, QComboBox, QGridLayout)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

# Import dei moduli separati
from .core_omniselector import (
    calculate_omnipd_model, 
    load_data_from_file,
    extract_data_from_rows,
    convert_time_minutes_to_seconds
)
from .widgets_omniselector import CSVColumnDialog, MmpRow
from .plotting_omniselector import format_plot, plot_ompd_curve, plot_residuals, plot_weff
from .events_omniselector import OmniSelectorEventHandler

try:
    from shared.styles import get_style, TEMI
except ImportError:
    from shared.styles import get_style
    TEMI = {"Forest Green": {}}
    def get_style(x):
        return "background-color: #061f17; color: white;"


class OmniSelectorAnalyzer(QWidget):
    def __init__(self, theme=None):
        super().__init__()
        self.setWindowTitle("Omniselector - Analyzer")
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
        
        # Event handler
        self.event_handler = OmniSelectorEventHandler(self)
        
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)

        # --- SIDEBAR SINISTRA ---
        self.sidebar = QVBoxLayout()
        
        lbl_title = QLabel("OMNISELECTOR INPUT")
        self.lbl_title = lbl_title  # Salva riferimento per aggiornamento tema
        self.sidebar.addWidget(lbl_title)

        # Theme Selector
        '''self.theme_selector = QComboBox()
        self.theme_selector.addItems(list(TEMI.keys()))
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.apply_selected_theme)
        self.sidebar.addWidget(self.theme_selector)'''

        self.info_lbl = QLabel("One must be sprint power (best 1-10s)\nMinimum 4 points!!")
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
        input_h.addWidget(self.min_in, 1)
        input_h.addWidget(self.sec_out, 1)
        conv_l.addLayout(input_h)
        self.sidebar.addWidget(self.conv_box)

        # Bottone Calcola
        self.btn_calc = QPushButton("⚙️ ELABORA MODELLO")
        self.btn_calc.clicked.connect(self.run_calculation)
        self.sidebar.addWidget(self.btn_calc)

        # Bottone Import CSV
        self.btn_import = QPushButton("📁 IMPORT CSV")
        self.btn_import.clicked.connect(self.import_file)
        self.sidebar.addWidget(self.btn_import)

        # Risultati
        self.res_box = QFrame()
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
        right_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        
        # Tab 1: OmPD Curve
        self.create_ompd_tab()
        
        # Tab 2: Residuals
        self.create_residuals_tab()
        
        # Tab 3: W'eff
        self.create_weff_tab()

        self.main_layout.addLayout(self.sidebar, 1)
        self.main_layout.addLayout(right_layout, 3)
        
        # Theme Selector in alto a destra
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()  # Spinge il selector a destra
    
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(list(TEMI.keys()))
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.apply_selected_theme)
        self.theme_selector.setMaximumWidth(90)
        self.theme_selector.setFixedHeight(10) 
        self.theme_selector.setStyleSheet("""
            QComboBox {
                font-size: 10px;
                padding: 1px 4px;
                min-height: 20px;
                max-height: 20px;
            }
            QComboBox::drop-down {
                width: 15px;
            }
        """)
        theme_layout.addWidget(self.theme_selector)
        
        right_layout.addLayout(theme_layout)
        right_layout.addWidget(self.tab_widget)

        # Applica gli stili iniziali
        self.update_widget_styles()
        
        self.load_initial_points()

    def create_ompd_tab(self):
        """Crea il tab principale OmPD"""
        tab1 = QWidget()
        layout1 = QVBoxLayout(tab1)
        
        colors = TEMI.get(self.current_theme, TEMI["Forest Green"])
        bg_color = colors.get("bg", "#061f17")
        
        self.figure1 = Figure(facecolor=bg_color)
        self.canvas1 = FigureCanvas(self.figure1)
        self.ax1 = self.figure1.add_subplot(111)
        format_plot(self.ax1, self.current_theme)
        
        # Toolbar
        toolbar1 = NavigationToolbar(self.canvas1, tab1)
        
        layout1.addWidget(toolbar1)
        layout1.addWidget(self.canvas1)
        
        self.tab_widget.addTab(tab1, "OmPD Curve")

    def create_residuals_tab(self):
        """Crea il tab dei residui"""
        tab2 = QWidget()
        layout2 = QVBoxLayout(tab2)
        
        colors = TEMI.get(self.current_theme, TEMI["Forest Green"])
        bg_color = colors.get("bg", "#061f17")
        
        self.figure2 = Figure(facecolor=bg_color)
        self.canvas2 = FigureCanvas(self.figure2)
        self.ax2 = self.figure2.add_subplot(111)
        format_plot(self.ax2, self.current_theme)
        
        # Toolbar
        toolbar2 = NavigationToolbar(self.canvas2, tab2)
        
        layout2.addWidget(toolbar2)
        layout2.addWidget(self.canvas2)
        
        self.tab_widget.addTab(tab2, "Residuals")

    def create_weff_tab(self):
        """Crea il tab W'eff"""
        tab3 = QWidget()
        layout3 = QVBoxLayout(tab3)
        
        colors = TEMI.get(self.current_theme, TEMI["Forest Green"])
        bg_color = colors.get("bg", "#061f17")
        
        self.figure3 = Figure(facecolor=bg_color)
        self.canvas3 = FigureCanvas(self.figure3)
        self.ax3 = self.figure3.add_subplot(111)
        format_plot(self.ax3, self.current_theme)
        
        # Toolbar
        toolbar3 = NavigationToolbar(self.canvas3, tab3)
        
        layout3.addWidget(toolbar3)
        layout3.addWidget(self.canvas3)
        
        self.tab_widget.addTab(tab3, "W'eff")

    def apply_selected_theme(self, tema_nome):
        """Cambia il tema dell'interfaccia e aggiorna grafici"""
        self.current_theme = tema_nome
        self.setStyleSheet(get_style(tema_nome))
        
        # Aggiorna i colori di background delle figure matplotlib
        colors = TEMI.get(tema_nome, TEMI["Forest Green"])
        bg_color = colors.get("bg", "#061f17")
        
        self.figure1.set_facecolor(bg_color)
        self.figure2.set_facecolor(bg_color)
        self.figure3.set_facecolor(bg_color)
        
        # Aggiorna gli stili specifici dei widget
        self.update_widget_styles()
        
        # Ridisegna i grafici con il nuovo tema
        self.update_ompd_plot()
        self.update_residuals_plot()
        self.update_weff_plot()
    
    def update_widget_styles(self):
        """Aggiorna gli stili dei widget in base al tema corrente"""
        colors = TEMI.get(self.current_theme, TEMI["Forest Green"])
        
        accent_color = colors.get("accent", "#4ade80")
        btn_color = colors.get("btn", "#16a34a")
        text_color = colors.get("text", "#f1f5f9")
        sidebar_color = colors.get("sidebar", "#0b2e24")
        btn_text_color = colors.get("btn_text", "#ffffff")
        bg_color = colors.get("bg", "#061f17")
        border_color = colors.get("border", "#334155")
        
        # Titolo sidebar
        self.lbl_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {accent_color};")
        
        # Info label
        self.info_lbl.setStyleSheet(f"color: {border_color}; font-style: italic; font-size: 11px;")
        
        # Titolo converter
        self.conv_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {accent_color};")
        
        # Output converter
        self.sec_out.setStyleSheet(f"font-weight: bold; color: {text_color}; font-size: 14px; padding: 6px;")

        # Box risultati senza bordo
        self.res_box.setStyleSheet(f"background-color: {sidebar_color}; border-radius: 10px; padding: 10px;")
        
        # TabWidget
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {border_color};
                background: {bg_color};
            }}
            QTabBar::tab {{
                background: {sidebar_color};
                color: {text_color};
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid {border_color};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            QTabBar::tab:selected {{
                background: {btn_color};
                color: {btn_text_color};
            }}
        """)
 

    def add_empty_row(self, t="", w=""):
        # Se t o w sono False (bool), sostituisci con stringa vuota
        t = "" if t is False else t
        w = "" if w is False else w
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
            seconds = convert_time_minutes_to_seconds(text)
            self.sec_out.setText(f"= {seconds} s")
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
        
        try:
            # Se CSV, chiedi quale colonna usare
            time_col_idx = 0
            power_col_idx = 1
            
            if file_path.lower().endswith('.csv'):
                df_csv = pd.read_csv(file_path, sep=None, engine="python")
                col_dialog = CSVColumnDialog(self, df_csv.columns.tolist())
                if col_dialog.exec() == QDialog.Accepted:
                    time_col_idx, power_col_idx = col_dialog.get_selection()
                else:
                    return
            
            # Carica dati dal file
            self.x_data, self.y_data = load_data_from_file(
                file_path, time_col_idx, power_col_idx
            )
            
            # Esegui il calcolo
            self._calculate_model()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'importazione:\n{str(e)}")
    
    def _calculate_model(self):
        """Calcola il modello Omniselector usando la logica core"""
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
            # Estrai dati dalle righe UI
            self.x_data, self.y_data = extract_data_from_rows(self.rows)
            
            # Calcola il modello
            self._calculate_model()

        except Exception as e:
            QMessageBox.critical(self, "Errore Calcolo", str(e))

    def update_ompd_plot(self):
        """Aggiorna il grafico OmPD principale"""
        if self.params is None:
            # Mostra solo il titolo e il colore tema
            self.ax1.clear()
            format_plot(self.ax1, self.current_theme)
            self.ax1.set_title("Omniselector Curve", color=TEMI.get(self.current_theme, TEMI["Forest Green"]).get("text", "#f1f5f9"), fontsize=14)
            self.canvas1.draw()
            return
        plot_ompd_curve(self.ax1, self.x_data, self.y_data, self.params, self.current_theme)
        self.canvas1.draw()
        # Connetti event hover al grafico OmPD
        self.event_handler.connect_ompd_hover()

    def update_residuals_plot(self):
        """Aggiorna il grafico dei residui"""
        if self.residuals is None:
            self.ax2.clear()
            format_plot(self.ax2, self.current_theme)
            self.ax2.set_title("OmPD Residuals", color=TEMI.get(self.current_theme, TEMI["Forest Green"]).get("text", "#f1f5f9"), fontsize=14)
            self.canvas2.draw()
            return
        plot_residuals(self.ax2, self.x_data, self.residuals, self.RMSE, self.MAE, self.current_theme)
        self.canvas2.draw()
        # Connetti event hover al grafico residui
        self.event_handler.connect_residuals_hover()

    def update_weff_plot(self):
        """Aggiorna il grafico W'eff"""
        if self.params is None:
            self.ax3.clear()
            format_plot(self.ax3, self.current_theme)
            self.ax3.set_title("OmPD Effective W'", color=TEMI.get(self.current_theme, TEMI["Forest Green"]).get("text", "#f1f5f9"), fontsize=14)
            self.canvas3.draw()
            return
        plot_weff(self.ax3, self.params, self.params[1], self.current_theme)
        self.canvas3.draw()
