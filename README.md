# bFactor Project
**Versione**: 0.5
**Data Ultimo Update**: 23 Gennaio 2026  
**Status**: ✅ In Produzione (Core Modules)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)]()
[![Science](https://img.shields.io/badge/Sports_Science-Performance-orange?style=for-the-badge)]()
[![Status](https://img.shields.io/badge/Status-In_Development-green?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)]()

> **Advanced Cycling Performance Analysis Suite**

**bFactor Project** è una suite software desktop sviluppata per allenatori, data analist e scienziati dello sport. Combina diversi strumenti per il monitoraggio delle sessioni e di periodi di allenamento.

---

## 🌟 Funzionalità Principali

Il software si divide in diversi moduli principali accessibili da un launcher unificato:

### 1. 📊 PEFFORT Analyzer (Performance/Effort)
Analisi automatizzata dei file di allenamento provenienti dai ciclocomputer.
* **Parsing File FIT:** Importazione diretta e pulizia dati.
* **Rilevamento Automatico:** Algoritmi per identificare sprint ed "efforts" sostenuti sopra specifiche soglie fisiologiche.
* **Zonal Analysis:** Classificazione degli sforzi basata su $CP$.
* **Reporting:** Generazione automatica di report PDF dettagliati con grafici interattivi (Plotly).

### 2. ⚡ OmniPD Calculator
Modellazione avanzata della curva Potenza-Durata.
* **Modello OmniPD:** Il modello OmniPD implementato è un modello unificato per descrivere l’intero profilo MMP, dagli sprint massimali agli sforzi di endurance prolungata. Integra Pmax, CP e W' in una formulazione fisiologicamente coerente, superando i limiti del modello CP classico alle durate brevi e molto lunghe. Introduce il concetto di W' efficace, che limita realisticamente l’espressione della riserva anaerobica nelle durate brevi e preserva W' come capacità fissa nel dominio severo. Per durate >30 min incorpora un termine log-lineare di fatica a lungo termine, migliorando l’accuratezza su dati MMP real-world. Il risultato è un modello continuo, interpretabile e robusto, adatto sia all’analisi scientifica sia all’applicazione pratica nel training e nel performance profiling. https://pubmed.ncbi.nlm.nih.gov/32131692/

### 3. 🧮 Omniselector
Filtraggio avanzato dei dati di una curva di potenza per l’analisi della curva CP (modello OmniPD) su subset specifici.
* **Filtri personalizzati:** Permette di selezionare intervalli temporali, esclusione di periodi, filtri per tipologia di sforzo o condizioni.
* **Analisi mirata:** Calcolo della curva CP/OmniPD solo sui dati filtrati, per valutazioni specifiche massimali.
* **Visualizzazione interattiva:** Grafici aggiornati in tempo reale in base ai filtri applicati.

### 4. 🫁 MetaboPower
Analisi e confronto tra test al metabolimetro e potenziometro.
* **Importazione dati:** Supporto per file da diversi metabolimetri (attualmente Cortex) e file FIT da powermeter.
* **Confronto soglie ventilatorie:** Visualizzazione e confronto tra VT1/VT2 rilevati da dati metabolici e potenza reale.
* **Grafici multiparametrici:** Overlay di parametri metabolici e potenza per analisi approfondita.
* **Esportazione dati e report:** Funzionalità di export e generazione report in fase di sviluppo.

### 5. 👥 bTeam (prototipo NOT WORKING)
Scheletro grafico e core di una piattaforma per la reportistica e il tracking delle squadre.
* **Gestione squadre e atleti:** CRUD completo, filtro per squadra, dettaglio atleta con dati opzionali e API key Intervals.icu.
* **Tracking attività:** Inserimento manuale, visualizzazione attività, preparazione per import automatico da Intervals.icu.
* **Storage locale sicuro:** Tutti i dati sensibili restano in locale, configurazione tramite file dedicato.
* **In sviluppo:** Modulo in fase prototipale, pensato per la gestione avanzata di team e la generazione di report settimanali.

### 6. 🚧 Work in Proggress

---

## 🛠️ Stack Tecnologico

Il progetto è costruito in **Python 3.10+** utilizzando:
* **GUI:** `PySide6` (Qt)
* **Data Science:** `NumPy`, `Pandas`, `SciPy`
* **Visualizzazione:** `Matplotlib`, `Plotly`
* **File Handling:** `fitparse`, parsing CSV/XLSX
* **Database/Storage:** `SQLite` tramite `SQLAlchemy ORM` (bTeam), storage locale sicuro
* **Export:** `xhtml2pdf` (report PDF)
* **Networking/API:** `requests` (integrazione Intervals.icu, in sviluppo)
* **Gestione configurazione:** file JSON custom (es. `bteam_config.json`, esclusi da Git)
* **Altre dipendenze:** gestione avanzata di temi/stili, modularizzazione tramite package Python

---

## 🚀 Installazione e Utilizzo

### Requisiti
Assicurati di avere Python 3.10+ installato con le librerie necessarie (requirements.txt)

### 1. Clona la repository
```bash
git clone https://github.com/il-bonvi/bFactor-Project.git
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
| 🎓 **Education** | BSc in Sport and Exercise Science · MSc Student in Physical Performance Science |
| 🏋️‍♂️🚴 **Expertise** | Sport Scientist & Performance Coach · Endurance and Strength Training |
| ⛰️ **Specialization** | Cycling & Endurance Sports|
| 📍 **Location** | Trento, Italy |
| 📫 **Contact** | https://linktr.ee/bonvicin.coaching |



---

## ⚖️ Copyright & License

> [!IMPORTANT]
> **© 2026 Andrea Bonvicin - bFactor Project.** > **PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI.** > La condivisione, distribuzione o riproduzione del codice sorgente è severamente vietata senza autorizzazione scritta dell'autore.

---