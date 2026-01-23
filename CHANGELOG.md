## [0.5] - 2026-01-23
### bTeam - Dashboard squadre/atleti (prototipo)
- Gestione squadre, atleti e attività con database locale (SQLite, SQLAlchemy)
- CRUD completo per squadre e atleti, filtro per squadra
- Dettaglio atleta con campi opzionali: data di nascita, peso, altezza, CP, W', note
- Salvataggio e visualizzazione API key Intervals.icu per ogni atleta
- Integrazione Intervals.icu (placeholder, import allenamenti in arrivo)
- Inserimento manuale attività
- Configurazione storage locale tramite bteam_config.json (in .gitignore)
- Tutti i dati sensibili restano locali

## [0.4.1] - 2026-01-22
### MetaboPower - Grafici e confronto VT1
- Aggiunti grafici di confronto VT1 tra parametri metabolici e potenza
- Tabella riassuntiva confronto VT1 (valori, differenze, note)
- Migliorata visualizzazione soglie ventilatorie

## [0.4] - 2026-01-21
### MetaboPower - Nuovo modulo di analisi metabolimetrica
**Descrizione**: Modulo specializzato per l'analisi comparativa dei dati metabolimetrici (respiratori) rispetto ai dati di potenza misurata dal power meter durante test incrementali (ramp test).

**Utilizzo**:
1. **Importazione dati**: 
   - Selezionare profilo metabolimetro (Cortex XLSX o CSV generico... nuovi in futuro)
   - Caricare file dati respiratori (VO₂, VCO₂, RER, potenza cardiaca, ecc.)
   - Caricare file dati FIT dal power meter (potenza in watt)

2. **Cortex**:
  A. **Selezione automatica della rampa**:
    - Interfaccia interattiva su grafico FIT per delimitare inizio/fine rampa
    - Click automatico per individuare transizione potenza zero → potenza effettiva

  B. **Visualizzazione confronto**:
    - Overlay temporale metabolimetro (potenza media) vs power meter
    - Medie mobili: 1s (istantaneo), 15s (primaria), 30s (smoothed)
    - Rilevamento automatico soglie ventilatorie (VT1, VT2, MAP) con visualizzazione verticale

  C. **Analisi multi-parametro**:
    - Tab per ogni parametro metabolico (VO₂, VCO₂, RER, FC, ecc.)
    - Traccia della potenza sovrapposta per correlazione diretta
    - Identificazione delle transizioni metaboliche

**Caratteristiche tecniche**:
- Architettura modulare: Parser specializzati, estrazione dati, plotting, GUI
- Supporto multi-metabolimetro tramite profili configurabili
- Export grafica completabile dall'utente (non ancora implementata)

## [0.3.1] - 2026-01-20
### Omniselector - UI Refinement
- **Redesign della sidebar**:
  - Sezioni sempre visibili: DATI, FILTRI, ELABORAZIONE, RISULTATI
  - Layout pulito senza bordi e sfondi grigi
- **Convertitore tempo integrato**:
  - Accorpamento nella sezione FILTRI (finestre temporali)
  - Aggiunta nota "fast conv" per chiarezza funzionale
  - Riduzione dello spazio laterale occupato
- **Coerenza con OmniPD Calculator**:
  - Stili uniformi tra i moduli
  - Theme selector identico in posizione e configurazione
  - Applicazione corretta del tema globale tramite `get_style()`
  - Stili specifici gestiti da `apply_widget_styles()`

## [0.3] - 2026-01-20
### Omniselector - Nuovo modulo
- Implementato modulo Omniselector completo con architettura modulare
- Workflow semplificato: caricamento CSV → filtraggio automatico → elaborazione
- Separazione chiara delle responsabilità:
  - **GUI**: Solo orchestrazione e callbacks UI
  - **Core**: Logica di business e calcoli
  - **Plotting**: Rendering grafici
  - **Widgets**: Componenti riutilizzabili
  - **UI Builder**: Costruzione interfaccia
- Codice più manutenibile e testabile
- Riuso facilitato delle funzioni tra moduli

### Miglioramenti grafici
  - Massimizzata area di visualizzazione grafici
  - Rimossi margini eccessivi su tutti e 4 i lati
- **OmniPD Calculator**: Aggiunto `tight_layout(pad=0.5)` a tutti i grafici
  - Coerenza visiva tra i moduli

## [0.2] - 2026-01-20
- Refactoring completo di gui_omniPD.py:
  - Tutti i widget principali ora aggiornano i colori in base al tema selezionato tramite update_widget_styles.
  - I pulsanti principali e le label usano colori dinamici dal tema.
  - I grafici vengono aggiornati automaticamente al cambio tema.
- Refactoring completo di plotting_omniPD.py:
  - Tutte le funzioni di plotting accettano ora il parametro theme e usano i colori dal dizionario TEMI.
  - I colori di sfondo, testo, linee e legende sono ora coerenti con il tema selezionato.
- Centralizzazione degli stili e dei colori in shared/styles.py (TEMI).
- Migliorata la coerenza visiva tra i vari componenti dell'interfaccia.