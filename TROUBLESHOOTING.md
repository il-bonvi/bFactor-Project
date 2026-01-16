# TROUBLESHOOTING - bFactor Performance Suite

**Guida per risolvere problemi comuni.**

---

## 🔴 Problemi all'Avvio

### ❌ "ModuleNotFoundError: No module named 'PEFFORT'"

**Possibili Cause:**
1. Dipendenze non installate
2. Virtual environment non attivato
3. Working directory sbagliata

**Soluzioni:**

```bash
# 1. Attivare virtual environment
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# 2. Reinstallare dipendenze
pip install -r requirements.txt

# 3. Assicurarsi di essere nella cartella giusta
cd /path/to/bFactor-Project
python main.py
```

### ❌ "PySide6 not found"

**Soluzione:**
```bash
pip install --upgrade PySide6
# O reinstallare
pip uninstall PySide6
pip install PySide6
```

### ❌ "No module named 'fitparse'"

**Soluzione:**
```bash
pip install fitparse

# Se non funziona:
pip install python-fitparse
```

### ❌ ImportError quando lancio main.py

**Debug:**
```bash
# Testare import singoli
python -c "from PEFFORT.gui_interface import EffortAnalyzer"
python -c "from omniPD_calculator import OmniPDAnalyzer"
python -c "from shared.styles import get_style"

# Se uno fallisce, il file __init__.py manca
# Controllare che esistano:
# - bFactor-Project/__init__.py
# - bFactor-Project/PEFFORT/__init__.py
# - bFactor-Project/omniPD_calculator/__init__.py
```

---

## 🔴 Problemi GUI

### ❌ Finestra non si apre / Crash immediato

**Controllare il terminal per errori:**
```bash
python -u main.py 2>&1
# -u = unbuffered output
# 2>&1 = reindirizza stderr a stdout
```

**Possibili Cause:**
- Display server non disponibile (Linux headless)
- Tema Forest Green non trovato
- Versione PySide6 incompatibile

**Soluzioni:**
```bash
# 1. Aggiornare PySide6
pip install --upgrade PySide6

# 2. Test tema
python -c "from shared.styles import get_style; print(get_style('Forest Green'))"

# 3. Test GUI minima
python << 'EOF'
from PySide6.QtWidgets import QApplication, QLabel
app = QApplication([])
label = QLabel("Test")
label.show()
print("✅ GUI works")
app.quit()
EOF
```

### ❌ Finestra PEFFORT non si apre

**Possibili Cause:**
1. File FIT non selezionato prima
2. Errore nell'analisi dati
3. Memoria insufficiente per file grande

**Soluzioni:**
```bash
# 1. Testare direttamente
python -m PEFFORT.gui_interface

# 2. Se non funziona, aggiornare dipendenze
pip install --upgrade pandas numpy plotly

# 3. Se file è troppo grande, convertire in CSV prima
# (vedi sezione "File FIT Problematici")
```

### ❌ Pulsanti non rispondono al click

**Possibili Cause:**
1. Thread principale bloccato
2. Errore non gestito in handler

**Soluzione:**
```bash
# Lanciare con output completo
python -u main.py 2>&1 | tee debug.log

# Cercare errori nel log
grep -i "error\|exception\|traceback" debug.log
```

---

## 🔴 Problemi File FIT

### ❌ "Error parsing FIT file"

**Cause Comuni:**
1. File FIT corrotto
2. Formato file non supportato
3. File molto grande

**Soluzioni:**
```bash
# 1. Verificare file non sia corrotto
# Provare con file FIT noto come funzionante

# 2. Se file è troppo grande (>1GB):
# Dividere con tool esterno o usare CSV

# 3. Controllare formato
file myfile.fit  # Dovrebbe dire "data"

# 4. Riparare file FIT (se possibile)
# Scaricare di nuovo dal device GPS
```

### ❌ "File too large" / App freeze

**Cause:**
- File FIT > 500 MB
- RAM insufficiente
- Campionamento troppo frequente (10 Hz)

**Soluzioni:**
```bash
# 1. Aumentare RAM disponibile
# Chiudere altre applicazioni

# 2. Convertire a CSV con meno campioni
# (usare tool esterno come fitparse-cli)

# 3. Se file è da allenamento lungo (8+ ore)
# Dividerlo manualmente in due file

# 4. Controllare memoria disponibile
free -h  # Linux
Get-Volume # PowerShell Windows
```

### ❌ "Power data missing" / Grafici vuoti

**Possibili Cause:**
1. File FIT senza sensore potenza
2. Power meter non era collegato
3. Dati corrotti

**Soluzioni:**
```bash
# 1. Controllare che device abbia power meter
# (Edge 1030+, Wahoo Elemnt Bolt, Garmin Vector, ecc.)

# 2. Se file da indoor (Zwift, TrainerRoad)
# Assicurarsi che l'export FIT includa potenza

# 3. Verificare dati con strumento esterno
# Es: GoldenCheetah, Strava API, ecc.
```

---

## 🔴 Problemi Export PDF

### ❌ "PDF generation failed" / "xhtml2pdf error"

**Possibili Cause:**
1. xhtml2pdf non installato
2. Path file output sbagliato
3. HTML malformato

**Soluzioni:**
```bash
# 1. Reinstallare xhtml2pdf
pip uninstall xhtml2pdf
pip install xhtml2pdf

# 2. Se error "PIL import failed"
pip install Pillow

# 3. Verificare permessi cartella output
chmod 755 /path/to/output  # Linux/macOS
icacls "C:\path\to\output" /grant Everyone:F  # Windows

# 4. Test minimo
python << 'EOF'
from xhtml2pdf import pisa
from io import BytesIO

html = "<h1>Test PDF</h1>"
output = BytesIO()
pisa.pisaDocument(BytesIO(html.encode()), output)
print("✅ xhtml2pdf works" if output.getvalue() else "❌ Failed")
EOF
```

