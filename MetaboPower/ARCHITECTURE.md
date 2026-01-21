# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

# ARCHITETTURA METABOPOWER - REFACTORING MODULARE

## Panoramica

La struttura di MetaboPower è stata refactorizzata per separare responsabilità e migliorare manutenibilità. L'architettura segue il pattern MVC con separazione tra GUI, logica di elaborazione dati e rendering grafico.

---

## Struttura Moduli

### 1. **gui_metapow.py** (GUI Layer - 650 righe)
**Responsabilità**: Solo interfaccia utente e gestione eventi

**Classi**:
- `ImportProfileDialog`: Dialog per selezione profilo importazione
- `MetaboPowerGUI`: Finestra principale dell'applicazione

**Metodi principali**:
- `setup_ui()`: Costruzione interfaccia (layout, widget, connessioni)
- `load_csv_file()`: Handler caricamento metabolimetro
- `load_fit_file()`: Handler caricamento power meter
- `show_overlaid_comparison()`: Handler confronto sovrapposto
- `show_vt_analysis()`: Handler analisi VT multi-tab
- `_process_metadata()`: Elaborazione e display metadati
- `_show_data_preview()`: Preview tabella dati
- `check_files_loaded()`: Abilitazione pulsanti analisi

**Delega a**:
- `data_extraction_metapow` per estrazione serie temporali
- `plotting_metapow` per creazione grafici

---

### 2. **data_extraction_metapow.py** (Data Layer - 200 righe)
**Responsabilità**: Estrazione, conversione e elaborazione dati

**Funzioni**:
- `hmsms_to_seconds(series)`: Converte h:mm:ss,ms → secondi totali
- `extract_metabolimeter_series(df)`: Estrae (tempo, potenza) da DataFrame metabolimetro
- `extract_fit_series(df)`: Estrae (tempo, potenza) da DataFrame FIT
- `find_ramp_start(power_series)`: Trova indice inizio rampa (potenza > 0)
- `find_vt_intersections(time, power, vt1, vt2, map)`: Calcola tempi intersezione soglie VT

**Caratteristiche**:
- Funzioni pure (input → output, no side effects)
- Conversioni formato centralizzate
- Rilevamento automatico colonne (fallback multipli)

---

### 3. **plotting_metapow.py** (Plotting Layer - 250 righe)
**Responsabilità**: Creazione e configurazione grafici matplotlib

**Funzioni**:
- `create_fit_selection_plot(time, power, parent)`: Grafico selezione fine rampa FIT
- `create_overlaid_comparison_plot(met_time, met_power, fit_time, fit_power, vt_times)`: Grafico confronto sovrapposto
- `create_vt_analysis_dialog(metabol_data, times, powers, vt_times, parent)`: Dialog con tab multipli per analisi VT
- `setup_fit_selection_click_handler(fig, ax, canvas, time, status, callback)`: Gestore click per selezione FIT

**Caratteristiche**:
- Separazione creazione grafici da logica business
- Configurazione stile centralizzata (colori, linestyle, font)
- Gestione eventi matplotlib isolata

---

### 4. **cortex_metapow.py** (Parser Specializzato - 220 righe)
**Responsabilità**: Parsing XLSX da Cortex Metabolic System

**Classe**: `CortexMetabolitParser`

**Metodi**:
- `load(file_path, settings)`: Caricamento file XLSX
- `_extract_metadata(ws, metadata_cells)`: Estrazione metadati paziente
- `_extract_columns(ws, header_row, subheader_row)`: Lettura intestazioni
- `_extract_data_rows(ws, data_start_row, num_columns)`: Lettura righe dati
- `_postprocess_metadata(df)`: Rilevamento TURN marker, colonne tempo/potenza
- `_normalize_decimals(df)`: Conversione virgola → punto

---

### 5. **genericsv_metapow.py** (Parser Specializzato - 180 righe)
**Responsabilità**: Parsing CSV generico con autodetection

**Classe**: `GenericCSVParser`

**Metodi**:
- `load(file_path, settings)`: Caricamento file CSV
- `_read_csv(file_path, settings)`: Lettura con autodetection separatore/header
- `_postprocess_metadata(df)`: Rilevamento colonne tempo/potenza
- `_normalize_decimals(df)`: Conversione decimali

---

### 6. **parser_metapow.py** (Orchestrator - 90 righe)
**Responsabilità**: Dispatcher verso parser specifici

**Classe**: `MetabolitDataParser`

**Metodi**:
- `load_file_with_profile(file_path, profile_name)`: Carica file usando profilo
- Delega a `cortex_parser` o `generic_csv_parser` in base al formato

