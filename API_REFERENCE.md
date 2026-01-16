# API REFERENCE - bFactor Performance Suite

**Documentazione tecnica completa di tutte le API e moduli.**

---

## 📈 PEFFORT - Effort Analyzer

Modulo per analisi avanzata di file FIT con rilevamento automatico sforzi e sprint.

### Import

```python
from PEFFORT.gui_interface import EffortAnalyzer, get_style
from PEFFORT.core_engine import (
    parse_fit, create_efforts, detect_sprints,
    format_time_hhmmss, format_time_mmss, get_zone_color
)
from PEFFORT.export_manager import (
    create_pdf_report, plot_unified_html
)
```

### EffortAnalyzer (GUI Class)

**Classe principale per interfaccia grafica.**

```python
from PySide6.QtWidgets import QApplication
from PEFFORT.gui_interface import EffortAnalyzer

app = QApplication([])
analyzer = EffortAnalyzer()
analyzer.showMaximized()
app.exec()
```

**Metodi Principali:**
- `open_file()` - Carica file FIT
- `analyze()` - Avvia analisi
- `export_pdf()` - Esporta PDF
- `export_html()` - Esporta HTML

### parse_fit(filepath: str) -> pd.DataFrame

Legge file FIT e restituisce DataFrame con dati sensoriali.

```python
from PEFFORT.core_engine import parse_fit

df = parse_fit('myfile.fit')
print(df.columns)  # timestamp, power, heart_rate, cadence, altitude, grade, speed, ...
print(len(df))     # numero di campioni
```

**Returns:**
- `pd.DataFrame` con colonne: timestamp, power, heart_rate, cadence, altitude, speed, grade

### create_efforts(df, ftp, window_sec, merge_pct, min_ftp_pct, trim_s, trim_pct, extend_s, extend_pct) -> List[Dict]

Rileva automaticamente sforzi sostenuti nel file.

```python
from PEFFORT.core_engine import create_efforts

efforts = create_efforts(
    df=df,
    ftp=280,                    # Critical Power (W)
    window_sec=60,              # Finestra rilevamento (s)
    merge_pct=15,               # % per merge efforts contigui
    min_ftp_pct=100,            # Soglia minima (% FTP)
    trim_s=10,                  # Trim inizio/fine (s)
    trim_pct=85,                # Trim soglia (%)
    extend_s=15,                # Extend boundaries (s)
    extend_pct=80               # Extend soglia (%)
)

for effort in efforts:
    print(f"Effort {effort['id']}: {effort['start_time']} - {effort['end_time']}")
    print(f"  Power: {effort['avg_power']}W, {effort['rel_power']}W/kg")
    print(f"  Duration: {effort['duration']}s")
```

**Parameters:**
- `df`: pd.DataFrame - Dati FIT
- `ftp`: float - Soglia potenza funzionale (W)
- `window_sec`: int - Finestra per rilevamento (default: 60)
- `merge_pct`: float - % differenza per merge (default: 15)
- `min_ftp_pct`: float - Soglia minima (default: 100)
- `trim_s`, `trim_pct`: int/float - Trim parametri
- `extend_s`, `extend_pct`: int/float - Extend parametri

**Returns:**
- List di Dict con chiavi:
  - `id`, `start_time`, `end_time`, `duration`
  - `avg_power`, `max_power`, `rel_power`
  - `start_idx`, `end_idx`

### detect_sprints(df, window=5, min_power=600) -> List[Dict]

Rileva automaticamente sprint nel file.

```python
from PEFFORT.core_engine import detect_sprints

sprints = detect_sprints(
    df=df,
    window=5,           # Finestra sprint (s)
    min_power=600       # Soglia potenza (W)
)

for sprint in sprints:
    print(f"Sprint: {sprint['duration']:.1f}s @ {sprint['avg_power']}W")
```

**Parameters:**
- `df`: pd.DataFrame - Dati FIT
- `window`: int - Finestra rilevamento (default: 5)
- `min_power`: float - Soglia minima (default: 600)

**Returns:**
- List di Dict con metriche sprint

### format_time_hhmmss(seconds: float) -> str

Formatta secondi in formato leggibile.

```python
from PEFFORT.core_engine import format_time_hhmmss

time_str = format_time_hhmmss(3661)
print(time_str)  # "1h1m1s"
```

### create_pdf_report(df, efforts, sprints, output_path, ftp, athlete_weight) -> None

Genera report PDF con grafici e tabelle.

