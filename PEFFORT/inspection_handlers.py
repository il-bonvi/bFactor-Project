# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
INSPECTION HANDLERS - Logica di modifica e gestione degli effort
Gestisce: applicazione modifiche, reset, eliminazione, salvataggio
"""

from typing import Optional, List, Tuple
import logging
from PySide6.QtWidgets import QMessageBox

from .peffort_engine import format_time_hhmmss
from .inspection_core import save_efforts_to_database
import pandas as pd

logger = logging.getLogger(__name__)


class EffortHandler:
    """Gestisce le operazioni su effort (modifica, reset, delete)"""
    
    def __init__(self, parent_widget):
        """
        Args:
            parent_widget: Reference alla InspectionTab per accedere a dati e UI
        """
        self.parent = parent_widget
    
    def apply_effort_change(self, time_sec: float, is_start: bool) -> bool:
        """
        Applica una modifica di inizio o fine dell'effort
        
        Args:
            time_sec: Tempo in secondi dove è stato cliccato
            is_start: True se modificare inizio, False se fine
        
        Returns: True se modifica applicata, False altrimenti
        """
        if self.parent.selected_effort_idx is None or not self.parent.current_efforts:
            return False
        
        try:
            # Ottieni l'effort CORRENTE dal manager
            start_idx, end_idx, avg = self.parent.current_efforts[self.parent.selected_effort_idx]
            time_sec_array = self.parent.current_df['time_sec'].values
            
            # Converti indici attuali a secondi
            current_start_sec = float(time_sec_array[start_idx])
            current_end_sec = float(time_sec_array[end_idx])
            
            # Arrotonda il click
            new_time_sec = round(time_sec)
            
            if is_start:
                # Modifica l'inizio
                if new_time_sec >= current_end_sec:
                    self.parent.status_label.setText("⚠️  Inizio deve essere prima di fine")
                    return False
                new_start = new_time_sec
                new_end = current_end_sec
            else:
                # Modifica la fine
                if new_time_sec <= current_start_sec:
                    self.parent.status_label.setText("⚠️  Fine deve essere dopo inizio")
                    return False
                new_start = current_start_sec
                new_end = new_time_sec
            
            # Applica la modifica tramite il manager
            if self.parent.inspection_manager:
                self.parent.inspection_manager.modify_effort(
                    self.parent.selected_effort_idx,
                    new_start,
                    new_end
                )
                self.parent.current_efforts = self.parent.inspection_manager.get_modified_efforts()
                self.parent.update_effort_detail_panel(self.parent.selected_effort_idx)
                self.parent.update_all_efforts_table()
                self.parent.render_inspection_plot()
                self.parent.status_label.setText("✓ Modifica applicata - non salvata")
                return True
            
        except Exception as e:
            logger.error(f"Errore applicazione modifica: {e}", exc_info=True)
            self.parent.status_label.setText(f"❌ Errore: {str(e)}")
            return False
    
    def reset_effort(self, effort_idx: Optional[int] = None) -> bool:
        """
        Ripristina un effort al valore originale
        
        Args:
            effort_idx: Indice effort (usa selected se None)
        
        Returns: True se reset applicato
        """
        idx = effort_idx if effort_idx is not None else self.parent.selected_effort_idx
        if idx is None:
            return False
        
        try:
            if self.parent.inspection_manager:
                self.parent.inspection_manager.reset_effort(idx)
                self.parent.update_effort_detail_panel(idx)
                self.parent.update_all_efforts_table()
                self.parent.status_label.setText("✓ Effort ripristinato")
                return True
        except Exception as e:
            logger.error(f"Errore reset effort: {e}", exc_info=True)
            self.parent.status_label.setText(f"❌ Errore: {str(e)}")
        
        return False
    
    def delete_effort(self, effort_idx: Optional[int] = None) -> bool:
        """
        Elimina un effort
        
        Args:
            effort_idx: Indice effort (usa selected se None)
        
        Returns: True se eliminato
        """
        idx = effort_idx if effort_idx is not None else self.parent.selected_effort_idx
        if idx is None:
            return False
        
        # Conferma eliminazione
        reply = QMessageBox.warning(
            self.parent,
            "Conferma eliminazione",
            f"Eliminare effort {idx + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return False
        
        try:
            if self.parent.inspection_manager:
                self.parent.inspection_manager.delete_effort(idx)
                self.parent.current_efforts = self.parent.inspection_manager.get_modified_efforts()
                
                # Aggiorna UI
                self.parent.effort_combo.blockSignals(True)
                self.parent.effort_combo.clear()
                
                # Verifica che il DataFrame abbia la colonna time_sec
                if 'time_sec' not in self.parent.current_df.columns:
                    logger.error("Colonna 'time_sec' non trovata nel DataFrame")
                    self.parent.effort_combo.blockSignals(False)
                    return
                
                for i, (start, end, avg) in enumerate(self.parent.current_efforts):
                    # Verifica che gli indici siano validi
                    if start >= len(self.parent.current_df) or end >= len(self.parent.current_df):
                        logger.warning(f"Indici effort #{i+1} fuori range: start={start}, end={end}, len={len(self.parent.current_df)}")
                        continue
                    
                    start_time = format_time_hhmmss(self.parent.current_df['time_sec'].iloc[start])
                    end_time = format_time_hhmmss(self.parent.current_df['time_sec'].iloc[end])
                    duration = int(self.parent.current_df['time_sec'].iloc[end] - self.parent.current_df['time_sec'].iloc[start])
                    display_text = f"#{i+1} | {start_time}→{end_time} | {duration}s | {avg:.0f}W"
                    self.parent.effort_combo.addItem(display_text, userData=i)
                self.parent.effort_combo.blockSignals(False)
                
                if len(self.parent.current_efforts) > 0:
                    self.parent.effort_combo.setCurrentIndex(0)
                
                self.parent.render_inspection_plot()
                self.parent.status_label.setText(f"✓ Effort eliminato - {len(self.parent.current_efforts)} rimasti")
                return True
        
        except Exception as e:
            logger.error(f"Errore eliminazione effort: {e}", exc_info=True)
            self.parent.status_label.setText(f"❌ Errore eliminazione: {str(e)}")
        
        return False
    
    def save_modifications(self) -> bool:
        """
        Salva le modifiche agli effort nel Database
        
        Returns: True se salvato con successo
        """
        if not self.parent.inspection_manager:
            self.parent.status_label.setText("❌ Nessun dato caricato")
            return False
        
        try:
            modified_efforts = self.parent.inspection_manager.get_modified_efforts()
            self.parent.current_efforts = modified_efforts
            
            # Rigenera il grafico
            self.parent.render_inspection_plot()
            
            # ========== SALVA NEL DATABASE ==========
            if self.parent.current_fit_path:
                save_efforts_to_database(self.parent.current_fit_path, modified_efforts)
                db_saved = "✓ Salvati anche nel Database"
            else:
                db_saved = "(Nessun FIT associato per salvare nel Database)"
            
            QMessageBox.information(
                self.parent,
                "✓ Modifiche Salvate",
                f"Salvate {len(modified_efforts)} efforts.\n\n"
                f"{db_saved}\n\n"
                "Le modifiche sono ora disponibili per l'export e l'analisi."
            )
            
            self.parent.status_label.setText(f"✓ {len(modified_efforts)} efforts salvati")
            logger.info(f"Modifiche salvate: {len(modified_efforts)} efforts")
            return True
            
        except Exception as e:
            logger.error(f"Errore salvataggio modifiche: {e}", exc_info=True)
            self.parent.status_label.setText("❌ Errore salvataggio")
            QMessageBox.critical(self.parent, "Errore", f"Errore salvataggio: {str(e)}")
            return False
