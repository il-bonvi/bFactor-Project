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