# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
PLOTTING_METAPOW.PY - Creazione grafici per MetaboPower
Funzioni per generare grafici di confronto, analisi VT, selezione segmenti
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import FuncFormatter, MultipleLocator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QTabWidget
from PySide6.QtGui import QFont
from typing import Optional, Tuple, Callable
from PySide6.QtCore import Qt


def format_seconds(seconds, pos):
    """Converte secondi in formato #m (solo minuti)"""
    m = int(seconds) // 60
    return f"{m}m"


def create_fit_selection_plot(time_fit: np.ndarray, power_fit: np.ndarray, 
                               parent_dialog: QDialog) -> Tuple[plt.Figure, plt.Axes, FigureCanvas, NavigationToolbar, QLabel]:
    """Crea il grafico per la selezione manuale della fine rampa FIT.
    
    Args:
        time_fit: Array tempo FIT
        power_fit: Array potenza FIT
        parent_dialog: Dialog parent per il canvas
    
    Returns:
        Tuple (fig, ax, canvas, status_label)
    """
    fig, ax = plt.subplots(figsize=(20, 10), dpi=100)
    canvas = FigureCanvas(fig)
    toolbar = NavigationToolbar(canvas, parent_dialog)
    
    ax.plot(time_fit, power_fit, label="Power meter", color="#2563eb", linewidth=2)
    ax.set_xlabel("Tempo" if time_fit is not None else "Indice", fontsize=11)
    ax.set_ylabel("Potenza (W)", fontsize=11)
    ax.set_title("Seleziona Fine Rampa FIT", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.2)

    # --- ZOOM PREDEFINITO: 2 minuti con media watt più alta, centrati, mostra anche 30s dopo ---
    try:
        # Assumiamo che time_fit sia in secondi e ordinato
        window_sec = 120  # 2 minuti
        post_sec = 30     # 30 secondi dopo
        if len(time_fit) > 0 and len(power_fit) == len(time_fit):
            # Calcola rolling mean su finestre di 2 minuti
            time_np = np.array(time_fit)
            power_np = np.array(power_fit)
            # Trova la differenza media tra i punti per step
            dt = np.median(np.diff(time_np)) if len(time_np) > 1 else 1.0
            win_size = max(1, int(window_sec / dt))
            if win_size < len(power_np):
                rolling = np.convolve(power_np, np.ones(win_size)/win_size, mode='valid')
                idx_max = np.argmax(rolling)
                # Trova il centro della finestra
                idx_center = idx_max + win_size // 2
                t_center = time_np[idx_center]
                t_start = t_center - window_sec/2
                t_end = t_center + window_sec/2 + post_sec
                # Limita ai dati disponibili
                t_start = max(time_np[0], t_start)
                t_end = min(time_np[-1], t_end)
                ax.set_xlim(left=t_start, right=t_end)
    except Exception as e:
        print(f"[DEBUG] Errore zoom automatico: {e}")

    fig.tight_layout()
    
    status = QLabel("Clicca sulla fine rampa (click sinistro) quindi chiudi la finestra")
    status.setStyleSheet("font-weight: bold; color: #2563eb; font-size: 12px;")
    return fig, ax, canvas, toolbar, status


