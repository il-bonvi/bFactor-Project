# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
GUI_METAPOW.PY - Interfaccia grafica per MetaboPower
GUI principale per confronto metabolimetro e power meter (SOLO UI)
Logica di estrazione dati e plotting delegata ai rispettivi moduli
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QGroupBox, QMessageBox,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pandas as pd
import numpy as np
from shared.styles import get_style, TEMI
from .parser_metapow import MetabolitDataParser
from .fit_parser_metapow import FitFileParser
from .config_metapow import get_profile_manager
from .data_extraction_metapow import (
    extract_metabolimeter_series, extract_fit_series, 
    find_ramp_start, find_vt_intersections, calculate_rolling_averages
)
from .plotting_metapow import (
    create_fit_selection_plot, setup_fit_selection_click_handler,
    create_overlaid_comparison_plot, create_overlaid_comparison_dialog, create_vt_analysis_dialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ImportProfileDialog(QDialog):
    """Dialog per selezionare il profilo di importazione"""
    
    def __init__(self, parent, available_profiles: dict):
        super().__init__(parent)
        self.selected_profile = None
        self.available_profiles = available_profiles
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Seleziona Profilo Importazione")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Titolo
        title = QLabel("Seleziona il tipo di file e il profilo di importazione:")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # ComboBox profili
        self.profile_combo = QComboBox()
        for profile_name, profile_data in self.available_profiles.items():
            display_name = profile_data.get("name", profile_name)
            self.profile_combo.addItem(f"{display_name}", profile_name)
        
        layout.addWidget(QLabel("Profilo:"))
        layout.addWidget(self.profile_combo)
        
        # Descrizione profilo
        self.description_label = QLabel()
        self.description_label.setStyleSheet("color: #64748b; font-size: 11px; padding: 10px; background-color: #f1f5f9; border-radius: 5px;")
        self.description_label.setWordWrap(True)
        self.update_description()
        self.profile_combo.currentIndexChanged.connect(self.update_description)
        layout.addWidget(self.description_label)
        
        layout.addStretch()
        
        # Pulsanti
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("✓ OK")
        btn_cancel = QPushButton("✗ Annulla")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
    
    def update_description(self):
        profile_name = self.profile_combo.currentData()
        profile = self.available_profiles.get(profile_name)
        if profile:
            description = profile.get("description", "")
            self.description_label.setText(description)
    
    def get_selected_profile(self):
        return self.profile_combo.currentData()


class MetaboPowerGUI(QMainWindow):
    """Interfaccia principale di MetaboPower"""
    
    def __init__(self, theme="Forest Green"):
        super().__init__()
        self.current_theme = theme
        self.csv_file = None
        self.fit_file = None
        self.parser = MetabolitDataParser()
        self.fit_parser = FitFileParser()
        self.profile_manager = get_profile_manager()
        
        # Container di dati (placeholder - logica delegata a data_extraction e plotting)
        class DataEngine:
            def __init__(self):
                self.csv_data = None
                self.fit_data = None
        self.engine = DataEngine()
        
        self.selected_fit_segment = None
        self.fit_end_idx = None
        self.met_end_idx = None
        self.met_ramp_start_idx = None  # Inizio rampa dal parser Cortex
        self.vt1 = None  # Soglia ventilatoria 1 (W)
        self.vt2 = None  # Soglia ventilatoria 2 (W)
        self.map = None  # Potenza aerobica massima (W)
        
        self.setup_ui()
        self.apply_theme(self.current_theme)
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        self.setWindowTitle("MetaboPower - Confronto Metabolimetro & Power Meter")
        self.setMinimumSize(1400, 900)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header con titolo e tema
        header_layout = QHBoxLayout()
        
        title = QLabel("🫁 MetaboPower")
        title.setObjectName("Header")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Selettore tema
        theme_label = QLabel("Tema:")
        theme_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(list(TEMI.keys()))
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.apply_theme)
        self.theme_selector.setFixedHeight(32)
        self.theme_selector.setMaximumWidth(200)
        
        header_layout.addWidget(theme_label)
        header_layout.addWidget(self.theme_selector)
        
        main_layout.addLayout(header_layout)
        
        # Sezione caricamento file
        files_group = QGroupBox("📁 Caricamento File")
        files_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        files_layout = QHBoxLayout()
        files_layout.setSpacing(20)
        
        # CSV Metabolimetro
        csv_layout = QVBoxLayout()
        csv_label = QLabel("CSV Metabolimetro")
        csv_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.csv_path_label = QLabel("Nessun file caricato")
        self.csv_path_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.btn_load_csv = QPushButton("📊 Carica ROW")
        self.btn_load_csv.setMinimumHeight(45)
        self.btn_load_csv.clicked.connect(self.load_csv_file)
        csv_layout.addWidget(csv_label)
        csv_layout.addWidget(self.csv_path_label)
        csv_layout.addWidget(self.btn_load_csv)
        
        # FIT Power Meter
        fit_layout = QVBoxLayout()
        fit_label = QLabel("FIT Power Meter")
        fit_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.fit_path_label = QLabel("Nessun file caricato")
        self.fit_path_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.btn_load_fit = QPushButton("📈 Carica FIT")
        self.btn_load_fit.setMinimumHeight(45)
        self.btn_load_fit.clicked.connect(self.load_fit_file)
        fit_layout.addWidget(fit_label)
        fit_layout.addWidget(self.fit_path_label)
        fit_layout.addWidget(self.btn_load_fit)
        
        files_layout.addLayout(csv_layout)
        files_layout.addLayout(fit_layout)
        files_group.setLayout(files_layout)
        main_layout.addWidget(files_group)
        
        # Sezione analisi
        analysis_group = QGroupBox("📊 Analisi e Confronto")
        analysis_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        analysis_layout = QVBoxLayout()
        
        # Sezione metadati
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setMaximumHeight(80)
        self.metadata_text.setText("Metadati paziente (XLSX): -")
        analysis_layout.addWidget(QLabel("Informazioni Paziente:"))
        analysis_layout.addWidget(self.metadata_text)
        
        # Tabella anteprima dati
        self.data_preview_table = QTableWidget()
        self.data_preview_table.setMaximumHeight(200)
        analysis_layout.addWidget(QLabel("Anteprima Dati (prime 10 righe):"))
        analysis_layout.addWidget(self.data_preview_table)
        
        # Pulsanti azione
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        self.btn_compare = QPushButton("📊 Confronto")
        self.btn_compare.setMinimumHeight(45)
        self.btn_compare.setEnabled(False)
        self.btn_compare.clicked.connect(self.show_overlaid_comparison)
        
        self.btn_analyze = QPushButton("⚡ Analizza")
        self.btn_analyze.setMinimumHeight(45)
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.clicked.connect(self.show_vt_analysis)
        
        self.btn_export = QPushButton("💾 Report")
        self.btn_export.setMinimumHeight(45)
        self.btn_export.setEnabled(False)
        
        action_layout.addWidget(self.btn_compare)
        action_layout.addWidget(self.btn_analyze)
        action_layout.addWidget(self.btn_export)
        
        analysis_layout.addLayout(action_layout)
        analysis_group.setLayout(analysis_layout)
        main_layout.addWidget(analysis_group)
        
        main_layout.addStretch()
        
        # Footer
        footer = QLabel("© 2026 bFactor Project | MetaboPower v0.1")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #64748b; font-size: 10px; margin-top: 10px;")
        main_layout.addWidget(footer)
    
    def apply_theme(self, theme_name):
        """Applica il tema selezionato"""
        self.current_theme = theme_name
        self.setStyleSheet(get_style(theme_name))
    
    def load_csv_file(self):
        """Carica il file metabolimetro: prima seleziona profilo, poi il file"""
        # Mostra dialog per scegliere il profilo
        available_profiles = self.profile_manager.get_all_profiles()
        
        dialog = ImportProfileDialog(self, available_profiles)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        profile_name = dialog.get_selected_profile()
        
        # Ottieni il profilo selezionato
        profile = available_profiles.get(profile_name)
        if not profile:
            QMessageBox.warning(self, "Errore", "Profilo non trovato")
            return
        
        # Costruisci il filtro file basato sulle estensioni del profilo
        extensions = profile.get("file_extensions", [])
        filter_parts = [f"*.{ext}" for ext in extensions]
        file_filter = " ".join(filter_parts) if filter_parts else "*"
        ext_display = "/".join(extensions).upper()
        file_dialog_filter = f"{ext_display} Files ({file_filter});;All Files (*)"
        
        # Apri il dialog per scegliere il file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleziona file {profile.get('name', profile_name)} ({ext_display})",
            "",
            file_dialog_filter
        )
        
        if not file_path:
            return
        
        # Carica il file con il profilo selezionato
        result = self.parser.load_file_with_profile(file_path, profile_name)
        
        if result["success"]:
            self.csv_file = file_path
            self.engine.csv_data = self.parser.get_data()
            profile_display = available_profiles[profile_name].get("name", profile_name)
            self.csv_path_label.setText(f"📄 {file_path.split('/')[-1]} ({profile_display})")
            self.csv_path_label.setStyleSheet("color: #4ade80; font-size: 11px;")
            
            # Processa metadati
            self._process_metadata(result["metadata"], available_profiles, profile_name)
            
            # Mostra preview dati
            self._show_data_preview()
            
            self.check_files_loaded()
        else:
            QMessageBox.critical(
                self,
                "Errore Caricamento",
                f"Errore: {result.get('error', 'Errore sconosciuto')}"
            )
    
    def _process_metadata(self, metadata: dict, available_profiles: dict, profile_name: str):
        """Processa e visualizza i metadati paziente"""
        if metadata:
            metadata_str = "Paziente: "
            if metadata.get("nome"):
                metadata_str += f"{metadata.get('nome')} {metadata.get('cognome')} | "
            metadata_str += f"D.N.: {metadata.get('data_nascita')} | "
            metadata_str += f"Genere: {metadata.get('genere')} | "
            metadata_str += f"Altezza: {metadata.get('altezza')} | "
            metadata_str += f"Peso: {metadata.get('peso')}"
            if metadata.get("turn_index") is not None:
                metadata_str += f" | Turn @ riga {metadata['turn_index']}"
            
            # Estrai e mostra VT1, VT2, MAP
            self.vt1 = metadata.get("vt1")
            self.vt2 = metadata.get("vt2")
            self.map = metadata.get("map")
            
            if self.vt1 is not None or self.vt2 is not None or self.map is not None:
                metadata_str += " | VT: "
                if self.vt1 is not None:
                    try:
                        self.vt1 = float(self.vt1)
                        metadata_str += f"VT1={self.vt1:.0f}W "
                    except:
                        self.vt1 = None
                if self.vt2 is not None:
                    try:
                        self.vt2 = float(self.vt2)
                        metadata_str += f"VT2={self.vt2:.0f}W "
                    except:
                        self.vt2 = None
                if self.map is not None:
                    try:
                        self.map = float(self.map)
                        metadata_str += f"MAP={self.map:.0f}W"
                    except:
                        self.map = None
            
            self.metadata_text.setText(metadata_str)
            
            # Preimposta fine rampa metabolimetro da 'turn' se presente
            if metadata.get("turn_index") is not None:
                self.met_end_idx = int(metadata["turn_index"])
            
            # Preimposta inizio rampa da 'ramp_start_index' (Cortex)
            if metadata.get("ramp_start_index") is not None:
                self.met_ramp_start_idx = int(metadata["ramp_start_index"])
        else:
            self.metadata_text.setText("Metadati paziente: - (profilo senza metadati)")
    
    def load_fit_file(self):
        """Carica il file FIT del power meter e mostra grafico per selezione fine"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona file FIT Power Meter",
            "",
            "FIT Files (*.fit);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Carica il file FIT
        result = self.fit_parser.load_file(file_path)
        
        if not result["success"]:
            QMessageBox.critical(
                self,
                "Errore Caricamento FIT",
                f"Errore: {result.get('error', 'Errore sconosciuto')}\n\nHai installato 'fitparse'? pip install fitparse"
            )
            return

        self.fit_file = file_path
        self.engine.fit_data = self.fit_parser.get_data()
        
        # Mostra grafico FIT per selezione manuale della fine
        self._show_fit_selection_dialog()
        
        if self.fit_end_idx is None:
            return  # Utente ha annullato
        
        self.selected_fit_segment = None
        self.fit_path_label.setText(f"📄 {file_path.split('/')[-1]} (fine: {self.fit_end_idx})")
        self.fit_path_label.setStyleSheet("color: #4ade80; font-size: 11px;")
        
        self.check_files_loaded()
    
    def _show_fit_selection_dialog(self):
        """Mostra il grafico FIT per selezionare manualmente la fine rampa"""
        if self.engine.fit_data is None or self.engine.fit_data.empty:
            QMessageBox.warning(self, "Dati FIT vuoti", "Nessun dato nel file FIT")
            return

        # Estrai serie FIT
        time_fit, power_fit = extract_fit_series(self.engine.fit_data)
        if power_fit is None:
            QMessageBox.warning(self, "Errore", "Impossibile trovare la colonna potenza nel FIT")
            return

        # Crea dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Seleziona Fine Rampa FIT – click sinistro sulla fine rampa")
        dialog.resize(1400, 800)
        dialog.showMaximized()
        dialog.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
        )
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        # Crea grafico
        fig, ax, canvas, toolbar, status = create_fit_selection_plot(time_fit, power_fit, dialog)
        layout.addWidget(toolbar)
        layout.addWidget(status)
        layout.addWidget(canvas, stretch=1)

        # Setup click handler
        time_fit_np = np.array(time_fit)
        
        def on_click_callback(idx):
            self.fit_end_idx = idx
        
        setup_fit_selection_click_handler(fig, ax, canvas, time_fit_np, status, on_click_callback)
        
        dialog.exec()
    
    def _show_data_preview(self):
        """Mostra anteprima dei dati nella tabella"""
        data = self.parser.get_data()
        if data is None:
            return
        
        # Mostra solo le prime 10 righe
        preview_data = data.head(10)
        
        self.data_preview_table.setColumnCount(len(preview_data.columns))
        self.data_preview_table.setRowCount(len(preview_data))
        
        self.data_preview_table.setHorizontalHeaderLabels(preview_data.columns)
        
        for row_idx, (_, row) in enumerate(preview_data.iterrows()):
            for col_idx, value in enumerate(row):
                # Formatta il valore per la visualizzazione
                display_value = str(value)[:30]  # Limita a 30 caratteri
                item = QTableWidgetItem(display_value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.data_preview_table.setItem(row_idx, col_idx, item)
        
        self.data_preview_table.resizeColumnsToContents()
    
    def check_files_loaded(self):
        """Abilita i pulsanti se entrambi i file sono caricati"""
        if self.csv_file and self.fit_file:
            self.btn_compare.setEnabled(True)
            self.btn_analyze.setEnabled(True)
            self.btn_export.setEnabled(True)

    def show_overlaid_comparison(self):
        """Mostra metabolimetro e FIT sovrapposti, scalati per tempo, allineati sulla fine rampa"""
        if self.engine.csv_data is None or self.engine.fit_data is None:
            QMessageBox.warning(self, "Dati mancanti", "Carica sia metabolimetro che FIT")
            return
        
        if self.met_end_idx is None or self.fit_end_idx is None:
            QMessageBox.warning(self, "Fine mancante", "Imposta le fine rampa per entrambi i dati")
            return

        # Estrai serie
        time_met, power_met = extract_metabolimeter_series(self.engine.csv_data)
        time_fit, power_fit = extract_fit_series(self.engine.fit_data)

        if power_met is None or power_fit is None:
            QMessageBox.warning(self, "Colonne mancanti", "Impossibile trovare le colonne potenza")
            return

        # Prepara dati per plot
        time_met_np = np.array(time_met)
        power_met_np = np.array(power_met)
        time_fit_np = np.array(time_fit)
        power_fit_np = np.array(power_fit)

        # Usa inizio rampa dal parser (se disponibile) altrimenti rileva da potenza
        if self.met_ramp_start_idx is not None:
            met_start_idx = self.met_ramp_start_idx
        else:
            met_start_idx = find_ramp_start(power_met_np)
        met_start_idx = max(0, min(met_start_idx, self.met_end_idx))

        # Finestra metabolimetro
        met_time = time_met_np[met_start_idx:self.met_end_idx + 1]
        met_data = power_met_np[met_start_idx:self.met_end_idx + 1]
        met_duration_sec = float(met_time[-1] - met_time[0]) if len(met_time) > 1 else 0.0

        # Finestra FIT
        fit_start_idx = max(0, int(self.fit_end_idx - round(met_duration_sec)))
        fit_time = time_fit_np[fit_start_idx:self.fit_end_idx + 1]
        fit_data = power_fit_np[fit_start_idx:self.fit_end_idx + 1]

        # Allinea tempi (x=0 all'inizio della rampa)
        met_time_aligned = met_time - met_time[0] if len(met_time) > 0 else np.arange(len(met_data), dtype=float)
        fit_time_aligned = fit_time - fit_time[0] if len(fit_time) > 0 else np.arange(len(fit_data), dtype=float)
        
        met_duration = met_time[-1] - met_time[0] if len(met_time) > 0 else 0
        fit_duration = fit_time[-1] - fit_time[0] if len(fit_time) > 0 else 0

        # Trova tempi intersezione VT
        vt1_time, vt2_time, map_time = find_vt_intersections(
            met_time_aligned, met_data, self.vt1, self.vt2, self.map
        )

        # Calcola medie mobili FIT (15s, 30s)
        fit_rolling_avgs = calculate_rolling_averages(fit_data, windows=[15, 30])

        # Crea dialog con rendering delegato a plotting_metapow
        dialog = create_overlaid_comparison_dialog(
            met_time_aligned, met_data, fit_time_aligned, fit_data,
            self.met_end_idx, self.fit_end_idx,
            vt1_time, vt2_time, map_time, fit_rolling_avgs,
            parent=self
        )
        
        dialog.exec()

    def show_vt_analysis(self):
        """Mostra grafico FIT con tab per analisi parametri metabolici"""
        if self.engine.csv_data is None or self.engine.fit_data is None:
            QMessageBox.warning(self, "Dati mancanti", "Carica sia metabolimetro che FIT")
            return
        
        if self.fit_end_idx is None or self.met_end_idx is None:
            QMessageBox.warning(self, "Fine mancante", "Imposta le fine rampa per entrambi i dati")
            return

        # Estrai serie
        time_met, power_met = extract_metabolimeter_series(self.engine.csv_data)
        time_fit, power_fit = extract_fit_series(self.engine.fit_data)

        if power_met is None or power_fit is None:
            QMessageBox.warning(self, "Colonne mancanti", "Impossibile trovare le colonne potenza")
            return

        # Prepara dati
        time_met_np = np.array(time_met)
        power_met_np = np.array(power_met)
        time_fit_np = np.array(time_fit)
        power_fit_np = np.array(power_fit)

        # Usa inizio rampa dal parser (se disponibile) altrimenti rileva da potenza
        if self.met_ramp_start_idx is not None:
            met_start_idx = self.met_ramp_start_idx
        else:
            met_start_idx = find_ramp_start(power_met_np)
        met_start_idx = max(0, min(met_start_idx, self.met_end_idx))

        # Finestra metabolimetro
        met_time = time_met_np[met_start_idx:self.met_end_idx + 1]
        met_data = power_met_np[met_start_idx:self.met_end_idx + 1]
        met_duration_sec = float(met_time[-1] - met_time[0]) if len(met_time) > 1 else 0.0

        # Finestra FIT
        fit_start_idx = max(0, int(self.fit_end_idx - round(met_duration_sec)))
        fit_time = time_fit_np[fit_start_idx:self.fit_end_idx + 1]
        fit_data = power_fit_np[fit_start_idx:self.fit_end_idx + 1]

        # Allinea tempi (x=0 all'inizio della rampa)
        met_time_aligned = met_time - met_time[0] if len(met_time) > 0 else np.arange(len(met_data), dtype=float)
        fit_time_aligned = fit_time - fit_time[0] if len(fit_time) > 0 else np.arange(len(fit_data), dtype=float)

        # Trova tempi VT
        vt1_time, vt2_time, map_time = find_vt_intersections(
            met_time_aligned, met_data, self.vt1, self.vt2, self.map
        )

        # Calcola medie mobili FIT (15s per analisi VT)
        fit_rolling_avgs = calculate_rolling_averages(fit_data, windows=[15])

        # Dati metabolici per tab
        metabol_data = self.engine.csv_data.iloc[met_start_idx:self.met_end_idx + 1]

        # Crea dialog con tab
        dialog = create_vt_analysis_dialog(
            metabol_data, met_time_aligned, fit_time_aligned, fit_data,
            vt1_time, vt2_time, map_time, fit_rolling_avgs, self
        )
        
        dialog.exec()
