"""Data handling and processing for Race Report GUI"""

import os
import re
import pandas as pd
from PySide6.QtWidgets import QMessageBox, QTableWidgetItem, QDialog
from PySide6.QtCore import Qt

from .naming_RR import compute_pdf_path_and_title
from .validation_RR import validate_rpe_column, validate_feel_column
from .transformations_RR import (
    remove_emoji, append_initials_to_name, normalize_moving_time, 
    format_seconds, get_75_status, handle_error_flags
)
from .dialogs_RR import TagEditorDialog
from .ui_builders_RR import reorder_and_filter_columns
from .progress_RR import ProgressContext


def import_csv(gui_instance):
    """Import CSV files and populate dataframes"""
    from PySide6.QtWidgets import QFileDialog
    
    files, _ = QFileDialog.getOpenFileNames(
        gui_instance,
        "Seleziona uno o più file CSV",
        "",
        "CSV Files (*.csv);;All Files (*)"
    )
    
    if not files:
        return
        
    try:
        with ProgressContext(gui_instance, "Caricamento CSV...", 100) as progress:
            # Step 1: Determine common directory
            progress.set_label("Preparazione...")
            progress.set_value(5)
            
            gui_instance.csv_dir = os.path.dirname(files[0])
            gui_instance.logo_file = os.path.join(os.path.dirname(__file__), 'LOGO.png')
            gui_instance.csv_files = [os.path.basename(f) for f in files]
            gui_instance.single_csv = len(gui_instance.csv_files) == 1
            
            # Step 2: Read CSV files
            progress.set_label("Lettura file CSV...")
            progress.set_value(10)
            
            dfs = []
            for i, f in enumerate(files):
                try:
                    dfi = pd.read_csv(f)
                    basename = os.path.splitext(os.path.basename(f))[0]
                    
                    if gui_instance.single_csv:
                        initials = ''
                    else:
                        basename_no_year = re.sub(r"\s*\d{4}\s*$", "", basename).strip()
                        parts = [p for p in re.split(r"\s+", basename_no_year) if p]
                        initials = ''.join([p[0].upper() for p in parts if p]) if parts else ''
                    
                    dfi['AthleteInit'] = initials
                    dfs.append(dfi)
                except Exception as e:
                    QMessageBox.warning(
                        gui_instance,
                        "Avviso",
                        f"Impossibile leggere '{os.path.basename(f)}': {e}"
                    )
                
                progress.set_value(10 + int((i + 1) / len(files) * 15))
            
            if not dfs:
                QMessageBox.critical(gui_instance, "Errore", "Nessun CSV valido letto")
                return
            
            # Step 3: Concatenate and clean
            progress.set_label("Processamento dati...")
            progress.set_value(25)
            
            gui_instance.raw_df = pd.concat(dfs, ignore_index=True, sort=False)
            
            if 'Tags' not in gui_instance.raw_df.columns:
                gui_instance.raw_df.insert(0, 'Tags', '')
            
            gui_instance.df = gui_instance.raw_df.copy()
            
            # Apply data cleaning (vectorized)
            gui_instance.df = gui_instance.df.drop(columns=['id'], errors='ignore')
            if 'Weight' in gui_instance.df.columns:
                gui_instance.df = gui_instance.df.drop(columns=['Weight'])
            
            progress.set_value(35)
            
            # Validate columns
            gui_instance.df = validate_rpe_column(gui_instance.df)
            gui_instance.df = validate_feel_column(gui_instance.df)
            
            # Process Name column (vectorized)
            if 'Name' in gui_instance.df.columns:
                gui_instance.df['Name'] = gui_instance.df['Name'].apply(remove_emoji)
                if 'AthleteInit' in gui_instance.df.columns:
                    gui_instance.df['Name'] = gui_instance.df.apply(
                        lambda row: append_initials_to_name(row['Name'], row['AthleteInit']),
                        axis=1
                    )
            
            progress.set_value(45)
            
            # Get 75% status (vectorized where possible)
            gui_instance.df['75%'] = gui_instance.df.apply(get_75_status, axis=1)
            
            # Numeric conversions (all vectorized)
            if 'Distance' in gui_instance.df.columns:
                gui_instance.df['Distance'] = (gui_instance.df['Distance'] / 1000).round(1)
            if 'Climbing' in gui_instance.df.columns:
                gui_instance.df['Climbing'] = gui_instance.df['Climbing'].fillna(0).astype(int)
            if 'Moving Time' in gui_instance.df.columns:
                gui_instance.df['Moving Time'] = gui_instance.df['Moving Time'].apply(normalize_moving_time)
            if 'Avg Speed' in gui_instance.df.columns:
                gui_instance.df['Avg Speed'] = (gui_instance.df['Avg Speed'] * 3.6).round(1)
            if 'Intensity' in gui_instance.df.columns:
                gui_instance.df = gui_instance.df.drop(columns=['Intensity'])
            if 'Variability' in gui_instance.df.columns:
                gui_instance.df = gui_instance.df.drop(columns=['Variability'])
            if 'Work' in gui_instance.df.columns:
                gui_instance.df['Work'] = (gui_instance.df['Work'] / 1000).round(0)
            if 'Work >FTP' in gui_instance.df.columns:
                gui_instance.df = gui_instance.df.rename(columns={'Work >FTP': 'Work >CP'})
                gui_instance.df['Work >CP'] = (gui_instance.df['Work >CP'] / 1000).round(0)
            if 'All Work>CP' in gui_instance.df.columns:
                gui_instance.df['All Work>CP'] = gui_instance.df['All Work>CP'].round(0)
            if 'Time Above CP' in gui_instance.df.columns:
                gui_instance.df['Time Above CP'] = gui_instance.df['Time Above CP'].apply(format_seconds)
            if 'Avg Above CP' in gui_instance.df.columns:
                gui_instance.df['Avg Above CP'] = gui_instance.df['Avg Above CP'].round(0)
            if 'kJ/h/kg' in gui_instance.df.columns:
                gui_instance.df['kJ/h/kg'] = gui_instance.df['kJ/h/kg'].round(1)
            if 'kJ/h/kg>CP' in gui_instance.df.columns:
                gui_instance.df['kJ/h/kg>CP'] = gui_instance.df['kJ/h/kg>CP'].round(1)
            
            progress.set_value(60)
            
            # Handle error flags
            gui_instance.df = handle_error_flags(gui_instance.df)
            
            # Sort and format Date
            progress.set_label("Ordinamento dati...")
            progress.set_value(70)
            
            if 'Date' in gui_instance.df.columns:
                parsed_dates = pd.to_datetime(gui_instance.raw_df['Date'], errors='coerce')
                date_only = parsed_dates.dt.normalize()
                if 'AthleteInit' not in gui_instance.df.columns:
                    gui_instance.df['AthleteInit'] = ''
                sort_frame = pd.DataFrame({
                    '_DateOnly': date_only,
                    '_AthleteInit': gui_instance.raw_df.get('AthleteInit', pd.Series(['']*len(gui_instance.raw_df)))
                })
                sort_frame['_AthleteInit'] = sort_frame['_AthleteInit'].fillna('').astype(str).str.upper()
                gui_instance.df = gui_instance.df.reset_index(drop=True)
                sort_frame = sort_frame.reset_index(drop=True)
                gui_instance.df = pd.concat([gui_instance.df, sort_frame], axis=1)
                gui_instance.df = gui_instance.df.sort_values(['_DateOnly', '_AthleteInit'], ascending=[True, True]).drop(columns=['_DateOnly', '_AthleteInit'])
                gui_instance.df['Date'] = pd.to_datetime(gui_instance.df['Date'], errors='coerce').dt.strftime('%d/%m')
            
            # Reorder columns
            progress.set_label("Riorganizzazione colonne...")
            progress.set_value(80)
            
            gui_instance.df = reorder_and_filter_columns(gui_instance.df)
            
            # Sync raw_df
            if 'Date' in gui_instance.df.columns:
                sorted_indices = gui_instance.df.index.tolist()
                gui_instance.raw_df = gui_instance.raw_df.iloc[sorted_indices].reset_index(drop=True)
            
            gui_instance.df = gui_instance.df.reset_index(drop=True)
            
            # Compute title
            progress.set_label("Titolo e visualizzazioni...")
            progress.set_value(85)
            
            pdf_path, title_text = compute_pdf_path_and_title(
                gui_instance.csv_dir, gui_instance.csv_files, gui_instance.single_csv,
                gui_instance.df, gui_instance.raw_df, custom_title=None
            )
            
            if title_text:
                gui_instance.title_edit.setText(title_text)
            
            # Generate visualizations
            gui_instance.generate_visualizations()
            
            # Populate table
            progress.set_value(95)
            populate_data_table(gui_instance)
            
            # Enable export
            gui_instance.btn_export.setEnabled(True)
            
            progress.set_value(100)
        
        QMessageBox.information(
            gui_instance,
            "Successo",
            f"Caricati {len(gui_instance.csv_files)} file CSV con {len(gui_instance.df)} gare"
        )
        
    except Exception as e:
        import traceback
        QMessageBox.critical(
            gui_instance,
            "Errore",
            f"Errore durante l'importazione:\n{str(e)}\n\n{traceback.format_exc()}"
        )


