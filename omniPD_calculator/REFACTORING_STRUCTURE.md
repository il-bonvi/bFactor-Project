# Refactoring OmniPD - Documentazione Struttura

## 📋 Sommario Suddivisione

Il file monolitico **gui_omniPD.py** (808 linee originali) è stato suddiviso in **5 moduli specializzati**, con **data handling integrato in core_omniPD.py** per coerenza.

### File Originale vs Nuova Struttura

```
PRIMA (1 file):
gui_omniPD.py: 808 linee (GUI + plotting + events + widgets + data handling)

DOPO (5 file):
├── gui_omniPD.py              460 linee  (Pura presentazione GUI + orchestrazione)
├── core_omniPD.py             226 linee  (Logica matematica + I/O dati + validazioni)
├── plotting_omniPD.py         181 linee  (Rendering grafici matplotlib)
├── widgets_omniPD.py           63 linee  (Dialog e componenti Qt custom)
└── events_omniPD.py           150 linee  (Event handler interazioni grafiche)

Totale: 1.080 linee (ma ben organizzate e riusabili)
```

---

## 📁 Descrizione Moduli

### 1. **gui_omniPD.py** (Presentazione GUI)
**Responsabilità:**
- Setup layout principale (sidebar + tab widget)
- Creazione dei tab con canvas matplotlib
- Binding eventi UI → funzioni core
- Aggiornamento visualizzazione
- Orchestrazione calcoli e display

**Classe principale:**
- `OmniPDAnalyzer(QWidget)`: Widget principale dell'app

**Metodi chiave:**
- `setup_ui()`: Costruisce interfaccia
- `run_calculation()`: Estrae dati e avvia calcolo
- `import_file()`: Carica dati da file
- `update_*_plot()`: Aggiorna grafici

**Imports interni:**
```python
from .core_omniPD import (
    calculate_omnipd_model,
    load_data_from_file,
    extract_data_from_rows,
    convert_time_minutes_to_seconds
)
from .widgets_omniPD import CSVColumnDialog, MmpRow
from .plotting_omniPD import format_plot, plot_ompd_curve, plot_residuals, plot_weff
from .events_omniPD import OmniPDEventHandler
```

---

### 2. **core_omniPD.py** (Logica di Business)
**Responsabilità:**
- Modello matematico OmniPD (4 parametri)
- Fitting curve e calcolo errori
- **Caricamento dati da file** (CSV, XLSX, XLSM)
- **Estrazione dati da input UI**
- **Validazione e pulizia dati**
- Utility per formattazione tempo

**Funzioni esportate:**

*Calcolo e Modelli:*
- `ompd_power(t, CP, W_prime, Pmax, A)`: Modello completo
- `ompd_power_short(t, CP, W_prime, Pmax)`: Curva base (t ≤ TCPmax)
- `w_eff(t, W_prime, CP, Pmax)`: W' efficace nel tempo
- `calculate_omnipd_model(t_data, p_data)`: Fitting completo con errori

*Data Handling:*
- `load_data_from_file(file_path, time_col_idx=0, power_col_idx=1)`: Carica CSV/XLSX/XLSM
- `extract_data_from_rows(rows)`: Estrae dati da righe UI
- `convert_time_minutes_to_seconds(minutes_str)`: Converte minuti → secondi

*Utility:*
- `_format_time_label(seconds)`: Formatta tempo in leggibile (es: "5m30s")

**Dipendenze:**
- numpy, pandas, scipy

---

### 3. **plotting_omniPD.py** (Visualizzazione Dati)
**Responsabilità:**
- Formattazione estetica comune per i plot
- Rendering grafico OmPD curve
- Rendering grafico dei residui
- Rendering grafico W'eff (Effective W')

**Funzioni esportate:**
- `format_plot(ax)`: Applica stile comune (colori tema, griglie)
- `plot_ompd_curve(ax, x_data, y_data, params)`: OmniPD con MMP data
- `plot_residuals(ax, x_data, residuals, RMSE, MAE)`: Residui con metriche
- `plot_weff(ax, params, W_prime)`: W' efficace con punto 99%

**Dipendenze:**
- matplotlib
- core_omniPD (per funzioni di calcolo e formato)

---

### 4. **widgets_omniPD.py** (Componenti Qt)
**Responsabilità:**
- Dialog per selezione colonne CSV
- Widget per input righe MMP

**Classi esportate:**
- `CSVColumnDialog(QDialog)`: Seleziona colonne da importare
- `MmpRow(QHBoxLayout)`: Input Tempo + Potenza

**Dipendenze:**
- PySide6.QtWidgets

---

### 5. **events_omniPD.py** (Gestione Interazioni Grafiche)
**Responsabilità:**
- Hover events su grafico OmPD
- Hover events su grafico residui
- Connessione/disconnessione event handler

