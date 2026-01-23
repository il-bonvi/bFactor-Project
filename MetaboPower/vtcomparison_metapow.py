# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
COMPAREVT_METAPOW.PY - Analisi e confronto soglie ventilatorie
Funzioni per comparare VT1/VT2/MAP tra metabolimetro e power meter
"""

import numpy as np
from typing import Optional
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from .data_extraction_metapow import (
    calculate_rolling_avg5_fit, calculate_rolling_centered15_fit,
    calculate_rolling_centered30_fit
)


def find_nearest_idx(time_array: np.ndarray, target_time: float) -> int:
    """Trova l'indice più vicino a un tempo target in un array di tempi.
    
    Args:
        time_array: Array dei tempi FIT
        target_time: Tempo target
    
    Returns:
        Indice più vicino
    """
    if len(time_array) == 0:
        return 0
    return int(np.abs(time_array - target_time).argmin())


def calculate_avg5_fit(vt_time: float, fit_time_aligned: np.ndarray, fit_data: np.ndarray) -> Optional[float]:
    """Calcola la media non centrata su 5 secondi precedenti (FIT 1s).
    
    Args:
        vt_time: Tempo VT (secondi)
        fit_time_aligned: Array tempi FIT allineati
        fit_data: Array potenza FIT
    
    Returns:
        Potenza media FIT nei 5 secondi precedenti a vt_time
    """
    if fit_time_aligned is None or fit_data is None or len(fit_data) == 0:
        return None
    
    idx = find_nearest_idx(fit_time_aligned, vt_time)
    # Prendi i 5 secondi precedenti (se 1 Hz: 5 punti precedenti)
    start_idx = max(0, idx - 5)
    end_idx = idx + 1
    
    if start_idx < len(fit_data):
        return float(np.mean(fit_data[start_idx:end_idx]))
    return None


def calculate_avg15_fit(vt_time: float, fit_time_aligned: np.ndarray, fit_data: np.ndarray) -> Optional[float]:
    """Calcola la media non centrata su 15 secondi precedenti (FIT 1s).
    
    Args:
        vt_time: Tempo VT (secondi)
        fit_time_aligned: Array tempi FIT allineati
        fit_data: Array potenza FIT
    
    Returns:
        Potenza media FIT nei 15 secondi precedenti a vt_time
    """
    if fit_time_aligned is None or fit_data is None or len(fit_data) == 0:
        return None
    
    idx = find_nearest_idx(fit_time_aligned, vt_time)
    # Prendi i 15 secondi precedenti (se 1 Hz: 15 punti precedenti)
    start_idx = max(0, idx - 15)
    end_idx = idx + 1
    
    if start_idx < len(fit_data):
        return float(np.mean(fit_data[start_idx:end_idx]))
    return None


def calculate_centered15_fit(vt_time: float, fit_time_aligned: np.ndarray, fit_data: np.ndarray) -> Optional[float]:
    """Calcola la media centrata su 15 secondi (7 prima + centro + 7 dopo - FIT 1s).
    
    Args:
        vt_time: Tempo VT (secondi)
        fit_time_aligned: Array tempi FIT allineati
        fit_data: Array potenza FIT
    
    Returns:
        Potenza media FIT in finestra centrata 15 secondi attorno a vt_time
    """
    if fit_time_aligned is None or fit_data is None or len(fit_data) == 0:
        return None
    
    idx = find_nearest_idx(fit_time_aligned, vt_time)
    # Prendi 7 secondi prima e 7 dopo (totale 15 con il centro)
    start_idx = max(0, idx - 7)
    end_idx = min(len(fit_data), idx + 8)  # +8 per includere il punto centrale e 7 dopo
    
    if start_idx < len(fit_data):
        return float(np.mean(fit_data[start_idx:end_idx]))
    return None


def calculate_centered30_fit(vt_time: float, fit_time_aligned: np.ndarray, fit_data: np.ndarray) -> Optional[float]:
    """Calcola la media centrata su 30 secondi (15 prima + centro + 15 dopo - FIT 1s).
    
    Args:
        vt_time: Tempo VT (secondi)
        fit_time_aligned: Array tempi FIT allineati
        fit_data: Array potenza FIT
    
    Returns:
        Potenza media FIT in finestra centrata 30 secondi attorno a vt_time
    """
    if fit_time_aligned is None or fit_data is None or len(fit_data) == 0:
        return None
    
    idx = find_nearest_idx(fit_time_aligned, vt_time)
    # Prendi 15 secondi prima e 15 dopo (totale 30 con il centro)
    start_idx = max(0, idx - 15)
    end_idx = min(len(fit_data), idx + 16)  # +16 per includere il punto centrale e 15 dopo
    
    if start_idx < len(fit_data):
        return float(np.mean(fit_data[start_idx:end_idx]))
    return None


def create_vt_comparison_dialog(vt1_metabol: Optional[float], vt2_metabol: Optional[float], 
                                 map_metabol: Optional[float],
                                 vt1_time: Optional[float], vt2_time: Optional[float],
                                 map_time: Optional[float],
                                 fit_time_aligned: np.ndarray, fit_data: np.ndarray,
                                 parent=None) -> QDialog:
    """Crea il dialog con tabella di confronto VT1, VT2, MAP tra metabolimetro e FIT.
    
    Args:
        vt1_metabol: VT1 dal file dati metabolimetro (W)
        vt2_metabol: VT2 dal file dati metabolimetro (W)
        map_metabol: MAP dal file dati metabolimetro (W)
        vt1_time: Tempo VT1 dal confronto tempo-potenza (secondi)
        vt2_time: Tempo VT2 dal confronto tempo-potenza (secondi)
        map_time: Tempo MAP dal confronto tempo-potenza (secondi)
        fit_time_aligned: Array tempi FIT allineati
        fit_data: Array potenza FIT
        parent: Widget parent
    
    Returns:
        QDialog configurato con tabella di confronto
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle("Confronto VT1 – VT2 – MAP: Metabolimetro vs Power Meter")
    dialog.setMinimumSize(1000, 500)
    dialog.setWindowFlags(
        Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
    )
    
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(10)
    
    # ========== TITOLO ==========
    title = QLabel("Analisi Soglie Ventilatorie: Confronto dati metabolimetro vs Power Meter")
    title_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
    title.setFont(title_font)
    layout.addWidget(title)
    
    # ========== TABELLA ==========
    table = QTableWidget()
    table.setColumnCount(6)
    table.setRowCount(3)
    table.setColumnWidth(0, 100)
    for i in range(1, 6):
        table.setColumnWidth(i, 150)
    
    # Headers
    headers = ["Parametro", "Metabolimetro\n(W)", "avg5s FIT\n(W)", "avg15s FIT\n(W)", 
               "cent15s FIT\n(W)", "cent30s FIT\n(W)"]
    table.setHorizontalHeaderLabels(headers)
    
    # Calcola medie FIT per ciascuna soglia
    vt1_avgs = {
        "avg5": calculate_avg5_fit(vt1_time, fit_time_aligned, fit_data) if vt1_time is not None else None,
        "avg15": calculate_avg15_fit(vt1_time, fit_time_aligned, fit_data) if vt1_time is not None else None,
        "cent15": calculate_centered15_fit(vt1_time, fit_time_aligned, fit_data) if vt1_time is not None else None,
        "cent30": calculate_centered30_fit(vt1_time, fit_time_aligned, fit_data) if vt1_time is not None else None,
    }
    
    vt2_avgs = {
        "avg5": calculate_avg5_fit(vt2_time, fit_time_aligned, fit_data) if vt2_time is not None else None,
        "avg15": calculate_avg15_fit(vt2_time, fit_time_aligned, fit_data) if vt2_time is not None else None,
        "cent15": calculate_centered15_fit(vt2_time, fit_time_aligned, fit_data) if vt2_time is not None else None,
        "cent30": calculate_centered30_fit(vt2_time, fit_time_aligned, fit_data) if vt2_time is not None else None,
    }
    
    map_avgs = {
        "avg5": calculate_avg5_fit(map_time, fit_time_aligned, fit_data) if map_time is not None else None,
        "avg15": calculate_avg15_fit(map_time, fit_time_aligned, fit_data) if map_time is not None else None,
        "cent15": calculate_centered15_fit(map_time, fit_time_aligned, fit_data) if map_time is not None else None,
        "cent30": calculate_centered30_fit(map_time, fit_time_aligned, fit_data) if map_time is not None else None,
    }
    
    # Popola righe
    rows_data = [
        ("VT1", vt1_metabol, vt1_avgs),
        ("VT2", vt2_metabol, vt2_avgs),
        ("MAP", map_metabol, map_avgs),
    ]
    
    for row_idx, (param_name, metabol_val, avgs_dict) in enumerate(rows_data):
        # Parametro
        item = QTableWidgetItem(param_name)
        item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        table.setItem(row_idx, 0, item)
        
        # Valore metabolimetro
        metabol_text = f"{metabol_val:.0f}" if metabol_val is not None else "N/A"
        item = QTableWidgetItem(metabol_text)
        item.setTextAlignment(Qt.AlignCenter)
        table.setItem(row_idx, 1, item)
        
        # Valori FIT (avg5, avg15, cent15, cent30)
        for col_idx, key in enumerate(["avg5", "avg15", "cent15", "cent30"], start=2):
            val = avgs_dict.get(key)
            text = f"{val:.0f}" if val is not None else "N/A"
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row_idx, col_idx, item)
    
    # Stile tabella
    table.setStyleSheet("""
        QTableWidget {
            gridline-color: #e2e8f0;
            border: 1px solid #cbd5e1;
        }
        QTableWidget::item {
            padding: 8px;
        }
        QHeaderView::section {
            background-color: #f1f5f9;
            padding: 8px;
            border: 1px solid #cbd5e1;
            font-weight: bold;
            font-size: 10px;
        }
    """)
    
    layout.addWidget(table)
    
    # ========== FOOTER ==========
    footer_text = QLabel(
        "• avg5s: Media 5s precedenti | • avg15s: Media 15s precedenti\n"
        "• cent15s: Media centrata 15s (±7.5s) | • cent30s: Media centrata 30s (±15s)"
    )
    footer_text.setStyleSheet("color: #64748b; font-size: 10px; margin-top: 10px;")
    footer_text.setWordWrap(True)
    layout.addWidget(footer_text)
    
    # ========== PULSANTI ==========
    button_layout_widget = QDialog()
    button_layout = layout  # Riusa il layout principale
    
    btn_close = QPushButton("Chiudi")
    btn_close.setMinimumHeight(40)
    btn_close.clicked.connect(dialog.accept)
    layout.addWidget(btn_close)
    
    return dialog