---

### 7. **config_metapow.py** (Configuration - 65 righe)
**Responsabilità**: Definizione profili importazione

**Strutture**:
- `IMPORT_PROFILES`: Dictionary con profili Cortex XLSX, Generic CSV
- `ImportProfileManager`: Gestore profili (get_all_profiles, get_profile)

---

### 8. **fit_parser_metapow.py** (FIT Parser - 120 righe)
**Responsabilità**: Parsing file FIT da power meter

**Classe**: `FitFileParser`
- Usa libreria `fitparse`
- Estrae record 'power' da file FIT

---

### 9. **core_metapow.py** (Core Engine - 80 righe)
**Responsabilità**: Logica di sincronizzazione metabolimetro/FIT

**Classe**: `MetaboPowerEngine`
- Container per dati CSV e FIT
- Metodi di allineamento temporale (attualmente non usati, logica in GUI)

---

## Flusso di Esecuzione

### Caricamento Metabolimetro
```
1. GUI: load_csv_file()
2. → ImportProfileDialog (utente sceglie profilo)
3. → parser.load_file_with_profile(path, profile_name)
4. → cortex_parser.load() o generic_csv_parser.load()
5. → GUI: _process_metadata() + _show_data_preview()
```

### Caricamento FIT
```
1. GUI: load_fit_file()
2. → fit_parser.load_file(path)
3. → GUI: _show_fit_selection_dialog()
4. → plotting.create_fit_selection_plot()
5. → plotting.setup_fit_selection_click_handler()
6. → Utente click → callback imposta fit_end_idx
```

### Confronto Sovrapposto
```
1. GUI: show_overlaid_comparison()
2. → data_extraction.extract_metabolimeter_series(csv_data)
3. → data_extraction.extract_fit_series(fit_data)
4. → data_extraction.find_ramp_start(power)
5. → Allineamento temporale (x=0 alla fine rampa)
6. → data_extraction.find_vt_intersections(time, power, vt1, vt2, map)
7. → plotting.create_overlaid_comparison_plot()
8. → Display in QDialog con NavigationToolbar
```

### Analisi VT
```
1. GUI: show_vt_analysis()
2. → data_extraction.extract_metabolimeter_series() + extract_fit_series()
3. → data_extraction.find_ramp_start() + find_vt_intersections()
4. → Filtra dati metabolici (solo rampa)
5. → plotting.create_vt_analysis_dialog()
6. → Crea un tab per ogni colonna numerica metabolimetro
7. → Ogni tab: FIT power (sfondo) + parametro metabolico (asse Y secondario) + linee VT
```

---

## Pattern Utilizzati

### Separation of Concerns
- **GUI**: Solo widget e slot handler
- **Data Extraction**: Solo manipolazione dati
- **Plotting**: Solo rendering grafico

### Delegation Pattern
- `MetabolitDataParser` delega a parser specifici
- `GUI` delega estrazione dati e plotting a moduli dedicati

### Pure Functions (Data Extraction)
- Input → Output, no side effects
- Testabili in isolamento
- Composizione funzionale

---

## Vantaggi del Refactoring

1. **Manutenibilità**: Ogni modulo ha responsabilità chiara
2. **Testabilità**: Funzioni pure facilmente testabili
3. **Riusabilità**: Funzioni data_extraction/plotting riusabili in altri contesti
4. **Leggibilità**: gui_metapow.py ridotto da 933 a 650 righe
5. **Estensibilità**: Aggiungere nuovi metabolimetri o grafici è isolato

---

## Prossimi Step (Opzionali)

1. **Spostare logica allineamento da GUI a core_metapow.py**
   - Creare `align_ramp_data(met_data, fit_data, met_end, fit_end)` in core
   - GUI chiama solo core per allineamento

2. **Aggiungere unit test**
   - Test per `hmsms_to_seconds()` con vari formati
   - Test per `find_ramp_start()` con edge cases
   - Test per `find_vt_intersections()` con soglie mancanti

3. **Aggiungere export grafici**
   - Funzione `export_plot_to_file(fig, path, format)` in plotting
   - Collegare a btn_export in GUI

4. **Gestione memoria matplotlib**
   - Aggiungere `plt.close(fig)` dopo uso
   - Risolvere warning "More than 20 figures opened"

---

## File di Backup

- `gui_metapow_old.py`: Versione monolitica originale (933 righe)
- Mantenuto per riferimento/rollback se necessario

---

© 2026 bFactor Project - MetaboPower Refactoring Documentation
