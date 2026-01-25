"""UI builders for Race Report GUI tabs"""

import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QTableWidget, QGroupBox, QFormLayout, QDoubleSpinBox,
    QColorDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


def create_dati_tab(parent):
    """Create DATI tab with editable table"""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Info label
    info = QLabel("Modifica i valori delle gare. Doppio click su una riga per gestire i tag (road/ITT/TTT e DNF/almDNF/errPWR/errHR).")
    layout.addWidget(info)
    
    # Table widget
    parent.data_table = QTableWidget()
    parent.data_table.setAlternatingRowColors(True)
    parent.data_table.doubleClicked.connect(parent.on_table_double_click)
    layout.addWidget(parent.data_table)
    
    # Buttons layout
    btn_layout = QHBoxLayout()
    
    btn_apply_data = QPushButton("Applica Modifiche Dati")
    btn_apply_data.clicked.connect(parent.apply_data_changes)
    btn_layout.addWidget(btn_apply_data)
    
    btn_layout.addStretch()
    
    layout.addLayout(btn_layout)
    
    return widget


def create_layout_tab(parent):
    """Create LAYOUT tab with controls for customization"""
    widget = QWidget()
    main_layout = QVBoxLayout(widget)
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll_widget = QWidget()
    layout = QVBoxLayout(scroll_widget)
    
    # Background color
    bg_group = QGroupBox("Colore Sfondo")
    bg_layout = QHBoxLayout()
    parent.bg_color_btn = QPushButton("Seleziona Colore")
    parent.bg_color_btn.clicked.connect(parent.select_bg_color)
    parent.bg_color_label = QLabel(parent.bg_color)
    parent.bg_color_label.setStyleSheet(f"background-color: {parent.bg_color}; padding: 5px;")
    bg_layout.addWidget(QLabel("Colore attuale:"))
    bg_layout.addWidget(parent.bg_color_label)
    bg_layout.addWidget(parent.bg_color_btn)
    bg_layout.addStretch()
    bg_group.setLayout(bg_layout)
    layout.addWidget(bg_group)
    
    # Logo Page 1 settings
    logo1_group = QGroupBox("Logo Pagina 1 (Tabella)")
    logo1_layout = QFormLayout()
    
    parent.logo_frac_spin = QDoubleSpinBox()
    parent.logo_frac_spin.setRange(0.01, 1.0)
    parent.logo_frac_spin.setSingleStep(0.01)
    parent.logo_frac_spin.setDecimals(2)
    parent.logo_frac_spin.setValue(parent.args.logo_frac)
    logo1_layout.addRow("Larghezza (frazione):", parent.logo_frac_spin)
    
    parent.logo_margin_right_spin = QDoubleSpinBox()
    parent.logo_margin_right_spin.setRange(0.0, 1.0)
    parent.logo_margin_right_spin.setSingleStep(0.01)
    parent.logo_margin_right_spin.setDecimals(2)
    parent.logo_margin_right_spin.setValue(parent.args.logo_margin_right)
    logo1_layout.addRow("Margine destro:", parent.logo_margin_right_spin)
    
    parent.logo_margin_top_spin = QDoubleSpinBox()
    parent.logo_margin_top_spin.setRange(0.0, 1.0)
    parent.logo_margin_top_spin.setSingleStep(0.01)
    parent.logo_margin_top_spin.setDecimals(2)
    parent.logo_margin_top_spin.setValue(parent.args.logo_margin_top)
    logo1_layout.addRow("Margine alto:", parent.logo_margin_top_spin)
    
    logo1_group.setLayout(logo1_layout)
    layout.addWidget(logo1_group)
    
    # Logo Other Pages settings
    logo2_group = QGroupBox("Logo Altre Pagine (Grafici)")
    logo2_layout = QFormLayout()
    
    parent.other_logo_frac_spin = QDoubleSpinBox()
    parent.other_logo_frac_spin.setRange(0.01, 1.0)
    parent.other_logo_frac_spin.setSingleStep(0.01)
    parent.other_logo_frac_spin.setDecimals(2)
    parent.other_logo_frac_spin.setValue(parent.args.other_logo_frac)
    logo2_layout.addRow("Larghezza (frazione):", parent.other_logo_frac_spin)
    
    parent.other_logo_margin_right_spin = QDoubleSpinBox()
    parent.other_logo_margin_right_spin.setRange(0.0, 1.0)
    parent.other_logo_margin_right_spin.setSingleStep(0.01)
    parent.other_logo_margin_right_spin.setDecimals(2)
    parent.other_logo_margin_right_spin.setValue(parent.args.other_logo_margin_right)
    logo2_layout.addRow("Margine destro:", parent.other_logo_margin_right_spin)
    
    parent.other_logo_margin_top_spin = QDoubleSpinBox()
    parent.other_logo_margin_top_spin.setRange(0.0, 1.0)
    parent.other_logo_margin_top_spin.setSingleStep(0.01)
    parent.other_logo_margin_top_spin.setDecimals(2)
    parent.other_logo_margin_top_spin.setValue(parent.args.other_logo_margin_top)
    logo2_layout.addRow("Margine alto:", parent.other_logo_margin_top_spin)
    
    logo2_group.setLayout(logo2_layout)
    layout.addWidget(logo2_group)
    
    layout.addStretch()
    scroll.setWidget(scroll_widget)
    main_layout.addWidget(scroll)
    
    # Apply button
    btn_apply_layout = QPushButton("Applica Modifiche Layout")
    btn_apply_layout.clicked.connect(parent.apply_layout_changes)
    main_layout.addWidget(btn_apply_layout)
    
    return widget


