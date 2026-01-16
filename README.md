# bFactor Performance Suite

**Versione**: 0.2  
**Data Ultimo Update**: 16 Gennaio 2026  
**Status**: ✅ In Produzione (Core Modules)

---

## 🚀 Panoramica

Suite modulare professionale per l'analisi avanzata di metriche di performance ciclistico. Comprende strumenti per analisi di file FIT, modellazione potenza-durata e validazione dati.

### Moduli Disponibili

| Modulo | Status | Descrizione |
|--------|--------|-------------|
| **📈 PEFFORT Analyzer** | ✅ Operativo | Analisi file FIT, rilevamento sforzi e sprint |
| **⚡ OmniPD Calculator** | ⏳ Sviluppo | Modello potenza-durata con curve CP/W'/Pmax |
| **🎯 Omniselector** | ⏳ Sviluppo (offline) | Selezione e validazione dati |
| **💦 DA AGG** | 🎉 EE | FUT |

---

## ⚡ Quick Start

### Esecuzione Principale (Launcher)

```bash
cd c:\Users\bonvi\Documents\GitHub\bFactor-Project
python main.py
```

Apre il **BfactorLauncher** con accesso a tutti i moduli.

### Esecuzione Moduli Singoli

#### PEFFORT Analyzer
```bash
python -m PEFFORT.gui_interface
```

#### OmniPD Calculator
```bash
python omniPD_calculator/main_omnipd.py
```

---

## 📊 PEFFORT Analyzer (✅ Operativo)

Analizzatore avanzato per file FIT con intelligenza artificiale per rilevamento automatico.

### Funzionalità

- **📥 Caricamento File FIT**
  - Supporta: Garmin Edge, Wahoo Elemnt, Stages, e altri GPS sportivi
  - Caricamento tramite GUI drag-and-drop

- **📈 Rilevamento Automatico**
  - ⚡ Sprint detection (finestra 5s, soglia 600W default)
  - 💪 Effort detection (sforzi sostenuti, finestra 60s default)
  - 🔄 Merge intelligente di efforts contigui
  - ✂️ Trim/Extend automatico di boundaries

- **📊 Metriche Calcolate**
  - Potenza media (W)
  - Potenza relativa (W/kg)
  - Percentuale FTP
  - VAM (Vertical Ascent Meter)
  - Energia (kJ)
  - Altitudine e gradiente

- **📊 Visualizzazioni**
  - Grafico interattivo Plotly (altitudine + potenza)
  - Tabelle dettagliate efforts e sprint
  - Annotazioni automatiche per sforzi principali

- **🎨 Tema Scuro Professionale**
  - Forest Green Dark Mode (default)
  - Supporto tema personalizzabile

- **📄 Export**
  - PDF Report con grafici e tabelle
  - HTML interattivo
  - CSV dati raw

### Parametri Configurabili

| Parametro | Default | Uso |
|-----------|---------|-----|
| **FTP** | - | Soglia potenza funzionale (W) |
| **Peso** | - | Peso atleta (kg) |
| **Window Effort** | 60s | Finestra rilevamento sforzi |
| **Merge %** | 15% | Differenza % per merge efforts |
| **Min FTP %** | 100% | Soglia minima potenza |
| **Trim (s/%)** | 10s/85% | Trim inizio/fine effort |
| **Extend (s/%)** | 15s/80% | Extend boundaries effort |
| **Window Sprint** | 5s | Finestra sprint |
| **Min Power Sprint** | 600W | Soglia minima sprint |

### Utilizzo Programmatico

```python
from PEFFORT.gui_interface import EffortAnalyzer, get_style
from PEFFORT.core_engine import parse_fit, create_efforts, detect_sprints
from PEFFORT.export_manager import create_pdf_report, plot_unified_html

# Caricare file FIT
df = parse_fit("myfile.fit")

# Rilevare sforzi
efforts = create_efforts(
    df, 
    ftp=280, 
    window_sec=60, 
    merge_pct=15, 
    min_ftp_pct=100
)

# Rilevare sprint
sprints = detect_sprints(df, window=5, min_power=600)

# Generare report PDF
create_pdf_report(
    df=df,
    efforts=efforts,
    sprints=sprints,
    output_path="report.pdf",
    ftp=280,
    athlete_weight=75
)
```

---

## ⚡ OmniPD Calculator (✅ Operativo)

Modello matematico per calcoli potenza-durata professionale.

### Modello OmniPD

Combina caratteristiche di diversi modelli in 4 parametri chiave:

```
P(t) = CP + (W'/t) * (1 - exp(-t*(Pmax-CP)/W')) + A*log(t/TCPmax)
```

**Parametri:**
- **CP** (Critical Power): Potenza sostenibile infinita (W)
- **W'** (W Prime): Capacità anaerobica massima (J)
- **Pmax**: Potenza massima (W)
- **A**: Fattore decadimento lungo termine

### Funzionalità

- **📥 Input Dati**
  - CSV con colonne: tempo (s), potenza (W), durata (s)
  - Interfaccia selettore colonne CSV
  - Validazione dati automatica

- **📊 Calcoli**
  - Fitting automatico del modello OmniPD
  - Calcolo errori e validazione fit
  - Stima parametri CP, W', Pmax, A

- **📈 Visualizzazioni**
  - Curve potenza-durata teoriche
  - Dati sperimentali vs modello
  - Grafico W' efficace nel tempo
  - Zone di potenza colorate

- **💾 Export**
  - Parametri modello (CSV)
  - Grafici (PNG/PDF)
  - Dati analitici completi

### Utilizzo Programmatico

