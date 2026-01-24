import os
import re
import datetime
import pandas as pd


def compute_pdf_path_and_title(csv_dir, csv_files, single_csv, df, raw_df, custom_title=None):
    """
    Riproduce la logica originale per definire titolo e nome PDF.
    Restituisce (pdf_path, title_text).
    """
    folder_name = os.path.basename(os.getcwd())
    csv_title = folder_name.upper()  # usato solo a scopo informativo
    pdf_base = re.sub(r'\s*\d{4}\s*$', '', folder_name).replace(' ', '_')

    if 'Date' in df.columns:
        orig_df = raw_df.copy()
        if 'Date' in orig_df.columns:
            orig_df = orig_df.assign(_DateSort=pd.to_datetime(orig_df['Date'], errors='coerce'))
            orig_df = orig_df.sort_values('_DateSort')
            last_date = orig_df['Date'].dropna().iloc[-1] if not orig_df['Date'].dropna().empty else None
            try:
                last_date_dt = pd.to_datetime(last_date)
                last_date_str = last_date_dt.strftime('%Y_%m_%d')
            except Exception:
                last_date_str = str(last_date).replace('/', '').replace('-', '') if last_date is not None else 'DATA'
        else:
            last_date_str = 'DATA'
    else:
        last_date_str = 'DATA'
    pdf_path = f"{pdf_base}_RaceReport_{last_date_str}.pdf"

    if single_csv:
        try:
            fname = csv_files[0]
            base = os.path.splitext(fname)[0]
            bn = base.replace('_', ' ').strip()
            bn_no_year = re.sub(r"[ _]?\d{4}\s*$", "", bn).strip()
            pdf_base_single = re.sub(r"\s+", "_", bn_no_year).strip().lower()
            today_str = datetime.date.today().strftime('%Y_%m_%d')
            pdf_path = f"{pdf_base_single}_RaceReport_{today_str}.pdf"
        except Exception:
            pass

    # Titolo
    title_text = None
    if single_csv:
        try:
            fname = csv_files[0]
            base = os.path.splitext(fname)[0]
            bn = base.replace('_', ' ').strip()
            m = re.search(r"(\d{4})\s*$", bn)
            if m:
                year = m.group(1)
                name_part = bn[:m.start()].strip()
            else:
                m2 = re.search(r"(\d{4})", bn)
                if m2:
                    year = m2.group(1)
                    name_part = (bn[:m2.start()] + bn[m2.end():]).strip()
                else:
                    year = '2025'
                    name_part = bn
            title_text = f"{name_part.upper()} {year}".strip()
        except Exception:
            title_text = None
    elif custom_title:
        title_text = custom_title

    return pdf_path, title_text
