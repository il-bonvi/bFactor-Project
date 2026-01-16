"""
GUI INTERFACE - Interfaccia grafica, temi e styling
Contiene: EffortAnalyzer class, TEMI, CSS styling, gestione UI
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QFileDialog, QLineEdit, QHBoxLayout, QMessageBox, QFrame,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QUrl, QBuffer, QIODevice, QRect
from PySide6.QtGui import QPixmap
import tempfile
import webbrowser
import base64
import sys
from pathlib import Path

from .core_engine import format_time_hhmmss
from .export_manager import create_pdf_report, plot_unified_html

# Aggiungi root al path per import shared
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from shared.styles import TEMI, get_style


# =====================
# GUI PRINCIPALE
# =====================
class EffortAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EFFORT ANALYZER")
        self.setMinimumSize(1280, 850)
        self.setStyleSheet(get_style("Forest Green"))

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(300)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(25, 25, 25, 25)
        side_layout.setSpacing(15)

        title = QLabel("bFactor Engine")
        title.setObjectName("Header")
        side_layout.addWidget(title)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(list(TEMI.keys()))
        self.theme_selector.currentTextChanged.connect(self.apply_selected_theme)
        side_layout.addWidget(self.theme_selector)

        # Profilo Atleta
        side_layout.addWidget(QLabel("PROFILO ATLETA", objectName="SectionTitle"))
        grid_athlete = QGridLayout()
        grid_athlete.setSpacing(10)
        grid_athlete.addWidget(QLabel("FTP (W)"), 0, 0)
        self.ftp_input = QLineEdit("280")
        grid_athlete.addWidget(self.ftp_input, 0, 1)
        grid_athlete.addWidget(QLabel("Peso (kg)"), 1, 0)
        self.weight_input = QLineEdit("70")
        grid_athlete.addWidget(self.weight_input, 1, 1)
        side_layout.addLayout(grid_athlete)

        # Efforts
        side_layout.addWidget(QLabel("EFFORTS", objectName="SectionTitle"))
        grid_eff = QGridLayout()
        grid_eff.setSpacing(10)
        grid_eff.addWidget(QLabel("Finestra (s)"), 0, 0)
        self.window_input = QLineEdit("60")
        grid_eff.addWidget(self.window_input, 0, 1)
        
        grid_eff.addWidget(QLabel("Merge (%)"), 1, 0)
        self.merge_input = QLineEdit("15")
        grid_eff.addWidget(self.merge_input, 1, 1)
        
        grid_eff.addWidget(QLabel("Min FTP (%)"), 2, 0)
        self.min_ftp_input = QLineEdit("100")
        grid_eff.addWidget(self.min_ftp_input, 2, 1)

        grid_eff.addWidget(QLabel("Trim (s/%)"), 3, 0)
        hbox_trim = QHBoxLayout()
        self.trim_win_input = QLineEdit("10")
        self.trim_low_input = QLineEdit("85")
        hbox_trim.addWidget(self.trim_win_input)
        hbox_trim.addWidget(self.trim_low_input)
        grid_eff.addLayout(hbox_trim, 3, 1)

        grid_eff.addWidget(QLabel("Ext (s/%)"), 4, 0)
        hbox_ext = QHBoxLayout()
        self.extend_win_input = QLineEdit("15")
        self.extend_low_input = QLineEdit("80")
        hbox_ext.addWidget(self.extend_win_input)
        hbox_ext.addWidget(self.extend_low_input)
        grid_eff.addLayout(hbox_ext, 4, 1)
        
        side_layout.addLayout(grid_eff)

        # Sprints
        side_layout.addWidget(QLabel("SPRINTS", objectName="SectionTitle"))
        grid_spr = QGridLayout()
        grid_spr.setSpacing(10)
        grid_spr.addWidget(QLabel("Finestra (s)"), 0, 0)
        self.sprint_window_input = QLineEdit("5")
        grid_spr.addWidget(self.sprint_window_input, 0, 1)
        
        grid_spr.addWidget(QLabel("Potenza Min"), 1, 0)
        self.min_sprint_power_input = QLineEdit("600")
        grid_spr.addWidget(self.min_sprint_power_input, 1, 1)
        side_layout.addLayout(grid_spr)

        # Pulsante Analizza
        self.btn_analyze = QPushButton("Analizza")
        self.btn_analyze.clicked.connect(self.analyze)
        self.btn_analyze.setEnabled(False)
        side_layout.addWidget(self.btn_analyze)

        side_layout.addStretch()

        self.btn_load = QPushButton("Carica FIT")
        self.btn_load.clicked.connect(self.select_file)
        side_layout.addWidget(self.btn_load)

        main_layout.addWidget(sidebar)

        # --- AREA CONTENUTO ---
        content_area = QVBoxLayout()
        content_area.setContentsMargins(15, 15, 15, 15)
        content_area.setSpacing(15)

        top_bar = QHBoxLayout()
        self.status_label = QLabel("Pronto per l'analisi")
        top_bar.addWidget(self.status_label)
        top_bar.addStretch()
        
        self.btn_browser = QPushButton("Apri nel Browser")
        self.btn_browser.clicked.connect(self.open_in_browser)
        self.btn_browser.setEnabled(False)
        top_bar.addWidget(self.btn_browser)
        
        self.btn_pdf = QPushButton("Esporta PDF Report")
        self.btn_pdf.clicked.connect(self.export_pdf_action)
        self.btn_pdf.setEnabled(False)
        top_bar.addWidget(self.btn_pdf)
        content_area.addLayout(top_bar)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background: #0f172a; border-radius: 8px;")
        content_area.addWidget(self.web_view, stretch=3)

        tables_container = QHBoxLayout()
        tables_container.setSpacing(15)

        self.table_efforts = QTableWidget()
        self.table_efforts.setColumnCount(5)
        self.table_efforts.setHorizontalHeaderLabels(["Inizio", "Durata", "Watt", "W/kg", "VAM"])
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
        
        content_area.addLayout(tables_container, stretch=1)
        main_layout.addLayout(content_area)

        self.file_path = None
        self.html_path = None
        self.current_df = None
        self.current_efforts = None
        self.current_sprints = None
        self.current_params_str = ""

    def apply_selected_theme(self, tema_nome):
        """Cambia il tema dell'interfaccia"""
        self.setStyleSheet(get_style(tema_nome))
        self.status_label.setText(f"Tema: {tema_nome}")

    def select_file(self):
        """Seleziona un file FIT da analizzare"""
        path, _ = QFileDialog.getOpenFileName(self, "Seleziona FIT", "", "FIT Files (*.fit)")
        if path:
            self.file_path = path
            self.btn_analyze.setEnabled(True)
            self.analyze()

    def analyze(self):
        """Esegue l'analisi completa"""
        if not self.file_path:
            self.status_label.setText("Seleziona prima un file FIT")
            return
        
        try:
            from .core_engine import parse_fit, create_efforts, merge_extend, split_included, detect_sprints
            
            self.status_label.setText("Analisi in corso...")
            QApplication.processEvents()
            
            ftp = float(self.ftp_input.text())
            weight = float(self.weight_input.text())
            window_sec = int(self.window_input.text())
            merge_pct = float(self.merge_input.text())
            min_ftp_pct = float(self.min_ftp_input.text())
            trim_win = int(self.trim_win_input.text())
            trim_low = float(self.trim_low_input.text())
            extend_win = int(self.extend_win_input.text())
            extend_low = float(self.extend_low_input.text())
            sprint_window_sec = int(self.sprint_window_input.text())
            min_sprint_power = float(self.min_sprint_power_input.text())
            
            df = parse_fit(self.file_path)
            efforts = create_efforts(df, ftp, window_sec, merge_pct, min_ftp_pct, trim_win, trim_low)
            efforts = merge_extend(df, efforts, merge_pct, trim_win, trim_low, extend_win, extend_low)
            efforts = split_included(df, efforts)
            sprints = detect_sprints(df, min_sprint_power, sprint_window_sec, merge_gap_sec=1)

            if len(efforts) == 0 and len(sprints) == 0:
                self.status_label.setText("Nessun effort o sprint trovato")
                return
            
            html = plot_unified_html(df, efforts, sprints, ftp, weight, 
                                    window_sec, merge_pct, min_ftp_pct, 
                                    trim_win, trim_low, extend_win, extend_low,
                                    sprint_window_sec, min_sprint_power)
            
            self.current_df = df
            self.current_efforts = efforts
            self.current_sprints = sprints
            self.current_params_str = (
                f"Efforts: Win {window_sec}s, Mrg {merge_pct}% | "
                f"Sprints: Win {sprint_window_sec}s, >{min_sprint_power}W"
            )

            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
            temp_file.write(html)
            temp_file.close()
            self.html_path = temp_file.name
            
            self.web_view.setUrl(QUrl.fromLocalFile(temp_file.name))
            
            self.btn_pdf.setEnabled(True)
            self.btn_browser.setEnabled(True)
            self.status_label.setText(f"✅ {len(efforts)} efforts + {len(sprints)} sprints")
            
            # Popola tabelle
            self.populate_tables(df, efforts, sprints, ftp, weight)
            
        except Exception as e:
            self.status_label.setText(f"Errore: {str(e)}")
            import traceback
            traceback.print_exc()

    def populate_tables(self, df, efforts, sprints, ftp, weight):
        """Popola le tabelle con i dati"""
        power = df["power"].values
        time_sec = df["time_sec"].values
        alt = df["altitude"].values
        dist = df["distance"].values
        hr = df["heartrate"].values
        grade = df["grade"].values

        # Tabella Efforts
        self.table_efforts.setRowCount(len(efforts))
        for i, (s, e, avg) in enumerate(efforts):
            seg_alt = alt[s:e]
            seg_time = time_sec[s:e]
            seg_dist = dist[s:e]
            
            duration = int(seg_time[-1] - seg_time[0] + 1)
            elevation_gain = seg_alt[-1] - seg_alt[0]
            dist_tot = seg_dist[-1] - seg_dist[0]
            vam = elevation_gain / (duration / 3600) if duration > 0 else 0
            w_kg = avg / weight if weight > 0 else 0

            self.table_efforts.setItem(i, 0, QTableWidgetItem(format_time_hhmmss(seg_time[0])))
            self.table_efforts.setItem(i, 1, QTableWidgetItem(f"{duration}s"))
            self.table_efforts.setItem(i, 2, QTableWidgetItem(f"{avg:.0f}"))
            self.table_efforts.setItem(i, 3, QTableWidgetItem(f"{w_kg:.2f}"))
            self.table_efforts.setItem(i, 4, QTableWidgetItem(f"{vam:.0f}"))

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

    def open_in_browser(self):
        """Apre il grafico HTML nel browser predefinito"""
        if self.html_path:
            webbrowser.open("file://" + self.html_path)
            self.status_label.setText("📂 Grafico aperto nel browser")
        else:
            self.status_label.setText("Nessun grafico disponibile")

    def export_pdf_action(self):
        """Esporta il report in PDF"""
        if self.current_df is None:
            return

        pdf_path, _ = QFileDialog.getSaveFileName(self, "Salva Report PDF", "", "PDF Files (*.pdf)")
        if pdf_path:
            self.status_label.setText("Cattura immagine...")
            QApplication.processEvents()

            left_margin = 1
            top_margin = 35
            right_margin = 130
            bottom_margin = 1

            graph_width = self.web_view.width() - left_margin - right_margin
            graph_height = self.web_view.height() - top_margin - bottom_margin

            rect = QRect(left_margin, top_margin, graph_width, graph_height)
            pixmap = self.web_view.grab(rect)
            
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            pixmap.save(buffer, "PNG")
            b64_data = base64.b64encode(buffer.data().data()).decode()

            ftp = float(self.ftp_input.text())
            weight = float(self.weight_input.text())
            
            success = create_pdf_report(
                self.current_df, 
                self.current_efforts, 
                self.current_sprints, 
                b64_data,
                ftp, 
                weight, 
                pdf_path,
                self.current_params_str
            )
            
            if success:
                self.status_label.setText(f"✅ PDF salvato!")
                QMessageBox.information(self, "Successo", "PDF generato!")
                webbrowser.open(pdf_path)
            else:
                self.status_label.setText("❌ Errore PDF")
                QMessageBox.critical(self, "Errore", "Impossibile generare il PDF.")
