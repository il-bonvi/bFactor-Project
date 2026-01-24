import os
import re
import sys
import pandas as pd


def read_and_prepare(csv_dir):
    """
    Legge tutti i CSV nella cartella, concatena e applica tutte le trasformazioni
    esattamente come nel file originale. Restituisce (df, raw_df, csv_files, single_csv).
    """
    if not os.path.isdir(csv_dir):
        print(f"Errore: la cartella specificata non esiste: {csv_dir}")
        sys.exit(1)

    csv_files = sorted([f for f in os.listdir(csv_dir) if f.lower().endswith('.csv')])
    if not csv_files:
        print(f"Nessun file CSV trovato nella cartella: {csv_dir}")
        sys.exit(1)

    print(f"Trovati {len(csv_files)} file CSV in '{csv_dir}': {csv_files}")
    single_csv = len(csv_files) == 1

    dfs = []
    for f in csv_files:
        fp = os.path.join(csv_dir, f)
        try:
            dfi = pd.read_csv(fp)
            basename = os.path.splitext(f)[0]
            if single_csv:
                initials = ''
            else:
                basename_no_year = re.sub(r"\s*\d{4}\s*$", "", basename).strip()
                parts = [p for p in re.split(r"\s+", basename_no_year) if p]
                initials = ''.join([p[0].upper() for p in parts if p]) if parts else ''
            dfi['AthleteInit'] = initials
            dfs.append(dfi)
        except Exception as e:
            print(f"Attenzione: impossibile leggere '{fp}': {e}")

    if not dfs:
        print(f"Nessun CSV valido letto in: {csv_dir}")
        sys.exit(1)

    raw_df = pd.concat(dfs, ignore_index=True, sort=False)
    df = raw_df.copy()

    # Drop/clean columns
    df = df.drop(columns=['id'], errors='ignore')
    if 'Weight' in df.columns:
        df = df.drop(columns=['Weight'])

    def valid_rpe(val):
        try:
            if pd.isnull(val):
                return False
            s = str(val).strip()
            m = re.search(r"(\d+)", s)
            if m:
                v = int(m.group(1))
                return 1 <= v <= 10
            try:
                v = float(s)
                return 1 <= int(round(v)) <= 10
            except:
                return False
        except:
            return False

    def valid_feel(val):
        try:
            if pd.isnull(val):
                return False
            s = str(val).strip()
            m = re.search(r"(\d+)", s)
            if m:
                v = int(m.group(1))
                return 1 <= v <= 4
            try:
                v = float(s)
                return 1 <= int(round(v)) <= 4
            except:
                return False
        except:
            return False

    if 'RPE' in df.columns:
        non_null_rpe = df['RPE'].dropna()
        perc_valid_rpe = non_null_rpe.apply(valid_rpe).mean() if len(non_null_rpe) else 0
        if perc_valid_rpe < 0.7:
            df = df.drop(columns=['RPE'])

    if 'Feel' in df.columns:
        non_null_feel = df['Feel'].dropna()
        perc_valid_feel = non_null_feel.apply(valid_feel).mean() if len(non_null_feel) else 0
        if perc_valid_feel < 0.7:
            df = df.drop(columns=['Feel'])

    def remove_emoji(text):
        if not isinstance(text, str):
            return text
        return re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)

    if 'Name' in df.columns:
        df['Name'] = df['Name'].apply(remove_emoji)
        if 'AthleteInit' in df.columns:
            def append_initials(name, init):
                try:
                    sname = '' if pd.isnull(name) else str(name).strip()
                    sinit = '' if pd.isnull(init) else str(init).strip()
                    if sinit == '':
                        return sname
                    if re.search(r"\([A-Z]{1,5}\)$", sname):
                        return sname
                    return f"{sname} ({sinit})" if sname != '' else f"({sinit})"
                except:
                    return name
            df['Name'] = [append_initials(n, i) for n, i in zip(df['Name'], df['AthleteInit'])]

    def get_75_status(row):
        for val in row.values:
            if isinstance(val, str):
                val_lower = val.lower()
                if '#dnf' in val_lower:
                    return 'DNF'
                if '#almdnf' in val_lower:
                    return '+'
        return ''

    df['75%'] = df.apply(get_75_status, axis=1)

    # Conversions/renames
    if 'Distance' in df.columns:
        df['Distance'] = (df['Distance'] / 1000).round(1)
    if 'Climbing' in df.columns:
        df['Climbing'] = df['Climbing'].fillna(0).astype(int)
    if 'Moving Time' in df.columns:
        def normalize_moving_time(x):
            try:
                if pd.isnull(x) or str(x).strip() == '':
                    return ''
                s = str(x).strip()
                if re.match(r'^\d+(?:\.\d+)?$', s):
                    secs = int(round(float(s)))
                    h, rem = divmod(secs, 3600)
                    m, sec = divmod(rem, 60)
                    return f"{h}:{m:02d}:{sec:02d}" if h > 0 else f"{m}:{sec:02d}"
                parts = s.split(':')
                if len(parts) == 3:
                    h = int(parts[0]); m = int(parts[1]); sec = int(round(float(parts[2])))
                    return f"{h}:{m:02d}:{sec:02d}"
                if len(parts) == 2:
                    m = int(parts[0]); sec = int(round(float(parts[1])))
                    return f"{m}:{sec:02d}"
                return s
            except Exception:
                return ''
        df['Moving Time'] = df['Moving Time'].apply(normalize_moving_time)
    if 'Avg Speed' in df.columns:
        df['Avg Speed'] = (df['Avg Speed'] * 3.6).round(1)
    if 'Intensity' in df.columns:
        df = df.drop(columns=['Intensity'])
    if 'Variability' in df.columns:
        df = df.drop(columns=['Variability'])
    if 'Work' in df.columns:
        df['Work'] = (df['Work'] / 1000).round(0)
    if 'Work >FTP' in df.columns:
        df = df.rename(columns={'Work >FTP': 'Work >CP'})
        df['Work >CP'] = (df['Work >CP'] / 1000).round(0)
    if 'All Work>CP' in df.columns:
        df['All Work>CP'] = df['All Work>CP'].round(0)
    if 'Time Above CP' in df.columns:
        def format_seconds(s):
            try:
                s = int(s)
                if s < 60:
                    return f"0:{s:02d}"
                m, s = divmod(s, 60)
                h, m = divmod(m, 60)
                if h > 0:
                    return f"{h}:{m:02d}:{s:02d}"
                else:
                    return f"{m}:{s:02d}"
            except:
                return ''
        df['Time Above CP'] = df['Time Above CP'].apply(format_seconds)
    if 'Avg Above CP' in df.columns:
        df['Avg Above CP'] = df['Avg Above CP'].round(0)
    if 'kJ/h/kg' in df.columns:
        df['kJ/h/kg'] = df['kJ/h/kg'].round(1)
    if 'kJ/h/kg>CP' in df.columns:
        df['kJ/h/kg>CP'] = df['kJ/h/kg>CP'].round(1)

    err_sensitive_cols = [
        'Avg Power', 'Average Power', 'Norm Power', 'Ride pMax', 'Work', 'Work >CP',
        'All Work>CP', 'Time Above CP', 'Avg Above CP', 'kJ/h/kg', 'kJ/h/kg>CP',
        'kJ', 'kJ > CP', 'ALL kJ > CP'
    ]
    for idx, row in df.iterrows():
        if any(isinstance(val, str) and '#errpwr' in val for val in row.values):
            for col in err_sensitive_cols:
                if col in df.columns:
                    df.at[idx, col] = float('nan')
        if any(isinstance(val, str) and '#errhr' in val for val in row.values):
            for col in ['Avg HR', 'Max HR']:
                if col in df.columns:
                    df.at[idx, col] = float('nan')

    if 'Date' in df.columns:
        parsed_dates = pd.to_datetime(raw_df['Date'], errors='coerce')
        date_only = parsed_dates.dt.normalize()
        if 'AthleteInit' not in df.columns:
            df['AthleteInit'] = ''
        sort_frame = pd.DataFrame({'_DateOnly': date_only, '_AthleteInit': raw_df.get('AthleteInit', pd.Series(['']*len(raw_df)))})
        sort_frame['_AthleteInit'] = sort_frame['_AthleteInit'].fillna('').astype(str).str.upper()
        df = df.reset_index(drop=True)
        sort_frame = sort_frame.reset_index(drop=True)
        df = pd.concat([df, sort_frame], axis=1)
        df = df.sort_values(['_DateOnly', '_AthleteInit']).drop(columns=['_DateOnly', '_AthleteInit'])
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%d/%m')

    return df, raw_df, csv_files, single_csv
