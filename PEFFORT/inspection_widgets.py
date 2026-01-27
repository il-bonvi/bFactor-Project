# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
INSPECTION WIDGETS - Costruzione e setup dei widget
Tabelle, combo box, pulsanti e layout della tab ispezione
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)
from PySide6.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
import numpy as np

from .peffort_engine import format_time_hhmmss

logger = logging.getLogger(__name__)


def build_top_bar(parent):
    """Costruisce la barra superiore (status, effort combo, salva)"""
    top_bar = QHBoxLayout()
    
    # Status label
    parent.status_label = QLabel("Inspection - Pronto")
    parent.status_label.setFont(QFont())
    top_bar.addWidget(parent.status_label)
    
    top_bar.addSpacing(20)
    
    # Effort selector
    selector_label = QLabel("📍 Effort:")
    selector_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
    top_bar.addWidget(selector_label)
    
    parent.effort_combo = QComboBox()
    parent.effort_combo.currentIndexChanged.connect(parent.on_effort_selected)
    parent.effort_combo.setMinimumWidth(280)
    parent.effort_combo.setMaximumWidth(400)
    
    # Styling combo
    parent.effort_combo.setStyleSheet("""
        QComboBox {
            background-color: #1e3a5f;
            color: #ffffff;
            border: 2px solid #3b82f6;
            border-radius: 4px;
            padding: 5px;
            font-size: 11px;
            font-weight: bold;
        }
        QComboBox:hover {
            background-color: #2a4a7f;
            border: 2px solid #60a5fa;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
        }
        QAbstractItemView {
            background-color: #1e293b;
            color: #ffffff;
            selection-background-color: #3b82f6;
            selection-color: #ffffff;
            outline: none;
            border: 1px solid #3b82f6;
        }
        QAbstractItemView::item {
            padding: 5px;
            height: 25px;
        }
        QAbstractItemView::item:selected {
            background-color: #3b82f6;
        }
    """)
    
    top_bar.addWidget(parent.effort_combo)
    top_bar.addStretch()
    
    # Save button
    parent.btn_save = QPushButton("Salva Modifiche")
    parent.btn_save.clicked.connect(parent.save_modifications)
    parent.btn_save.setEnabled(False)
    top_bar.addWidget(parent.btn_save)
    
    return top_bar


def build_graph_widget(parent):
    """Costruisce il widget grafico Matplotlib"""
    graph_container = QVBoxLayout()
    graph_container.setContentsMargins(0, 0, 0, 0)
    graph_container.setSpacing(0)
    
    # Figure e canvas
    parent.figure = Figure(figsize=(18, 10), dpi=100)
    parent.canvas = FigureCanvas(parent.figure)
    parent.canvas.mpl_connect('button_press_event', parent.on_graph_click)
    graph_container.addWidget(parent.canvas)
    
    # Toolbar
    parent.toolbar = NavigationToolbar2QT(parent.canvas, parent)
    graph_container.addWidget(parent.toolbar)
    
    # Contenitore
    graph_widget = QWidget()
    graph_widget.setLayout(graph_container)
    graph_widget.setStyleSheet("background: #0f172a; border-radius: 8px;")
    
    return graph_widget


def build_detail_panel(parent):
    """Costruisce il pannello dettagli a destra"""
    right_panel = QVBoxLayout()
    right_panel.setSpacing(6)
    right_panel.setContentsMargins(8, 0, 0, 0)
    
    # Sezione dettagli
    right_panel.addWidget(QLabel("DETTAGLI EFFORT", objectName="SectionTitle"))
    
    # Tabella dettagli
    parent.table_effort_detail = QTableWidget()
    parent.table_effort_detail.setColumnCount(2)
    parent.table_effort_detail.setRowCount(8)
    parent.table_effort_detail.setHorizontalHeaderLabels(["Proprietà", "Valore"])
    parent.table_effort_detail.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    parent.table_effort_detail.verticalHeader().setVisible(False)
    
    # Popola righe
    properties = [
        "Inizio (hh:mm:ss)",
        "Fine (hh:mm:ss)",
        "Durata (s)",
        "Watt Medi",
        "W/kg",
        "Potenza Picco",
        "HR Media",
        "HR Max"
    ]
    for i, prop in enumerate(properties):
        parent.table_effort_detail.setItem(i, 0, QTableWidgetItem(prop))
        parent.table_effort_detail.setItem(i, 1, QTableWidgetItem("---"))
    
    right_panel.addWidget(parent.table_effort_detail, stretch=2)
    
    # Sezione modifica bordi
    right_panel.addWidget(QLabel("MODIFICA BORDI", objectName="SectionTitle"))
    
    ctrl_layout = QVBoxLayout()
    ctrl_layout.setSpacing(8)
    
    # Pulsanti inizio/fine
    set_bounds_h = QHBoxLayout()
    set_bounds_h.setSpacing(5)
    
    parent.btn_set_start = QPushButton("📍 Imposta Inizio")
    parent.btn_set_start.setStyleSheet("background-color: #06b6d4; color: white;")
    parent.btn_set_start.clicked.connect(parent.activate_set_start)
    set_bounds_h.addWidget(parent.btn_set_start)
    
    parent.btn_set_end = QPushButton("🏁 Imposta Fine")
    parent.btn_set_end.setStyleSheet("background-color: #f97316; color: white;")
    parent.btn_set_end.clicked.connect(parent.activate_set_end)
    set_bounds_h.addWidget(parent.btn_set_end)
    
    ctrl_layout.addLayout(set_bounds_h)
    
    # Valori correnti
    current_h = QHBoxLayout()
    current_h.addWidget(QLabel("Inizio:"))
    parent.label_start_val = QLabel("-")
    parent.label_start_val.setStyleSheet("font-weight: bold; color: #06b6d4;")
    current_h.addWidget(parent.label_start_val)
    current_h.addSpacing(20)
    current_h.addWidget(QLabel("Fine:"))
    parent.label_end_val = QLabel("-")
    parent.label_end_val.setStyleSheet("font-weight: bold; color: #f97316;")
    current_h.addWidget(parent.label_end_val)
    current_h.addStretch()
    ctrl_layout.addLayout(current_h)
    
    # Pulsanti reset/delete
    btn_h = QHBoxLayout()
    btn_h.setSpacing(5)
    
    parent.btn_reset_effort = QPushButton("Reset Effort")
    parent.btn_reset_effort.clicked.connect(parent.reset_current_effort)
    btn_h.addWidget(parent.btn_reset_effort)
    
    parent.btn_delete_effort = QPushButton("Elimina Effort")
    parent.btn_delete_effort.setStyleSheet("color: #ff6b6b;")
    parent.btn_delete_effort.clicked.connect(parent.delete_current_effort)
    btn_h.addWidget(parent.btn_delete_effort)
    
    ctrl_layout.addLayout(btn_h)
    
    right_panel.addLayout(ctrl_layout)
    right_panel.addStretch()
    
    return right_panel


