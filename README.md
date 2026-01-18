# ⚡ bFactor Project
**Versione**: 0.2
**Data Ultimo Update**: 18 Gennaio 2026  
**Status**: ✅ In Produzione (Core Modules)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Science](https://img.shields.io/badge/Sports_Science-Performance-orange?style=for-the-badge)](https://univr.it)
[![Status](https://img.shields.io/badge/Status-In_Development-green?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)]()

> **Advanced Cycling Performance Analysis Suite**

**bFactor Project** è una suite software desktop sviluppata per allenatori, scienziati dello sport e atleti d'élite. Combina l'analisi dettagliata dei file di allenamento (`.fit`) con modelli matematici avanzati di potenza-durata (OmniPD), offrendo una visione completa sulle capacità fisiologiche dell'atleta.

Sviluppato da **Andrea Bonvicin** (MSc Student, Univr, Endurance & Strenght Coach), il progetto colma il divario tra la teoria scientifica ($CP$, $W'$, $P_{max}$) e l'applicazione pratica sul campo.

---

## 🌟 Funzionalità Principali

Il software si divide in due moduli principali accessibili da un launcher unificato:

### 1. 📊 PEFFORT Analyzer (Performance/Effort)
Analisi automatizzata dei file di allenamento provenienti dai ciclocomputer.
* **Parsing File FIT:** Importazione diretta e pulizia dati.
* **Rilevamento Automatico:** Algoritmi per identificare sprint ed "efforts" sostenuti sopra specifiche soglie fisiologiche.
* **Zonal Analysis:** Classificazione degli sforzi basata su $CP$, $VO_2max$ e capacità anaerobica.
* **Reporting:** Generazione automatica di report PDF dettagliati con grafici interattivi (Plotly).

### 2. ⚡ OmniPD Calculator
Modellazione avanzata della curva Potenza-Durata.
* **Modello OmniPD:** Il modello OmniPD implementato è un modello unificato per descrivere l’intero profilo MMP, dagli sprint massimali agli sforzi di endurance prolungata. Integra Pmax, CP e W' in una formulazione fisiologicamente coerente, superando i limiti del modello CP classico alle durate brevi e molto lunghe. Introduce il concetto di W' efficace, che limita realisticamente l’espressione della riserva anaerobica nelle durate brevi e preserva W' come capacità fissa nel dominio severo. Per durate >30 min incorpora un termine log-lineare di fatica a lungo termine, migliorando l’accuratezza su dati MMP real-world. Il risultato è un modello continuo, interpretabile e robusto, adatto sia all’analisi scientifica sia all’applicazione pratica nel training e nel performance profiling. **https://pubmed.ncbi.nlm.nih.gov/32131692/**

---

## 🛠️ Stack Tecnologico

Il progetto è costruito in **Python 3.10+** utilizzando:
* **GUI:** `PySide6` (Qt)
* **Data Science:** `NumPy`, `Pandas`, `SciPy`
* **Visualizzazione:** `Matplotlib` e `Plotly`
* **File Handling:** `fitparse`
* **Export:** `xhtml2pdf`

---

## 🚀 Installazione e Utilizzo

### Requisiti
Assicurati di avere Python 3.10+ installato con le librerie necessarie (requirements.txt)

### 1. Clona la repository
```bash
git clone [https://github.com/tuo-username/bFactor-Project.git](https://github.com/tuo-username/bFactor-Project.git)
cd bFactor-Project
```

### 2. Installa dipendenze
```bash
pip install -r requirements.txt
```

### 3. Avvia l'applicazione
```bash
python main.py
```
---

## 👤 Autore

| **Andrea Bonvicin** | |
| :--- | :--- |
| 🎓 **Qualifiche** | MSc Student in Physical Performance Science @ [Univr](https://www.univr.it) |
| 🚴 **Expertise** | Performance Coach | Mountain Sports & Cycling Specialist |
| 📍 **Sede** | Trento, Italia |
| 📫 **Contatti** | [Inserisci qui il tuo link LinkedIn o Email] |

---

## ⚖️ Copyright & License

> [!IMPORTANT]
> **© 2026 Andrea Bonvicin - bFactor Project.** > **PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI.** > La condivisione, distribuzione o riproduzione del codice sorgente è severamente vietata senza autorizzazione scritta dell'autore.

---