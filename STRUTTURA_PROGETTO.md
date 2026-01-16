# 📁 STRUTTURA_PROGETTO - Guida all'Architettura

**Documentazione completa della struttura di bFactor Performance Suite.**

---

## 📋 Versione

**Versione**: 0.2  
**Data**: 16 Gennaio 2026  
**Status**: ✅ Completa

---

## 🎯 Panoramica Struttura

bFactor è organizzato come **suite modulare professionale** con Python packages corretti e import relativi.

```
bFactor-Project/
├── 🚀 Entry Point
├── 📦 Packages (PEFFORT, omniPD, shared)
├── 📊 Moduli (core, GUI, export)
└── 📚 Documentazione
```

---

## 📂 Struttura Completa

```
bFactor-Project/
│
├── __init__.py                          # ✨ Package root
├── main.py                              # 🚀 LAUNCHER PRINCIPALE
│
├── PEFFORT/                             # 📈 Modulo Analisi FIT
│   ├── __init__.py                      # Package PEFFORT
│   ├── main.py                          # Entry point standalone
│   ├── gui_interface.py                 # GUI principale (EffortAnalyzer)
│   ├── core_engine.py                   # Logica pura (parse_fit, efforts, sprints)
│   └── export_manager.py                # Export PDF/HTML
│
├── omniPD_calculator/                   # ⚡ Modulo Potenza-Durata
│   ├── __init__.py                      # Package omniPD
│   ├── gui_omnipd.py                    # GUI calcolatore
│   ├── omnipd_core.py                   # Logica matematica OmniPD
│   ├── engine_omnipd.py                 # Engine calcoli
│   ├── main_omnipd.py                   # Entry point standalone
│   └── omniPD_standalone.py             # Utilità standalone
│
├── percentile_selector/                 # 🎯 Placeholder
│
├── shared/                              # 🎨 Risorse Condivise
│   ├── __init__.py
│   └── styles.py                        # Temi e styling
│
└── DOCUMENTAZIONE/ (11 file)
    ├── INDEX.md                         # 📚 Guida navigazione (START HERE!)
    ├── README.md                        # 🎯 Panoramica generale
    ├── INSTALLATION.md                  # 🔧 Guida installazione
    ├── TROUBLESHOOTING.md               # 🆘 Soluzione problemi
    ├── API_REFERENCE.md                 # 📖 Documentazione API
    ├── MANIFEST.md                      # 📋 Catalogo file
    ├── VERSION.md                       # 📦 Versionamento
    ├── CHANGELOG.md                     # 📝 Storico modifiche
    ├── REFACTORING_SUMMARY.md           # 🔄 Modifiche tecniche
    ├── STRUTTURA_PROGETTO.md            # 📁 (questo file)
    └── QUICK_START.txt                  # ⚡ Quick reference
```

---

## 🚀 Entry Points

### 1. **Launcher Principale** (Consigliato)
```bash
python main.py
```
Apre BfactorLauncher con accesso a tutti i moduli.

**Quando usare**: Sempre per utenti normali

### 2. **PEFFORT Standalone**
```bash
python -m PEFFORT.gui_interface
# Oppure
python PEFFORT/main.py
```
Apre EffortAnalyzer direttamente.

**Quando usare**: Sviluppo PEFFORT, bypass launcher

### 3. **OmniPD Standalone**
```bash
python omniPD_calculator/main_omnipd.py
# Oppure
python -m omniPD_calculator.gui_omnipd
```
Apre OmniPD Calculator direttamente.

**Quando usare**: Sviluppo OmniPD, bypass launcher

---

## 📦 Package Architecture

### Root Package

**File**: `bFactor-Project/__init__.py`

```python
"""
bFactor Performance Suite - Suite modulare per analisi performance ciclistico
"""

__version__ = "0.2"
__author__ = "Andrea Bonvicin"
```

**Risultato**: 
- `import bFactor` funziona
- `from bFactor import ...` possibile

### PEFFORT Package

**File**: `PEFFORT/__init__.py`

```python
"""
PEFFORT - Modulo di analisi file FIT
"""

from .gui_interface import EffortAnalyzer, get_style

__all__ = ['EffortAnalyzer', 'get_style']
```

