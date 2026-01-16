"""
STRUTTURA PROGETTO bFactor - Refactoring Completato
================================================

## Struttura del Progetto

bFactor-Project/
├── __init__.py                          # Package root
├── main.py                              # 🚀 Launcher principale (NUOVO)
│
└── PEFFORT/                             # Modulo PEFFORT
    ├── __init__.py                      # Package PEFFORT
    ├── main.py                          # Support file (aggiornato)
    ├── core_engine.py                   # Logica pura (aggiornato import)
    ├── export_manager.py                # Esportazione PDF (aggiornato import)
    └── gui_interface.py                 # GUI principale (aggiornato import)


## Passaggi Completati

### ✅ 1. Sistemazione Package
- Creato `__init__.py` nella root del progetto
- Creato `__init__.py` in PEFFORT/
- Permette import come package: `from PEFFORT.gui_interface import ...`

### ✅ 2. Refactoring Import in PEFFORT
- **gui_interface.py**: Cambiati import da `import core_engine` a `from .core_engine import`
- **export_manager.py**: Cambiati import da `import core_engine` a `from .core_engine import`
- Gli import sono ora **relativi**, consentendo esecuzione da qualsiasi percorso

### ✅ 3. Riscritto main.py (root)
Nuovo Launcher elegante con:
- **Tema Forest Green** (dark mode professionale)
- **3 Pulsanti Principali**:
  - 📈 PEFFORT Analyzer - Apre l'analizzatore in finestra massimizzata
  - 🎯 Omniselector - Messaggio "In fase di sviluppo"
  - ⚡ OmniPD Calculator - Messaggio "In fase di sviluppo"
- **Stili Professionali**:
  - Colori dinamici (hover effect, pressed state)
  - Funzioni `lighten_color()` e `darken_color()` per animazioni
  - Font personalizzati e layout elegante
- **Gestione Finestre**:
  - La finestra PEFFORT rimane in memoria
  - Multipli clic non creano finestre duplicate
  - Supporto per portare in primo piano la finestra PEFFORT

### ✅ 4. Pulizia File PEFFORT
- Rimosso blocco `if __name__ == "__main__"` da PEFFORT/main.py
- Convertito in funzione `launch_peffort()` (opzionale)
- Nessun blocco attivo che interferisce con il launcher principale


## Come Usare il Progetto

### Esecuzione Normale (consigliato)
```bash
cd c:\Users\bonvi\Documents\GitHub\bFactor-Project
python main.py
```

Questo apre il launcher principale con i 3 pulsanti.


### Uso Programmatico
```python
# Importare moduli come package
from PEFFORT.gui_interface import EffortAnalyzer, get_style
from PEFFORT.core_engine import parse_fit, create_efforts
from PEFFORT.export_manager import create_pdf_report

# Usare i moduli
analyzer = EffortAnalyzer()
analyzer.show()
```


## Vantaggi della Nuova Struttura

1. **Modularità**: Ogni modulo è indipendente e importabile
2. **Scalabilità**: Facile aggiungere altri moduli (Omniselector, OmniPD)
3. **Manutenibilità**: Chiaro punto di ingresso e gerarchie package
4. **Professionalità**: Launcher elegante con tema coerente
5. **Portabilità**: Import relativi funzionano da qualsiasi percorso


## Configurazione IDE (VS Code)

Per miglior supporto dell'intellisense, aggiungere a `.vscode/settings.json`:
```json
{
    "python.analysis.extraPaths": [
        "${workspaceFolder}"
    ]
}
```


## Prossimi Passi Suggeriti

1. Implementare i moduli Omniselector e OmniPD
2. Aggiungere __init__.py a quelle cartelle
3. Importarli nel launcher con i pulsanti funzionanti
4. Aggiungere file di configurazione (config.py)
5. Implementare logging centralizzato


---
Progetto trasformato in suite modulare professionale! 🎉
"""