def populate_data_table(gui_instance):
    """Populate the data table with current dataframe"""
    if gui_instance.df is None:
        return
    
    # Set up table
    gui_instance.data_table.setRowCount(len(gui_instance.df))
    gui_instance.data_table.setColumnCount(len(gui_instance.df.columns))
    gui_instance.data_table.setHorizontalHeaderLabels(gui_instance.df.columns.tolist())
    
    # Fill data
    for i, row in gui_instance.df.iterrows():
        for j, col in enumerate(gui_instance.df.columns):
            value = row[col]
            if pd.isna(value):
                text = ""
            else:
                text = str(value)
            
            item = QTableWidgetItem(text)
            
            # Make Tags column editable, others read-only
            if col == 'Tags':
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                # Add icon or visual hint
                if text:
                    item.setText(f"🏷️ {text}")
            else:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            
            gui_instance.data_table.setItem(i, j, item)
    
    # Resize columns to content
    gui_instance.data_table.resizeColumnsToContents()


def on_table_double_click(gui_instance, index):
    """Handle double click on table to edit tags"""
    row = index.row()
    
    if row < 0 or row >= len(gui_instance.df):
        return
    
    # Get current row data
    row_data = gui_instance.df.iloc[row]
    
    # Open tag editor dialog
    dialog = TagEditorDialog(row_data, gui_instance)
    if dialog.exec() == QDialog.Accepted:
        selected_tags = dialog.get_tags()
        tag_str = ' '.join(sorted(selected_tags))
        
        # Always store tags in the Tags column
        if 'Tags' in gui_instance.df.columns:
            gui_instance.df.at[row, 'Tags'] = tag_str
        
        # Refresh the table display
        populate_data_table(gui_instance)


def apply_data_changes(gui_instance):
    """Apply changes from data table back to dataframe"""
    if gui_instance.df is None:
        return
    
    try:
        # Update dataframe from table
        for i in range(gui_instance.data_table.rowCount()):
            for j in range(gui_instance.data_table.columnCount()):
                item = gui_instance.data_table.item(i, j)
                if item is not None:
                    value = item.text()
                    col_name = gui_instance.df.columns[j]
                    
                    # Remove emoji from Tags column for processing
                    if col_name == 'Tags':
                        value = value.replace('🏷️ ', '').strip()
                    
                    # Try to convert to appropriate type
                    if value == "":
                        gui_instance.df.iloc[i, j] = None
                    else:
                        gui_instance.df.iloc[i, j] = value
        
        # Invalidate cache since data changed
        gui_instance.invalidate_figure_cache()
        
        # Regenerate visualizations
        gui_instance.generate_visualizations()
        
        QMessageBox.information(gui_instance, "Successo", "Modifiche ai dati applicate!")
        
    except Exception as e:
        QMessageBox.critical(gui_instance, "Errore", f"Errore nell'applicare le modifiche:\n{str(e)}")
