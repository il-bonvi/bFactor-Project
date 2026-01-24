import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def create_distance_figure(df, bg_color, logo_file):
    if 'Distance' not in df.columns or 'Date' not in df.columns:
        return None
    plot_df = df.copy().reset_index(drop=True)
    plot_df['Distance (km)'] = plot_df['Distance']
    if 'Climbing' in plot_df.columns:
        plot_df['Climbing (m)'] = plot_df['Climbing']
    plot_df = plot_df.iloc[::-1].reset_index(drop=True)
    finished_mask = (plot_df['75%'] != 'DNF') if '75%' in plot_df.columns else pd.Series([True]*len(plot_df))
    plot_df_finished = plot_df[finished_mask]
    y_labels = list(plot_df['Date'])
    dnf_mask = (plot_df['75%'] == 'DNF') if '75%' in plot_df.columns else pd.Series([False]*len(plot_df))
    DIST_COLOR = '#4169e1'
    TIME_COLOR = '#b22222'
    fig2, ax2 = plt.subplots(figsize=(9, max(4, len(plot_df)*0.45)))

    def time_to_hours(t):
        try:
            if pd.isnull(t) or str(t).strip() == '':
                return 0
            parts = [p for p in str(t).split(':') if p != '']
            parts = [float(p) for p in parts]
            if len(parts) == 3:
                h, m, s = parts
                return h + m/60 + s/3600
            if len(parts) == 2:
                m, s = parts
                return m/60 + s/3600
            return float(parts[0]) / 3600.0
        except Exception:
            return 0

    moving_hours = plot_df['Moving Time'].apply(time_to_hours) if 'Moving Time' in plot_df.columns else [0]*len(plot_df)
    moving_labels = plot_df['Moving Time'] if 'Moving Time' in plot_df.columns else ['']*len(plot_df)
    bars1 = ax2.barh(range(len(plot_df)), plot_df['Distance (km)'], color=DIST_COLOR, height=0.4, label='Distanza (km)')
    for i, bar in enumerate(bars1):
        if dnf_mask.iloc[i]:
            bar.set_hatch('//'); bar.set_edgecolor('#a9441a')

    mean_dist = plot_df_finished['Distance (km)'].mean()
    if pd.notna(mean_dist):
        ax2.axvline(mean_dist, color=DIST_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)

    ax3 = ax2.twiny()
    ELEV_COLOR = '#228B22'
    if 'Climbing (m)' in plot_df.columns:
        max_dist = plot_df['Distance (km)'].max()
        max_elev = plot_df['Climbing (m)'].max()
        elev_len = plot_df['Climbing (m)'] / max_elev * (max_dist * 0.5)
        bars3 = ax2.barh(range(len(plot_df)), elev_len, color=ELEV_COLOR, height=0.4, left=0, alpha=1, zorder=3)
        step = 250
        max_marker = ((int(max_elev) + step - 1) // step) * step
        for tick in range(step, max_marker+1, step):
            marker_x = tick / max_elev * (max_dist * 0.5)
            ax2.axvline(marker_x, color=ELEV_COLOR, linestyle=':', linewidth=1, alpha=0.5, zorder=4)
        mean_elev = plot_df_finished['Climbing (m)'].mean() if 'Climbing (m)' in plot_df_finished.columns else None
        if mean_elev is not None:
            mean_elev_x = mean_elev / max_elev * (max_dist * 0.5)
            ax2.axvline(mean_elev_x, color=ELEV_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)

    bars2 = ax3.barh([i+0.4 for i in range(len(plot_df))], moving_hours, color=TIME_COLOR, height=0.4, label='Durata (h)')
    for i, bar in enumerate(bars2):
        if dnf_mask.iloc[i]:
            bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
    ax2.set_yticks(range(len(plot_df)))
    ax2.set_yticklabels(y_labels, fontsize=7)
    n = len(plot_df)
    if n > 0:
        lower = -0.2; upper = (n - 1) + 0.6
        ax2.set_ylim(lower, upper)
        fig2.subplots_adjust(top=0.95, bottom=0.05)

    y_min, y_max = ax2.get_ylim(); y_text = y_min - 0.08
    ax2.text(mean_dist, y_text, f"{mean_dist:.1f}", color=DIST_COLOR, fontsize=6, ha='center', va='top', fontweight='bold', zorder=11)
    if 'Climbing (m)' in plot_df.columns:
        max_dist = plot_df['Distance (km)'].max()
        max_elev = plot_df['Climbing (m)'].max()
        step = 250
        max_marker = ((int(max_elev) + step - 1) // step) * step
        for tick in range(step, max_marker+1, step):
            marker_x = tick / max_elev * (max_dist * 0.5)
            ax2.text(marker_x, y_text, f'{tick}m', color='#000000', fontsize=6, ha='center', va='bottom', zorder=5)
        mean_elev = plot_df_finished['Climbing (m)'].mean() if 'Climbing (m)' in plot_df_finished.columns else None
        if mean_elev is not None:
            mean_elev_x = mean_elev / max_elev * (max_dist * 0.5)
            ax2.text(mean_elev_x, y_text, f"{mean_elev:.0f}", color=ELEV_COLOR, fontsize=6, ha='center', va='top', fontweight='bold', zorder=11)

    ax2.set_xlabel('Distanza (km)'); ax2.set_ylabel(''); ax2.set_title('Distanza e Durata per Gara'); ax2.grid(axis='x', linestyle=':', alpha=0.5)
    min_dist = plot_df['Distance (km)'].min(); max_dist = plot_df['Distance (km)'].max()
    ax2.set_xlim(left=0, right=max_dist+20)
    valid_hours = [h for h, f in zip(moving_hours, finished_mask) if h > 0 and f]
    max_time = max(valid_hours) if valid_hours else 1
    ax3.set_xlim(left=0, right=max_time+0.2)
    ax3.set_xlabel('Durata (h)', color='#222222'); ax3.tick_params(axis='x', colors='#222222')
    tick_step = 0.5; ticks = np.arange(0, max_time+0.5, tick_step)
    def hfmt(x, pos=None):
        h = int(x); m = int(round((x-h)*60)); return f"{h}:{m:02d}"
    ax3.set_xticks(ticks); ax3.set_xticklabels([hfmt(t) for t in ticks])
    if any(moving_hours):
        valid_hours = [h for h, f in zip(moving_hours, finished_mask) if h > 0 and f]
        mean_time = sum(valid_hours)/len(valid_hours) if valid_hours else 0
        mean_h = int(mean_time); mean_m = int(round((mean_time - mean_h) * 60))
        mean_time_str = f"{mean_h}:{mean_m:02d}"
        ax3.axvline(mean_time, color=TIME_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
        y_min3, y_max3 = ax3.get_ylim(); y_text3_top = y_max3 + 0.08
        ax3.text(mean_time, y_text3_top, mean_time_str, color=TIME_COLOR, fontsize=6, ha='center', va='bottom', fontweight='bold', zorder=11)
    if 'Name' in plot_df.columns:
        name_x = 1; font_kwargs = dict(fontsize=7, fontweight='bold', color='#222222', family='DejaVu Sans')
        dist_offset = 0.4; time_offset = 0.02
        for i, (bar, name, dist, t_h) in enumerate(zip(bars1, plot_df['Name'], plot_df['Distance (km)'], moving_hours)):
            name_str = str(name)
            tag75 = str(plot_df['75%'].iloc[i]).strip() if '75%' in plot_df.columns else ''
            if tag75 == '+':
                name_str += ' (DNF 75%+)'
            elif tag75.upper() == 'DNF':
                name_str += ' (DNF)'
            ax2.text(name_x, bar.get_y() + bar.get_height()/2, name_str, va='center', ha='left', color='#ffffff', fontsize=7, fontweight='bold', clip_on=True, transform=ax2.transData)
            if 'Climbing (m)' in plot_df.columns:
                elev_val = plot_df['Climbing (m)'].iloc[i]
                ax2.text(bar.get_width()+0.4, bar.get_y() + bar.get_height()/2, f"{dist:.1f} km | {elev_val} m", va='center', ha='left', **font_kwargs)
            else:
                ax2.text(bar.get_width()+0.4, bar.get_y() + bar.get_height()/2, f"{dist:.1f} km", va='center', ha='left', **font_kwargs)
        for i, (bar, t_label) in enumerate(zip(bars2, moving_labels)):
            ax3.text(bar.get_width()+0.02, bar.get_y() + bar.get_height()/2, f"{t_label}", va='center', ha='left', **font_kwargs)
    fig2.tight_layout()
    return fig2


def create_power_hr_figure(df, bg_color, logo_file):
    avg_power_col = None; np_col = None
    for col in df.columns:
        if col.lower() in ['avg power', 'average power', 'potenza media']:
            avg_power_col = col
        if col.lower() in ['normalized power', 'np', 'potenza normalizzata', 'norm power']:
            np_col = col
    if not (avg_power_col and np_col) or 'Date' not in df.columns:
        return None

    power_df = df.copy().reset_index(drop=True)
    power_df = power_df.iloc[::-1].reset_index(drop=True)
    finished_mask = (power_df['75%'] != 'DNF') if '75%' in power_df.columns else pd.Series([True]*len(power_df))
    power_df_finished = power_df[finished_mask]
    y_labels = list(power_df['Date'])
    dnf_mask = (power_df['75%'] == 'DNF') if '75%' in power_df.columns else pd.Series([False]*len(power_df))
    AVG_COLOR = '#ff8c00'; NP_COLOR = '#4682b4'; AVGHR_COLOR = "#000000"; MAXHR_COLOR = "#ec0c0c"
    fig3, axp = plt.subplots(figsize=(9, max(4, len(power_df)*0.45)))
    bar_height = 0.4
    bars_np = axp.barh(range(len(power_df)), power_df[np_col], color=NP_COLOR, height=bar_height, label='Potenza Normalizzata (W)', zorder=2)
    bars_avg = axp.barh(range(len(power_df)), power_df[avg_power_col], color=AVG_COLOR, height=bar_height, label='Potenza Media (W)', zorder=3)
    for i, bar in enumerate(bars_np):
        if dnf_mask.iloc[i]:
            bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
    for i, bar in enumerate(bars_avg):
        if dnf_mask.iloc[i]:
            bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
    axp.set_yticks(range(len(power_df))); axp.set_yticklabels(y_labels, fontsize=7)
    axp.set_xlabel('Potenza (W)'); axp.set_ylabel(''); axp.set_title('Potenza e FC per Gara'); axp.grid(axis='x', linestyle=':', alpha=0.5)
    max_power = max(power_df[avg_power_col].max(), power_df[np_col].max())
    min_power = min(power_df[avg_power_col].min(), power_df[np_col].min())
    min_x = min_power - 100; min_x = ((min_x + 49) // 50) * 50 if min_x > 0 else 0
    axp.set_xlim(left=min_x, right=max_power*1.15+10)
    n = len(power_df)
    if n > 0:
        lower = -0.2; upper = (n - 1) + 0.6
        axp.set_ylim(lower, upper); fig3.subplots_adjust(top=0.95, bottom=0.05)

    avg_hr_col = None; max_hr_col = None
    for col in df.columns:
        if col.lower() in ['avg hr', 'average hr', 'hr medio']:
            avg_hr_col = col
        if col.lower() in ['max hr', 'hr max', 'hr massimo']:
            max_hr_col = col
    if avg_hr_col and max_hr_col:
        axhr = axp.twiny()
        bars_maxhr = axhr.barh([i+0.4 for i in range(len(power_df))], power_df[max_hr_col], color=MAXHR_COLOR, height=bar_height, label='Max HR', zorder=2, alpha=1)
        bars_avghr = axhr.barh([i+0.4 for i in range(len(power_df))], power_df[avg_hr_col], color=AVGHR_COLOR, height=bar_height, label='Avg HR', zorder=3, alpha=1)
        for i, bar in enumerate(bars_maxhr):
            if dnf_mask.iloc[i]:
                bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
        for i, bar in enumerate(bars_avghr):
            if dnf_mask.iloc[i]:
                bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
        axhr.set_xlabel('Frequenza Cardiaca (bpm)', color='#222222'); axhr.tick_params(axis='x', colors='#222222')
        max_hr_val = max(power_df[avg_hr_col].max(), power_df[max_hr_col].max())
        min_hr = min(power_df[avg_hr_col].min(), power_df[max_hr_col].min())
        max_hr_ceil = int((max_hr_val + 19) // 20 * 20)
        min_xhr = min_hr - 10; min_xhr = ((min_xhr + 4) // 5) * 5 if min_xhr > 0 else 0
        axhr.set_xlim(left=min_xhr, right=max_hr_ceil)
        mean_avghr = power_df_finished[avg_hr_col].mean(); mean_maxhr = power_df_finished[max_hr_col].mean()
        y_minhr, y_maxhr = axhr.get_ylim(); y_texthr_top = y_maxhr + 0.08
        if pd.notna(mean_avghr):
            axhr.axvline(mean_avghr, color=AVGHR_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
            axhr.text(mean_avghr, y_texthr_top, f"{int(round(mean_avghr))}", color=AVGHR_COLOR, fontsize=6, ha='center', va='bottom', fontweight='bold', zorder=11)
        if pd.notna(mean_maxhr):
            axhr.axvline(mean_maxhr, color=MAXHR_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
            axhr.text(mean_maxhr, y_texthr_top, f"{int(round(mean_maxhr))}", color=MAXHR_COLOR, fontsize=6, ha='center', va='bottom', fontweight='bold', zorder=11)
        font_kwargs = dict(fontsize=7, fontweight='bold', color='#222222', family='DejaVu Sans')
        avghr_offset = 0.02; maxhr_offset = 0.02
        for i, (bar_avghr, bar_maxhr, avghr, maxhr) in enumerate(zip(bars_avghr, bars_maxhr, power_df[avg_hr_col], power_df[max_hr_col])):
            if pd.isnull(avghr) or pd.isnull(maxhr):
                continue
            avghr_str = str(int(avghr)) if isinstance(avghr, (int, float)) and float(avghr).is_integer() else str(avghr)
            maxhr_str = str(int(maxhr)) if isinstance(maxhr, (int, float)) and float(maxhr).is_integer() else str(maxhr)
            axhr.text(bar_avghr.get_width()+avghr_offset, bar_avghr.get_y() + bar_avghr.get_height()/2, f"{avghr_str} bpm", va='center', ha='left', color='#222222', fontsize=7, fontweight='bold', family='DejaVu Sans', zorder=4)
            axhr.text(bar_maxhr.get_width()+maxhr_offset, bar_maxhr.get_y() + bar_maxhr.get_height()/2, f"{maxhr_str} bpm", va='center', ha='left', color='#222222', fontsize=7, fontweight='bold', family='DejaVu Sans', zorder=4)

    mean_avg = power_df_finished[avg_power_col].mean(); mean_np = power_df_finished[np_col].mean()
    y_minp, y_maxp = axp.get_ylim(); y_textp = y_minp - 0.08
    if pd.notna(mean_avg):
        axp.axvline(mean_avg, color=AVG_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
        axp.text(mean_avg, y_textp, f"{int(round(mean_avg))}", color=AVG_COLOR, fontsize=6, ha='center', va='top', fontweight='bold', zorder=11)
    if pd.notna(mean_np):
        axp.axvline(mean_np, color=NP_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
        axp.text(mean_np, y_textp, f"{int(round(mean_np))}", color=NP_COLOR, fontsize=6, ha='center', va='top', fontweight='bold', zorder=11)

    font_kwargs = dict(fontsize=7, fontweight='bold', color='#222222', family='DejaVu Sans')
    avg_offset = 0.4; np_offset = 0.4; name_x = min_x + 1
    for i, (bar_avg, bar_np, name, avg, npw) in enumerate(zip(
        bars_avg, bars_np, power_df['Name'], power_df[avg_power_col], power_df[np_col]
    )):
        name_str = str(name)
        tag75 = str(power_df['75%'].iloc[i]).strip() if '75%' in power_df.columns else ''
        if tag75 == '+':
            name_str += ' (DNF 75%+)'
        elif tag75.upper() == 'DNF':
            name_str += ' (DNF)'
        avg_str = str(int(avg)) if isinstance(avg, (int, float)) and float(avg).is_integer() else str(avg)
        npw_str = str(int(npw)) if isinstance(npw, (int, float)) and float(npw).is_integer() else str(npw)
        if pd.isnull(avg) and pd.isnull(npw):
            axp.text(name_x, bar_avg.get_y() + bar_avg.get_height()/2, name_str, va='center', ha='left', color='#000000', fontsize=7, fontweight='bold', clip_on=True, transform=axp.transData)
        else:
            axp.text(name_x, bar_avg.get_y() + bar_avg.get_height()/2, name_str, va='center', ha='left', color='#ffffff', fontsize=7, fontweight='bold', clip_on=True, transform=axp.transData)
        if not pd.isnull(avg):
            axp.text(bar_avg.get_width()+avg_offset, bar_avg.get_y() + bar_avg.get_height()/2, f"{avg_str} W", va='center', ha='left', **font_kwargs)
        if not pd.isnull(npw):
            axp.text(bar_np.get_width()+np_offset, bar_np.get_y() + bar_np.get_height()/2, f"{npw_str} W", va='center', ha='left', color='#222222', fontsize=7, fontweight='bold', family='DejaVu Sans', zorder=4)

    fig3.tight_layout()
    return fig3


def create_work_figure(df, bg_color, logo_file):
    work_col = None; work_cp_col = None; kjhkg_col = None; kjhkgcp_col = None
    for col in df.columns:
        if col.lower() in ['work', 'work (kj)']:
            work_col = col
        if col.lower() in ['all work>cp', 'all work>cp (kj)']:
            work_cp_col = col
        if col.lower() in ['kj/h/kg']:
            kjhkg_col = col
        if col.lower() in ['kj/h/kg>cp']:
            kjhkgcp_col = col
    if not (work_col and work_cp_col and kjhkg_col and kjhkgcp_col) or 'Date' not in df.columns:
        return None

    work_df = df.copy().reset_index(drop=True)
    work_df = work_df.iloc[::-1].reset_index(drop=True)
    key_cols = [work_col, work_cp_col, kjhkg_col, kjhkgcp_col]
    valid_mask = work_df[key_cols].notnull().all(axis=1)
    work_df = work_df[valid_mask].reset_index(drop=True)
    finished_mask = (work_df['75%'] != 'DNF') if '75%' in work_df.columns else pd.Series([True]*len(work_df))
    work_df_finished = work_df[finished_mask]
    y_labels = list(work_df['Date'])
    dnf_mask = (work_df['75%'] == 'DNF') if '75%' in work_df.columns else pd.Series([False]*len(work_df))
    KJ_COLOR = "#1cda2c"; KJCP_COLOR = "#d81515"; KJHKG_COLOR = "#19c2b9"; KJHKGCP_COLOR = "#96258c"
    fig4, axw = plt.subplots(figsize=(9, max(4, len(work_df)*0.45)))
    bar_height = 0.4
    bars_kj = axw.barh(range(len(work_df)), work_df[work_col], color=KJ_COLOR, height=bar_height, label='kJ', zorder=2)
    bars_kjcp = axw.barh(range(len(work_df)), work_df[work_cp_col], color=KJCP_COLOR, height=bar_height, label='ALL kJ >CP', zorder=3)
    for i, bar in enumerate(bars_kj):
        if dnf_mask.iloc[i]:
            bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
    for i, bar in enumerate(bars_kjcp):
        if dnf_mask.iloc[i]:
            bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
    axw2 = axw.twiny()
    bars_kjhkg = axw2.barh([i+0.4 for i in range(len(work_df))], work_df[kjhkg_col], color=KJHKG_COLOR, height=bar_height, label='kJ/h/kg', zorder=2)
    bars_kjhkgcp = axw2.barh([i+0.4 for i in range(len(work_df))], work_df[kjhkgcp_col], color=KJHKGCP_COLOR, height=bar_height, label='kJ/h/kg >CP', zorder=3)
    for i, bar in enumerate(bars_kjhkg):
        if dnf_mask.iloc[i]:
            bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
    for i, bar in enumerate(bars_kjhkgcp):
        if dnf_mask.iloc[i]:
            bar.set_hatch('//'); bar.set_edgecolor('#a9441a')
    axw.set_yticks(range(len(work_df))); axw.set_yticklabels(y_labels, fontsize=7)
    axw.set_xlabel('Lavoro (kJ)'); axw.set_ylabel(''); axw.set_title('Lavoro Totale e Relativo per Gara'); axw.grid(axis='x', linestyle=':', alpha=0.5)
    min_x = 0; max_kj = max(work_df[work_col].max(), work_df[work_cp_col].max())
    axw.set_xlim(left=min_x, right=max_kj*1.15+10)
    min_x2 = 0; max_kjhkg = max(work_df[kjhkg_col].max(), work_df[kjhkgcp_col].max())
    axw2.set_xlim(left=min_x2, right=max_kjhkg*1.15+1)
    n = len(work_df)
    if n > 0:
        lower = -0.2; upper = (n - 1) + 0.6
        axw.set_ylim(lower, upper); fig4.subplots_adjust(top=0.95, bottom=0.05)
    axw2.set_xlabel('Lavoro Relativo (kJ/h/kg)', color='#222222'); axw2.tick_params(axis='x', colors='#222222')

    mean_kj = work_df_finished[work_col].mean(); mean_kjcp = work_df_finished[work_cp_col].mean()
    mean_kjhkg = work_df_finished[kjhkg_col].mean(); mean_kjhkgcp = work_df_finished[kjhkgcp_col].mean()
    y_minw, y_maxw = axw.get_ylim(); y_textw = y_minw - 0.08
    if pd.notna(mean_kj):
        axw.axvline(mean_kj, color=KJ_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
        axw.text(mean_kj, y_textw, f"{int(round(mean_kj))}", color=KJ_COLOR, fontsize=6, ha='center', va='top', fontweight='bold', zorder=11)
    if pd.notna(mean_kjcp):
        axw.axvline(mean_kjcp, color=KJCP_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
        axw.text(mean_kjcp, y_textw, f"{int(round(mean_kjcp))}", color=KJCP_COLOR, fontsize=6, ha='center', va='top', fontweight='bold', zorder=11)
    y_minw2, y_maxw2 = axw2.get_ylim(); y_textw2_top = y_maxw2 + 0.08
    if pd.notna(mean_kjhkg):
        axw2.axvline(mean_kjhkg, color=KJHKG_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
        axw2.text(mean_kjhkg, y_textw2_top, f"{mean_kjhkg:.1f}", color=KJHKG_COLOR, fontsize=6, ha='center', va='bottom', fontweight='bold', zorder=11)
    if pd.notna(mean_kjhkgcp):
        axw2.axvline(mean_kjhkgcp, color=KJHKGCP_COLOR, linestyle='--', linewidth=0.5, alpha=0.85, zorder=10)
        axw2.text(mean_kjhkgcp, y_textw2_top, f"{mean_kjhkgcp:.1f}", color=KJHKGCP_COLOR, fontsize=6, ha='center', va='bottom', fontweight='bold', zorder=11)

    font_kwargs = dict(fontsize=7, fontweight='bold', color='#222222', family='DejaVu Sans')
    kj_offset = 1; kjcp_offset = 1; kjhkg_offset = 0.02; kjhkgcp_offset = 0.02; name_x = 10
    for i, (bar_kj, bar_kjcp, bar_kjhkg, bar_kjhkgcp, name, kj, kjcp, kjhkg, kjhkgcp) in enumerate(zip(
            bars_kj, bars_kjcp, bars_kjhkg, bars_kjhkgcp,
            work_df['Name'], work_df[work_col], work_df[work_cp_col], work_df[kjhkg_col], work_df[kjhkgcp_col])):
        name_str = str(name)
        tag75 = str(work_df['75%'].iloc[i]).strip() if '75%' in work_df.columns else ''
        if tag75 == '+':
            name_str += ' (DNF 75%+)'
        elif tag75.upper() == 'DNF':
            name_str += ' (DNF)'
        kj_str = str(int(kj)) if isinstance(kj, (int, float)) and float(kj).is_integer() else str(kj)
        kjcp_str = str(int(kjcp)) if isinstance(kjcp, (int, float)) and float(kjcp).is_integer() else str(kjcp)
        kjhkg_str = f"{kjhkg:.1f}" if isinstance(kjhkg, float) else str(kjhkg)
        kjhkgcp_str = f"{kjhkgcp:.1f}" if isinstance(kjhkgcp, float) else str(kjhkgcp)
        axw.text(name_x, bar_kj.get_y() + bar_kj.get_height()/2, name_str, va='center', ha='left', color='#ffffff', fontsize=7, fontweight='bold', clip_on=True, transform=axw.transData)
        axw.text(bar_kj.get_width()+kj_offset, bar_kj.get_y() + bar_kj.get_height()/2, f"{kj_str} kJ", va='center', ha='left', **font_kwargs)
        perc = 0
        try:
            perc = (kjcp / kj * 100) if kj else 0
        except Exception:
            perc = float('nan')
        if isinstance(perc, float) and (np.isnan(perc) or np.isinf(perc)):
            perc_str = ""
        else:
            perc_str = f"{int(round(perc))}%"
        perc_offset = -2
        axw.text(bar_kjcp.get_width()+perc_offset, bar_kjcp.get_y() + bar_kjcp.get_height()/2, perc_str, va='center', ha='right', color='#111111', fontsize=7, fontweight='bold', zorder=4)
        axw.text(bar_kjcp.get_width()+kjcp_offset, bar_kjcp.get_y() + bar_kjcp.get_height()/2, f"{kjcp_str} kJ > CP", va='center', ha='left', color='#222222', fontsize=7, fontweight='bold', family='DejaVu Sans', zorder=4)
        axw2.text(bar_kjhkg.get_width()+kjhkg_offset, bar_kjhkg.get_y() + bar_kjhkg.get_height()/2, f"{kjhkg_str} kJ/h/kg", va='center', ha='left', **font_kwargs)
        axw2.text(bar_kjhkgcp.get_width()+kjhkgcp_offset, bar_kjhkgcp.get_y() + bar_kjhkgcp.get_height()/2, f"{kjhkgcp_str} kJ/h/kg > CP", va='center', ha='left', color='#222222', fontsize=7, fontweight='bold', family='DejaVu Sans', zorder=4)

    fig4.tight_layout()
    return fig4
