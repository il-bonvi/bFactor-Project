# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
Omniselector GUI - Interfaccia grafica (pura presentazione)
"""
import numpy as np
import pandas as pd

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QFileDialog, QDialog, QTabWidget)
from PySide6.QtCore import Qt

# Import dei moduli separati
from .core_omniselector import (
    calculate_omnipd_model, 
    load_data_from_file,
    convert_time_minutes_to_seconds,
    apply_data_filters
)
from .widgets_omniselector import CSVColumnDialog, TimeWindowsDialog
from .plotting_omniselector import (
    format_plot, plot_ompd_curve, plot_residuals, plot_weff,
    draw_time_windows, plot_raw_points
)
from .events_omniselector import OmniSelectorEventHandler
from .ui_builder_omniselector import (
    create_sidebar_widgets, create_ompd_tab, create_residuals_tab,
    create_weff_tab, create_theme_selector, apply_widget_styles
)

try:
    from shared.styles import get_style, TEMI
except ImportError:
    from shared.styles import get_style
    TEMI = {"Forest Green": {}}
    def get_style(x):
        return "background-color: #061f17; color: white;"


class OmniSelectorAnalyzer(QWidget):
    def __init__(self, theme=None):
        super().__init__()
        self.setWindowTitle("Omniselector - Analyzer")
        self.setMinimumSize(1200, 800)
        if theme is None:
            theme = "Forest Green"
        self.current_theme = theme
        self.setStyleSheet(get_style(theme))
        
        self.params = None
        self.x_data = None
        self.y_data = None
        self.residuals = None
        self.RMSE = None
        self.MAE = None
        self.raw_x_data = None
        self.raw_y_data = None
        self.time_windows = [
            (120, 240),
            (240, 480),
            (480, 900),
            (900, 1800),
            (1800, 2700),
            (2700, 4500),
        ]
        self.percentile_min = 0.0
        self.values_per_window = 1
        self.sprint_value = 10.0  # default sprint value in seconds
        self.selected_mask = None
        
        # Variabili per hover
        self.hover_ann_points = None
        self.ann_curve = None
        self.cursor_point = None
        self.hover_ann_residuals = None
        self.marker_line = None
        self.marker_text = None
        
        # Connection IDs per eventi
        self.cid_ompd = None
        self.cid_residuals = None
        self.cid_weff = None
        
        # Event handler
        self.event_handler = OmniSelectorEventHandler(self)
        
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)

        # Crea sidebar con tutti i widget
        create_sidebar_widgets(self)

        # Area destra con tab
        right_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        
        # Crea i tre tab
        create_ompd_tab(self)
        create_residuals_tab(self)
        create_weff_tab(self)

        # Assembla il layout
        self.main_layout.addLayout(self.sidebar, 1)
        self.main_layout.addLayout(right_layout, 3)
        
        # Theme selector in alto a destra
        theme_layout = create_theme_selector(self)
        right_layout.addLayout(theme_layout)
        right_layout.addWidget(self.tab_widget)

        # Applica gli stili iniziali
        apply_widget_styles(self)

    def apply_selected_theme(self, tema_nome):
        """Cambia il tema dell'interfaccia e aggiorna grafici"""
        self.current_theme = tema_nome
        self.setStyleSheet(get_style(tema_nome))
        
        # Aggiorna i colori di background delle figure matplotlib
        colors = TEMI.get(tema_nome, TEMI["Forest Green"])
        bg_color = colors.get("bg", "#061f17")
        
        self.figure1.set_facecolor(bg_color)
        self.figure2.set_facecolor(bg_color)
        self.figure3.set_facecolor(bg_color)
        
        # Aggiorna gli stili specifici dei widget
        apply_widget_styles(self)
        
        # Ridisegna i grafici con il nuovo tema
        self.update_ompd_plot()
        self.update_residuals_plot()
        self.update_weff_plot()
 



    def open_time_windows_dialog(self):
        dlg = TimeWindowsDialog(self, defaults=self.time_windows)
        if dlg.exec() == QDialog.Accepted:
            try:
                self.time_windows = dlg.get_windows()
            except Exception as e:
                QMessageBox.critical(self, "Errore finestre", str(e))

    def _update_filter_params(self):
        """Aggiorna i parametri di filtraggio dall'UI"""
        try:
            self.percentile_min = float(self.percentile_input.text().strip() or 0)
        except ValueError:
            self.percentile_min = 0.0
        try:
            self.values_per_window = int(self.count_input.text().strip() or 1)
        except ValueError:
            self.values_per_window = 1
        try:
            self.sprint_value = float(self.sprint_input.text().strip() or 10)
        except ValueError:
            self.sprint_value = 10.0

    def _apply_filters(self, x_data, y_data):
        """Applica i filtri usando la funzione del core module"""
        self._update_filter_params()
        return apply_data_filters(
            x_data, y_data, 
            self.time_windows, 
            self.percentile_min, 
            self.values_per_window, 
            self.sprint_value,
            self.params
        )

    def _draw_time_windows(self, ax):
        """Disegna le finestre temporali sul grafico"""
        draw_time_windows(ax, self.time_windows, self.current_theme)

    def _plot_raw_points(self, ax, overlay_selected=True):
        """Disegna i punti raw sul grafico"""
        plot_raw_points(ax, self.raw_x_data, self.raw_y_data, 
                       self.selected_mask, overlay_selected, self.current_theme)

    def convert_time(self, text):
        try:
            seconds = convert_time_minutes_to_seconds(text)
            self.sec_out.setText(f"= {seconds} s")
        except:
            self.sec_out.setText("= 0 s")

    def import_file(self):
        """Importa dati da file CSV o Excel e li carica nelle celle senza filtrare."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona file",
            "",
            "Excel/CSV files (*.xlsm *.xlsx *.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Se CSV, chiedi quale colonna usare
            time_col_idx = 0
            power_col_idx = 1
            
            if file_path.lower().endswith('.csv'):
                df_csv = pd.read_csv(file_path, sep=None, engine="python")
                col_dialog = CSVColumnDialog(self, df_csv.columns.tolist())
                if col_dialog.exec() == QDialog.Accepted:
                    time_col_idx, power_col_idx = col_dialog.get_selection()
                else:
                    return
            
            # Carica dati dal file e popolali nelle celle
            self.raw_x_data, self.raw_y_data = load_data_from_file(
                file_path, time_col_idx, power_col_idx
            )
            self.params = None
            self.residuals = None
            self.RMSE = None
            self.MAE = None
            self.selected_mask = None
            self.x_data = None
            self.y_data = None
            self.update_ompd_plot()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'importazione:\n{str(e)}")
    
    def _calculate_model(self):
        """Calcola il modello Omniselector usando la logica core"""
        try:
            if self.x_data is None or len(self.x_data) < 4:
                raise ValueError("Dati insufficienti")
            
            # Usa la logica di calcolo dal core
            result = calculate_omnipd_model(self.x_data, self.y_data)
            
            # Estrai i risultati
            self.params = result['params']
            self.residuals = result['residuals']
            self.RMSE = result['RMSE']
            self.MAE = result['MAE']
            
            CP = result['CP']
            W_prime = result['W_prime']
            Pmax = result['Pmax']
            A = result['A']

            # Aggiornamento Label
            self.lbl_cp.setText(f"CP: {CP:.0f} W")
            self.lbl_wprime.setText(f"W': {W_prime:.0f} J")
            self.lbl_pmax.setText(f"Pmax: {Pmax:.0f} W")
            self.lbl_a.setText(f"A: {A:.2f}")
            self.lbl_rmse.setText(f"RMSE: {self.RMSE:.2f} W")
            self.lbl_mae.setText(f"MAE: {self.MAE:.2f} W")

            # Aggiornamento Grafici
            self.update_ompd_plot()
            self.update_residuals_plot()
            self.update_weff_plot()

        except Exception as e:
            QMessageBox.critical(self, "Errore Calcolo", str(e))

    def run_calculation(self):
        # Pulisci vecchie connessioni di hover
        if self.cid_ompd is not None:
            self.canvas1.mpl_disconnect(self.cid_ompd)
            self.cid_ompd = None
        if self.cid_residuals is not None:
            self.canvas2.mpl_disconnect(self.cid_residuals)
            self.cid_residuals = None
        
        try:
            # Usa i dati raw già caricati dal CSV
            if self.raw_x_data is None or self.raw_y_data is None:
                raise ValueError("Carica prima un file CSV")
            
            self.x_data, self.y_data, self.selected_mask = self._apply_filters(self.raw_x_data, self.raw_y_data)
            
            # Calcola il modello
            self._calculate_model()

        except Exception as e:
            QMessageBox.critical(self, "Errore Calcolo", str(e))

    def update_ompd_plot(self):
        """Aggiorna il grafico OmPD principale"""
        if self.params is None:
            self.ax1.clear()
            format_plot(self.ax1, self.current_theme)
            self._draw_time_windows(self.ax1)
            self._plot_raw_points(self.ax1, overlay_selected=False)
            self.ax1.set_title("Omniselector Curve", color=TEMI.get(self.current_theme, TEMI["Forest Green"]).get("text", "#f1f5f9"), fontsize=14)
            self.canvas1.draw()
            return
        plot_ompd_curve(self.ax1, self.x_data, self.y_data, self.params, self.current_theme)
        self._draw_time_windows(self.ax1)
        self._plot_raw_points(self.ax1, overlay_selected=True)
        self.canvas1.draw()
        # Connetti event hover al grafico OmPD
        self.event_handler.connect_ompd_hover()

    def update_residuals_plot(self):
        """Aggiorna il grafico dei residui"""
        if self.residuals is None:
            self.ax2.clear()
            format_plot(self.ax2, self.current_theme)
            self.ax2.set_title("Omniselector Residuals", color=TEMI.get(self.current_theme, TEMI["Forest Green"]).get("text", "#f1f5f9"), fontsize=14)
            self.canvas2.draw()
            return
        plot_residuals(self.ax2, self.x_data, self.residuals, self.RMSE, self.MAE, self.current_theme)
        self.canvas2.draw()
        # Connetti event hover al grafico residui
        self.event_handler.connect_residuals_hover()

    def update_weff_plot(self):
        """Aggiorna il grafico W'eff"""
        if self.params is None:
            self.ax3.clear()
            format_plot(self.ax3, self.current_theme)
            self.ax3.set_title("OmPD Effective W'", color=TEMI.get(self.current_theme, TEMI["Forest Green"]).get("text", "#f1f5f9"), fontsize=14)
            self.canvas3.draw()
            return
        plot_weff(self.ax3, self.params, self.params[1], self.current_theme)
        self.canvas3.draw()