def build_efforts_table(parent):
    """Costruisce la tabella con tutti gli effort"""
    table = QTableWidget()
    table.setColumnCount(6)
    table.setHorizontalHeaderLabels([
        "Idx", "Inizio", "Fine", "Durata (s)", "Watt Medi", "Stato"
    ])
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setVisible(False)
    table.setMaximumHeight(120)
    table.itemSelectionChanged.connect(parent.on_table_selection_changed)
    
    parent.table_all_efforts = table
    return table


def update_detail_panel(parent, effort_idx: int):
    """Aggiorna il pannello dettagli per un effort specifico"""
    if effort_idx < 0 or effort_idx >= len(parent.current_efforts):
        return
    
    try:
        start_idx, end_idx, avg_power = parent.current_efforts[effort_idx]
        
        power = parent.current_df['power'].values
        time_sec = parent.current_df['time_sec'].values
        
        # Controlla se la colonna heartrate esiste
        if 'heartrate' in parent.current_df.columns:
            hr = parent.current_df['heartrate'].values
        else:
            hr = np.zeros(len(power))  # Array di zeri se heartrate non disponibile
        
        seg_power = power[start_idx:end_idx]
        seg_time = time_sec[start_idx:end_idx]
        seg_hr = hr[start_idx:end_idx]
        
        start_time = seg_time[0]
        end_time = seg_time[-1]
        duration = int(end_time - start_time)
        
        power_peak = seg_power.max() if len(seg_power) > 0 else 0
        w_kg = avg_power / parent.current_weight if parent.current_weight > 0 else 0
        hr_mean = seg_hr[seg_hr > 0].mean() if (seg_hr > 0).any() else 0
        hr_max = seg_hr.max() if len(seg_hr) > 0 else 0
        
        # Aggiorna tabella
        parent.table_effort_detail.setItem(0, 1, QTableWidgetItem(format_time_hhmmss(start_time)))
        parent.table_effort_detail.setItem(1, 1, QTableWidgetItem(format_time_hhmmss(end_time)))
        parent.table_effort_detail.setItem(2, 1, QTableWidgetItem(f"{duration}"))
        parent.table_effort_detail.setItem(3, 1, QTableWidgetItem(f"{avg_power:.0f}"))
        parent.table_effort_detail.setItem(4, 1, QTableWidgetItem(f"{w_kg:.2f}"))
        parent.table_effort_detail.setItem(5, 1, QTableWidgetItem(f"{power_peak:.0f}"))
        parent.table_effort_detail.setItem(6, 1, QTableWidgetItem(f"{hr_mean:.0f}"))
        parent.table_effort_detail.setItem(7, 1, QTableWidgetItem(f"{int(hr_max)}"))
        
        # Aggiorna label inizio/fine
        parent.label_start_val.setText(str(int(start_time)))
        parent.label_end_val.setText(str(int(end_time)))
        
        logger.info(f"Effort {effort_idx} detail panel updated")
        
    except Exception as e:
        logger.error(f"Errore aggiornamento dettagli effort: {e}", exc_info=True)


def update_efforts_table(parent):
    """Aggiorna la tabella con tutti gli effort"""
    try:
        time_sec = parent.current_df['time_sec'].values
        
        parent.table_all_efforts.setRowCount(len(parent.current_efforts))
        
        for i, (start_idx, end_idx, avg) in enumerate(parent.current_efforts):
            start_time = time_sec[start_idx]
            end_time = time_sec[end_idx]
            duration = int(end_time - start_time)
            
            # Highlight riga selezionata
            bg_color = "#1e3a5f" if i == parent.selected_effort_idx else None
            
            row_data = [
                str(i + 1),
                format_time_hhmmss(start_time),
                format_time_hhmmss(end_time),
                f"{duration}s",
                f"{avg:.0f}",
                "✏️ Modificato" if parent.inspection_manager and parent.inspection_manager.is_modified(i) else "✓"
            ]
            
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                if bg_color:
                    item.setBackground(QColor(bg_color))
                parent.table_all_efforts.setItem(i, j, item)
        
    except Exception as e:
        logger.error(f"Errore aggiornamento tabella: {e}", exc_info=True)
