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
                             QTabWidget, QScrollArea)
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from .plotting_omniselector import format_plot

try:
    from shared.styles import TEMI, get_style
except ImportError:
    TEMI = {"Forest Green": {}}
    def get_style(x):
        return "background-color: #061f17; color: white;"


def create_sidebar_widgets(analyzer):

    analyzer.sidebar = QVBoxLayout()
    analyzer.sidebar.setSpacing(10)
    
    # Titolo
    lbl_title = QLabel("OMNISELECTOR")
    analyzer.lbl_title = lbl_title
    analyzer.sidebar.addWidget(lbl_title)

    # SEZIONE DATI (Import)
    _create_data_section(analyzer)
    
    # SEZIONE FILTRI (con finestre temporali e convertitore)
    _create_filters_section(analyzer)

    # SEZIONE ELABORAZIONE
    _create_processing_section(analyzer)

    # SEZIONE RISULTATI
    _create_results_section(analyzer)
    
    analyzer.sidebar.addStretch()


def _create_section(title, content_widget):
    """Crea una sezione con titolo"""
    section_frame = QFrame()
    section_frame.setObjectName("section_frame")
    section_layout = QVBoxLayout(section_frame)
    section_layout.setContentsMargins(0, 0, 0, 0)
    section_layout.setSpacing(5)
    
    # Header label
    header_label = QLabel(title)
    header_label.setObjectName("section_header")
    
    # Content frame
    content_frame = QFrame()
    content_frame.setObjectName("section_content")
    content_layout = QVBoxLayout(content_frame)
    content_layout.setContentsMargins(10, 10, 10, 10)
    content_layout.addWidget(content_widget)
    
    section_layout.addWidget(header_label)
    section_layout.addWidget(content_frame)
    
    return section_frame


def _create_data_section(analyzer):
    """Crea la sezione Import Dati"""
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setSpacing(8)
    
    analyzer.btn_import = QPushButton("📁 Importa File CSV")
    analyzer.btn_import.clicked.connect(analyzer.import_file)
    layout.addWidget(analyzer.btn_import)
    
    section = _create_section("📂 DATI", content)
    analyzer.sidebar.addWidget(section)