def reorder_and_filter_columns(df):
    """
    Applica l'ordine di colonne come nel PDF e rimuove colonne totalmente vuote.
    Colonne nel PDF ordine + colonne rimanenti a destra.
    """
    # Mappa rinomina colonne (stessa logica di table_page_RR.py)
    col_map = {
        'Date': 'Date',
        'Name': 'Race',
        'Distance': 'Dist (km)',
        'Climbing': 'El (m)',
        'Moving Time': 'Time',
        'Avg Speed': 'Avg (km/h)',
        'Avg HR': 'Avg HR',
        'Max HR': 'Max HR',
        'Avg Power': 'AvgP (W)',
        'Average Power': 'AvgP (W)',
        'Norm Power': 'NP (W)',
        'Ride pMax': 'PMax (W)',
        'Activity pMax': 'PMax (W)',
        'Work': 'kJ',
        'Work >CP': 'kJ > CP',
        'Work >FTP': 'kJ > CP',
        'All Work>CP': 'ALL kJ > CP',
        'kJ/kg': 'kJ/kg',
        'kJ/kg > CP': 'kJ/kg>CP',
        'kJ/h/kg': 'kJ/h/kg',
        'kJ/h/kg>CP': 'kJ/h/kg>CP',
        'Time Above CP': 't > CP',
        'Avg Above CP': 'AvgP > CP',
        '75%': '75%'
    }
    
    # Ordine preferito dal PDF
    preferred_order = [
        'Tags', 'Date', 'Race', 'Dist (km)', 'El (m)', 'Time', 'Avg (km/h)',
        'Avg HR', 'Max HR', 'AvgP (W)', 'NP (W)', 'PMax (W)',
        'kJ', 'kJ > CP', 'ALL kJ > CP', 'kJ/kg', 'kJ/kg>CP', 'kJ/h/kg', 'kJ/h/kg>CP',
        't > CP', 'AvgP > CP', 'RPE', 'Feel', '75%'
    ]
    
    # Rinomina colonne
    df_renamed = df.rename(columns=col_map)
    
    # Seleziona colonne presenti e non vuote
    existing_cols = [c for c in preferred_order if c in df_renamed.columns]
    
    # Aggiungi altre colonne non nel preferred_order (a destra)
    other_cols = [c for c in df_renamed.columns if c not in existing_cols]
    final_cols_order = existing_cols + other_cols
    
    df_final = df_renamed[final_cols_order]
    
    # Rimuovi colonne totalmente vuote
    df_final = df_final.dropna(axis=1, how='all')
    
    return df_final
