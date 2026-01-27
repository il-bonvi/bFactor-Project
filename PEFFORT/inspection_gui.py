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
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import QTimer

import pandas as pd

from .peffort_engine import format_time_hhmmss
from .inspection_core import (
    InspectionManager, 
    load_efforts_from_database,
    get_saved_effort_info
)
from .inspection_builder import plot_inspection_figure
from .inspection_handlers import EffortHandler
from .inspection_widgets import (
    build_top_bar, build_graph_widget, build_detail_panel,
    build_efforts_table, update_detail_panel, update_efforts_table
)

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
        self.current_fit_path: Optional[str] = None
        
        # Stato
        self.selected_effort_idx: Optional[int] = None
        self.zoom_level: float = 1.0
        self.click_mode: Optional[str] = None
        
        # Handler
        self.effort_handler = EffortHandler(self)
        
        # Timer debounce
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.render_inspection_plot)
        self.preview_timer.setInterval(500)
        
        self.init_ui()
        
    def init_ui(self):
        """Inizializza UI della tab ispezione"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Top bar
        top_bar = build_top_bar(self)
        layout.addLayout(top_bar)
        
        # Main content (grafico + dettagli)
        content_layout = self._build_content_layout()
        layout.addLayout(content_layout, stretch=1)
        layout.setSpacing(2)
        
        # Tabella effort
        table = build_efforts_table(self)
        layout.addWidget(table, stretch=0)
    
    def _build_content_layout(self):
        """Costruisce il layout principale (grafico + pannello destra)"""
        from PySide6.QtWidgets import QHBoxLayout
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(8)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Grafico
        graph_widget = build_graph_widget(self)
        content_layout.addWidget(graph_widget, stretch=4)
        
        # Pannello dettagli
        right_panel = build_detail_panel(self)
        content_layout.addLayout(right_panel, stretch=0.75)
        
        return content_layout
        
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
        update_detail_panel(self, effort_idx)
    
    def update_all_efforts_table(self):
        """Aggiorna la tabella con tutti gli effort"""
        update_efforts_table(self)
    
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
        self.effort_handler.apply_effort_change(time_sec, is_start=is_start)
    
    def reset_current_effort(self):
        """Ripristina l'effort al valore originale"""
        self.effort_handler.reset_effort()
    
    def delete_current_effort(self):
        """Elimina l'effort corrente"""
        self.effort_handler.delete_effort()
    
    def save_modifications(self):
        """Salva le modifiche agli effort e nel Database"""
        self.effort_handler.save_modifications()
    
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
