# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
Omniselector UI Builder - Funzioni per costruzione interfaccia grafica
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QComboBox, QGridLayout,
                             QTabWidget)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from .plotting_omniselector import format_plot

try:
    from shared.styles import TEMI
except ImportError:
    TEMI = {"Forest Green": {}}


def create_sidebar_widgets(analyzer):
    """
    Crea tutti i widget della sidebar sinistra
    
    Args:
        analyzer: istanza di OmniSelectorAnalyzer
    """
    analyzer.sidebar = QVBoxLayout()
    
    # Titolo
    lbl_title = QLabel("OMNISELECTOR INPUT")
    analyzer.lbl_title = lbl_title
    analyzer.sidebar.addWidget(lbl_title)

    # CONVERTITORE
    _create_converter_widget(analyzer)
    
    # FILTRI
    _create_filters_widget(analyzer)

    # Bottoni
    analyzer.btn_calc = QPushButton("⚙️ ELABORA MODELLO")
    analyzer.btn_calc.clicked.connect(analyzer.run_calculation)
    analyzer.sidebar.addWidget(analyzer.btn_calc)

    analyzer.btn_import = QPushButton("📁 IMPORT CSV")
    analyzer.btn_import.clicked.connect(analyzer.import_file)
    analyzer.sidebar.addWidget(analyzer.btn_import)

    # Risultati
    _create_results_widget(analyzer)


def _create_converter_widget(analyzer):
    """Crea il widget del convertitore tempo"""
    analyzer.conv_box = QFrame()
    analyzer.conv_box.setObjectName("converter_box")
    conv_l = QVBoxLayout(analyzer.conv_box)
    conv_l.setContentsMargins(12, 10, 12, 10)
    conv_l.setSpacing(8)
    
    analyzer.conv_title = QLabel("⚡ Quick Converter")
    analyzer.conv_title.setAlignment(Qt.AlignCenter)
    conv_l.addWidget(analyzer.conv_title)
    
    input_h = QHBoxLayout()
    input_h.setSpacing(10)
    analyzer.min_in = QLineEdit()
    analyzer.min_in.setPlaceholderText("Minuti")
    analyzer.min_in.setMinimumHeight(32)
    analyzer.min_in.textChanged.connect(analyzer.convert_time)
    analyzer.sec_out = QLabel("= 0 s")
    analyzer.sec_out.setAlignment(Qt.AlignCenter)
    analyzer.sec_out.setMinimumWidth(80)
    input_h.addWidget(analyzer.min_in, 1)
    input_h.addWidget(analyzer.sec_out, 1)
    conv_l.addLayout(input_h)
    analyzer.sidebar.addWidget(analyzer.conv_box)


def _create_filters_widget(analyzer):
    """Crea il widget dei filtri"""
    analyzer.filter_box = QFrame()
    filter_l = QVBoxLayout(analyzer.filter_box)
    filter_l.setContentsMargins(12, 10, 12, 10)
    filter_l.setSpacing(8)
    
    analyzer.filter_title = QLabel("🎯 Filtri selezione")
    analyzer.filter_title.setAlignment(Qt.AlignCenter)
    filter_l.addWidget(analyzer.filter_title)

    btn_windows = QPushButton("Imposta finestre")
    btn_windows.clicked.connect(analyzer.open_time_windows_dialog)
    filter_l.addWidget(btn_windows)

    perc_row = QHBoxLayout()
    perc_row.addWidget(QLabel("Percentile min:"))
    analyzer.percentile_input = QLineEdit("80")
    analyzer.percentile_input.setPlaceholderText("0-100")
    perc_row.addWidget(analyzer.percentile_input)
    filter_l.addLayout(perc_row)

    count_row = QHBoxLayout()
    count_row.addWidget(QLabel("Valori/finestre:"))
    analyzer.count_input = QLineEdit("3")
    analyzer.count_input.setPlaceholderText("es. 3")
    count_row.addWidget(analyzer.count_input)
    filter_l.addLayout(count_row)

    sprint_row = QHBoxLayout()
    sprint_row.addWidget(QLabel("Sprint (s):"))
    analyzer.sprint_input = QLineEdit("10")
    analyzer.sprint_input.setPlaceholderText("es. 10")
    sprint_row.addWidget(analyzer.sprint_input)
    filter_l.addLayout(sprint_row)

    analyzer.sidebar.addWidget(analyzer.filter_box)


def _create_results_widget(analyzer):
    """Crea il widget dei risultati"""
    analyzer.res_box = QFrame()
    res_l = QGridLayout(analyzer.res_box)
    res_l.setSpacing(8)
    
    analyzer.lbl_cp = QLabel("CP: -- W")
    analyzer.lbl_wprime = QLabel("W': -- J")
    analyzer.lbl_pmax = QLabel("Pmax: -- W")
    analyzer.lbl_a = QLabel("A: --")
    analyzer.lbl_rmse = QLabel("RMSE: -- W")
    analyzer.lbl_mae = QLabel("MAE: -- W")
    
    # Colonna 1 (sinistra): CP, W', Pmax, A
    res_l.addWidget(analyzer.lbl_cp, 0, 0)
    res_l.addWidget(analyzer.lbl_wprime, 1, 0)
    res_l.addWidget(analyzer.lbl_pmax, 2, 0)
    res_l.addWidget(analyzer.lbl_a, 3, 0)
    
    # Colonna 2 (destra): RMSE, MAE
    res_l.addWidget(analyzer.lbl_rmse, 0, 1)
    res_l.addWidget(analyzer.lbl_mae, 1, 1)
    
    analyzer.sidebar.addWidget(analyzer.res_box)