def create_overlaid_comparison_plot(met_time_aligned: np.ndarray, met_data: np.ndarray,
                                    fit_time_aligned: np.ndarray, fit_data: np.ndarray,
                                    met_end_idx: int, fit_end_idx: int,
                                    vt1_time: Optional[float] = None, 
                                    vt2_time: Optional[float] = None, 
                                    map_time: Optional[float] = None,
                                    fit_rolling_avgs: Optional[dict] = None) -> Tuple[plt.Figure, plt.Axes]:
    """Crea il grafico di confronto sovrapposto metabolimetro vs FIT.
    
    Args:
        met_time_aligned: Tempo metabolimetro allineato (x=0 alla fine)
        met_data: Potenza metabolimetro
        fit_time_aligned: Tempo FIT allineato (x=0 alla fine)
        fit_data: Potenza FIT
        met_end_idx: Indice fine rampa metabolimetro
        fit_end_idx: Indice fine rampa FIT
        vt1_time: Tempo intersezione VT1 (opzionale)
        vt2_time: Tempo intersezione VT2 (opzionale)
        map_time: Tempo intersezione MAP (opzionale)
        fit_rolling_avgs: Dictionary con medie mobili FIT {window: array} (opzionale)
    
    Returns:
        Tuple (fig, ax)
    """
    fig, ax = plt.subplots(figsize=(22, 11), dpi=100)
    
    # Plot curve di potenza
    ax.plot(met_time_aligned, met_data, 
            label=f"Metabolimetro", 
            color="#16a34a", linewidth=2)
    
    # FIT 1s: linea tratteggiata blu, alpha 0.6
    ax.plot(fit_time_aligned, fit_data, 
            label=f"Power meter 1s", 
            color="#2563eb", linestyle="-", linewidth=0.8, alpha=0.6)
    
    # Plot medie mobili FIT (se fornite)
    if fit_rolling_avgs:
        # 15s: linea continua arancione, alpha 1
        if "15s" in fit_rolling_avgs:
            ax.plot(fit_time_aligned, fit_rolling_avgs["15s"],
                   label=f"Power meter media 15s",
                   color="#f97316",
                   linestyle="-",
                   linewidth=2,
                   alpha=1.0)
        
        # 30s: linea tratteggiata gialla, alpha 0.6
        if "30s" in fit_rolling_avgs:
            ax.plot(fit_time_aligned, fit_rolling_avgs["30s"],
                   label=f"Power meter media 30s",
                   color="#eab308",
                   linestyle="--",
                   linewidth=2,
                   alpha=0.6)
    
    # Linea fine rampa
    ax.axvline(x=0, color="red", linestyle=":", linewidth=1.5, alpha=0.6, label="Fine rampa")
    
    # Etichette
    ax.set_xlabel("Tempo (minuti:secondi)", fontsize=12)
    ax.set_ylabel("Potenza (W)", fontsize=12)
    ax.set_title("Confronto Metabolimetro vs Power Meter", 
                 fontsize=13, fontweight="bold")
    
    # Formatter asse X: ogni minuto, formato #m
    ax.xaxis.set_major_locator(MultipleLocator(60))
    ax.xaxis.set_major_formatter(FuncFormatter(format_seconds))
    
    # Imposta limiti assi: X da 0, Y da 0
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    
    # Aggiungi linee VT (verticali al tempo di intersezione)
    if vt1_time is not None:
        ax.axvline(x=vt1_time, color="orange", linestyle="--", linewidth=1.5, 
                   alpha=0.7, label="VT1")
    if vt2_time is not None:
        ax.axvline(x=vt2_time, color="red", linestyle="--", linewidth=1.5, 
                   alpha=0.7, label="VT2")
    if map_time is not None:
        ax.axvline(x=map_time, color="purple", linestyle="--", linewidth=1.5, 
                   alpha=0.7, label="MAP")
    
    ax.legend(fontsize=11, loc="upper left")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    
    return fig, ax


