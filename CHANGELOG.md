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