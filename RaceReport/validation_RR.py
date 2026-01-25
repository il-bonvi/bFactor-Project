import re
import pandas as pd


def valid_rpe(val):
    """Valida se un valore RPE è nel range 1-10"""
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
        except (ValueError, TypeError):
            return False
    except (ValueError, TypeError, AttributeError):
        return False


def valid_feel(val):
    """Valida se un valore Feel è nel range 1-4"""
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
        except (ValueError, TypeError):
            return False
    except (ValueError, TypeError, AttributeError):
        return False


def validate_rpe_column(df):
    """Rimuove la colonna RPE se meno del 70% dei valori è valido"""
    if 'RPE' in df.columns:
        non_null_rpe = df['RPE'].dropna()
        perc_valid_rpe = non_null_rpe.apply(valid_rpe).mean() if len(non_null_rpe) else 0
        if perc_valid_rpe < 0.7:
            df = df.drop(columns=['RPE'])
    return df


def validate_feel_column(df):
    """Rimuove la colonna Feel se meno del 70% dei valori è valido"""
    if 'Feel' in df.columns:
        non_null_feel = df['Feel'].dropna()
        perc_valid_feel = non_null_feel.apply(valid_feel).mean() if len(non_null_feel) else 0
        if perc_valid_feel < 0.7:
            df = df.drop(columns=['Feel'])
    return df
