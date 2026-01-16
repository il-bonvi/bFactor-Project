# bFactor Performance Suite

Suite modulare professionale per l'analisi avanzata di metriche di performance ciclistico.

## 🚀 Avvio Rapido

```bash
# Navigare alla cartella del progetto
cd c:\Users\bonvi\Documents\GitHub\bFactor-Project

# Eseguire il launcher
python main.py
```

## 📋 Funzionalità

### ✅ PEFFORT Analyzer (Operativo)
Analisi avanzata di file FIT con:
- 📊 Rilevamento automatico sforzi sostenuti (efforts)
- ⚡ Rilevamento automatico sprint
- 📈 Grafici interattivi Plotly
- 📄 Esportazione report PDF
- 🎨 Tema Forest Green (dark mode)
- 🔧 Parametri configurabili

**Funzionalità**:
- Caricamento file FIT
- Calcolo VAM, W/kg, percentuale FTP
- Analisi zone di potenza
- Visualizzazione altitude, gradient
- Stima energia (kJ)

### 🔧 Omniselector (In sviluppo)
Selezione e validazione dati

### ⚡ OmniPD Calculator (In sviluppo)
Calcoli potenza-durata e modelli

## 📁 Struttura Progetto

```
bFactor-Project/
├── __init__.py                    # Package root
├── main.py                        # 🎯 Launcher principale
├── REFACTORING_SUMMARY.md         # Questo file
│
└── PEFFORT/                       # Modulo di analisi
    ├── __init__.py
    ├── core_engine.py             # Logica pura
    ├── gui_interface.py           # Interfaccia GUI
    ├── export_manager.py          # Esportazione
    └── main.py                    # Entry point alternativo
```

## 🔧 Requisiti

- Python 3.8+
- PySide6
- pandas
- numpy
- fitparse
- plotly
- xhtml2pdf

### Installazione dipendenze

```bash
pip install PySide6 pandas numpy fitparse plotly xhtml2pdf
```

## 📖 Uso Programmatico

### Importare moduli

```python
from PEFFORT.gui_interface import EffortAnalyzer, get_style
from PEFFORT.core_engine import parse_fit, create_efforts, detect_sprints
from PEFFORT.export_manager import create_pdf_report, plot_unified_html
```

### Usare EffortAnalyzer

```python
from PySide6.QtWidgets import QApplication
from PEFFORT.gui_interface import EffortAnalyzer

app = QApplication([])
analyzer = EffortAnalyzer()
analyzer.showMaximized()
app.exec()
```

### Analisi programmatica

```python
from PEFFORT.core_engine import parse_fit, create_efforts

# Caricare FIT
df = parse_fit("myfile.fit")

# Creare efforts
efforts = create_efforts(df, ftp=280, window_sec=60, merge_pct=15, min_ftp_pct=100)
```

## 🎨 Temi Disponibili

Il progetto supporta più temi Dark Mode:

- **Forest Green** ✨ (predefinito)
- Deep Ocean
- VO2
- ABCoaching

Cambio tema in PEFFORT: Selezionare da dropdown nella sidebar sinistra

## 📊 File FIT

Il progetto analizza file `.fit` da:
- Garmin Edge (GPS sportivi)
- Wahoo Elemnt
- Stages
- Altri dispositivi compatibili con formato FIT

## 🛠️ Configurazione

### Parametri Efforts

- **Finestra (s)**: Durata finestra per rilevamento (default: 60s)
- **Merge (%)**: Differenza % per merge efforts (default: 15%)
- **Min FTP (%)**: Soglia minima in % FTP (default: 100%)
- **Trim (s/%)**: Finestra e soglia trim (default: 10s, 85%)
- **Extend (s/%)**: Finestra e soglia extend (default: 15s, 80%)

### Parametri Sprint

- **Finestra (s)**: Durata finestra sprint (default: 5s)
- **Potenza Min**: Soglia minima potenza (default: 600W)

## 📊 Output

### Visualizzazioni
- Grafico interattivo altitudine vs potenza
- Tabelle dettagliate efforts e sprint
- Annotazioni automatiche per sforzi principali

### Report PDF
- Grafico massimizzato
- Tabelle efforts e sprint
- Metadati FTP e peso atleta
- Parametri analisi

## 🐛 Troubleshooting

### ImportError: No module named 'PySide6'
```bash
pip install PySide6
```

### File FIT non si carica
- Verificare che il file sia un vero FIT (magic number: `.FIT`)
- Provare con un altro dispositivo
- Controllare permessi di lettura

### Grafico non si visualizza
- Assicurarsi che ci siano sforzi/sprint nel file
- Verificare i parametri di rilevamento
- Controllare console per messaggi di errore

## 📝 Note di Sviluppo

- Codebase modulare: facile aggiungere nuovi moduli
- Import relativi: robusti e portabili
- Theme system: Aggiungere nuovi temi in `TEMI` dict
- Estensibile: Subclassare `EffortAnalyzer` per custom UI

## 📞 Supporto

Per bug report o feature request, contattare lo sviluppatore.

---

**bFactor Performance Suite v1.0** | © 2024 Andrea Bonvicin
