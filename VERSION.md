# bFactor Performance Suite - Versioning

## Versione Corrente: 0.2

**Data Release**: 16 Gennaio 2026  
**Status**: ✅ Working

---

## Changelog Versioni

### 🎉 v0.2 - OmniPD Integration & Easter Egg
**Data**: 16 Gennaio 2026

#### Nuove Funzionalità
- ⚡ **OmniPD Analyzer Integration**
  - Implementato metodo `open_omnipd()` nel launcher
  - Supporto gestione finestra massimizzata
  - Evita duplicazione finestre (come PEFFORT)
  - Import: `from omniPD_calculator import OmniPDAnalyzer`

- 💦 **Easter Egg "Amalia allenati"**
  - Pulsante speciale nel launcher principale
  - Messaggio divertente: "UOOOPS NON FUNZ"
  - Testo: "Amalia non vuole allenarsi. Riprova un altro giorno"
  - Click su Omniselector attiva lo stesso messaggio

#### Modifiche ai File
- **main.py (root)**
  - Aggiunto `self.omnipd_window = None`
  - Aggiunto import OmniPDAnalyzer
  - Aggiunto pulsante "💦 Amalia allenati" (indice [1,0])
  - Implementato `open_omnipd()` method
  - Collegamento btn_omnipd a `open_omnipd()`

- **README.md**
  - Aggiunto numero versione (0.2)
  - Aggiunta sezione Amalia allenati (Easter Egg)
  - Riordino funzionalità

- **CHANGELOG.md**
  - Update versione da 1.0 a 0.2
  - Tracciamento modifiche v0.2 vs v1.0

- **REFACTORING_SUMMARY.md**
  - Aggiunto versione 0.2 nel header
  - Documentazione open_omnipd()
  - Dettagli easter egg

- **STRUTTURA_PROGETTO.md**
  - Aggiunto versione 0.2 nel header
  - Update da 3 a 4 pulsanti principali
  - Documentazione gestione omnipd_window

#### Pulsanti Launcher (stato attuale)
| Pulsante | Status | Colore | Funzione |
|----------|--------|--------|----------|
| 📈 PEFFORT Analyzer | ✅ Operativo | Verde (#16a34a) | open_peffort() |
| 🎯 Omniselector | ⏳ Sviluppo | Blu (#2563eb) | show_in_development() |
| ⚡ OmniPD Calculator | ✅ Nuovo | Viola (#7c3aed) | open_omnipd() |
| 💦 Amalia allenati | 🎉 Easter Egg | Arancione (#ea580c) | show_in_development() |

---

### 🚀 v1.0 - Initial Modular Suite (Base)
**Data**: 16 Gennaio 2026

#### Caratteristiche Principali
- Trasformazione da singola app a suite modulare
- Package structure con __init__.py
- Launcher centralizzato (main.py root)
- Tema Forest Green integrato
- Import relativi in PEFFORT
- 3 pulsanti principali:
  - PEFFORT Analyzer ✅
  - Omniselector ⏳
  - OmniPD Calculator ⏳

#### Moduli Base
- PEFFORT (core_engine, gui_interface, export_manager)
- OmniPD Calculator (placeholder)
- Percentile Selector (placeholder)
- Shared styles (Forest Green theme)

---

## Roadmap Futuro

### v0.3 (Prossima)
- [ ] Implementare Omniselector base
- [ ] Miglioramenti UI launcher
- [ ] Configurazione centralizzata (config.py)

### v1.0+ (Lungo termine)
- [ ] Implementare OmniPD Calculator completo
- [ ] Implementare Percentile Selector
- [ ] Sistema logging centralizzato
- [ ] Database persistenza
- [ ] Export/Import dati
- [ ] Tema personalizzato per utente

---

## File Versionati

Ultimo aggiornamento: **16 Gennaio 2026**

| File | Versione | Status |
|------|----------|--------|
| main.py | 0.2 | ✅ Aggiornato |
| README.md | 0.2 | ✅ Aggiornato |
| CHANGELOG.md | 0.2 | ✅ Aggiornato |
| REFACTORING_SUMMARY.md | 0.2 | ✅ Aggiornato |
| STRUTTURA_PROGETTO.md | 0.2 | ✅ Aggiornato |
| VERSION.md | 0.2 | ✨ Nuovo |

---

## Come Controllare la Versione

```bash
# Visualizzare info versione
python main.py

# Leggere questo file
cat VERSION.md

# Controllare git tag (se disponibile)
git tag -l
```

---

**Maintained by**: Andrea Bonvicin  
**Project**: bFactor Performance Suite  
**License**: TBD