**Risultato**:
- `from PEFFORT import EffortAnalyzer` funziona
- `from PEFFORT.gui_interface import ...` funziona
- `from PEFFORT.core_engine import ...` funziona

### omniPD_calculator Package

**File**: `omniPD_calculator/__init__.py`

```python
"""
OmniPD Calculator - Modulo calcoli potenza-durata
"""

from .gui_omnipd import OmniPDAnalyzer

__all__ = ['OmniPDAnalyzer']
```

**Risultato**:
- `from omniPD_calculator import OmniPDAnalyzer` funziona
- `from omniPD_calculator.omnipd_core import ...` funziona

### Shared Package

**File**: `shared/__init__.py`

```python
"""
Shared - Risorse condivise tra moduli
"""

from .styles import TEMI, get_style

__all__ = ['TEMI', 'get_style']
```

**Risultato**:
- `from shared.styles import ...` funziona
- `from shared import get_style` funziona

---

## 🔗 Dipendenze e Import

### Import Relativi (Interno a PEFFORT)

```python
# PEFFORT/gui_interface.py
from .core_engine import format_time_hhmmss, parse_fit
from .export_manager import create_pdf_report

# PEFFORT/export_manager.py  
from .core_engine import format_time_mmss, get_zone_color
```

**Vantaggi**:
- Indipendenti da cwd (current working directory)
- Seguono PEP 328
- Facili da testare

### Import da Root

```python
# main.py (root)
from PEFFORT.gui_interface import EffortAnalyzer
from omniPD_calculator import OmniPDAnalyzer
from shared.styles import get_style
```

**Vantaggi**:
- Chiari e leggibili
- Import assoluti per package
- Espliciti (no ambiguità)

### Import Programmatico

```python
# Nel tuo script esterno
import sys
sys.path.insert(0, '/path/to/bFactor-Project')

from PEFFORT.core_engine import parse_fit
from omniPD_calculator.omnipd_core import calculate_omnipd_model

df = parse_fit('myfile.fit')
params = calculate_omnipd_model(time_data, power_data)
```

---

## 📖 Moduli Dettagliati

### PEFFORT - Effort Analyzer

#### `gui_interface.py`
**Responsabilità**: Interfaccia grafica

```python
class EffortAnalyzer(QWidget):
    """GUI principale per analisi FIT"""
    
    def __init__(self):
        # Initializzazione UI
        # Creazione sidebar, canvas, tabelle
        
    def open_file(self):
        """Apre file picker e carica FIT"""
        
    def analyze(self):
        """Esegue analisi con parametri selezionati"""
        
    def export_pdf(self):
        """Esporta report PDF"""

def get_style(theme_name: str) -> str:
    """Restituisce CSS stylesheet per tema"""
```

**Import Usati**:
```python
from .core_engine import format_time_hhmmss
from .export_manager import create_pdf_report, plot_unified_html
```

#### `core_engine.py`
**Responsabilità**: Logica pura e calcoli

```python
def parse_fit(filepath: str) -> pd.DataFrame:
    """Legge file FIT, restituisce DataFrame"""
    
def create_efforts(df, ftp, window_sec, ...) -> List[Dict]:
    """Rileva sforzi sostenuti"""
    
def detect_sprints(df, window, min_power) -> List[Dict]:
    """Rileva sprint"""
    
def format_time_hhmmss(seconds: float) -> str:
    """Formatta secondi in "1h30m45s" """
    
def get_zone_color(power_pct: float) -> str:
    """Restituisce colore in base zona potenza"""
```

**No Import PEFFORT**: Modulo standalone

#### `export_manager.py`
**Responsabilità**: Export PDF/HTML

```python
def create_pdf_report(df, efforts, sprints, output_path, ftp, athlete_weight):
    """Genera report PDF con grafici e tabelle"""
    
def plot_unified_html(df, efforts, sprints, ftp) -> str:
    """Genera grafico HTML interattivo Plotly"""
```

**Import Usati**:
```python
from .core_engine import format_time_hhmmss, format_time_mmss, get_zone_color
```

