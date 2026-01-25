import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib as mpl
import pandas as pd
import numpy as np


FEEL_COLORS = {
    1: '#6633cc',
    2: '#009e80',
    3: '#dbac00',
    4: '#ff7f0e',
    5: '#dd0447',
}


def build_table_figure(df, raw_df, args, logo_file, bg_color):
    """
    Ricrea la pagina tabella (dati + statistiche) con la stessa logica.
    Restituisce (fig, df_table) dove df_table è la tabella principale con colonne finali.
    """
    # Mappa rinomina colonne
    col_map = {
        'Date': 'Date',
        'Name': 'Race',
        'Distance': 'Dist (km)',
        'Climbing': 'El (m)',
        'Moving Time': 'Time',
        'Avg Speed': 'Avg (km/h)',
        'Avg HR': 'Avg HR',
        'Max HR': 'Max HR',
        'Avg Power': 'AvgP (W)',
        'Average Power': 'AvgP (W)',
        'Norm Power': 'NP (W)',
        'Ride pMax': 'PMax (W)',
        'Activity pMax': 'PMax (W)',
        'Work': 'kJ',
        'Work >CP': 'kJ > CP',
        'Work >FTP': 'kJ > CP',
        'All Work>CP': 'ALL kJ > CP',
        'kJ/kg': 'kJ/kg',
        'kJ/kg > CP': 'kJ/kg>CP',
        'kJ/h/kg': 'kJ/h/kg',
        'kJ/h/kg>CP': 'kJ/h/kg>CP',
        'Time Above CP': 't > CP',
        'Avg Above CP': 'AvgP > CP',
        '75%': '75%'
    }

    preferred_order = [
        'Date', 'Race', 'Dist (km)', 'El (m)', 'Time', 'Avg (km/h)',
        'Avg HR', 'Max HR', 'AvgP (W)', 'NP (W)', 'PMax (W)',
        'kJ', 'kJ > CP', 'ALL kJ > CP', 'kJ/kg', 'kJ/kg>CP', 'kJ/h/kg', 'kJ/h/kg>CP',
        't > CP', 'AvgP > CP', 'RPE', 'Feel', '75%'
    ]

    df_table = df.rename(columns=col_map)
    final_cols = [c for c in preferred_order if c in df_table.columns]
    df_table = df_table[final_cols]

    def parse_time_to_seconds(val):
        import numpy as _np
        if pd.isnull(val):
            return None
        try:
            if isinstance(val, (int, _np.integer)):
                return int(val)
            if isinstance(val, (float, _np.floating)):
                return int(round(val))
        except Exception:
            pass
        s = str(val).strip()
        if s == '':
            return None
        parts = s.split(':')
        try:
            if len(parts) == 3:
                h = int(parts[0]); m = int(parts[1]); sec = float(parts[2])
                return int(round(h*3600 + m*60 + sec))
            if len(parts) == 2:
                m = int(parts[0]); sec = float(parts[1])
                return int(round(m*60 + sec))
            return int(round(float(s)))
        except Exception:
            return None

    def format_seconds(sec):
        if sec is None:
            return ''
        sec = int(sec)
        h, rem = divmod(sec, 3600)
        m, s = divmod(rem, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"

    def mean_time_str(series):
        vals = [parse_time_to_seconds(v) for v in series]
        vals = [v for v in vals if v is not None]
        if not vals:
            return ''
        mean_sec = int(round(sum(vals)/len(vals)))
        return format_seconds(mean_sec)

    # Mean row
    cols = list(df.columns)
    mean_row = []
    for idx, col in enumerate(cols):
        if idx == 0:
            mean_row.append('')
        else:
            if col.lower() == 'moving time':
                mean_row.append(mean_time_str(df[col]))
            elif col.lower() == 'time above cp':
                mean_row.append(mean_time_str(df[col]))
            elif pd.api.types.is_numeric_dtype(df[col]):
                mean_val = df[col].mean()
                if pd.api.types.is_float_dtype(df[col]):
                    decimals = df[col].astype(str).str.split('.').str[1].str.len().max()
                    decimals = 1 if decimals and decimals > 0 else 0
                    mean_row.append(round(mean_val, decimals))
                else:
                    mean_row.append(int(round(mean_val)))
            else:
                mean_row.append('')

    df_with_mean = pd.concat([df, pd.DataFrame([mean_row], columns=df.columns)], ignore_index=True)

    def sum_time_str(series):
        vals = [parse_time_to_seconds(v) for v in series]
        vals = [v for v in vals if v is not None]
        if not vals:
            return ''
        return format_seconds(sum(vals))

    total_row = []
    num_races = len(df)
    empty_total_cols = set([
        'Avg Speed', 'Avg HR', 'Max HR', 'Avg Power', 'Average Power', 'Normalized Power', 'NP', 'Max Power',
        'Avg Above CP', 'kJ/h/kg', 'kJ/h/kg>CP', 'RPE', 'Feel'
    ])
    for idx, col in enumerate(cols):
        if idx == 0:
            total_row.append(str(num_races))
        else:
            colname = col_map.get(col, col)
            if col.lower() == 'moving time':
                total_row.append(sum_time_str(df[col]))
            elif col.lower() == 'time above cp':
                total_row.append(sum_time_str(df[col]))
            elif any(col.lower() == c.lower() for c in empty_total_cols):
                total_row.append('')
            elif colname in ['NP (W)', 'PMax (W)']:
                total_row.append('')
            elif pd.api.types.is_numeric_dtype(df[col]):
                total_val = df[col].sum()
                if pd.api.types.is_float_dtype(df[col]):
                    decimals = df[col].astype(str).str.split('.').str[1].str.len().max()
                    decimals = 1 if decimals and decimals > 0 else 0
                    total_row.append(round(total_val, decimals))
                else:
                    total_row.append(int(round(total_val)))
            else:
                total_row.append('')

    df_with_mean_total = pd.concat([df_with_mean, pd.DataFrame([total_row], columns=df.columns)], ignore_index=True)

    df_stats = df_with_mean_total.rename(columns=col_map)
    df_stats = df_stats[final_cols].iloc[-2:]

    finished_mask = (df_table['75%'] != 'DNF') if '75%' in df_table.columns else pd.Series([True]*len(df_table))
    df_finished = df_table[finished_mask]
    finished_row = []
    empty_total_cols = set([
        'Avg (km/h)', 'Avg HR', 'Max HR', 'AvgP (W)', 'NP (W)', 'PMax (W)',
        'AvgP > CP', 'kJ/h/kg', 'kJ/h/kg>CP', 'RPE', 'Feel'
    ])
    for idx, col in enumerate(df_table.columns):
        if idx == 0:
            finished_row.append(str(len(df_finished)))
        else:
            col_lower = col.lower()
            if col_lower in ['time', 'moving time', 't > cp', 'time above cp']:
                vals = [parse_time_to_seconds(v) for v in df_finished[col]]
                vals = [v for v in vals if v is not None]
                finished_row.append('' if not vals else format_seconds(int(sum(vals))))
            elif col in empty_total_cols:
                finished_row.append('')
            elif pd.api.types.is_numeric_dtype(df_finished[col]):
                total_val = df_finished[col].sum()
                if pd.api.types.is_float_dtype(df_finished[col]):
                    decimals = df_finished[col].astype(str).str.split('.').str[1].str.len().max()
                    decimals = 1 if decimals and decimals > 0 else 0
                    finished_row.append(round(total_val, decimals))
                else:
                    finished_row.append(int(round(total_val)))
            else:
                finished_row.append('')

    avg_finished_row = []
    std_finished_row = []
    for idx, col in enumerate(df_table.columns):
        if idx == 0:
            avg_finished_row.append(''); std_finished_row.append('')
        else:
            col_lower = col.lower()
            if col_lower in ['time', 'moving time', 't > cp', 'time above cp']:
                vals = [parse_time_to_seconds(v) for v in df_finished[col]]
                vals = [v for v in vals if v is not None]
                if not vals:
                    avg_finished_row.append(''); std_finished_row.append('')
                else:
                    mean_sec = int(round(sum(vals)/len(vals)))
                    avg_finished_row.append(format_seconds(mean_sec))
                    std_sec = int(round(np.std(vals)))
                    std_finished_row.append(format_seconds(std_sec))
            elif pd.api.types.is_numeric_dtype(df_finished[col]):
                mean_val = df_finished[col].mean(); std_val = df_finished[col].std()
                if pd.api.types.is_float_dtype(df_finished[col]):
                    decimals = df_finished[col].astype(str).str.split('.').str[1].str.len().max()
                    decimals = 1 if decimals and decimals > 0 else 0
                    avg_finished_row.append(round(mean_val, decimals))
                    std_finished_row.append(int(round(std_val)) if decimals == 0 else round(std_val, decimals))
                else:
                    avg_finished_row.append(int(round(mean_val)))
                    std_finished_row.append(int(round(std_val)))
            else:
                avg_finished_row.append(''); std_finished_row.append('')

    avg_total_row = df_stats.iloc[0].copy()
    total_row = df_stats.iloc[1].copy()
    df_stats = pd.DataFrame([avg_finished_row, std_finished_row, avg_total_row, finished_row, total_row], columns=df_stats.columns)

    if 'Race' in final_cols:
        race_idx = final_cols.index('Race')
        df_stats.iloc[0, race_idx] = 'AvgFinished'
        df_stats.iloc[1, race_idx] = 'StdDev'
        df_stats.iloc[2, race_idx] = 'AvgTotal'
        df_stats.iloc[3, race_idx] = 'Finished'
        df_stats.iloc[4, race_idx] = 'Total'
    else:
        race_idx = None

    df_stats = df_stats.astype(object)
    for i, val in enumerate(df_stats.iloc[1]):
        if race_idx is not None and i != race_idx and str(val).strip() != '':
            df_stats.iloc[1, i] = f'± {val}'

    # Header colors
    header_color_map = {c: '#c2c2c2' for c in [
        'Date', 'Race', 'Dist (km)', 'El (m)', 'Time', 'Avg (km/h)',
        'Avg HR', 'Max HR', 'AvgP (W)', 'NP (W)', 'PMax (W)',
        'kJ', 'kJ > CP', 'ALL kJ > CP', 'kJ/kg', 'kJ/kg>CP', 'kJ/h/kg', 'kJ/h/kg>CP',
        't > CP', 'AvgP > CP', 'RPE', 'Feel', '75%']}
    header_textcolor_map = {
        'Date': "#222222", 'Race': "#222222", 'Dist (km)': '#222222', 'El (m)': '#222222', 'Time': '#222222', 'Avg (km/h)': '#222222',
        'Avg HR': "#e41111", 'Max HR': '#e41111', 'AvgP (W)': "#a200ff", 'NP (W)': '#a200ff', 'PMax (W)': '#a200ff',
        'kJ': "#19BE59", 'kJ > CP': "#d11212", 'ALL kJ > CP': '#d11212', 'kJ/kg': '#19BE59', 'kJ/kg>CP': '#d11212',
        'kJ/h/kg': '#19BE59', 'kJ/h/kg>CP': '#d11212', 't > CP': "#944DCE", 'AvgP > CP': '#944DCE', 'RPE': '#222222', 'Feel': '#222222', '75%': '#222222'
    }
    header_colors = [header_color_map.get(col, '#e0e0e0') for col in final_cols]
    header_textcolors = [header_textcolor_map.get(col, '#222222') for col in final_cols]

    # Column widths
    fig_tmp, ax_tmp = plt.subplots(figsize=(12, 2))
    header_font = mpl.font_manager.FontProperties(size=8)
    cell_font = mpl.font_manager.FontProperties(size=7)
    header_widths = []
    value_widths = []
    for col in final_cols:
        t = ax_tmp.text(0, 0, str(col), fontproperties=header_font)
        fig_tmp.canvas.draw()
        bbox = t.get_window_extent(renderer=fig_tmp.canvas.get_renderer())
        header_widths.append(bbox.width)
        t.remove()
        max_val_width = 0
        for val in df_table[col].astype(str):
            tval = ax_tmp.text(0, 0, val, fontproperties=cell_font)
            fig_tmp.canvas.draw()
            vbbox = tval.get_window_extent(renderer=fig_tmp.canvas.get_renderer())
            max_val_width = max(max_val_width, vbbox.width)
            tval.remove()
        value_widths.append(max_val_width)
    plt.close(fig_tmp)

    col_widths_pt = [max(h, v) + 10 for h, v in zip(header_widths, value_widths)]
    total_pt = sum(col_widths_pt)
    fig_width = (total_pt / 72) if total_pt > 0 else 4
    fig_width = min(max(fig_width, 4), 50)

    main_rows = len(df_table)
    stats_rows = len(df_stats)
    fig_height = min(0.05 + main_rows*0.2 + 1*0.2 + stats_rows*0.2 + 0.05, 50)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('off')

    # Title
    title_text = args.custom_title  # sarà sostituito dal chiamante se serve
    if title_text:
        fig.suptitle(title_text, fontsize=20, fontweight='bold', y=0.98)
        try:
            fig.subplots_adjust(top=0.95, left=0.03, right=0.97, bottom=0.01)
        except Exception:
            pass

    # Helpers
    def df_to_clean_list(df_in):
        force_one_decimal_cols = {"Avg (km/h)", "Dist (km)", "kJ/kg", "kJ/kg>CP", "kJ/h/kg", "kJ/h/kg>CP"}
        force_int_avg_cols = {"kJ", "kJ > CP", "ALL kJ > CP", "AvgP > CP", "Avg HR", "Max HR", "AvgP (W)", "NP (W)", "PMax (W)"}
        result = []
        for row_idx, row in enumerate(df_in.itertuples(index=False, name=None)):
            formatted_row = []
            for i, v in enumerate(row):
                col = df_in.columns[i]
                colname = str(col)
                is_stat_row = False
                if 'Race' in df_in.columns:
                    race_idx = list(df_in.columns).index('Race')
                    if row[race_idx] in ['AvgFinished', 'AvgTotal', 'Finished', 'Total']:
                        is_stat_row = True
                if (row_idx in [0,1,3,4] or is_stat_row) and colname in force_int_avg_cols:
                    if pd.isnull(v) or v == "":
                        formatted_row.append("")
                    else:
                        try:
                            formatted_row.append(str(int(round(float(v)))))
                        except Exception:
                            formatted_row.append(str(v))
                elif pd.isnull(v) or v == "":
                    formatted_row.append("")
                elif pd.api.types.is_numeric_dtype(df_in[col]):
                    if colname in force_one_decimal_cols:
                        try:
                            formatted_row.append(f"{float(v):.1f}")
                        except Exception:
                            formatted_row.append(str(v))
                    elif isinstance(v, float) and v.is_integer():
                        formatted_row.append(str(int(v)))
                    else:
                        if isinstance(v, float):
                            nonnull = df_in[col].dropna()
                            if not nonnull.empty and all(x == int(x) or (round(x,1) == x) for x in nonnull):
                                formatted_row.append(f"{v:.1f}")
                            else:
                                formatted_row.append(str(v))
                        else:
                            formatted_row.append(str(v))
                else:
                    formatted_row.append(str(v))
            result.append(formatted_row)
        return result

    table_data = df_to_clean_list(df_table)
    blank_row = [''] * len(final_cols)
    table_data.append(blank_row)
    table_data.append(list(final_cols))
    for row in df_to_clean_list(df_stats):
        table_data.append(list(row))

    col_widths = [w/total_pt for w in col_widths_pt] if total_pt > 0 else [1/len(final_cols)]*len(final_cols)
    table = ax.table(cellText=table_data, colLabels=final_cols, loc='center', cellLoc='center', colWidths=[w/sum(col_widths_pt) for w in col_widths_pt])
    table.auto_set_font_size(False)
    table.set_fontsize(7)

    for (row, col), cell in table.get_celld().items():
        cell.get_text().set_verticalalignment('center')
        is_main_header = row == 0
        is_stats_header = row == len(df_table) + 2
        if is_main_header or is_stats_header:
            if col < len(header_colors):
                cell.set_facecolor(header_colors[col])
                cell.get_text().set_color(header_textcolors[col])
                cell.set_edgecolor(header_textcolors[col])
            else:
                cell.set_facecolor('#e0e0e0')
                cell.get_text().set_color('#222222')
                cell.set_edgecolor('#222222')
            cell.set_linewidth(1.2)
            cell.get_text().set_fontweight('bold')
        elif row == len(df_table) + 1:
            cell.set_facecolor('white'); cell.set_linewidth(0); cell.visible_edges = ''
            cell.get_text().set_text("")
        elif row > 0:
            if col < len(header_textcolors):
                cell.set_edgecolor(header_textcolors[col])
            else:
                cell.set_edgecolor('#222222')
            stats_start = len(df_table) + 2
            stats_colors = ['#ffe599', '#fff2cc', '#c9daf8', '#d9ead3', '#f4cccc']
            if stats_start <= row < stats_start + 5:
                if row - stats_start == 2:
                    cell.get_text().set_fontstyle('italic'); cell.get_text().set_fontsize(6)
                if row - stats_start == 3:
                    cell.set_facecolor('#b6d7a8')
                else:
                    cell.set_facecolor(stats_colors[row - stats_start])

            if 1 <= row <= len(df_table):
                colname = final_cols[col]
                is_dnf_row = False
                try:
                    dnf_col_idx = final_cols.index('75%') if '75%' in final_cols else None
                    if dnf_col_idx is not None:
                        dnf_val = table_data[row-1][dnf_col_idx]
                        if isinstance(dnf_val, str) and dnf_val.strip().upper() == 'DNF':
                            is_dnf_row = True
                except Exception:
                    pass
                if is_dnf_row:
                    cell.get_text().set_fontstyle('italic')
                    cell.get_text().set_color('#a9441a')
                else:
                    dnf_col_idx = final_cols.index('75%') if '75%' in final_cols else None
                    non_dnf_mask = []
                    for r in range(len(df_table)):
                        if dnf_col_idx is not None:
                            dnf_val = table_data[r][dnf_col_idx]
                            non_dnf_mask.append(not (isinstance(dnf_val, str) and dnf_val.strip().upper() == 'DNF'))
                        else:
                            non_dnf_mask.append(True)
                    duration_cols = {'Time', 'Moving Time', 't > CP', 'Time Above CP'}
                    if colname in duration_cols:
                        def to_sec(val):
                            if pd.isnull(val) or val == '':
                                return None
                            parts = str(val).split(':')
                            try:
                                if len(parts) == 2:
                                    return int(parts[0])*60 + int(parts[1])
                                elif len(parts) == 3:
                                    return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
                            except (ValueError, IndexError):
                                return None
                            return None
                        col_vals_sec = np.array([to_sec(v) for v in df_table[colname].values], dtype=float)
                        col_vals_sec = np.array([v for v, keep in zip(col_vals_sec, non_dnf_mask) if keep and v is not None], dtype=float)
                        try:
                            cell_val_sec = to_sec(table_data[row-1][col])
                        except Exception:
                            cell_val_sec = None
                        if len(col_vals_sec) > 0 and cell_val_sec is not None:
                            max_val = np.nanmax(col_vals_sec); min_val = np.nanmin(col_vals_sec)
                            if np.isclose(cell_val_sec, max_val, atol=1e-8):
                                cell.get_text().set_fontweight('bold')
                            if np.isclose(cell_val_sec, min_val, atol=1e-8):
                                cell.get_text().set_fontstyle('italic'); cell.get_text().set_color('#0a2fa5')
                    elif pd.api.types.is_numeric_dtype(df_table[colname]) or colname in ['kJ/kg', 'kJ/kg>CP']:
                        col_vals = df_table[colname].values
                        try:
                            cell_val = float(df_table[colname].iloc[row-1]) if colname in ['kJ/kg', 'kJ/kg>CP'] else float(table_data[row-1][col])
                        except (ValueError, TypeError):
                            cell_val = None
                        col_vals_num = np.array([v for v, keep in zip(col_vals, non_dnf_mask) if pd.notnull(v) and keep], dtype=float)
                        if len(col_vals_num) > 0 and cell_val is not None:
                            if colname == 'Feel':
                                try:
                                    val_int = int(cell_val)
                                    color = FEEL_COLORS.get(val_int, '#222222')
                                    cell.get_text().set_color(color); cell.get_text().set_fontweight('bold')
                                except Exception:
                                    cell.get_text().set_color('#222222'); cell.get_text().set_fontweight('bold')
                            else:
                                max_val = np.nanmax(col_vals_num); min_val = np.nanmin(col_vals_num)
                                if np.isclose(cell_val, max_val, atol=1e-8):
                                    cell.get_text().set_fontweight('bold')
                                if np.isclose(cell_val, min_val, atol=1e-8):
                                    cell.get_text().set_fontstyle('italic'); cell.get_text().set_color('#0a2fa5')

    return fig, df_table
