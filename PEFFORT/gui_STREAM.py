# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
GUI STREAM - Scheda visualizzazione stream (solo stream potenza)
Analisi effort senza GPS/altimetria - ideale per indoor trainer
"""

from typing import Optional, List, Tuple, Dict, Any
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import tempfile
import webbrowser
import pandas as pd

from .engine_PEFFORT import format_time_hhmmss

logger = logging.getLogger(__name__)


class StreamTab(QWidget):
    """Tab per visualizzazione stream - solo stream potenza"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.html_path: Optional[str] = None
        
    def init_ui(self):
        """Inizializza UI della tab stream"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Top bar
        top_bar = QHBoxLayout()
        self.status_label = QLabel("Vista stream - Pronto")
        top_bar.addWidget(self.status_label)
        top_bar.addStretch()
        
        self.btn_browser = QPushButton("Apri nel Browser")
        self.btn_browser.clicked.connect(self.open_in_browser)
        self.btn_browser.setEnabled(False)
        top_bar.addWidget(self.btn_browser)
        
        layout.addLayout(top_bar)
        
        # Web view per il grafico
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background: #0f172a; border-radius: 8px;")
        # Configura settings per caricare Mapbox/tile da pagine HTML locali
        from PySide6.QtWebEngineCore import QWebEngineSettings
        web_settings = self.web_view.settings()
        web_settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        layout.addWidget(self.web_view, stretch=3)
        
        # Tabelle efforts e sprints
        tables_container = QHBoxLayout()
        tables_container.setSpacing(15)
        
        self.table_efforts = QTableWidget()
        self.table_efforts.setColumnCount(5)
        self.table_efforts.setHorizontalHeaderLabels(["Inizio", "Durata", "Watt", "W/kg", "kJ"])
        self.table_efforts.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_efforts.verticalHeader().setVisible(False)
        
        self.table_sprints = QTableWidget()
        self.table_sprints.setColumnCount(4)
        self.table_sprints.setHorizontalHeaderLabels(["Inizio", "Picco (W)", "Watt Medi", "HR Max"])
        self.table_sprints.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_sprints.verticalHeader().setVisible(False)
        
        eff_layout = QVBoxLayout()
        eff_layout.addWidget(QLabel("SUSTAINED EFFORTS", objectName="SectionTitle"))
        eff_layout.addWidget(self.table_efforts)
        
        spr_layout = QVBoxLayout()
        spr_layout.addWidget(QLabel("SPRINT & SURGES", objectName="SectionTitle"))
        spr_layout.addWidget(self.table_sprints)
        
        tables_container.addLayout(eff_layout, stretch=2)
        tables_container.addLayout(spr_layout, stretch=1)
        
        layout.addLayout(tables_container, stretch=1)
        
    def update_analysis(self, df: pd.DataFrame, efforts: List[Tuple[int, int, float]], 
                       sprints: List[Dict[str, Any]], ftp: float, weight: float,
                       params_str: str):
        """Aggiorna la visualizzazione con i nuovi dati analizzati"""
        try:
            from .exporter_STREAM import plot_stream_html
            
            logger.info("Generazione grafico stream...")
            self.status_label.setText("⏳ Generazione grafico...")
            
            # Genera HTML con grafico potenza vs tempo
            html = plot_stream_html(df, efforts, sprints, ftp, weight)
            
            # Salva e visualizza
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
            temp_file.write(html)
            temp_file.close()
            self.html_path = temp_file.name
            self.web_view.setUrl(QUrl.fromLocalFile(temp_file.name))
            
            self.btn_browser.setEnabled(True)
            self.status_label.setText(f"✅ Grafico stream generato: {len(efforts)} efforts + {len(sprints)} sprints")
            
            # Popola tabelle
            self.populate_tables(df, efforts, sprints, ftp, weight)
            
            logger.info("Grafico stream generato con successo")
            
        except Exception as e:
            logger.error(f"Errore generazione grafico stream: {e}", exc_info=True)
            self.status_label.setText("❌ Errore generazione grafico")
            QMessageBox.critical(self, "Errore", f"Errore generazione grafico: {str(e)}")
    
    def populate_tables(self, df: pd.DataFrame, efforts: List[Tuple[int, int, float]], 
                       sprints: List[Dict[str, Any]], ftp: float, weight: float):
        """Popola le tabelle con i dati"""
        try:
            power = df["power"].values
            time_sec = df["time_sec"].values
            hr = df["heartrate"].values
            
            # Tabella Efforts
            self.table_efforts.setRowCount(len(efforts))
            for i, (s, e, avg) in enumerate(efforts):
                seg_time = time_sec[s:e]
                seg_power = power[s:e]
                
                duration = int(seg_time[-1] - seg_time[0] + 1)
                w_kg = avg / weight if weight > 0 else 0
                
                # Calcola energia (kJ)
                energy_j = 0
                for j in range(s, min(e-1, len(time_sec)-1)):
                    dt = time_sec[j+1] - time_sec[j]
                    if dt > 0 and dt < 30:
                        energy_j += power[j] * dt
                energy_kj = energy_j / 1000
                
                self.table_efforts.setItem(i, 0, QTableWidgetItem(format_time_hhmmss(seg_time[0])))
                self.table_efforts.setItem(i, 1, QTableWidgetItem(f"{duration}s"))
                self.table_efforts.setItem(i, 2, QTableWidgetItem(f"{avg:.0f}"))
                self.table_efforts.setItem(i, 3, QTableWidgetItem(f"{w_kg:.2f}"))
                self.table_efforts.setItem(i, 4, QTableWidgetItem(f"{energy_kj:.1f}"))
            
            # Tabella Sprints
            self.table_sprints.setRowCount(len(sprints))
            for i, sprint in enumerate(sprints):
                start, end = sprint['start'], sprint['end']
                seg_power = power[start:end]
                seg_time = time_sec[start:end]
                seg_hr = hr[start:end]
                
                max_hr = seg_hr.max() if seg_hr[seg_hr > 0].any() else 0
                
                self.table_sprints.setItem(i, 0, QTableWidgetItem(format_time_hhmmss(seg_time[0])))
                self.table_sprints.setItem(i, 1, QTableWidgetItem(f"{seg_power.max():.0f}"))
                self.table_sprints.setItem(i, 2, QTableWidgetItem(f"{sprint['avg']:.0f}"))
                self.table_sprints.setItem(i, 3, QTableWidgetItem(f"{int(max_hr)}"))
            
            logger.info(f"Tabelle stream populate: {len(efforts)} efforts, {len(sprints)} sprints")
        except Exception as e:
            logger.error(f"Errore popolazione tabelle indoor: {e}", exc_info=True)
    
    def open_in_browser(self):
        """Apre il grafico nel browser predefinito"""
        if self.html_path:
            webbrowser.open("file://" + self.html_path)
            self.status_label.setText("📂 Grafico aperto nel browser")
            logger.info("Grafico indoor aperto nel browser")
        else:
            self.status_label.setText("❌ Nessun grafico disponibile")