---

### OmniPD Calculator - Potenza-Durata

#### `gui_omnipd.py`
**Responsabilità**: Interfaccia grafica

```python
class OmniPDAnalyzer(QWidget):
    """GUI per calcoli potenza-durata"""
    
    def __init__(self):
        # UI con tab per input/output
        # Sezione caricamento CSV
        # Sezione grafico risultati
        
    def load_csv(self):
        """Carica dati da CSV"""
        
    def calculate(self):
        """Esegue fitting del modello"""
        
    def export_results(self):
        """Esporta parametri e grafici"""
```

#### `omnipd_core.py`
**Responsabilità**: Logica matematica

```python
def ompd_power(t, CP, W_prime, Pmax, A) -> np.ndarray:
    """Modello OmniPD completo"""
    
def ompd_power_short(t, CP, W_prime, Pmax) -> np.ndarray:
    """Modello OmniPD per t ≤ TCPmax"""
    
def w_eff(t, W_prime, CP, Pmax) -> np.ndarray:
    """W' efficace nel tempo"""
    
def calculate_omnipd_model(t_data, p_data) -> Dict:
    """Curve fitting per parametri OmniPD"""
```

#### `engine_omnipd.py`
**Responsabilità**: Engine calcoli avanzati

```python
# Funzioni ausiliarie per calcoli
# Ottimizzazioni numeriche
# Validazione dati
```

---

### Shared - Risorse Condivise

#### `styles.py`
**Responsabilità**: Temi e styling

```python
TEMI = {
    "Forest Green": { ... },
    "Deep Ocean": { ... },
    "VO2": { ... },
    "ABCoaching": { ... }
}

def get_style(theme_name: str) -> str:
    """Restituisce CSS completo per tema"""
```

---

## 🏗️ Dependency Graph

```
main.py (root launcher)
├── imports PEFFORT.gui_interface
│   ├── imports .core_engine
│   └── imports .export_manager
│       └── imports .core_engine
├── imports omniPD_calculator
│   ├── imports .gui_omnipd
│   │   └── imports .omnipd_core
│   └── imports .omnipd_core
└── imports shared.styles
```

**Proprietà**:
- ✅ No circular imports
- ✅ Hierachy ben definita
- ✅ Facile da testare

---

## 🧪 Testing Structure

### Possibile Struttura Tests

```
tests/
├── __init__.py
├── test_peffort/
│   ├── test_core_engine.py
│   ├── test_gui_interface.py
│   └── test_export_manager.py
├── test_omnipd/
│   ├── test_omnipd_core.py
│   └── test_gui_omnipd.py
└── test_integration.py
```

### Eseguire Tests

```bash
# Tutti i test
pytest tests/

# Test specifico modulo
pytest tests/test_peffort/test_core_engine.py

# Con coverage
pytest tests/ --cov=PEFFORT --cov=omniPD_calculator
```

---

## 🔄 Workflow di Sviluppo

### Aggiungere Nuova Feature a PEFFORT

1. **Modificare core_engine.py** (logica)
   ```python
   def new_function():
       pass
   ```

2. **Aggiornare gui_interface.py** (UI)
   ```python
   from .core_engine import new_function
   # Usare nella GUI
   ```

3. **Aggiornare export_manager.py** (se serve export)
   ```python
   # Esportare risultati nuova feature
   ```

4. **Test**
   ```bash
   python -m PEFFORT.gui_interface
   ```

### Aggiungere Nuovo Modulo

1. **Creare cartella**: `new_module/`

2. **Creare __init__.py**:
   ```python
   """New Module"""
   from .gui import NewGUI
   __all__ = ['NewGUI']
   ```

3. **Creare moduli**:
   - `gui.py` - Interfaccia
   - `core.py` - Logica
   - `export.py` - Export

4. **Aggiornare launcher** in `main.py`:
   ```python
   from new_module import NewGUI
   # Aggiungere pulsante...
   ```

---

## 📊 Convenzioni Codice

### Naming Conventions