### ❌ PDF generato ma grafico è vuoto

**Cause:**
1. Plotly non genera immagine statica
2. Matplotlib backend non supportato

**Soluzione:**
```bash
# Aggiornare Plotly e kaleido
pip install --upgrade plotly kaleido
```

---

## 🔴 Problemi OmniPD Calculator

### ❌ Curve fitting non converge

**Possibili Cause:**
1. Dati sperimentali non sufficienti
2. Valori iniziali parametri non realistici
3. Rumore nei dati troppo alto

**Soluzioni:**
```bash
# 1. Verificare numero campioni
# Minimo: ~20 punti
# Ideale: 50-100 punti

# 2. Controllare che dati siano realistici
# CP: 200-400W per ciclisti amatori
# W': 15000-30000J per ciclisti amatori
# Pmax: 1000-2000W per ciclisti amatori

# 3. Filtrare outliers prima fitting
import pandas as pd
df = pd.read_csv('data.csv')
df = df[(df['power_W'] > 0) & (df['power_W'] < 3000)]  # esempio
```

### ❌ "Insufficient data" error

**Soluzione:**
```python
# Assicurarsi di avere almeno 20 punti
t_data = np.array([...])  # almeno 20 valori
p_data = np.array([...])  # almeno 20 valori

if len(t_data) < 20:
    print("❌ Dati insufficienti. Minimo 20 punti richiesti.")
else:
    params = calculate_omnipd_model(t_data, p_data)
```

---

## 🔴 Problemi Performance

### ❌ App lento / Freezes

**Possibili Cause:**
1. File FIT molto grande
2. Troppe feature di plotting attive
3. Ram insufficiente

**Soluzioni:**
```bash
# 1. Controllare memoria usata
# Linux: top, htop
# macOS: Activity Monitor
# Windows: Task Manager

# 2. Chiudere altre applicazioni
# Specialmente browser, IDE

# 3. Disabilitare preview grafico real-time (se presente)

# 4. Aumentare memoria per Python
# Nei prossimi setting IDE se possibile
```

### ❌ Grafico Plotly lento a caricareusi

**Soluzione:**
```bash
# Aggiornare Plotly
pip install --upgrade plotly

# Oppure usare rendering statico (PNG)
# Invece di HTML interattivo
```

---

## 🔴 Problemi Linux/macOS

### ❌ "No module named 'matplotlib.backends.backend_qt5agg'"

**Soluzione:**
```bash
pip install PyQt5
# Oppure
pip install PySide6
```

### ❌ Display server error su SSH / Headless

**Soluzione:**
```bash
# Usare backend non-interattivo
export QT_QPA_PLATFORM=offscreen
python main.py

# Oppure usare Xvfb (virtual display)
xvfb-run python main.py
```

---

## 🔴 Problemi Windows

### ❌ "WindowsError: [Error 5] Access is denied"

**Soluzione:**
```bash
# Lanciare PowerShell come Administrator
# Oppure assicurarsi permessi su cartella

# Se problema di antivirus, aggiungere eccezione:
# Settings → Virus & threat protection → Manage exceptions
```

### ❌ Python non trovato dopo installazione

**Soluzioni:**
```bash
# 1. Aggiungere Python a PATH manualmente
# Oppure reinstallare e spuntare "Add Python to PATH"

# 2. Verificare Python 3
python --version
# Oppure
python3 --version
```

---

## 🔵 Debug Avanzato

### Abilitare Logging Dettagliato

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.debug("Messaggio debug")
```

### Traceback Completo

```bash
# Lanciare Python con traceback completo
python -X dev main.py

# Oppure
python -m pdb main.py  # debugger interattivo
```

### Controllare Versioni Package

```bash
pip show PySide6 pandas numpy fitparse plotly scipy
```

### Verificare sys.path

```python
import sys
for path in sys.path:
    print(path)
```

---

## ✅ Checklist Diagnostic

Se hai problemi, eseguire questa checklist:

- [ ] Python ≥3.8 installato? `python --version`
- [ ] Virtual environment attivato? `which python` vs `which python3`
- [ ] File requirements.txt installato? `pip list | grep -E 'PySide|pandas'`
- [ ] Nella cartella corretta? `pwd` oppure `cd /path/to/bFactor-Project`
- [ ] File __init__.py presenti? `ls __init__.py PEFFORT/__init__.py`
- [ ] Permessi cartelle OK? `ls -la` controllare permessi
- [ ] Display disponibile? (su SSH: `echo $DISPLAY`)
- [ ] RAM sufficiente? `free -h` o Task Manager
- [ ] File FIT valido? Provare con file di test noto

---

## 📞 Report Bug

Se il problema persiste:

1. **Raccogliere info di sistema:**
```bash
python << 'EOF'
import sys, platform, pkg_resources

print(f"Python: {sys.version}")
print(f"OS: {platform.system()} {platform.release()}")
print(f"Packages: {[f'{d.project_name}=={d.version}' for d in pkg_resources.working_set]}")
EOF
```

2. **Salvare debug log:**
```bash
python -u main.py 2>&1 | tee bug_report.log
```

3. **Allegare a bug report:**
   - bug_report.log
   - Output di `python -V`
   - Output di `pip list`
   - Descrizione steps per riprodurre

---

**Versione**: 0.2  
**Data**: 16 Gennaio 2026  
**Status**: ✅ Verificato
