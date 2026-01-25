import re
import pandas as pd


def remove_emoji(text):
    """Rimuove emoji e caratteri speciali da testo"""
    if not isinstance(text, str):
        return text
    return re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)


def append_initials_to_name(name, initials):
    """Aggiunge le iniziali al nome dell'atleta se non già presenti"""
    try:
        sname = '' if pd.isnull(name) else str(name).strip()
        sinit = '' if pd.isnull(initials) else str(initials).strip()
        if sinit == '':
            return sname
        if re.search(r"\([A-Z]{1,5}\)$", sname):
            return sname
        return f"{sname} ({sinit})" if sname != '' else f"({sinit})"
    except (ValueError, TypeError, AttributeError):
        return name


def normalize_moving_time(x):
    """Normalizza il tempo di movimento nel formato HH:MM:SS o MM:SS"""
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


def format_seconds(s):
    """Formatta secondi nel formato MM:SS o HH:MM:SS"""
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
    except (ValueError, TypeError):
        return ''


def get_75_status(row):
    """Estrae lo status 75% dalla riga (DNF o +)"""
    for val in row.values:
        if isinstance(val, str):
            val_lower = val.lower()
            if '#dnf' in val_lower:
                return 'DNF'
            if '#almdnf' in val_lower:
                return '+'
    return ''


def handle_error_flags(df):
    """Gestisce i flag #errpwr e #errhr invalidando i dati correlati"""
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
    return df


def format_numeric_columns(df):
    """Applica la formattazione a tutte le colonne numeriche secondo le regole"""
    if 'Distance' in df.columns:
        df['Distance'] = (df['Distance'] / 1000).round(1)
    if 'Climbing' in df.columns:
        df['Climbing'] = df['Climbing'].fillna(0).astype(int)
    if 'Moving Time' in df.columns:
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
        df['Time Above CP'] = df['Time Above CP'].apply(format_seconds)
    if 'Avg Above CP' in df.columns:
        df['Avg Above CP'] = df['Avg Above CP'].round(0)
    if 'kJ/h/kg' in df.columns:
        df['kJ/h/kg'] = df['kJ/h/kg'].round(1)
    if 'kJ/h/kg>CP' in df.columns:
        df['kJ/h/kg>CP'] = df['kJ/h/kg>CP'].round(1)
    return df