```python
from PEFFORT.export_manager import create_pdf_report

create_pdf_report(
    df=df,
    efforts=efforts,
    sprints=sprints,
    output_path='report.pdf',
    ftp=280,
    athlete_weight=75
)
```

### get_style(theme_name: str) -> str

Restituisce stylesheet CSS per tema.

```python
from PEFFORT.gui_interface import get_style

style = get_style("Forest Green")
my_widget.setStyleSheet(style)
```

**Temi disponibili:**
- `"Forest Green"` - Default, dark mode verde
- `"Deep Ocean"` - Dark mode blu
- `"VO2"` - Dark mode rosso
- `"ABCoaching"` - Dark mode viola

---

## ⚡ OmniPD - Potenza-Durata Calculator

Modulo per modello matematico potenza-durata professionale.

### Import

```python
from omniPD_calculator import OmniPDAnalyzer
from omniPD_calculator.omnipd_core import (
    ompd_power, ompd_power_short, w_eff,
    calculate_omnipd_model, _format_time_label
)
```

### OmniPDAnalyzer (GUI Class)

**Classe principale per interfaccia grafica.**

```python
from PySide6.QtWidgets import QApplication
from omniPD_calculator import OmniPDAnalyzer

app = QApplication([])
analyzer = OmniPDAnalyzer()
analyzer.show()
app.exec()
```

### ompd_power(t, CP, W_prime, Pmax, A) -> np.ndarray

Calcola curve potenza-durata OmniPD complete.

```python
from omniPD_calculator.omnipd_core import ompd_power
import numpy as np

time = np.linspace(1, 3600, 1000)  # 1s a 1h
CP, W_prime, Pmax, A = 280, 25000, 1500, 50

power = ompd_power(time, CP, W_prime, Pmax, A)
# power[0] ≈ potenza massima (primo secondo)
# power[-1] ≈ CP + decadimento lungo termine
```

**Parameters:**
- `t`: np.ndarray or float - Tempo (secondi)
- `CP`: float - Critical Power (W)
- `W_prime`: float - W Prime (J)
- `Pmax`: float - Potenza massima (W)
- `A`: float - Fattore decadimento

**Returns:**
- np.ndarray di potenze calcolate (W)

**Formula:**
```
P(t) = CP + (W'/t) * (1 - exp(-t*(Pmax-CP)/W')) + A*log(t/TCPmax)
```

### ompd_power_short(t, CP, W_prime, Pmax) -> np.ndarray

Calcola curve OmniPD per tempi ≤ TCPmax (no decadimento).

```python
from omniPD_calculator.omnipd_core import ompd_power_short

time = np.linspace(1, 1800, 100)  # 0-30 minuti
power = ompd_power_short(time, CP=280, W_prime=25000, Pmax=1500)
```

### w_eff(t, W_prime, CP, Pmax) -> np.ndarray

Calcola W' efficace nel tempo (quanto della capacità anaerobica è usata).

```python
from omniPD_calculator.omnipd_core import w_eff

time = np.array([1, 5, 10, 60, 300])  # vari tempi
w_effective = w_eff(time, W_prime=25000, CP=280, Pmax=1500)
# w_effective[i] = quanto di W' è utilizzato al tempo t[i]
```

### calculate_omnipd_model(t_data, p_data) -> Dict

Calcola i parametri OmniPD da dati sperimentali usando curve fitting.

```python
from omniPD_calculator.omnipd_core import calculate_omnipd_model
import numpy as np
import pandas as pd

# Dati sperimentali
df = pd.read_csv('power_durata.csv')  # colonne: time_s, power_W
t_data = df['time_s'].values
p_data = df['power_W'].values

params = calculate_omnipd_model(t_data, p_data)

print(f"CP: {params['CP']:.1f} W")
print(f"W': {params['W_prime']:.0f} J")
print(f"Pmax: {params['Pmax']:.0f} W")
print(f"A: {params['A']:.2f}")
print(f"R²: {params['r_squared']:.4f}")
print(f"RMSE: {params['rmse']:.1f} W")
```

**Returns:**
- Dict con chiavi:
  - `CP`, `W_prime`, `Pmax`, `A` - Parametri modello
  - `r_squared` - Coefficiente determinazione (0-1, più alto = migliore)
  - `rmse` - Root mean square error (W)
  - `errors` - Dict con errori per parametro

### _format_time_label(seconds) -> str

Formatta secondi in etichetta leggibile per grafici.

```python
from omniPD_calculator.omnipd_core import _format_time_label

label = _format_time_label(3661)
print(label)  # "1h1m" oppure formato simile
```

---

## 🎨 Shared - Risorse Condivise

### get_style(theme_name: str) -> str