def create_overlaid_comparison_dialog(met_time_aligned: np.ndarray, met_data: np.ndarray,
                                      fit_time_aligned: np.ndarray, fit_data: np.ndarray,
                                      met_end_idx: int, fit_end_idx: int,
                                      vt1_time: Optional[float] = None, 
                                      vt2_time: Optional[float] = None, 
                                      map_time: Optional[float] = None,
                                      fit_rolling_avgs: Optional[dict] = None,
                                      parent = None) -> QDialog:
    """Crea il dialog di confronto sovrapposto metabolimetro vs FIT.
    
    Args:
        met_time_aligned: Tempo metabolimetro allineato
        met_data: Potenza metabolimetro
        fit_time_aligned: Tempo FIT allineato
        fit_data: Potenza FIT
        met_end_idx: Indice fine rampa metabolimetro
        fit_end_idx: Indice fine rampa FIT
        vt1_time: Tempo intersezione VT1 (opzionale)
        vt2_time: Tempo intersezione VT2 (opzionale)
        map_time: Tempo intersezione MAP (opzionale)
        fit_rolling_avgs: Dictionary con medie mobili FIT (opzionale)
        parent: Widget parent
    
    Returns:
        QDialog configurato con grafico di confronto
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle("Confronto Metabolimetro vs Power Meter")
    dialog.resize(1600, 900)
    dialog.showMaximized()
    dialog.setWindowFlags(
        Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
    )
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(0, 0, 0, 0)
    
    fig, ax = create_overlaid_comparison_plot(
        met_time_aligned, met_data, fit_time_aligned, fit_data,
        met_end_idx, fit_end_idx,
        vt1_time, vt2_time, map_time, fit_rolling_avgs
    )
    
    canvas = FigureCanvas(fig)
    toolbar = NavigationToolbar(canvas, dialog)
    layout.addWidget(toolbar)
    layout.addWidget(canvas, stretch=1)
    
    return dialog


def create_vt_analysis_dialog(metabol_data: pd.DataFrame, met_time_aligned: np.ndarray,
                               fit_time_aligned: np.ndarray, fit_data: np.ndarray,
                               vt1_time: Optional[float], vt2_time: Optional[float], 
                               map_time: Optional[float],
                               fit_rolling_avgs: Optional[dict],
                               parent) -> QDialog:
    """Crea il dialog con tab multipli per analisi VT.
    
    Args:
        metabol_data: DataFrame con dati metabolimetro (solo rampa)
        met_time_aligned: Tempo metabolimetro allineato
        fit_time_aligned: Tempo FIT allineato
        fit_data: Potenza FIT
        vt1_time: Tempo intersezione VT1
        vt2_time: Tempo intersezione VT2
        map_time: Tempo intersezione MAP
        fit_rolling_avgs: Dictionary con medie mobili FIT (opzionale)
        parent: Widget parent
    
    Returns:
        QDialog configurato con tab per ogni parametro metabolico
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle("Analisi VT – Parametri Metabolici vs Power Meter")
    dialog.showMaximized()
    # Rendi la finestra ridimensionabile e con le icone standard
    dialog.setWindowFlag(Qt.WindowType.Window, True)
    dialog.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
    dialog.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
    dialog.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, True)
    
    main_layout = QVBoxLayout(dialog)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    tab_widget = QTabWidget()
    
    # Ottieni colonne numeriche ed escludi tutte le varianti di WR, Watt, Power, Work Rate
    # Escludi solo la colonna 'WR (W)'
    numeric_cols = [col for col in metabol_data.select_dtypes(include=['number']).columns.tolist() if col.strip().lower() != 'wr (w)']
    
    # Crea un tab per ogni colonna metabolica (escludendo WR)
    for col_name in numeric_cols:
        try:
            col_data = pd.to_numeric(metabol_data[col_name], errors='coerce').fillna(0).values
            
            # Crea figura
            fig, ax = plt.subplots(figsize=(20, 10), dpi=100)
            canvas = FigureCanvas(fig)
            
            # Plot FIT power 1s (sfondo e linea tratteggiata blu, alpha 0.7)
            ax.fill_between(fit_time_aligned, fit_data, alpha=0.06, color="blue")
            ax.plot(fit_time_aligned, fit_data, color="#2563eb", linestyle="-", 
                   linewidth=0.5, alpha=0.5, label="Power meter 1s")
            
            # Plot FIT media 15s (se disponibile) - linea continua arancione, alpha 1
            if fit_rolling_avgs and "15s" in fit_rolling_avgs:
                ax.plot(fit_time_aligned, fit_rolling_avgs["15s"], 
                       color="#f97316", linestyle="-", linewidth=2, alpha=1.0,
                       label="Power meter media 15s")
            
            # Plot parametro metabolico (asse Y secondario)
            ax2 = ax.twinx()
            ax2.plot(met_time_aligned, col_data, color="green", linewidth=2, 
                    label=f"{col_name}")
            
            # Aggiungi linee VT (fisse, calcolate dalla potenza metabolimetro)
            if vt1_time is not None:
                ax.axvline(x=vt1_time, color="orange", linestyle="--", linewidth=1.5, 
                          alpha=0.6, label="VT1")
            if vt2_time is not None:
                ax.axvline(x=vt2_time, color="red", linestyle="--", linewidth=1.5, 
                          alpha=0.6, label="VT2")
            if map_time is not None:
                ax.axvline(x=map_time, color="purple", linestyle="--", linewidth=1.5, 
                          alpha=0.6, label="MAP")
            
            # Etichette
            ax.set_xlabel("Tempo (minuti:secondi)", fontsize=12)
            ax.set_ylabel("Potenza (W)", fontsize=12, color="blue")
            ax2.set_ylabel(f"{col_name}", fontsize=12, color="green")
            ax.set_title(f"Analisi {col_name} vs Power Meter", fontsize=13, fontweight="bold")
            
            # Formatter asse X: ogni minuto, formato #m
            ax.xaxis.set_major_locator(MultipleLocator(60))
            ax.xaxis.set_major_formatter(FuncFormatter(format_seconds))
            
            # Imposta limiti assi: X da 0, Y potenza da 0, Y parametro dal minimo
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)
            
            # Y secondario (parametro metabolico) dal minimo al massimo
            col_min = col_data.min()
            col_max = col_data.max()
            ax2.set_ylim(bottom=col_min, top=col_max * 1.1)  # 10% di margine superiore
            
            ax.legend(fontsize=10, loc="upper left")
            ax.grid(True, alpha=0.2)
            fig.tight_layout()
            
            # Aggiungi tab
            tab_layout = QVBoxLayout()
            tab_layout.addWidget(canvas)
            tab_widget_inner = QWidget()
            tab_widget_inner.setLayout(tab_layout)
            tab_widget.addTab(tab_widget_inner, col_name[:20])  # Limita nome tab
            
        except Exception as e:
            print(f"Errore creazione tab {col_name}: {e}")
            plt.close(fig)  # Chiudi figura in caso di errore
            continue
    
    main_layout.addWidget(tab_widget)
    return dialog