```python
from omniPD_calculator.gui_omnipd import OmniPDAnalyzer
from omniPD_calculator.omnipd_core import (
    ompd_power, ompd_power_short, calculate_omnipd_model, w_eff
)
import numpy as np

# Generare curve teoriche
time = np.linspace(1, 3600, 1000)
CP, W_prime, Pmax, A = 280, 25000, 1500, 50
power = ompd_power(time, CP, W_prime, Pmax, A)

# Calcolare modello da dati
params = calculate_omnipd_model(time_data, power_data)
print(f"CP: {params['CP']:.1f}W")
print(f"W': {params['W_prime']:.0f}J")
print(f"Pmax: {params['Pmax']:.0f}W")
```

---

## 🎯 Omniselector (⏳ In Sviluppo)

**Modulo dedicato a selezione e validazione dati avanzata.**

Funzionalità previste:
- Selezione intervalli temporali
- Validazione dati
- Filtri avanzati
- Annotazioni personalizzate

---

## 💦 Easter Egg: Amalia allenati (🎉)

Easter egg speciale nel launcher principale.

```
"Amalia non vuole allenarsi. Riprova un altro giorno"
```

Accedi cliccando su "💦 Amalia allenati" nel BfactorLauncher.

---

## 📁 Struttura Progetto

```
bFactor-Project/
├── main.py                          🚀 Launcher principale
├── __init__.py                      Package root
├── VERSION.md                       Versionamento
├── README.md                        (questo file)
├── CHANGELOG.md                     Storico modifiche
│
├── PEFFORT/                         📈 Modulo Analisi FIT
│   ├── __init__.py
│   ├── gui_interface.py            GUI principale
│   ├── core_engine.py              Logica pura
│   ├── export_manager.py           Export PDF/HTML
│   └── main.py                     Entry point alternativo
│
├── omniPD_calculator/              ⚡ Modulo Potenza-Durata
│   ├── __init__.py
│   ├── gui_omnipd.py               GUI calcolatore
│   ├── omnipd_core.py              Logica matematica
│   ├── engine_omnipd.py            Engine calcoli
│   ├── main_omnipd.py              Entry point standalone
│   └── omniPD_standalone.py        Utilità standalone
│
├── percentile_selector/            🎯 (Placeholder)
│
└── shared/                          🎨 Risorse Condivise
    ├── __init__.py
    ├── styles.py                   Temi e styling
    └── themes/ (?)                 Temi personalizzati
```

---

## 🔧 Requisiti

- **Python**: 3.8+
- **GUI**: PySide6
- **Dati**: pandas, numpy
- **FIT**: fitparse
- **Plot**: plotly, matplotlib
- **Export**: xhtml2pdf
- **Calcoli**: scipy

### Installazione Dipendenze

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install PySide6 pandas numpy fitparse plotly matplotlib xhtml2pdf scipy
```

---

## 🎨 Temi Disponibili

Il progetto supporta temi Dark Mode professionali:

| Tema | Colore Primario | Uso |
|------|-----------------|-----|
| **Forest Green** | #16a34a | Default (consigliato) |
| **Deep Ocean** | #0369a1 | Alternative |
| **VO2** | #dc2626 | Alternative |
| **ABCoaching** | #7c3aed | Alternative |

Cambio tema in PEFFORT: Selezionare da dropdown nella sidebar.

---

## 🔌 Import e Utilizzo Programmatico

### Importare Moduli come Package

```python
# PEFFORT
from PEFFORT.gui_interface import EffortAnalyzer, get_style
from PEFFORT.core_engine import parse_fit, create_efforts, detect_sprints
from PEFFORT.export_manager import create_pdf_report, plot_unified_html

# OmniPD
from omniPD_calculator.gui_omnipd import OmniPDAnalyzer
from omniPD_calculator.omnipd_core import calculate_omnipd_model, ompd_power

# Shared
from shared.styles import TEMI, get_style
```

### Esecuzione GUI nel Codice

```python
from PySide6.QtWidgets import QApplication
from PEFFORT.gui_interface import EffortAnalyzer

app = QApplication([])
analyzer = EffortAnalyzer()
analyzer.showMaximized()
app.exec()
```

---

## 🚀 Comandi Utili

```bash
# Verificare sintassi Python
python -m py_compile main.py
python -m py_compile PEFFORT/gui_interface.py
python -m py_compile omniPD_calculator/gui_omnipd.py

# Testare import moduli
python -c "from PEFFORT.gui_interface import EffortAnalyzer; print('✅ PEFFORT OK')"
python -c "from omniPD_calculator import OmniPDAnalyzer; print('✅ OmniPD OK')"

# Lanciare launcher principale
python main.py

# Lanciare moduli singoli
python omniPD_calculator/main_omnipd.py
```

---

## 📋 Changelog

Vedere [CHANGELOG.md](CHANGELOG.md) per storico completo delle modifiche.

**Versioni Principali:**
- **0.2** (Corrente) - OmniPD Integration, Easter Egg
- **1.0** (Base) - Suite modulare, PEFFORT operativo

---

## ✅ Checklist Stato Progetto

- ✅ Package structure (Python packages con __init__.py)
- ✅ Launcher centralizzato (main.py root)
- ✅ PEFFORT Analyzer (completo e operativo)
- ✅ OmniPD Calculator (completo e operativo)
- ✅ Tema Forest Green integrato
- ✅ Import relativi in PEFFORT
- ✅ Gestione finestre intelligente
- ⏳ Omniselector (in sviluppo)
- ⏳ Percentile Selector (in sviluppo)
- 🎉 Easter Egg Amalia (implementato)

---

## 🤝 Contributi

Segnalare problemi o suggerimenti via issue/PR.

---

## 📄 Licenza

TBD

---

**Sviluppato da**: Andrea Bonvicin  
**Data**: 16 Gennaio 2026  
**Progetto**: bFactor Performance Suite