Restituisce stylesheet CSS per il tema selezionato.

```python
from shared.styles import get_style

# Tema default
style_green = get_style("Forest Green")

# Tema alternativo
style_ocean = get_style("Deep Ocean")

my_widget.setStyleSheet(style_green)
```

### TEMI - Dizionario Temi

```python
from shared.styles import TEMI

# Lista temi disponibili
for theme_name, colors in TEMI.items():
    print(f"Tema: {theme_name}")
    print(f"  Colori: {list(colors.keys())}")

# Colori tema Forest Green
fg_colors = TEMI["Forest Green"]
print(fg_colors['background'])  # #061f17
print(fg_colors['accent'])      # #4ade80
```

**Temi Disponibili:**
- Forest Green
- Deep Ocean
- VO2
- ABCoaching

**Colori per Tema:**
- `background` - Sfondo principale
- `sidebar` - Barra laterale
- `accent` - Colore evidenziazione
- `button` - Pulsanti
- `input` - Campi input
- `text` - Testo principale
- `border` - Bordi

---

## 🚀 Launcher - BfactorLauncher

### Classe BfactorLauncher

Launcher centralizzato per accesso a tutti i moduli.

```python
from main import BfactorLauncher

# Istanziare e mostrare
launcher = BfactorLauncher()
launcher.show()
```

**Metodi:**
- `open_peffort()` - Apre PEFFORT Analyzer
- `open_omnipd()` - Apre OmniPD Calculator
- `show_in_development()` - Mostra messaggio modulo in sviluppo

**Attributi:**
- `peffort_window` - Riferimento finestra PEFFORT (None se non aperta)
- `omnipd_window` - Riferimento finestra OmniPD (None se non aperta)

---

## 📚 Esempi di Utilizzo Completo

### Analisi Completa FIT

```python
import pandas as pd
from PEFFORT.core_engine import (
    parse_fit, create_efforts, detect_sprints,
    format_time_hhmmss
)
from PEFFORT.export_manager import create_pdf_report

# 1. Caricare file FIT
df = parse_fit('activity.fit')

# 2. Rilevare sforzi
efforts = create_efforts(
    df, ftp=280, window_sec=60, merge_pct=15, min_ftp_pct=100
)

# 3. Rilevare sprint
sprints = detect_sprints(df, window=5, min_power=600)

# 4. Generare report
create_pdf_report(
    df=df,
    efforts=efforts,
    sprints=sprints,
    output_path='analysis.pdf',
    ftp=280,
    athlete_weight=75
)

# 5. Print metriche
for i, effort in enumerate(efforts):
    print(f"Effort {i+1}: {effort['avg_power']}W, "
          f"Durata: {format_time_hhmmss(effort['duration'])}")
```

### Calcolo Modello OmniPD

```python
import pandas as pd
import numpy as np
from omniPD_calculator.omnipd_core import (
    calculate_omnipd_model, ompd_power, w_eff
)

# 1. Carica dati sperimentali
df = pd.read_csv('power_data.csv')

# 2. Calcola modello
params = calculate_omnipd_model(df['time_s'], df['power_W'])

# 3. Genera curve teoriche
time_theory = np.logspace(0, 3.5, 1000)  # 1s a ~3000s
power_theory = ompd_power(
    time_theory,
    params['CP'],
    params['W_prime'],
    params['Pmax'],
    params['A']
)

# 4. Analizza W' efficace
w_effective_1min = w_eff(60, params['W_prime'], params['CP'], params['Pmax'])
print(f"W' a 1 minuto: {w_effective_1min:.0f} J")
```

---

## 🔗 Dipendenze Interne

### Import Relativi (PEFFORT)

```python
# gui_interface.py
from .core_engine import format_time_hhmmss
from .export_manager import create_pdf_report, plot_unified_html

# export_manager.py
from .core_engine import (format_time_hhmmss, format_time_mmss, get_zone_color)
```

### Import Package (root)

```python
# main.py
from PEFFORT.gui_interface import EffortAnalyzer
from omniPD_calculator import OmniPDAnalyzer
from shared.styles import get_style
```

---

## ⚠️ Note Importanti

1. **Thread Safety**: GUI operations devono avvenire nel thread principale
2. **Memory**: File FIT grandi (>1 GB) richiedono molta RAM
3. **Versioni**: PySide6 ≥6.2 richiesto per compatibility
4. **Import**: Usare import relativi in PEFFORT, assoluti da esterno

---

**Versione API**: 0.2  
**Data**: 16 Gennaio 2026  
**Status**: ✅ Stabile