def show_vt_comparison_dialog(engine, vt1_metabol: Optional[float], vt2_metabol: Optional[float],
                               map_metabol: Optional[float], fit_end_idx: int, met_end_idx: int,
                               met_ramp_start_idx: Optional[int], parent=None) -> bool:
    """Gestisce l'estrazione dati e mostra il dialog di confronto VT.
    
    Questa funzione centralizza tutta la logica di confronto VT per facilità di modifica.
    
    Args:
        engine: DataEngine con csv_data e fit_data
        vt1_metabol: VT1 dal metabolimetro (W)
        vt2_metabol: VT2 dal metabolimetro (W)
        map_metabol: MAP dal metabolimetro (W)
        fit_end_idx: Indice fine rampa FIT
        met_end_idx: Indice fine rampa metabolimetro
        met_ramp_start_idx: Indice inizio rampa metabolimetro
        parent: Widget parent
    
    Returns:
        True se dialog eseguito correttamente, False se errore
    """
    # Import qui per evitare dipendenze circolari
    from .data_extraction_metapow import (
        extract_metabolimeter_series, extract_fit_series,
        find_ramp_start, find_vt_intersections
    )
    
    # Validazioni
    if engine.csv_data is None or engine.fit_data is None:
        QMessageBox.warning(parent, "Dati mancanti", "Carica sia metabolimetro che FIT")
        return False
    
    if fit_end_idx is None or met_end_idx is None:
        QMessageBox.warning(parent, "Fine mancante", "Imposta le fine rampa per entrambi i dati")
        return False
    
    # Estrai serie
    time_met, power_met = extract_metabolimeter_series(engine.csv_data)
    time_fit, power_fit = extract_fit_series(engine.fit_data)
    
    if power_met is None or power_fit is None:
        QMessageBox.warning(parent, "Colonne mancanti", "Impossibile trovare le colonne potenza")
        return False
    
    # Prepara dati
    time_met_np = np.array(time_met)
    power_met_np = np.array(power_met)
    time_fit_np = np.array(time_fit)
    power_fit_np = np.array(power_fit)
    
    # Usa inizio rampa dal parser (se disponibile) altrimenti rileva da potenza
    if met_ramp_start_idx is not None:
        met_start_idx = met_ramp_start_idx
    else:
        met_start_idx = find_ramp_start(power_met_np)
    met_start_idx = max(0, min(met_start_idx, met_end_idx))
    
    # Finestra metabolimetro
    met_time = time_met_np[met_start_idx:met_end_idx + 1]
    met_data = power_met_np[met_start_idx:met_end_idx + 1]
    met_duration_sec = float(met_time[-1] - met_time[0]) if len(met_time) > 1 else 0.0
    
    # Finestra FIT
    fit_start_idx = max(0, int(fit_end_idx - round(met_duration_sec)))
    fit_time = time_fit_np[fit_start_idx:fit_end_idx + 1]
    fit_data = power_fit_np[fit_start_idx:fit_end_idx + 1]
    
    # Allinea tempi (x=0 all'inizio della rampa)
    met_time_aligned = met_time - met_time[0] if len(met_time) > 0 else np.arange(len(met_data), dtype=float)
    fit_time_aligned = fit_time - fit_time[0] if len(fit_time) > 0 else np.arange(len(fit_data), dtype=float)
    
    # Trova tempi VT
    vt1_time, vt2_time, map_time = find_vt_intersections(
        met_time_aligned, met_data, vt1_metabol, vt2_metabol, map_metabol
    )
    
    # Crea e mostra dialog con tabella di confronto
    dialog = create_vt_comparison_dialog(
        vt1_metabol, vt2_metabol, map_metabol,
        vt1_time, vt2_time, map_time,
        fit_time_aligned, fit_data, parent
    )
    
    dialog.exec()
    return True
