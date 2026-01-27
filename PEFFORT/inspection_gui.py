# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
GUI INSPECTION - Scheda di ispezione visuale degli effort
Permette zoom, pan, e modifica manuale dei bordi degli effort
"""

from typing import Optional, List, Tuple, Dict, Any
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QInputDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import pandas as pd
import json
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure

from .peffort_engine import format_time_hhmmss
from .inspection_core import (
    InspectionManager, 
    load_efforts_from_database,
    save_efforts_to_database,
    get_saved_effort_info
)
from .inspection_builder import plot_inspection_figure

logger = logging.getLogger(__name__)


class InspectionTab(QWidget):
    """Tab per ispezione visuale e modifica degli effort"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inspection_manager: Optional[InspectionManager] = None
        self.current_df: Optional[pd.DataFrame] = None
        self.current_efforts: List[Tuple[int, int, float]] = []
        self.current_sprints: List[Dict[str, Any]] = []
        self.current_ftp: float = 280
        self.current_weight: float = 70
        self.html_path: Optional[str] = None
        self.current_fit_path: Optional[str] = None  # Percorso FIT attualmente caricato
        
        # Stato di selezione
        self.selected_effort_idx: Optional[int] = None
        self.zoom_level: float = 1.0
        self.click_mode: Optional[str] = None  # 'start' o 'end' quando in modalità di selezione
        
        # Timer per debounce live preview
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.render_inspection_plot)
        self.preview_timer.setInterval(500)  # 500ms debounce
        
        self.init_ui()
        
    def init_ui(self):
        """Inizializza UI della tab ispezione"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # ============ TOP BAR ============
        top_bar = QHBoxLayout()
        
        self.status_label = QLabel("Inspection - Pronto")
        self.status_label.setFont(QFont())
        top_bar.addWidget(self.status_label)
        
        top_bar.addSpacing(20)
        
        # Selezione effort - MIGLIORATO
        selector_label = QLabel("📍 Effort:")
        selector_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        top_bar.addWidget(selector_label)
        
        self.effort_combo = QComboBox()
        self.effort_combo.currentIndexChanged.connect(self.on_effort_selected)
        self.effort_combo.setMinimumWidth(280)
        self.effort_combo.setMaximumWidth(400)
        
        # Styling migliorato per visibilità
        self.effort_combo.setStyleSheet("""
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
        
        top_bar.addWidget(self.effort_combo)
        
        top_bar.addStretch()
        
        self.btn_save = QPushButton("Salva Modifiche")
        self.btn_save.clicked.connect(self.save_modifications)
        self.btn_save.setEnabled(False)
        top_bar.addWidget(self.btn_save)
        
        layout.addLayout(top_bar)
        
        # ============ MAIN CONTENT ============
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Canvas Matplotlib per il grafico interattivo
        graph_container = QVBoxLayout()
        graph_container.setContentsMargins(0, 0, 0, 0)
        graph_container.setSpacing(0)
        self.figure = Figure(figsize=(18, 10), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('button_press_event', self.on_graph_click)
        graph_container.addWidget(self.canvas)
        
        # Toolbar di navigazione Matplotlib (zoom, pan, home, etc.)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        graph_container.addWidget(self.toolbar)
        
        # Widget contenitore per il grafico
        graph_widget = QWidget()
        graph_widget.setLayout(graph_container)
        graph_widget.setStyleSheet("background: #0f172a; border-radius: 8px;")
        content_layout.addWidget(graph_widget, stretch=4)
        
        # ============ RIGHT PANEL - DETTAGLI EFFORT ============
        right_panel = QVBoxLayout()
        right_panel.setSpacing(6)
        right_panel.setContentsMargins(8, 0, 0, 0)
        
        right_panel.addWidget(QLabel("DETTAGLI EFFORT", objectName="SectionTitle"))
        
        # Tabella dettagli effort corrente
        self.table_effort_detail = QTableWidget()
        self.table_effort_detail.setColumnCount(2)
        self.table_effort_detail.setRowCount(8)
        self.table_effort_detail.setHorizontalHeaderLabels(["Proprietà", "Valore"])
        self.table_effort_detail.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_effort_detail.verticalHeader().setVisible(False)
        
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
            self.table_effort_detail.setItem(i, 0, QTableWidgetItem(prop))
            self.table_effort_detail.setItem(i, 1, QTableWidgetItem("---"))
        
        right_panel.addWidget(self.table_effort_detail, stretch=2)
        
        # Controlli di modifica
        right_panel.addWidget(QLabel("MODIFICA BORDI", objectName="SectionTitle"))
        
        ctrl_layout = QVBoxLayout()
        ctrl_layout.setSpacing(8)
        
        # Pulsanti per impostare inizio/fine
        set_bounds_h = QHBoxLayout()
        set_bounds_h.setSpacing(5)
        
        self.btn_set_start = QPushButton("📍 Imposta Inizio")
        self.btn_set_start.setStyleSheet("background-color: #06b6d4; color: white;")
        self.btn_set_start.clicked.connect(self.activate_set_start)
        set_bounds_h.addWidget(self.btn_set_start)
        
        self.btn_set_end = QPushButton("🏁 Imposta Fine")
        self.btn_set_end.setStyleSheet("background-color: #f97316; color: white;")
        self.btn_set_end.clicked.connect(self.activate_set_end)
        set_bounds_h.addWidget(self.btn_set_end)
        
        ctrl_layout.addLayout(set_bounds_h)
        
        # Mostra valori correnti
        current_h = QHBoxLayout()
        current_h.addWidget(QLabel("Inizio:"))
        self.label_start_val = QLabel("-")
        self.label_start_val.setStyleSheet("font-weight: bold; color: #06b6d4;")
        current_h.addWidget(self.label_start_val)
        current_h.addSpacing(20)
        current_h.addWidget(QLabel("Fine:"))
        self.label_end_val = QLabel("-")
        self.label_end_val.setStyleSheet("font-weight: bold; color: #f97316;")
        current_h.addWidget(self.label_end_val)
        current_h.addStretch()
        ctrl_layout.addLayout(current_h)
        
        # Pulsanti di reset
        btn_h = QHBoxLayout()
        btn_h.setSpacing(5)
        self.btn_reset_effort = QPushButton("Reset Effort")
        self.btn_reset_effort.clicked.connect(self.reset_current_effort)
        btn_h.addWidget(self.btn_reset_effort)
        
        self.btn_delete_effort = QPushButton("Elimina Effort")
        self.btn_delete_effort.setStyleSheet("color: #ff6b6b;")
        self.btn_delete_effort.clicked.connect(self.delete_current_effort)
        btn_h.addWidget(self.btn_delete_effort)
        
        ctrl_layout.addLayout(btn_h)
        
        right_panel.addLayout(ctrl_layout)
        
        right_panel.addStretch()
        
        content_layout.addLayout(right_panel, stretch=0.75)
        
        layout.addLayout(content_layout, stretch=1)
        layout.setSpacing(2)
        
        # ============ BOTTOM - TABELLA TUTTI EFFORTS ============
        self.table_all_efforts = QTableWidget()
        self.table_all_efforts.setColumnCount(6)
        self.table_all_efforts.setHorizontalHeaderLabels([
            "Idx", "Inizio", "Fine", "Durata (s)", "Watt Medi", "Stato"
        ])
        self.table_all_efforts.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_all_efforts.verticalHeader().setVisible(False)
        self.table_all_efforts.setMaximumHeight(120)
        self.table_all_efforts.itemSelectionChanged.connect(self.on_table_selection_changed)
        
        layout.addWidget(self.table_all_efforts, stretch=0)
        
    def update_analysis(self, df: pd.DataFrame, efforts: List[Tuple[int, int, float]],
                       sprints: List[Dict[str, Any]], ftp: float, weight: float,
                       params_str: str, fit_path: Optional[str] = None):
        """Aggiorna l'ispezione con i nuovi dati analizzati"""
        try:
            logger.info("Aggiornamento dati inspection tab")
            
            self.current_fit_path = fit_path  # Salva il percorso FIT
            self.current_df = df.copy()
            self.current_efforts = list(efforts)  # Copia della lista
            self.current_sprints = sprints
            self.current_ftp = ftp
            self.current_weight = weight
            
            # ========== CARICAMENTO EFFORT DA DATABASE ==========
            # Se abbiamo il percorso FIT, cerchiamo effort salvati nel Database
            if fit_path and self.try_load_efforts_from_database(fit_path):
                # Gli effort sono stati caricati da database
                logger.info("Effort caricati dal Database")
            
            # Inizializza inspection manager
            self.inspection_manager = InspectionManager(
                df=df,
                efforts=self.current_efforts,
                sprints=sprints,
                ftp=ftp,
                weight=weight
            )
            
            # Aggiorna combo effort
            self.effort_combo.blockSignals(True)
            self.effort_combo.clear()
            for i, (start, end, avg) in enumerate(self.current_efforts):
                start_time = format_time_hhmmss(df['time_sec'].iloc[start])
                end_time = format_time_hhmmss(df['time_sec'].iloc[end])
                duration = int(df['time_sec'].iloc[end] - df['time_sec'].iloc[start])
                # Formato leggibile con più info
                display_text = f"#{i+1} | {start_time}→{end_time} | {duration}s | {avg:.0f}W"
                self.effort_combo.addItem(display_text, userData=i)
            self.effort_combo.blockSignals(False)
            
            # Seleziona primo effort
            if len(self.current_efforts) > 0:
                self.effort_combo.setCurrentIndex(0)
                self.on_effort_selected(0)
            
            # Genera grafico
            self.render_inspection_plot()
            
            self.status_label.setText(
                f"✅ {len(self.current_efforts)} efforts caricati"
            )
            self.btn_save.setEnabled(True)
            
            logger.info("Inspection tab aggiornato con successo")
            
        except Exception as e:
            logger.error(f"Errore aggiornamento inspection: {e}", exc_info=True)
            self.status_label.setText("❌ Errore caricamento dati")
            QMessageBox.critical(self, "Errore", f"Errore caricamento: {str(e)}")
    
    def render_inspection_plot(self):
        """Renderizza il grafico Matplotlib"""
        if self.current_df is None or not self.current_efforts:
            return
        
        try:
            self.status_label.setText("⏳ Generazione grafico ispezione...")
            
            # Pulisci la figura esistente
            self.figure.clear()
            
            # Crea il grafico direttamente sulla figura del canvas
            from .inspection_builder import plot_inspection_figure
            plot_inspection_figure(
                self.figure,
                self.current_df,
                self.current_efforts,
                self.current_sprints,
                self.current_ftp,
                self.current_weight,
                zoom_level=self.zoom_level
            )
            
            # Ridisegna il canvas
            self.canvas.draw_idle()
            
            self.status_label.setText("✓ Grafico caricato - Clicca i bottoni per impostare i bordi")
            logger.info("Grafico Matplotlib renderizzato")
            
        except Exception as e:
            logger.error(f"Errore rendering inspection plot: {e}", exc_info=True)
            self.status_label.setText("❌ Errore generazione grafico")
            QMessageBox.critical(self, "Errore", f"Errore grafico: {str(e)}")
    
    def on_graph_click(self, event):
        """Gestisce i click sul grafico Matplotlib per impostare i bordi"""
        if event.inaxes is None or self.selected_effort_idx is None or not hasattr(self, 'click_mode'):
            return
        
        # Se non siamo in modalità di selezione, ignora
        if self.click_mode is None:
            return
        
        # Ottieni la coordinata X (tempo)
        time_sec = event.xdata
        if time_sec is None:
            return
        
        # Applica la modifica in base alla modalità
        is_start = (self.click_mode == 'start')
        self._apply_effort_change(float(time_sec), is_start=is_start)
        
        # Resetta la modalità di selezione
        self.click_mode = None
        self.btn_set_start.setStyleSheet("background-color: #06b6d4; color: white;")
        self.btn_set_end.setStyleSheet("background-color: #f97316; color: white;")
    
    def on_effort_selected(self, idx: int):
        """Seleziona un effort dalla combo"""
        if idx < 0 or idx >= len(self.current_efforts):
            return
        
        self.selected_effort_idx = idx
        self.update_effort_detail_panel(idx)
        self.update_all_efforts_table()
    
    def update_effort_detail_panel(self, effort_idx: int):
        """Aggiorna il pannello dettagli dell'effort selezionato"""
        if effort_idx < 0 or effort_idx >= len(self.current_efforts):
            return
        
        try:
            start_idx, end_idx, avg_power = self.current_efforts[effort_idx]
            
            power = self.current_df['power'].values
            time_sec = self.current_df['time_sec'].values
            hr = self.current_df['heartrate'].values
            
            seg_power = power[start_idx:end_idx+1]
            seg_time = time_sec[start_idx:end_idx+1]
            seg_hr = hr[start_idx:end_idx+1]
            
            start_time = seg_time[0]
            end_time = seg_time[-1]
            duration = int(end_time - start_time)
            
            power_peak = seg_power.max() if len(seg_power) > 0 else 0
            w_kg = avg_power / self.current_weight if self.current_weight > 0 else 0
            hr_mean = seg_hr[seg_hr > 0].mean() if (seg_hr > 0).any() else 0
            hr_max = seg_hr.max() if len(seg_hr) > 0 else 0
            
            # Aggiorna tabella dettagli
            self.table_effort_detail.setItem(0, 1, QTableWidgetItem(format_time_hhmmss(start_time)))
            self.table_effort_detail.setItem(1, 1, QTableWidgetItem(format_time_hhmmss(end_time)))
            self.table_effort_detail.setItem(2, 1, QTableWidgetItem(f"{duration}"))
            self.table_effort_detail.setItem(3, 1, QTableWidgetItem(f"{avg_power:.0f}"))
            self.table_effort_detail.setItem(4, 1, QTableWidgetItem(f"{w_kg:.2f}"))
            self.table_effort_detail.setItem(5, 1, QTableWidgetItem(f"{power_peak:.0f}"))
            self.table_effort_detail.setItem(6, 1, QTableWidgetItem(f"{hr_mean:.0f}"))
            self.table_effort_detail.setItem(7, 1, QTableWidgetItem(f"{int(hr_max)}"))
            
            # Aggiorna label dei valori attuali
            self.label_start_val.setText(str(int(start_time)))
            self.label_end_val.setText(str(int(end_time)))
            
            logger.info(f"Effort {effort_idx} selected - duration: {duration}s")
            
        except Exception as e:
            logger.error(f"Errore aggiornamento dettagli effort: {e}", exc_info=True)
    
    def update_all_efforts_table(self):
        """Aggiorna la tabella con tutti gli effort"""
        try:
            time_sec = self.current_df['time_sec'].values
            
            self.table_all_efforts.setRowCount(len(self.current_efforts))
            
            for i, (start_idx, end_idx, avg) in enumerate(self.current_efforts):
                start_time = time_sec[start_idx]
                end_time = time_sec[end_idx]
                duration = int(end_time - start_time)
                
                # Highlight riga selezionata
                bg_color = "#1e3a5f" if i == self.selected_effort_idx else None
                
                row_data = [
                    str(i + 1),
                    format_time_hhmmss(start_time),
                    format_time_hhmmss(end_time),
                    f"{duration}s",
                    f"{avg:.0f}",
                    "✏️ Modificato" if self.inspection_manager and self.inspection_manager.is_modified(i) else "✓"
                ]
                
                for j, data in enumerate(row_data):
                    item = QTableWidgetItem(data)
                    if bg_color:
                        from PySide6.QtGui import QColor
                        item.setBackground(QColor(bg_color))
                    self.table_all_efforts.setItem(i, j, item)
            
        except Exception as e:
            logger.error(f"Errore aggiornamento tabella: {e}", exc_info=True)
    
    def on_table_selection_changed(self):
        """Sincronizza selezione da tabella a combo"""
        selected_rows = self.table_all_efforts.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            self.effort_combo.blockSignals(True)
            self.effort_combo.setCurrentIndex(row)
            self.effort_combo.blockSignals(False)
            self.on_effort_selected(row)
    
    def activate_set_start(self):
        """Attiva modalità per selezionare l'inizio dal grafico"""
        if self.selected_effort_idx is None:
            self.status_label.setText("⚠️  Seleziona prima un effort")
            return
        
        self.click_mode = 'start'
        self.btn_set_start.setStyleSheet("background-color: #3b82f6; color: white; font-weight: bold;")
        self.status_label.setText("🖱️  Clicca sul grafico per impostare l'inizio...")
    
    def activate_set_end(self):
        """Attiva modalità per selezionare la fine dal grafico"""
        if self.selected_effort_idx is None:
            self.status_label.setText("⚠️  Seleziona prima un effort")
            return
        
        self.click_mode = 'end'
        self.btn_set_end.setStyleSheet("background-color: #f97316; color: white; font-weight: bold;")
        self.status_label.setText("🖱️  Clicca sul grafico per impostare la fine...")
    
    def _apply_effort_change(self, time_sec: float, is_start: bool):
        """Applica una modifica di inizio o fine dell'effort"""
        if self.selected_effort_idx is None or not self.current_efforts:
            return
        
        try:
            # Ottieni l'effort CORRENTE dal manager
            start_idx, end_idx, avg = self.current_efforts[self.selected_effort_idx]
            time_sec_array = self.current_df['time_sec'].values
            
            # Converti indici attuali a secondi
            current_start_sec = float(time_sec_array[start_idx])
            current_end_sec = float(time_sec_array[end_idx])
            
            # Arrotonda il click
            new_time_sec = round(time_sec)
            
            if is_start:
                # Modifica l'inizio
                if new_time_sec >= current_end_sec:
                    self.status_label.setText("⚠️  Inizio deve essere prima di fine")
                    return
                new_start = new_time_sec
                new_end = current_end_sec
            else:
                # Modifica la fine
                if new_time_sec <= current_start_sec:
                    self.status_label.setText("⚠️  Fine deve essere dopo inizio")
                    return
                new_start = current_start_sec
                new_end = new_time_sec
            
            # Applica la modifica tramite il manager
            if self.inspection_manager:
                self.inspection_manager.modify_effort(
                    self.selected_effort_idx,
                    new_start,
                    new_end
                )
                self.current_efforts = self.inspection_manager.get_modified_efforts()
                self.update_effort_detail_panel(self.selected_effort_idx)
                self.update_all_efforts_table()
                self.render_inspection_plot()
                self.status_label.setText("✓ Modifica applicata - non salvata")
            
        except Exception as e:
            logger.error(f"Errore applicazione modifica: {e}", exc_info=True)
            self.status_label.setText(f"❌ Errore: {str(e)}")
    
    def reset_current_effort(self):
        """Ripristina l'effort al valore originale"""
        if self.selected_effort_idx is None:
            return
        
        if self.inspection_manager:
            self.inspection_manager.reset_effort(self.selected_effort_idx)
            self.update_effort_detail_panel(self.selected_effort_idx)
            self.update_all_efforts_table()
            self.status_label.setText("✓ Effort ripristinato")
    
    def delete_current_effort(self):
        """Elimina l'effort corrente"""
        if self.selected_effort_idx is None:
            return
        
        reply = QMessageBox.warning(
            self,
            "Conferma eliminazione",
            f"Eliminare effort {self.selected_effort_idx + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.inspection_manager:
                self.inspection_manager.delete_effort(self.selected_effort_idx)
                self.current_efforts = self.inspection_manager.get_modified_efforts()
                
                # Aggiorna UI
                self.effort_combo.blockSignals(True)
                self.effort_combo.clear()
                for i, (start, end, avg) in enumerate(self.current_efforts):
                    start_time = format_time_hhmmss(self.current_df['time_sec'].iloc[start])
                    end_time = format_time_hhmmss(self.current_df['time_sec'].iloc[end])
                    duration = int(self.current_df['time_sec'].iloc[end] - self.current_df['time_sec'].iloc[start])
                    display_text = f"#{i+1} | {start_time}→{end_time} | {duration}s | {avg:.0f}W"
                    self.effort_combo.addItem(display_text, userData=i)
                self.effort_combo.blockSignals(False)
                
                if len(self.current_efforts) > 0:
                    self.effort_combo.setCurrentIndex(0)
                
                self.render_inspection_plot()
                self.status_label.setText(f"✓ Effort eliminato - {len(self.current_efforts)} rimasti")
    
    def save_modifications(self):
        """Salva le modifiche agli effort e nel Database"""
        if not self.inspection_manager:
            self.status_label.setText("❌ Nessun dato caricato")
            return
        
        try:
            modified_efforts = self.inspection_manager.get_modified_efforts()
            self.current_efforts = modified_efforts
            
            # Rigenera il grafico per mostrare le modifiche salvate
            self.render_inspection_plot()
            
            # ========== SALVA NEL DATABASE ==========
            if self.current_fit_path:
                save_efforts_to_database(self.current_fit_path, modified_efforts)
                db_saved = "✓ Salvati anche nel Database"
            else:
                db_saved = "(Nessun FIT associato per salvare nel Database)"
            
            QMessageBox.information(
                self,
                "✓ Modifiche Salvate",
                f"Salvate {len(modified_efforts)} efforts.\n\n"
                f"{db_saved}\n\n"
                "Le modifiche sono ora disponibili per l'export e l'analisi."
            )
            
            self.status_label.setText(f"✓ {len(modified_efforts)} efforts salvati")
            logger.info(f"Modifiche salvate: {len(modified_efforts)} efforts")
            
        except Exception as e:
            logger.error(f"Errore salvataggio modifiche: {e}", exc_info=True)
            self.status_label.setText("❌ Errore salvataggio")
            QMessageBox.critical(self, "Errore", f"Errore salvataggio: {str(e)}")
    
    # ========================================================================
    # DATABASE METHODS - Caricamento/Salvataggio su disco
    # ========================================================================
    
    def try_load_efforts_from_database(self, fit_path: str) -> bool:
        """
        Tenta di caricare effort dal Database per il FIT specificato.
        Se trovato, chiede conferma all'utente prima di caricare.
        
        Returns: True se effort caricati, False altrimenti
        """
        try:
            # Verifica se esiste file effort nel database
            info = get_saved_effort_info(fit_path)
            if not info:
                return False
            
            # Chiedi conferma all'utente
            result = QMessageBox.question(
                self,
                "Effort Salvati Trovati",
                f"Trovati {info['effort_count']} effort salvati per questo FIT.\n"
                f"Data: {info['created']}\n\n"
                "Vuoi caricare gli effort rettificati?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if result != QMessageBox.StandardButton.Yes:
                return False
            
            # Carica gli effort
            loaded_efforts = load_efforts_from_database(fit_path)
            if loaded_efforts:
                self.current_efforts = loaded_efforts
                self.status_label.setText(f"✓ Caricati {len(loaded_efforts)} effort dal Database")
                logger.info(f"Effort caricati dal Database: {len(loaded_efforts)}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Errore caricamento effort da database: {e}", exc_info=True)
            return False
    
    def save_efforts_to_database(self):
        """Salva gli effort modificati nel Database JSON"""
        if not self.current_fit_path:
            QMessageBox.warning(
                self,
                "Avviso",
                "Nessun FIT caricato. Impossibile salvare."
            )
            return
        
        if not self.inspection_manager or not self.current_efforts:
            QMessageBox.warning(
                self,
                "Avviso",
                "Nessun effort da salvare."
            )
            return
        
        try:
            # Salva nel database
            success = save_efforts_to_database(
                self.current_fit_path,
                self.current_efforts
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "✓ Salvato",
                    f"Salvati {len(self.current_efforts)} effort nel Database.\n\n"
                    "La prossima volta che carichi questo FIT potrai ricaricare "
                    "gli effort rettificati automaticamente."
                )
                self.status_label.setText(f"💾 {len(self.current_efforts)} effort salvati nel Database")
                logger.info(f"Effort salvati nel Database: {self.current_fit_path}")
            else:
                QMessageBox.critical(
                    self,
                    "Errore",
                    "Errore durante il salvataggio nel Database."
                )
                self.status_label.setText("❌ Errore salvataggio Database")
                
        except Exception as e:
            logger.error(f"Errore salvataggio nel Database: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore: {str(e)}"
            )