def _create_filters_section(analyzer):
    """Crea la sezione Filtri con finestre temporali e convertitore integrato"""
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setSpacing(10)
    
    # === FINESTRE TEMPORALI ===
    windows_label = QLabel("⏱️ Finestre Temporali")
    windows_label.setStyleSheet("font-weight: bold; font-size: 11px;")
    layout.addWidget(windows_label)
    
    # Convertitore minuti->secondi con nota
    conv_row = QHBoxLayout()
    fast_conv_label = QLabel("fast conv")
    fast_conv_label.setStyleSheet("color: #64748b; font-size: 9px; font-style: italic;")
    conv_row.addWidget(fast_conv_label)
    conv_row.addWidget(QLabel("Min:"))
    analyzer.min_in = QLineEdit()
    analyzer.min_in.setPlaceholderText("es. 5")
    analyzer.min_in.setMaximumWidth(60)
    analyzer.min_in.textChanged.connect(analyzer.convert_time)
    analyzer.sec_out = QLabel("= 0 s")
    conv_row.addWidget(analyzer.min_in)
    conv_row.addWidget(analyzer.sec_out)
    conv_row.addStretch()
    layout.addLayout(conv_row)
    
    # Input finestre temporali (area scrollabile con QScrollArea)
    analyzer.time_windows_inputs = []
    analyzer.time_windows_container = QWidget()
    analyzer.time_windows_layout = QVBoxLayout(analyzer.time_windows_container)
    analyzer.time_windows_layout.setSpacing(4)
    analyzer.time_windows_layout.setContentsMargins(0, 0, 0, 0)
    
    # Aggiungi 6 finestre di default con valori comuni
    default_values = ["120", "240", "480", "900", "1800", "2700"]
    for i, default_val in enumerate(default_values):
        window_row = QHBoxLayout()
        window_input = QLineEdit()
        window_input.setPlaceholderText(f"Finestra {i+1} (s)")
        window_input.setText(default_val)
        window_row.addWidget(window_input)
        analyzer.time_windows_layout.addLayout(window_row)
        analyzer.time_windows_inputs.append(window_input)
    
    # Aggiungi stretch per evitare che le finestre siano troppo compresse
    analyzer.time_windows_layout.addStretch()
    
    # Wrap in QScrollArea per scrollabilità
    scroll_area = QScrollArea()
    scroll_area.setWidget(analyzer.time_windows_container)
    scroll_area.setWidgetResizable(True)
    scroll_area.setMaximumHeight(150)
    scroll_area.setStyleSheet("QScrollArea { border: 1px solid #334155; }")
    
    # Bottoni per gestire finestre
    btn_row = QHBoxLayout()
    btn_add = QPushButton("+ Aggiungi")
    btn_add.clicked.connect(lambda: _add_time_window(analyzer))
    btn_add.setMaximumWidth(80)
    btn_reset = QPushButton("↻ Reset")
    btn_reset.clicked.connect(lambda: _reset_time_windows(analyzer))
    btn_reset.setMaximumWidth(80)
    btn_row.addWidget(btn_add)
    btn_row.addWidget(btn_reset)
    btn_row.addStretch()
    layout.addLayout(btn_row)
    
    layout.addWidget(scroll_area)
    
    # Separator
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setObjectName("separator")
    layout.addWidget(separator)
    
    # === FILTRI AGGIUNTIVI ===
    filters_label = QLabel("🎯 Parametri Selezione")
    filters_label.setStyleSheet("font-weight: bold; font-size: 11px;")
    layout.addWidget(filters_label)
    
    perc_row = QHBoxLayout()
    perc_row.addWidget(QLabel("Percentile min:"))
    analyzer.percentile_input = QLineEdit("80")
    analyzer.percentile_input.setPlaceholderText("0-100")
    analyzer.percentile_input.setMaximumWidth(60)
    # Aggiungi validazione
    analyzer.percentile_input.textChanged.connect(
        lambda text: _validate_percentile_input(analyzer.percentile_input, text)
    )
    perc_row.addWidget(analyzer.percentile_input)
    perc_row.addStretch()
    layout.addLayout(perc_row)

    count_row = QHBoxLayout()
    count_row.addWidget(QLabel("Valori/finestre:"))
    analyzer.count_input = QLineEdit("3")
    analyzer.count_input.setPlaceholderText("es. 3")
    analyzer.count_input.setMaximumWidth(60)
    # Aggiungi validazione
    analyzer.count_input.textChanged.connect(
        lambda text: _validate_positive_int_input(analyzer.count_input, text)
    )
    count_row.addWidget(analyzer.count_input)
    count_row.addStretch()
    layout.addLayout(count_row)

    sprint_row = QHBoxLayout()
    sprint_row.addWidget(QLabel("Sprint (s):"))
    analyzer.sprint_input = QLineEdit("10")
    analyzer.sprint_input.setPlaceholderText("es. 10")
    analyzer.sprint_input.setMaximumWidth(60)
    # Aggiungi validazione
    analyzer.sprint_input.textChanged.connect(
        lambda text: _validate_positive_float_input(analyzer.sprint_input, text)
    )
    sprint_row.addWidget(analyzer.sprint_input)
    sprint_row.addStretch()
    layout.addLayout(sprint_row)
    
    section = _create_section("🎯 FILTRI", content)
    analyzer.sidebar.addWidget(section)


def _add_time_window(analyzer):
    """Aggiunge una nuova finestra temporale"""
    window_row = QHBoxLayout()
    window_input = QLineEdit()
    window_input.setPlaceholderText(f"Finestra {len(analyzer.time_windows_inputs)+1} (s)")
    window_row.addWidget(window_input)
    analyzer.time_windows_layout.addLayout(window_row)
    analyzer.time_windows_inputs.append(window_input)


