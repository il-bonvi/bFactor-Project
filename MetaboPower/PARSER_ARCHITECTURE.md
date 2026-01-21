# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
PARSER ARCHITECTURE METAPOW
Struttura modulare per supportare molteplici metabolimetri

DESCRIZIONE:
La nuova architettura suddivide il parsing in moduli specializzati, uno per ogni
tipo di metabolimetro supportato. Questo permette scalabilità e manutenibilità.

MODULI:
1. parser_metapow.py (ORCHESTRATOR)
   ├─ Classe MetabolitDataParser
   ├─ Delega a parser specifici in base al profilo
   ├─ Sincronizza dati e metadati tra delegati
   └─ Fornisce interfaccia unificata (load_file, load_file_with_profile, get_data, etc.)

2. cortex_metapow.py (CORTEX XLSX)
   ├─ Classe CortexMetabolitParser
   ├─ Legge XLSX con header @ riga 117, dati @ riga 119
   ├─ Estrae metadati da celle specifiche (C27, C28, C30, etc.)
   ├─ Detalla marcatore TURN (colonna 3)
   ├─ Normalizza decimali
   └─ Ritorna (data, metadata) via get_data() e get_metadata()

3. genericsv_metapow.py (CSV GENERICO)
   ├─ Classe GenericCSVParser
   ├─ Autodetect separatore (,;TAB) e intestazione
   ├─ Estrae colonne tempo e potenza per keyword
   ├─ Normalizza decimali
   └─ Ritorna (data, metadata) via get_data() e get_metadata()

FLUSSO DI CARICAMENTO:
1. GUI chiama parser_metapow.MetabolitDataParser.load_file_with_profile(path, profile_name)
2. Parser legge il profilo da config_metapow.IMPORT_PROFILES
3. In base a settings['format'], delega:
   - "xlsx" → cortex_metapow.CortexMetabolitParser.load()
   - "csv"  → genericsv_metapow.GenericCSVParser.load()
4. Parser delegato carica il file e ritorna risultato
5. Parser orchestrator sincronizza self.data e self.metadata
6. GUI accede a parser.get_data() e parser.get_metadata()

AGGIUNGERE UN NUOVO METABOLIMETRO:
1. Creare nuovo file: <nomemetabolimetro>_metapow.py
2. Implementare classe con metodo load(file_path: str, settings: Dict) → Dict
3. Implementare get_data() e get_metadata()
4. Aggiungere profilo in config_metapow.IMPORT_PROFILES:
   {
       "metabolimetro_name": {
           "name": "Display Name",
           "description": "Description",
           "file_extensions": ["ext1", "ext2"],
           "settings": { ... profilo-specifico ... }
       }
   }
5. Aggiungere delegato in parser_metapow.py __init__
6. Aggiungere caso nel load_file_with_profile() per il formato

CONVENZIONI:
- Ogni modulo ha una sola classe principale: <Metabolimetro>MetabolitParser
- Metodo load() ritorna sempre Dict con chiavi: success, file_type, rows, columns, metadata, error
- Metodo get_data() ritorna pd.DataFrame o None
- Metodo get_metadata() ritorna Dict con metadati estratti
- Metodo get_summary() ritorna Dict con info sul caricamento

PROFILI ATTUALI:
- cortex_xlsx: Cortex XLSX (header=117, subheader=118, data_start=119)
- generic_csv: CSV generico con autodetect (nessun vincolo di struttura)
"""