def setup_fit_selection_click_handler(fig: plt.Figure, ax: plt.Axes, canvas: FigureCanvas,
                                       time_fit_np: np.ndarray, status_label: QLabel,
                                       on_click_callback: Callable[[int], None]):
    """Configura il gestore eventi click per la selezione della fine rampa FIT.
    
    Args:
        fig: Figura matplotlib
        ax: Axes matplotlib
        canvas: Canvas Qt
        time_fit_np: Array numpy con tempi FIT
        status_label: Label per mostrare lo stato
        on_click_callback: Funzione chiamata con l'indice selezionato
    """
    vline_fit = [None]  # Lista mutabile per closure
    
    def nearest_idx(series_np, xval):
        if series_np is None or len(series_np) == 0:
            return None
        return int(np.abs(series_np - xval).argmin())
    
    def on_click(event):
        if event.inaxes != ax or event.xdata is None:
            return
        if event.button == 1:  # Click sinistro
            idx = nearest_idx(time_fit_np, event.xdata)
            if idx is not None:
                x_pos = time_fit_np[idx]
                if vline_fit[0]:
                    vline_fit[0].remove()
                vline_fit[0] = ax.axvline(x=x_pos, color="#2563eb", linestyle="--", linewidth=2)
                status_label.setText(f"✓ Fine FIT impostata: indice {idx} – chiudi la finestra per procedere")
                canvas.draw_idle()
                on_click_callback(idx)
    
    fig.canvas.mpl_connect('button_press_event', on_click)
