import sys
import os
import pandas as pd
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QMessageBox,
    QTabWidget, QScrollArea
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

from .naming_RR import compute_pdf_path_and_title
from .table_page_RR import build_table_figure
from .branding_RR import add_branding_to_figure, add_branding_to_other_pages
from .plots_RR import create_distance_figure, create_power_hr_figure, create_work_figure
from .cli_args_RR import parse_args
from .validation_RR import valid_rpe, valid_feel, validate_rpe_column, validate_feel_column
from .transformations_RR import (
    remove_emoji, append_initials_to_name, normalize_moving_time, format_seconds,
    get_75_status, handle_error_flags, format_numeric_columns
)


class RaceReportGUI(QMainWindow):
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
        self.args = None
        self.bg_color = '#d9e8dd'
        self.logo_file = None
        
        # Figures
        self.fig_table = None
        self.fig_distance = None
        self.fig_power = None
        self.fig_work = None
        
        self.init_ui()
        
    def init_ui(self):
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
        
        # Tab widget for viewing
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Export section
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        self.btn_export = QPushButton("Esporta PDF")
        self.btn_export.clicked.connect(self.export_pdf)
        self.btn_export.setEnabled(False)
        export_layout.addWidget(self.btn_export)
        
        main_layout.addLayout(export_layout)
        
    def import_csv(self):
        """Import one or more CSV files selected by user"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleziona uno o più file CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not files:
            return
            
        try:
            # Determine common directory
            self.csv_dir = os.path.dirname(files[0])
            
            # Parse args with defaults
            self.args = parse_args(args=[])
            self.bg_color = self.args.bg_color
            
            # Cerca sempre il logo nella cartella del modulo Python
            self.logo_file = os.path.join(os.path.dirname(__file__), 'LOGO.png')
            
            # Read selected CSV files with same logic as read_and_prepare
            self.csv_files = [os.path.basename(f) for f in files]
            self.single_csv = len(self.csv_files) == 1
            
            dfs = []
            for f in files:
                try:
                    dfi = pd.read_csv(f)
                    basename = os.path.splitext(os.path.basename(f))[0]
                    
                    if self.single_csv:
                        initials = ''
                    else:
                        # Remove year and create initials from name
                        basename_no_year = re.sub(r"\s*\d{4}\s*$", "", basename).strip()
                        parts = [p for p in re.split(r"\s+", basename_no_year) if p]
                        initials = ''.join([p[0].upper() for p in parts if p]) if parts else ''
                    
                    dfi['AthleteInit'] = initials
                    dfs.append(dfi)
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Avviso",
                        f"Impossibile leggere '{os.path.basename(f)}': {e}"
                    )
            
            if not dfs:
                QMessageBox.critical(self, "Errore", "Nessun CSV valido letto")
                return
            
            # Concatenate dataframes
            self.raw_df = pd.concat(dfs, ignore_index=True, sort=False)
            self.df = self.raw_df.copy()
            
            # Apply data cleaning (same as data_prep.py)
            self.df = self.df.drop(columns=['id'], errors='ignore')
            if 'Weight' in self.df.columns:
                self.df = self.df.drop(columns=['Weight'])
            
            # Validate RPE and Feel columns
            self.df = validate_rpe_column(self.df)
            self.df = validate_feel_column(self.df)
            
            # Remove emojis from Name and append initials
            if 'Name' in self.df.columns:
                self.df['Name'] = self.df['Name'].apply(remove_emoji)
                if 'AthleteInit' in self.df.columns:
                    self.df['Name'] = [append_initials_to_name(n, i) for n, i in zip(self.df['Name'], self.df['AthleteInit'])]
            
            # Get 75% status
            self.df['75%'] = self.df.apply(get_75_status, axis=1)
            
            # Conversions and formatting
            if 'Distance' in self.df.columns:
                self.df['Distance'] = (self.df['Distance'] / 1000).round(1)
            if 'Climbing' in self.df.columns:
                self.df['Climbing'] = self.df['Climbing'].fillna(0).astype(int)
            if 'Moving Time' in self.df.columns:
                self.df['Moving Time'] = self.df['Moving Time'].apply(normalize_moving_time)
            if 'Avg Speed' in self.df.columns:
                self.df['Avg Speed'] = (self.df['Avg Speed'] * 3.6).round(1)
            if 'Intensity' in self.df.columns:
                self.df = self.df.drop(columns=['Intensity'])
            if 'Variability' in self.df.columns:
                self.df = self.df.drop(columns=['Variability'])
            if 'Work' in self.df.columns:
                self.df['Work'] = (self.df['Work'] / 1000).round(0)
            if 'Work >FTP' in self.df.columns:
                self.df = self.df.rename(columns={'Work >FTP': 'Work >CP'})
                self.df['Work >CP'] = (self.df['Work >CP'] / 1000).round(0)
            if 'All Work>CP' in self.df.columns:
                self.df['All Work>CP'] = self.df['All Work>CP'].round(0)
            if 'Time Above CP' in self.df.columns:
                self.df['Time Above CP'] = self.df['Time Above CP'].apply(format_seconds)
            if 'Avg Above CP' in self.df.columns:
                self.df['Avg Above CP'] = self.df['Avg Above CP'].round(0)
            if 'kJ/h/kg' in self.df.columns:
                self.df['kJ/h/kg'] = self.df['kJ/h/kg'].round(1)
            if 'kJ/h/kg>CP' in self.df.columns:
                self.df['kJ/h/kg>CP'] = self.df['kJ/h/kg>CP'].round(1)
            
            # Handle error flags (#errpwr, #errhr)
            self.df = handle_error_flags(self.df)
            
            # Sort and format Date
            if 'Date' in self.df.columns:
                parsed_dates = pd.to_datetime(self.raw_df['Date'], errors='coerce')
                date_only = parsed_dates.dt.normalize()
                if 'AthleteInit' not in self.df.columns:
                    self.df['AthleteInit'] = ''
                sort_frame = pd.DataFrame({
                    '_DateOnly': date_only,
                    '_AthleteInit': self.raw_df.get('AthleteInit', pd.Series(['']*len(self.raw_df)))
                })
                sort_frame['_AthleteInit'] = sort_frame['_AthleteInit'].fillna('').astype(str).str.upper()
                self.df = self.df.reset_index(drop=True)
                sort_frame = sort_frame.reset_index(drop=True)
                self.df = pd.concat([self.df, sort_frame], axis=1)
                self.df = self.df.sort_values(['_DateOnly', '_AthleteInit']).drop(columns=['_DateOnly', '_AthleteInit'])
                self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce').dt.strftime('%d/%m')
            
            # Compute default title (same logic as naming.py)
            pdf_path, title_text = compute_pdf_path_and_title(
                self.csv_dir, self.csv_files, self.single_csv,
                self.df, self.raw_df, custom_title=None
            )
            
            if title_text:
                self.title_edit.setText(title_text)
            
            # Generate visualizations
            self.generate_visualizations()
            
            # Enable export
            self.btn_export.setEnabled(True)
            
            QMessageBox.information(
                self,
                "Successo",
                f"Caricati {len(self.csv_files)} file CSV con {len(self.df)} gare"
            )
            
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self,
                "Errore",
                f"Errore durante l'importazione:\n{str(e)}\n\n{traceback.format_exc()}"
            )
    
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
    
    def generate_visualizations(self):
        """Generate all figures and display in tabs"""
        # Clear existing tabs
        self.tabs.clear()
        
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
        
        self.tabs.addTab(scroll, title)
    
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
            # Regenerate with current title
            custom_title = self.title_edit.text().strip() or None
            args_with_title = type('Args', (), {**vars(self.args), 'custom_title': custom_title})()
            
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
    app = QApplication(sys.argv)
    window = RaceReportGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