def create_ompd_tab(analyzer):
    """Crea il tab principale OmPD"""
    tab1 = QWidget()
    layout1 = QVBoxLayout(tab1)
    
    colors = TEMI.get(analyzer.current_theme, TEMI["Forest Green"])
    bg_color = colors.get("bg", "#061f17")
    
    analyzer.figure1 = Figure(facecolor=bg_color)
    analyzer.canvas1 = FigureCanvas(analyzer.figure1)
    analyzer.ax1 = analyzer.figure1.add_subplot(111)
    format_plot(analyzer.ax1, analyzer.current_theme)
    
    # Rimuovi margini per massimizzare l'area del grafico
    analyzer.figure1.tight_layout(pad=0.5)
    
    toolbar1 = NavigationToolbar(analyzer.canvas1, tab1)
    
    layout1.addWidget(toolbar1)
    layout1.addWidget(analyzer.canvas1)
    
    analyzer.tab_widget.addTab(tab1, "OmPD Curve")


def create_residuals_tab(analyzer):
    """Crea il tab dei residui"""
    tab2 = QWidget()
    layout2 = QVBoxLayout(tab2)
    
    colors = TEMI.get(analyzer.current_theme, TEMI["Forest Green"])
    bg_color = colors.get("bg", "#061f17")
    
    analyzer.figure2 = Figure(facecolor=bg_color)
    analyzer.canvas2 = FigureCanvas(analyzer.figure2)
    analyzer.ax2 = analyzer.figure2.add_subplot(111)
    format_plot(analyzer.ax2, analyzer.current_theme)
    
    # Rimuovi margini per massimizzare l'area del grafico
    analyzer.figure2.tight_layout(pad=0.5)
    
    toolbar2 = NavigationToolbar(analyzer.canvas2, tab2)
    
    layout2.addWidget(toolbar2)
    layout2.addWidget(analyzer.canvas2)
    
    analyzer.tab_widget.addTab(tab2, "Residuals")


def create_weff_tab(analyzer):
    """Crea il tab W'eff"""
    tab3 = QWidget()
    layout3 = QVBoxLayout(tab3)
    
    colors = TEMI.get(analyzer.current_theme, TEMI["Forest Green"])
    bg_color = colors.get("bg", "#061f17")
    
    analyzer.figure3 = Figure(facecolor=bg_color)
    analyzer.canvas3 = FigureCanvas(analyzer.figure3)
    analyzer.ax3 = analyzer.figure3.add_subplot(111)
    format_plot(analyzer.ax3, analyzer.current_theme)
    
    # Rimuovi margini per massimizzare l'area del grafico
    analyzer.figure3.tight_layout(pad=0.5)
    
    toolbar3 = NavigationToolbar(analyzer.canvas3, tab3)
    
    layout3.addWidget(toolbar3)
    layout3.addWidget(analyzer.canvas3)
    
    analyzer.tab_widget.addTab(tab3, "W'eff")


def create_theme_selector(analyzer):
    """Crea il selettore tema in alto a destra"""
    theme_layout = QHBoxLayout()
    theme_layout.addStretch()
    
    analyzer.theme_selector = QComboBox()
    analyzer.theme_selector.addItems(list(TEMI.keys()))
    analyzer.theme_selector.setCurrentText(analyzer.current_theme)
    analyzer.theme_selector.currentTextChanged.connect(analyzer.apply_selected_theme)
    analyzer.theme_selector.setMaximumWidth(90)
    analyzer.theme_selector.setFixedHeight(10) 
    analyzer.theme_selector.setStyleSheet("""
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
    theme_layout.addWidget(analyzer.theme_selector)
    
    return theme_layout


def apply_widget_styles(analyzer):
    """Aggiorna gli stili dei widget in base al tema corrente"""
    colors = TEMI.get(analyzer.current_theme, TEMI["Forest Green"])
    
    accent_color = colors.get("accent", "#4ade80")
    btn_color = colors.get("btn", "#16a34a")
    text_color = colors.get("text", "#f1f5f9")
    sidebar_color = colors.get("sidebar", "#0b2e24")
    btn_text_color = colors.get("btn_text", "#ffffff")
    bg_color = colors.get("bg", "#061f17")
    border_color = colors.get("border", "#334155")
    
    # Titolo sidebar
    analyzer.lbl_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {accent_color};")
    
    # Titolo converter
    analyzer.conv_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {accent_color};")
    
    # Output converter
    analyzer.sec_out.setStyleSheet(f"font-weight: bold; color: {text_color}; font-size: 14px; padding: 6px;")

    # Box risultati
    analyzer.res_box.setStyleSheet(f"background-color: {sidebar_color}; border-radius: 10px; padding: 10px;")
    
    # TabWidget
    analyzer.tab_widget.setStyleSheet(f"""
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
