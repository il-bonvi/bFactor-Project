# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
GUI 3D MAP - Scheda visualizzazione mappa 3D interattiva
Vista "drone view" della traccia con terrain e altimetria
"""

from typing import Optional, List, Tuple, Dict, Any
import logging
import webbrowser
import tempfile
import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)


class Map3DTab(QWidget):
    """Tab per visualizzazione 3D della traccia con terrain"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_df: Optional[pd.DataFrame] = None
        self.last_efforts: Optional[List[Tuple[int, int, float]]] = None
        self.last_ftp: Optional[float] = None
        self.last_weight: Optional[float] = None
        self.init_ui()
        
    def init_ui(self):
        """Inizializza UI della tab 3D map"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Titolo
        title = QLabel("📍 Vista 3D - Mappa Interattiva con Terrain")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #60a5fa;")
        layout.addWidget(title)
        
        # Descrizione
        desc = QLabel(
            "Visualizza la traccia in 3D con terrain reale e altimetria.\n"
            "La mappa si apre nel browser con controlli interattivi.\n\n"
            "⚠️ Carica un file FIT prima di usare questa tab."
        )
        desc.setStyleSheet("color: #9ca3af; font-size: 13px; line-height: 1.6;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Spacer
        layout.addSpacing(20)
        
        # Bottone principale
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_3d = QPushButton("🗺️ Apri Vista 3D")
        self.btn_3d.setEnabled(False)
        self.btn_3d.setMinimumSize(200, 45)
        self.btn_3d.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #1e40af, #1e3a8a);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            QPushButton:hover:!pressed {
                background: linear-gradient(135deg, #1e3a8a, #172554);
                box-shadow: 0 4px 15px rgba(30, 64, 175, 0.4);
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #172554, #0f172a);
            }
            QPushButton:disabled {
                background: #4b5563;
                color: #9ca3af;
                cursor: not-allowed;
            }
        """)
        self.btn_3d.clicked.connect(self.open_3d_map)
        button_layout.addWidget(self.btn_3d)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Status
        layout.addSpacing(20)
        self.status_label = QLabel("Status: Pronto")
        self.status_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def update_analysis(self, df: pd.DataFrame, efforts: List[Tuple[int, int, float]],
                       sprints: List[Dict[str, Any]], ftp: float, weight: float,
                       params_str: str):
        """Aggiorna i dati disponibili per la visualizzazione 3D"""
        try:
            # Verifica coordinate GPS
            if 'position_lat' not in df.columns or 'position_long' not in df.columns:
                self.status_label.setText("❌ GPS non disponibile")
                self.btn_3d.setEnabled(False)
                return
            
            # Cache dati
            self.last_df = df
            self.last_efforts = efforts
            self.last_ftp = ftp
            self.last_weight = weight
            
            # Abilita bottone
            self.btn_3d.setEnabled(True)
            num_efforts = len(efforts)
            distance_km = (df['distance'].values[-1] - df['distance'].values[0]) / 1000 if 'distance' in df.columns else 0
            self.status_label.setText(f"✅ Pronto: {distance_km:.1f} km | {num_efforts} efforts")
            
            logger.info(f"Tab 3D Map pronta: {distance_km:.1f} km con {num_efforts} efforts")
            
        except Exception as e:
            logger.error(f"Errore update 3D map: {e}", exc_info=True)
            self.status_label.setText("❌ Errore nel caricamento dei dati")
    
    def open_3d_map(self):
        """Genera e apre la mappa 3D nel browser"""
        if self.last_df is None or self.last_efforts is None:
            QMessageBox.warning(self, "Attenzione", 
                              "Carica un file FIT prima di aprire la vista 3D")
            return
        
        try:
            self.status_label.setText("⏳ Generazione mappa 3D...")
            
            from .map3d_builder import generate_3d_map_html
            
            logger.info("Generazione mappa 3D...")
            
            html = generate_3d_map_html(
                self.last_df,
                self.last_efforts,
                self.last_ftp,
                self.last_weight
            )
            
            # Salva in file temporaneo
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', delete=False, suffix='.html', encoding='utf-8'
            )
            temp_file.write(html)
            temp_file.close()
            
            # Apri nel browser
            webbrowser.open("file://" + temp_file.name)
            
            self.status_label.setText("✅ Mappa 3D aperta nel browser")
            logger.info("Mappa 3D aperta nel browser")
            
        except Exception as e:
            logger.error(f"Errore apertura mappa 3D: {e}", exc_info=True)
            self.status_label.setText("❌ Errore generazione mappa")
            QMessageBox.critical(self, "Errore", f"Errore: {str(e)}")