**Classe esportata:**
- `OmniPDEventHandler`: Gestore centralizzato
  - Metodi: `connect_ompd_hover()`, `connect_residuals_hover()`

**Dipendenze:**
- numpy
- core_omniPD
- Fitting curve e calcolo errori
- Utility per formattazione tempo

---

## 🔄 Flusso di Dati

```
┌─────────────────────────────────────────┐
│       User Interaction (GUI)            │
│  (Button click, File import, Input)     │
└────────────────┬────────────────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  gui_omniPD.py      │
        │  Event handlers     │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  core_omniPD.py     │
        │  Data loading &     │
        │  Validation         │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  core_omniPD.py     │
        │  Model calculation  │
        │  (fitting)          │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ plotting_omniPD.py  │
        │  Render graphs      │
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │ events_omniPD.py    │
        │ Connect interactions│
        └────────┬────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │   Display Results   │
        │  with annotations   │
        └─────────────────────┘
```

---

## 📦 Imports Pubblici

### In __init__.py (API esportata):
```python
from .gui_omniPD import OmniPDAnalyzer

# Core - Business Logic
from .core_omniPD import (
    calculate_omnipd_model,
    ompd_power, ompd_power_short, w_eff,
    load_data_from_file,
    extract_data_from_rows,
    convert_time_minutes_to_seconds
)

# Components
from .widgets_omniPD import CSVColumnDialog, MmpRow
from .plotting_omniPD import plot_ompd_curve, plot_residuals, plot_weff
from .events_omniPD import OmniPDEventHandler
```

### Utilizzo Programmatico:
```python
# Importazione completa app
from omniPD_calculator import OmniPDAnalyzer

# Importazione per calcoli standalone
from omniPD_calculator import calculate_omnipd_model, load_data_from_file

# Importazione per visualizzazione
from omniPD_calculator import plot_ompd_curve, plot_residuals
```

---

## ✅ Vantaggi della Suddivisione

| Aspetto | Vantaggio |
|---------|-----------|
| **Separazione concern** | Ogni file ha UNA responsabilità |
| **Manutenibilità** | Modifiche isolate senza effetti collaterali |
| **Testabilità** | Core e plotting testabili indipendentemente |
| **Riusabilità** | core_omniPD può essere usato senza GUI |
| **Scalabilità** | Facile aggiungere visualizzazioni |
| **Readability** | File piccoli (max 460 righe) e focalizzati |
| **Debugging** | Stack trace puliti |
| **Coerenza** | Data handling in core (no duplicazione) |

---

## 📈 Statistiche Refactoring

| Metrica | Prima | Dopo |
|---------|-------|------|
| **File Python** | 1 | 5 |
| **Righe gui_omniPD** | 808 | 460 |
| **Complessità ciclomatica** | Alta | Bassa per file |
| **Coesione** | Bassa | Alta |
| **Accoppiamento** | Alto | Basso |
| **Testabilità** | Difficile | Facile |

---

## 🚀 Utilizzo

### Avvio standalone GUI:
```bash
python -m omniPD_calculator.main_omniPD
```

### Utilizzo come libreria:
```python
from omniPD_calculator import (
    calculate_omnipd_model,
    load_data_from_file,
    plot_ompd_curve
)

# Carica dati
t_data, p_data = load_data_from_file("data.csv", time_col_idx=0, power_col_idx=1)

# Calcola modello
result = calculate_omnipd_model(t_data, p_data)

# Visualizza (con pyplot)
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
plot_ompd_curve(ax, t_data, p_data, result['params'])
plt.show()
```

---

## 📝 Architettura Logica

```
┌─────────────────────────────────────────────┐
│         OmniPD Application                  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   Presentation Layer (GUI)          │   │
│  │   ├─ gui_omniPD.py (460 linee)      │   │
│  │   ├─ widgets_omniPD.py (63 linee)   │   │
│  │   └─ events_omniPD.py (150 linee)   │   │
│  └──────────────┬──────────────────────┘   │
│                 │                           │
│  ┌──────────────▼──────────────────────┐   │
│  │   Visualization Layer               │   │
│  │   └─ plotting_omniPD.py (181 linee) │   │
│  └──────────────┬──────────────────────┘   │
│                 │                           │
│  ┌──────────────▼──────────────────────┐   │
│  │   Business Logic Layer              │   │
│  │   └─ core_omniPD.py (226 linee)     │   │
│  │      ├─ Model calculations          │   │
│  │      ├─ Data I/O & validation       │   │
│  │      └─ Utility functions           │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

---

**Data refactoring:** 20 Gennaio 2026  
**Stato:** Completo - Data handling integrato in core  
**Versione struttura:** 2.0  
**Autore:** bFactor Project