- **Packages**: `lowercase_with_underscores` (es: `omniPD_calculator`)
- **Modules**: `lowercase_with_underscores` (es: `core_engine.py`)
- **Classes**: `PascalCase` (es: `EffortAnalyzer`)
- **Functions**: `lowercase_with_underscores` (es: `parse_fit()`)
- **Constants**: `UPPERCASE_WITH_UNDERSCORES` (es: `TCPMAX`)
- **Private**: `_leading_underscore` (es: `_format_time_label()`)

### Import Order

```python
# 1. Standard library
import sys
from pathlib import Path

# 2. Third party
from PySide6.QtWidgets import QWidget
import pandas as pd

# 3. Local - relative
from .core_engine import parse_fit
from .export_manager import create_pdf_report

# 4. Local - absolute (solo da root)
from PEFFORT.gui_interface import EffortAnalyzer
from shared.styles import get_style
```

### Docstring Convention

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Descrizione breve.
    
    Descrizione dettagliata se necessaria.
    
    Args:
        param1: Descrizione param1
        param2: Descrizione param2
    
    Returns:
        bool: Descrizione return value
        
    Raises:
        ValueError: Quando...
        
    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

---

## 🚀 Scalabilità Futura

### Aggiungere Modulo Omniselector

```
percentile_selector/
├── __init__.py
├── gui_selector.py
├── core_selector.py
└── export_selector.py
```

### Aggiungere Modulo Custom

```
custom_module/
├── __init__.py
├── gui_custom.py
├── core_custom.py
└── engine_custom.py
```

### Aggiornare Launcher

```python
from custom_module import CustomGUI

class BfactorLauncher:
    def open_custom(self):
        if self.custom_window is not None and self.custom_window.isVisible():
            self.custom_window.raise_()
        else:
            self.custom_window = CustomGUI()
            self.custom_window.showMaximized()
```

---

## 🎯 Principi Architetturali

### Separation of Concerns (SoC)

Ogni modulo ha responsabilità ben definita:
- **GUI** (`gui_*.py`) - Interfaccia utente
- **Core** (`core_*.py` o `*_core.py`) - Logica pura
- **Export** (`export_*.py`) - Output dati

### DRY (Don't Repeat Yourself)

Codice condiviso in `shared/`:
- Stili e temi
- Utilità comuni
- Configurazioni

### SOLID Principles

- **S** (Single Responsibility): Ogni classe ha un ruolo
- **O** (Open/Closed): Facile estendere, difficile modificare
- **L** (Liskov): Interfacce consistenti
- **I** (Interface Segregation): No grandi interfacce monolitiche
- **D** (Dependency Inversion): Dipendere da astrazioni

---

## 📈 Performance Considerations

### Memory Usage

- **GUI lenta**: File FIT >500MB, ridurre campionamento
- **Plot lento**: Usare rendering statico vs interattivo
- **Import lento**: Lazy load moduli pesanti

### Database (Futuro)

Se necessaria persistenza:
```
database/
├── models.py
├── queries.py
└── migrations/
```

### Caching (Futuro)

Se necessario caching:
```
cache/
├── __init__.py
└── cache_manager.py
```

---

## 📚 Riferimenti

### File Correlati

- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Come è strutturato
- [API_REFERENCE.md](API_REFERENCE.md) - Cosa puoi usare
- [INSTALLATION.md](INSTALLATION.md) - Come installare
- [README.md](README.md) - Panoramica

### PEP Standards

- **PEP 8**: Style Guide
- **PEP 257**: Docstring Conventions
- **PEP 328**: Relative Imports
- **PEP 420**: Namespace Packages

---

## ✅ Checklist Struttura

- ✅ __init__.py in tutti i packages
- ✅ Import relativi in PEFFORT
- ✅ Import assoluti da root
- ✅ No circular imports
- ✅ Nomi file coerenti
- ✅ Docstring complete
- ✅ Convenzioni naming seguite
- ✅ Hierarchy ben definita
- ✅ SoC rispettato
- ✅ Scalabile per nuovi moduli

---

**Versione**: 0.2  
**Data**: 16 Gennaio 2026  
**Status**: ✅ Completato  
**Last Update**: Per v0.2 aggiornato con OmniPD integration
