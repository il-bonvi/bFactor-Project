# INSTALLATION GUIDE - bFactor Performance Suite

**Guida completa per l'installazione e configurazione.**

---

## 📋 Prerequisiti

- **Sistema Operativo**: Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)
- **Python**: 3.8 o superiore (3.10+ consigliato)
- **Spazio Disco**: ~500 MB
- **RAM**: 4 GB minimo (8 GB consigliato)

---

## 🔧 Installazione Rapida

### 1. Clonare il Repository

```bash
git clone https://github.com/user/bFactor-Project.git
cd bFactor-Project
```

### 2. Creare Virtual Environment (Consigliato)

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installare Dipendenze

```bash
pip install -r requirements.txt
```

Se il file non esiste, installarle manualmente:

```bash
pip install PySide6 pandas numpy fitparse plotly matplotlib xhtml2pdf scipy
```

### 4. Verificare Installazione

```bash
python -c "from PEFFORT.gui_interface import EffortAnalyzer; print('✅ PEFFORT OK')"
python -c "from omniPD_calculator import OmniPDAnalyzer; print('✅ OmniPD OK')"
```

### 5. Lanciare l'Applicazione

```bash
python main.py
```

---

## 🐍 Configurazione Python

### Versione Consigliata

| Versione | Status | Note |
|----------|--------|------|
| 3.8 | ⚠️ Minimo | Supported, ma vecchio |
| 3.9 | ✅ OK | Stabile |
| **3.10+** | ✅ Consigliato | Migliore performance |
| 3.12 | ✅ OK | Più recente |

### Controllare Versione Python

```bash
python --version
```

### Aggiornare Python

**Windows:**
- Scaricare da https://www.python.org/downloads/
- O usare: `winget install Python.Python.3.11`

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

---

## 📦 Dipendenze Dettagliate

### Core Dependencies

| Pacchetto | Versione | Uso |
|-----------|----------|-----|
| **PySide6** | ≥6.2 | GUI Framework |
| **pandas** | ≥1.3 | Data manipulation |
| **numpy** | ≥1.20 | Array operations |
| **scipy** | ≥1.7 | Calcoli scientifici |

### File Processing

| Pacchetto | Versione | Uso |
|-----------|----------|-----|
| **fitparse** | ≥1.2 | Parsing file FIT |
| **matplotlib** | ≥3.4 | Visualizzazione base |
| **plotly** | ≥5.0 | Grafici interattivi |

### Export

| Pacchetto | Versione | Uso |
|-----------|----------|-----|
| **xhtml2pdf** | ≥0.2 | Export PDF |

### Installazione Singoli Pacchetti

```bash
# Se install da requirements.txt fallisce, provare singolarmente:
pip install PySide6==6.6.0
pip install pandas==2.0.3
pip install numpy==1.24.3
pip install fitparse==1.2.0
pip install plotly==5.14.0
pip install matplotlib==3.7.1
pip install xhtml2pdf==0.2.15
pip install scipy==1.11.0
```

---

## 🔍 Troubleshooting Installazione

### Problema: "ModuleNotFoundError: No module named 'PySide6'"

**Soluzione:**
```bash
pip install --upgrade PySide6
# O reinstallare tutto
pip install --force-reinstall -r requirements.txt
```

### Problema: "Python version not supported"

**Soluzione:**
```bash
# Verificare versione
python --version

# Se < 3.8, aggiornare Python
# Usare poi l'interprete nuovo:
python3.11 -m venv venv
```

### Problema: Permission Denied su Linux/macOS

**Soluzione:**
```bash
sudo chown -R $USER:$USER /path/to/bFactor-Project
pip install --user -r requirements.txt
```

### Problema: "fitparse" non si installa

**Soluzione (alternativa):**
```bash
pip install fitparse-fork
# Oppure da source:
git clone https://github.com/dtcooper/python-fitparse.git
cd python-fitparse
pip install -e .
```

---

## 🖥️ IDE Setup

### VS Code

1. **Installare Estensioni:**
   - Python (Microsoft)
   - Pylance
   - PySide6 Tools (optional)

2. **Configurare Interpreter:**
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Scegliere `.venv\Scripts\python.exe`

3. **Configurare settings.json:**

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.analysis.extraPaths": [
        "${workspaceFolder}"
    ],
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python"
}
```

### PyCharm

1. **Configurare Project Interpreter:**
   - File → Settings → Project → Python Interpreter
   - Aggiungere venv → OK

2. **Mark Directories:**
   - Click destro su folder → "Mark Directory As" → Sources Root

---

## 🧪 Test Post-Installazione

### 1. Test Imports

```bash
python -c "
from PEFFORT.gui_interface import EffortAnalyzer
from PEFFORT.core_engine import parse_fit
from PEFFORT.export_manager import create_pdf_report
from omniPD_calculator import OmniPDAnalyzer
from shared.styles import get_style
print('✅ Tutti gli import OK')
"
```

### 2. Test Launcher GUI

```bash
python main.py
```

Dovrebbe aprirsi la finestra del launcher. Test:
- ✅ Finestra si apre senza errori
- ✅ Tema Forest Green visibile
- ✅ 4 pulsanti presenti
- ✅ Clic su PEFFORT apre Effort Analyzer

### 3. Test PEFFORT Standalone

```bash
python -m PEFFORT.gui_interface
```

### 4. Test OmniPD Standalone

```bash
python omniPD_calculator/main_omnipd.py
```

---

## 🔄 Aggiornamenti

### Aggiornare Dipendenze

```bash
pip install --upgrade -r requirements.txt
```

### Aggiornare Singolo Pacchetto

```bash
pip install --upgrade PySide6
```

### Pulire Cache Python

```bash
# Rimuovere __pycache__
find . -type d -name __pycache__ -exec rm -r {} +

# Rimuovere .pyc
find . -type f -name "*.pyc" -delete
```

---

## 🚀 Avvio Programmatico

### Da Script Python

```python
from PySide6.QtWidgets import QApplication
from PEFFORT.gui_interface import EffortAnalyzer

app = QApplication([])
analyzer = EffortAnalyzer()
analyzer.showMaximized()
app.exec()
```

### Importare come Modulo

```python
import sys
sys.path.insert(0, '/path/to/bFactor-Project')

from PEFFORT.core_engine import parse_fit, create_efforts
from omniPD_calculator.omnipd_core import calculate_omnipd_model

# Usare i moduli
df = parse_fit('myfile.fit')
efforts = create_efforts(df, ftp=280)
```

---

## 🐞 Debug Mode

### Abilitare Logging

```bash
# Lanciare con logging debug
python -u main.py 2>&1 | tee debug.log
```

### Controllare Versioni Installate

```bash
pip list | grep -E 'PySide|pandas|numpy|fitparse|plotly'
```

### Check Python Path

```bash
python -c "import sys; print('\n'.join(sys.path))"
```

---

## 📞 Supporto

Se hai problemi:

1. **Controllare questo file** per la soluzione
2. **Eseguire i test post-installazione**
3. **Ricreare virtual environment**:
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # o .\venv\Scripts\Activate.ps1 su Windows
   pip install -r requirements.txt
   ```

---

**Versione**: 0.2  
**Data**: 16 Gennaio 2026  
**Status**: ✅ Verificato
