# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
EXPORTER PLANIMETRIA - Generazione mappa 2D con effort annotations
Vista dall'alto degli effort su coordinate geografiche
"""

from typing import List, Tuple, Dict, Any
import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from .engine_PEFFORT import format_time_hhmmss, get_zone_color

logger = logging.getLogger(__name__)

# Token Mapbox pubblico per rendering in QWebEngineView
# Questo è un token pubblico di esempio - può essere sostituito con uno personale
pio.templates.default = "plotly"
MAPBOX_TOKEN = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"


def calculate_zoom_level(lat_values, lon_values):
    """
    Calcola il livello di zoom ottimale basato sull'estensione geografica della traccia.
    Utilizza la formula empirica di Mapbox per fit all bounds.
    """
    lat_range = np.nanmax(lat_values) - np.nanmin(lat_values)
    lon_range = np.nanmax(lon_values) - np.nanmin(lon_values)
    
    # Usa il range maggiore per determinare lo zoom
    max_range = max(lat_range, lon_range)
    
    # Formula empirica per Mapbox zoom level
    # Più range è grande, zoom è basso (view più ampia)
    if max_range > 1.0:
        zoom = 8
    elif max_range > 0.5:
        zoom = 9
    elif max_range > 0.2:
        zoom = 10
    elif max_range > 0.1:
        zoom = 11
    elif max_range > 0.05:
        zoom = 12
    else:
        zoom = 13
    
    return zoom


def plot_planimetria_html(df: pd.DataFrame, efforts: List[Tuple[int, int, float]],
                          sprints: List[Dict[str, Any]], ftp: float, weight: float,
                          map_style: str = "open-street-map") -> str:
    """
    Genera mappa planimetrica HTML con efforts e sprints evidenziati.
    
    Args:
        df: DataFrame con dati attività (deve contenere position_lat, position_long)
        efforts: Lista efforts (start, end, avg_power)
        sprints: Lista sprints {start, end, avg}
        ftp: Functional Threshold Power
        weight: Peso atleta
        
    Returns:
        HTML string con mappa Plotly interattiva
    """
    logger.info("Generazione mappa planimetrica...")

    allowed_styles = {
        "open-street-map",
        "carto-positron",
    }
    if map_style not in allowed_styles:
        logger.warning("Map style '%s' non valido, fallback a open-street-map", map_style)
        map_style = "open-street-map"
    
    # Accedi alle coordinate GPS
    lat = df['position_lat'].values
    lon = df['position_long'].values
    
    power = df["power"].values
    time_sec = df["time_sec"].values
    dist_km = df["distance_km"].values
    distance = df["distance"].values
    hr = df["heartrate"].values
    alt = df["altitude"].values
    grade = df["grade"].values
    cadence = df["cadence"].values
    
    # Calcolo Joules cumulative
    joules_cumulative = np.zeros(len(power))
    joules_over_cp_cumulative = np.zeros(len(power))
    for i in range(1, len(power)):
        dt = time_sec[i] - time_sec[i-1]
        if dt > 0 and dt < 30:
            joules_cumulative[i] = joules_cumulative[i-1] + power[i] * dt
            if power[i] >= ftp:
                joules_over_cp_cumulative[i] = joules_over_cp_cumulative[i-1] + power[i] * dt
            else:
                joules_over_cp_cumulative[i] = joules_over_cp_cumulative[i-1]
        else:
            joules_cumulative[i] = joules_cumulative[i-1]
            joules_over_cp_cumulative[i] = joules_over_cp_cumulative[i-1]
    
    # Rimuovi punti senza coordinate
    valid = ~np.isnan(lat) & ~np.isnan(lon) & (lat != 0) & (lon != 0)
    if not valid.any():
        logger.error("Nessuna coordinata GPS valida")
        raise ValueError("Nessuna coordinata GPS valida nel file")
    
    fig = go.Figure()
    
    # Traccia principale - percorso completo
    step = max(1, len(lat[valid]) // 2000)
    fig.add_trace(go.Scattermapbox(
        lat=lat[valid][::step],
        lon=lon[valid][::step],
        mode='lines',
        line=dict(color="#EEFF00", width=3), #COLORE TRACCIA PLANIMETRIA
        name='Percorso',
        hoverinfo='skip',
        showlegend=False
    ))
    
    # EFFORTS - segmenti colorati sulla mappa
    efforts_with_idx = [(i, eff) for i, eff in enumerate(efforts)]
    sorted_efforts = sorted(efforts_with_idx, key=lambda x: x[1][2], reverse=True)
    
    for idx, (orig_idx, (s, e, avg)) in enumerate(sorted_efforts):
        seg_lat = lat[s:e]
        seg_lon = lon[s:e]
        seg_power = power[s:e]
        seg_time = time_sec[s:e]
        seg_dist = dist_km[s:e]
        seg_alt = alt[s:e]
        seg_hr = hr[s:e]
        seg_cadence = cadence[s:e]
        seg_grade = grade[s:e]
        seg_distance = distance[s:e]
        
        color = get_zone_color(avg, ftp)
        
        duration = int(seg_time[-1] - seg_time[0] + 1)
        dist_tot = seg_dist[-1] - seg_dist[0]
        dist_tot_m = seg_distance[-1] - seg_distance[0]
        elevation_gain = seg_alt[-1] - seg_alt[0]
        avg_grade = (elevation_gain / dist_tot_m * 100) if dist_tot_m > 0 else 0
        max_grade = seg_grade.max() if len(seg_grade) > 0 else 0
        
        vam = elevation_gain / (duration / 3600) if duration > 0 else 0
        w_kg = avg / weight if weight > 0 else 0
        avg_speed = dist_tot / (duration / 3600) if duration > 0 else 0
        
        # Best 5s
        best_5s_watt = 0
        best_5s_watt_kg = 0
        if len(seg_power) >= 5 and weight > 0:
            best_5s = max([seg_power[i:i+5].mean() for i in range(len(seg_power)-4)])
            best_5s_watt = int(best_5s)
            best_5s_watt_kg = best_5s / weight
        
        # Cadence
        valid_cadence = seg_cadence[seg_cadence > 0]
        avg_cadence = valid_cadence.mean() if len(valid_cadence) > 0 else 0
        
        # Heart rate
        valid_hr = seg_hr[seg_hr > 0]
        avg_hr = valid_hr.mean() if len(valid_hr) > 0 else 0
        max_hr = valid_hr.max() if len(valid_hr) > 0 else 0
        
        # 1º metà vs 2º metà
        half = len(seg_power) // 2
        avg_watts_first = seg_power[:half].mean() if half > 0 else 0
        avg_watts_second = seg_power[half:].mean() if len(seg_power) > half else 0
        watts_ratio = avg_watts_first / avg_watts_second if avg_watts_second > 0 else 0
        
        # kJ calculations
        kj = joules_cumulative[e-1] / 1000 if e-1 < len(joules_cumulative) else 0
        kj_over_cp = joules_over_cp_cumulative[e-1] / 1000 if e-1 < len(joules_over_cp_cumulative) else 0
        kj_kg = (kj / weight) if weight > 0 else 0
        kj_kg_over_cp = (kj_over_cp / weight) if weight > 0 else 0
        hours_seg = duration / 3600
        kj_h_kg = (kj / hours_seg / weight) if hours_seg > 0 and weight > 0 else 0
        kj_h_kg_over_cp = (kj_over_cp / hours_seg / weight) if hours_seg > 0 and weight > 0 else 0
        
        # VAM teorico (solo se salita significativa)
        gradient_factor = 2 + (avg_grade / 10) if avg_grade > 0 else 2
        vam_teorico = (avg / weight) * (gradient_factor * 100) if weight > 0 else 0
        
        hover_lines = [
            f"<b>Effort #{orig_idx + 1}</b>",
            f"⚡ {avg:.0f} W | 5\"🔺{best_5s_watt} W 🌀 {avg_cadence:.0f} rpm",
            f"⏱️ {duration}s | 🕒 {format_time_hhmmss(seg_time[0])} | {(avg/ftp*100):.0f}%",
            f"⚖️ {w_kg:.2f} W/kg | 5\"🔺{best_5s_watt_kg:.2f} W/kg",
            f"🔀 {avg_watts_first:.0f} W | {avg_watts_second:.0f} W | {watts_ratio:.2f}",
        ]
        if len(valid_hr) > 0:
            hover_lines.append(f"❤️ ∅{avg_hr:.0f} bpm | 🔺{max_hr:.0f} bpm")
        hover_lines.append(f"🚴‍♂️ {avg_speed:.1f} km/h 📏 {dist_tot:.2f} km | ∅ {avg_grade:.1f}% | 🔺{max_grade:.1f}%")
        
        if avg_grade >= 4.5:
            diff_vam = abs(vam_teorico - vam)
            arrow = '⬆️' if vam_teorico - vam > 0 else ('⬇️' if vam_teorico - vam < 0 else '')
            wkg_teoric = vam / (gradient_factor * 100)
            diff_wkg = w_kg - wkg_teoric
            perc_err = (diff_wkg / w_kg * 100) if w_kg != 0 else 0
            sign = '+' if perc_err > 0 else ('-' if perc_err < 0 else '')
            hover_lines.append(f"🚵‍♂️ {vam:.0f} m/h {arrow} {diff_vam:.0f} m/h | {abs(diff_wkg):.2f} W/kg")
            hover_lines.append(f"🧮 {vam_teorico:.0f} m/h | {wkg_teoric:.2f} W/kg | {sign}{abs(perc_err):.1f}%")
        else:
            hover_lines.append(f"🚵‍♂️ {vam:.0f} m/h")
        
        hover_lines.append(f"🔋 {kj:.0f} kJ | {kj_over_cp:.0f} kJ > CP")
        hover_lines.append(f"💪 {kj_kg:.1f} kJ/kg | {kj_kg_over_cp:.1f} kJ/kg > CP")
        hover_lines.append(f"🔥 {kj_h_kg:.1f} kJ/h/kg | {kj_h_kg_over_cp:.1f} kJ/h/kg > CP")
        
        hover_text = "<br>".join(hover_lines)
        hover_text_list = [hover_text] * len(seg_lat)
        
        fig.add_trace(go.Scattermapbox(
            lat=seg_lat,
            lon=seg_lon,
            mode='lines',
            line=dict(color=color, width=6),
            name=f"Effort #{orig_idx + 1} ({avg:.0f}W)",
            text=hover_text_list,
            hoverinfo='text',
            hoverlabel=dict(bgcolor=color, font=dict(color='white', size=12))
        ))
    
    # SPRINTS - markers sulla mappa
    for i, sprint in enumerate(sprints):
        start, end = sprint['start'], sprint['end']
        
        # Punto centrale dello sprint
        mid = (start + end) // 2
        if mid >= len(lat) or np.isnan(lat[mid]) or np.isnan(lon[mid]):
            continue
            
        seg_power = power[start:end]
        seg_time = time_sec[start:end]
        seg_hr = hr[start:end]
        seg_cadence = df["cadence"].values[start:end]
        
        duration = int(seg_time[-1] - seg_time[0] + 1)
        w_kg = sprint['avg'] / weight if weight > 0 else 0
        
        # Cadence
        valid_cadence = seg_cadence[seg_cadence > 0]
        avg_cadence = valid_cadence.mean() if len(valid_cadence) > 0 else 0
        
        # Heart rate
        valid_hr = seg_hr[seg_hr > 0]
        max_hr = valid_hr.max() if len(valid_hr) > 0 else 0
        
        hover_text = (
            f"<b>Sprint #{i + 1}</b><br>" +
            f"⚡ {sprint['avg']:.0f} W (peak {seg_power.max():.0f}W) 🌀 {avg_cadence:.0f} rpm<br>" +
            f"⏱️ {duration}s | 🕒 {format_time_hhmmss(seg_time[0])}<br>" +
            f"⚖️ {w_kg:.2f} W/kg | Peak {seg_power.max()/weight:.2f} W/kg<br>" +
            f"❤️ Max {max_hr:.0f} bpm"
        )
        
        fig.add_trace(go.Scattermapbox(
            lat=[lat[mid]],
            lon=[lon[mid]],
            mode='markers',
            marker=dict(
                size=15,
                color='red',
                symbol='star'
            ),
            name=f"Sprint #{i + 1}",
            text=hover_text,
            hoverinfo='text',
            hoverlabel=dict(bgcolor='red', font=dict(color='white', size=12))
        ))
    
    # Layout mappa
    # Calcola centro mappa
    center_lat = np.nanmean(lat[valid])
    center_lon = np.nanmean(lon[valid])
    
    # Calcola zoom dinamico in base all'estensione della traccia
    zoom_level = calculate_zoom_level(lat[valid], lon[valid])
    
    fig.update_layout(
        mapbox=dict(
            accesstoken=MAPBOX_TOKEN,
            style=map_style,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom_level
        ),
        autosize=True,
        margin=dict(l=0, r=0, t=30, b=0),
        title=dict(
            text="PLANIMETRIA - Vista dall'alto degli Effort",
            font=dict(size=18, color='#333'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#333",
            borderwidth=1
        ),
        hovermode='closest',
        dragmode='pan'
    )
    
    html = fig.to_html(
        config={
            'displayModeBar': True, 
            'responsive': True, 
            'displaylogo': False,
            'scrollZoom': True,
            'modeBarButtonsToAdd': ['pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d'],
            'modeBarButtonsToRemove': []
        }
    )
    logger.info("Mappa planimetrica generata")
    return html