def _reset_time_windows(analyzer):
    """Ripristina le finestre temporali ai valori di default"""
    default_values = ["120", "240", "480", "900", "1800", "2700"]
    
    # Ripristina i primi 6 campi ai valori di default
    for i in range(min(6, len(analyzer.time_windows_inputs))):
        analyzer.time_windows_inputs[i].setText(default_values[i])
    
    # Svuota eventuali campi aggiuntivi
    for i in range(6, len(analyzer.time_windows_inputs)):
        analyzer.time_windows_inputs[i].clear()


def _validate_percentile_input(line_edit, text):
    """Valida che il percentile sia tra 0-100"""
    if text == "":
        return
    try:
        value = float(text)
        if not (0 <= value <= 100):
            line_edit.setStyleSheet("QLineEdit { background-color: #ff6b6b; color: white; }")
            return
        line_edit.setStyleSheet("")
    except ValueError:
        line_edit.setStyleSheet("QLineEdit { background-color: #ff6b6b; color: white; }")


def _validate_positive_int_input(line_edit, text):
    """Valida che il valore sia un intero positivo"""
    if text == "":
        return
    try:
        value = int(text)
        if value <= 0:
            line_edit.setStyleSheet("QLineEdit { background-color: #ff6b6b; color: white; }")
            return
        line_edit.setStyleSheet("")
    except ValueError:
        line_edit.setStyleSheet("QLineEdit { background-color: #ff6b6b; color: white; }")


def _validate_positive_float_input(line_edit, text):
    """Valida che il valore sia un float positivo"""
    if text == "":
        return
    try:
        value = float(text)
        if value < 0:
            line_edit.setStyleSheet("QLineEdit { background-color: #ff6b6b; color: white; }")
            return
        line_edit.setStyleSheet("")
    except ValueError:
        line_edit.setStyleSheet("QLineEdit { background-color: #ff6b6b; color: white; }")


def _create_processing_section(analyzer):
    """Crea la sezione Elaborazione"""
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setSpacing(8)
    
    analyzer.btn_calc = QPushButton("⚙️ Elabora Modello")
    analyzer.btn_calc.clicked.connect(analyzer.run_calculation)
    layout.addWidget(analyzer.btn_calc)
    
    section = _create_section("⚙️ ELABORAZIONE", content)
    analyzer.sidebar.addWidget(section)


def _create_results_section(analyzer):
    """Crea la sezione Risultati"""
    content = QWidget()
    layout = QGridLayout(content)
    layout.setSpacing(8)
    
    analyzer.lbl_cp = QLabel("CP: -- W")
    analyzer.lbl_wprime = QLabel("W': -- J")
    analyzer.lbl_pmax = QLabel("Pmax: -- W")
    analyzer.lbl_a = QLabel("A: --")
    analyzer.lbl_rmse = QLabel("RMSE: -- W")
    analyzer.lbl_mae = QLabel("MAE: -- W")
    
    # Colonna 1 (sinistra): CP, W', Pmax, A
    layout.addWidget(analyzer.lbl_cp, 0, 0)
    layout.addWidget(analyzer.lbl_wprime, 1, 0)
    layout.addWidget(analyzer.lbl_pmax, 2, 0)
    layout.addWidget(analyzer.lbl_a, 3, 0)
    
    # Colonna 2 (destra): RMSE, MAE
    layout.addWidget(analyzer.lbl_rmse, 0, 1)
    layout.addWidget(analyzer.lbl_mae, 1, 1)
    
    section = _create_section("📊 RISULTATI", content)
    analyzer.sidebar.addWidget(section)


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
    analyzer.theme_selector.setMaximumWidth(110)
    analyzer.theme_selector.setMinimumHeight(28)
    analyzer.theme_selector.setStyleSheet("""
        QComboBox {
            font-size: 10px;
            padding: 4px 8px;
            min-height: 28px;
            background-color: #0b2e24;
            color: #f1f5f9;
            border: 1px solid #334155;
            border-radius: 4px;
        }
        QComboBox::drop-down {
            width: 20px;
            border: none;
        }
        QComboBox::down-arrow {
            image: none;
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
    
    # Output converter
    analyzer.sec_out.setStyleSheet(f"font-weight: bold; color: {text_color}; font-size: 14px; padding: 6px;")
    
    # Box risultati
    if hasattr(analyzer, 'res_box'):
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
