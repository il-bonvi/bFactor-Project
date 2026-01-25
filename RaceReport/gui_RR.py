"""Race Report GUI - Main application window"""

import sys
import os
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QMessageBox,
    QTabWidget, QScrollArea, QColorDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# Internal imports
from .naming_RR import compute_pdf_path_and_title
from .table_page_RR import build_table_figure
from .branding_RR import add_branding_to_figure, add_branding_to_other_pages
from .plots_RR import create_distance_figure, create_power_hr_figure, create_work_figure
from .cli_args_RR import parse_args

# Modular components
from .ui_builders_RR import create_dati_tab, create_layout_tab
from .data_handlers_RR import (
    import_csv as import_csv_handler,
    populate_data_table as populate_data_table_handler,
    on_table_double_click as on_table_double_click_handler,
    apply_data_changes as apply_data_changes_handler
)
from .progress_RR import ProgressContext


class RaceReportGUI(QMainWindow):
    """Main GUI class for Race Report Generator"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Race Report Generator")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data storage
        self.df = None
        self.raw_df = None
        self.csv_files = []
        self.single_csv = False
        self.csv_dir = None
        
        # Initialize args with defaults
        self.args = parse_args(args=[])
        self.bg_color = self.args.bg_color
        self.logo_file = None
        
        # Figures
        self.fig_table = None
        self.fig_distance = None
        self.fig_power = None
        self.fig_work = None
        
        # Cache for figure data (to avoid regeneration if data hasn't changed)
        self._fig_cache = {
            'table': None,
            'distance': None,
            'power': None,
            'work': None,
            'title': None,
            'bg_color': None
        }
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Top toolbar
        toolbar = QHBoxLayout()
        
        btn_import = QPushButton("Importa CSV")
        btn_import.clicked.connect(self.import_csv)
        toolbar.addWidget(btn_import)
        
        btn_import_logo = QPushButton("Importa Logo")
        btn_import_logo.clicked.connect(self.import_logo)
        toolbar.addWidget(btn_import_logo)
        
        toolbar.addStretch()
        main_layout.addLayout(toolbar)
        
        # Title section
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Titolo:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Titolo del report (lascia vuoto per automatico)")
        title_layout.addWidget(self.title_edit)
        main_layout.addLayout(title_layout)
        
        # Main tab widget
        self.main_tabs = QTabWidget()
        main_layout.addWidget(self.main_tabs)
        
        # Create DATI tab
        self.dati_tab = create_dati_tab(self)
        self.main_tabs.addTab(self.dati_tab, "DATI")
        
        # Create LAYOUT tab (contains layout controls + preview tabs on the right)
        self.layout_tab = create_layout_tab(self)
        self.main_tabs.addTab(self.layout_tab, "LAYOUT")
        
        # Export section
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.btn_export = QPushButton("Esporta PDF")
        self.btn_export.clicked.connect(self.export_pdf)
        self.btn_export.setEnabled(False)
        export_layout.addWidget(self.btn_export)
        
        main_layout.addLayout(export_layout)
    
    # ============================================================================
    # Data Handling Delegated Methods
    # ============================================================================
    
    def import_csv(self):
        """Delegate to data handler"""
        import_csv_handler(self)
    
    def populate_data_table(self):
        """Delegate to data handler"""
        populate_data_table_handler(self)
    
    def on_table_double_click(self, index):
        """Delegate to data handler"""
        on_table_double_click_handler(self, index)
    
    def apply_data_changes(self):
        """Delegate to data handler"""
        apply_data_changes_handler(self)
    
    # ============================================================================
    # Layout Controls
    # ============================================================================
    
    def select_bg_color(self):
        """Open color picker for background color"""
        color = QColorDialog.getColor(QColor(self.bg_color), self, "Seleziona Colore Sfondo")
        if color.isValid():
            self.bg_color = color.name()
            self.bg_color_label.setText(self.bg_color)
            self.bg_color_label.setStyleSheet(f"background-color: {self.bg_color}; padding: 5px;")
            self.invalidate_figure_cache()
            self.generate_visualizations()
    
    def apply_layout_changes(self):
        """Apply layout changes and regenerate visualizations"""
        if self.df is None:
            QMessageBox.warning(self, "Avviso", "Carica prima i dati CSV")
            return
        
        try:
            # Update args with new layout settings
            self.args.logo_frac = self.logo_frac_spin.value()
            self.args.logo_margin_right = self.logo_margin_right_spin.value()
            self.args.logo_margin_top = self.logo_margin_top_spin.value()
            self.args.other_logo_frac = self.other_logo_frac_spin.value()
            self.args.other_logo_margin_right = self.other_logo_margin_right_spin.value()
            self.args.other_logo_margin_top = self.other_logo_margin_top_spin.value()
            
            # Invalidate cache since layout changed
            self.invalidate_figure_cache()
            
            # Regenerate visualizations
            self.generate_visualizations()
            
            QMessageBox.information(self, "Successo", "Layout aggiornato!")
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore nell'applicare il layout:\n{str(e)}")
    
    # ============================================================================
    # Logo Management
    # ============================================================================
    
    def import_logo(self):
        """Import a custom logo file"""
        logo_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona un file logo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if not logo_path:
            return
        
        try:
            # Verify the file exists and is a valid image
            from PIL import Image
            img = Image.open(logo_path)
            img.verify()
            
            # Store the logo path (overwrites previous)
            self.logo_file = logo_path
            
            # Regenerate visualizations if data is loaded
            if self.df is not None:
                self.generate_visualizations()
                QMessageBox.information(
                    self,
                    "Successo",
                    f"Logo importato da:\n{logo_path}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Successo",
                    f"Logo importato da:\n{logo_path}\n\n(Carica i CSV per vederlo applicato)"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"File logo non valido:\n{str(e)}"
            )
    
    def invalidate_figure_cache(self):
        """Invalidate figure cache when data changes"""
        self._fig_cache = {
            'table': None,
            'distance': None,
            'power': None,
            'work': None,
            'title': None,
            'bg_color': None
        }
    
    # ============================================================================
    # Visualization & PDF Export
    # ============================================================================
    
    def generate_visualizations(self):
        """Generate all figures and display in tabs"""
        # Clear existing tabs
        self.preview_tabs.clear()
        
        # Close previous figures
        if self.fig_table:
            plt.close(self.fig_table)
        if self.fig_distance:
            plt.close(self.fig_distance)
        if self.fig_power:
            plt.close(self.fig_power)
        if self.fig_work:
            plt.close(self.fig_work)
        
        # Get custom title
        custom_title = self.title_edit.text().strip() or None
        args_with_title = type('Args', (), {**vars(self.args), 'custom_title': custom_title})()
        
        # Table page
        self.fig_table, df_table = build_table_figure(
            self.df, self.raw_df, args_with_title, self.logo_file, self.bg_color
        )
        add_branding_to_figure(
            self.fig_table,
            logo_path=self.logo_file,
            bg_color=self.bg_color,
            logo_w_frac=self.args.logo_frac,
            margin_right=self.args.logo_margin_right,
            margin_top=self.args.logo_margin_top
        )
        self.add_figure_tab("Tabella", self.fig_table)
        
        # Distance figure
        self.fig_distance = create_distance_figure(self.df, self.bg_color, self.logo_file)
        if self.fig_distance:
            add_branding_to_other_pages(
                self.fig_distance,
                logo_path=self.logo_file,
                bg_color=self.bg_color,
                logo_w_frac=self.args.other_logo_frac,
                margin_right=self.args.other_logo_margin_right,
                margin_top=self.args.other_logo_margin_top
            )
            self.add_figure_tab("Distanza e Tempo", self.fig_distance)
        
        # Power/HR figure
        self.fig_power = create_power_hr_figure(self.df, self.bg_color, self.logo_file)
        if self.fig_power:
            add_branding_to_other_pages(
                self.fig_power,
                logo_path=self.logo_file,
                bg_color=self.bg_color,
                logo_w_frac=self.args.other_logo_frac,
                margin_right=self.args.other_logo_margin_right,
                margin_top=self.args.other_logo_margin_top
            )
            self.add_figure_tab("Potenza e FC", self.fig_power)
        
        # Work figure
        self.fig_work = create_work_figure(self.df, self.bg_color, self.logo_file)
        if self.fig_work:
            add_branding_to_other_pages(
                self.fig_work,
                logo_path=self.logo_file,
                bg_color=self.bg_color,
                logo_w_frac=self.args.other_logo_frac,
                margin_right=self.args.other_logo_margin_right,
                margin_top=self.args.other_logo_margin_top
            )
            self.add_figure_tab("Lavoro", self.fig_work)
    
    def add_figure_tab(self, title, figure):
        """Add a matplotlib figure as a tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        canvas = FigureCanvas(figure)
        scroll.setWidget(canvas)
        
        self.preview_tabs.addTab(scroll, title)
    
    def export_pdf(self):
        """Export to PDF with custom location"""
        if self.df is None:
            QMessageBox.warning(self, "Avviso", "Nessun dato caricato")
            return
        
        # Get save location
        default_name, _ = compute_pdf_path_and_title(
            self.csv_dir, self.csv_files, self.single_csv,
            self.df, self.raw_df, custom_title=self.title_edit.text().strip() or None
        )
        
        pdf_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva PDF",
            os.path.join(self.csv_dir, default_name),
            "PDF Files (*.pdf)"
        )
        
        if not pdf_path:
            return
        
        try:
            with ProgressContext(self, "Esportazione PDF...", 100) as progress:
                # Regenerate with current title
                custom_title = self.title_edit.text().strip() or None
                args_with_title = type('Args', (), {**vars(self.args), 'custom_title': custom_title})()
                
                progress.set_label("Generando tabella...")
                progress.set_value(10)
                
                with PdfPages(pdf_path) as pdf:
                    # Table page
                    fig_table, _ = build_table_figure(
                        self.df, self.raw_df, args_with_title, self.logo_file, self.bg_color
                    )
                    add_branding_to_figure(
                        fig_table,
                        logo_path=self.logo_file,
                        bg_color=self.bg_color,
                        logo_w_frac=self.args.logo_frac,
                        margin_right=self.args.logo_margin_right,
                        margin_top=self.args.logo_margin_top
                    )
                    pdf.savefig(fig_table)
                    plt.close(fig_table)
                    
                    progress.set_value(30)
                    progress.set_label("Generando grafici...")
                    
                    # Distance
                    fig_dist = create_distance_figure(self.df, self.bg_color, self.logo_file)
                    if fig_dist:
                        add_branding_to_other_pages(
                            fig_dist,
                            logo_path=self.logo_file,
                            bg_color=self.bg_color,
                            logo_w_frac=self.args.other_logo_frac,
                            margin_right=self.args.other_logo_margin_right,
                            margin_top=self.args.other_logo_margin_top
                        )
                        pdf.savefig(fig_dist)
                        plt.close(fig_dist)
                    
                    progress.set_value(50)
                    
                    # Power
                    fig_pwr = create_power_hr_figure(self.df, self.bg_color, self.logo_file)
                    if fig_pwr:
                        add_branding_to_other_pages(
                            fig_pwr,
                            logo_path=self.logo_file,
                            bg_color=self.bg_color,
                            logo_w_frac=self.args.other_logo_frac,
                            margin_right=self.args.other_logo_margin_right,
                            margin_top=self.args.other_logo_margin_top
                        )
                        pdf.savefig(fig_pwr)
                        plt.close(fig_pwr)
                    
                    progress.set_value(75)
                    
                    # Work
                    fig_wrk = create_work_figure(self.df, self.bg_color, self.logo_file)
                    if fig_wrk:
                        add_branding_to_other_pages(
                            fig_wrk,
                            logo_path=self.logo_file,
                            bg_color=self.bg_color,
                            logo_w_frac=self.args.other_logo_frac,
                            margin_right=self.args.other_logo_margin_right,
                            margin_top=self.args.other_logo_margin_top
                        )
                        pdf.savefig(fig_wrk)
                        plt.close(fig_wrk)
                    
                    progress.set_value(95)
            
            # Dialog con due opzioni: OK e Apri PDF
            msg = QMessageBox(self)
            msg.setWindowTitle("Successo")
            msg.setText(f"PDF esportato in:\n{pdf_path}")
            btn_ok = msg.addButton("OK", QMessageBox.AcceptRole)
            btn_open = msg.addButton("Apri PDF", QMessageBox.ActionRole)
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            if msg.clickedButton() == btn_open:
                try:
                    import platform
                    if platform.system() == "Windows":
                        os.startfile(pdf_path)
                    elif platform.system() == "Darwin":
                        os.system(f"open '{pdf_path}'")
                    else:
                        os.system(f"xdg-open '{pdf_path}'")
                except Exception as e:
                    print(f"Impossibile aprire automaticamente il PDF: {e}")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore durante l'esportazione:\n{str(e)}"
            )


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = RaceReportGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
