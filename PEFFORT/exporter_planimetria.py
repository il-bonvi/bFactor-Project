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
from .engine_PEFFORT import format_time_hhmmss, get_zone_color

logger = logging.getLogger(__name__)


def plot_planimetria_html(df: pd.DataFrame, efforts: List[Tuple[int, int, float]], 
                          sprints: List[Dict[str, Any]], ftp: float, weight: float) -> str:
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
    
    # Accedi alle coordinate GPS
    lat = df['position_lat'].values
    lon = df['position_long'].values
    
    power = df["power"].values
    time_sec = df["time_sec"].values
    dist_km = df["distance_km"].values
    hr = df["heartrate"].values
    
    # Rimuovi punti senza coordinate
    valid = ~np.isnan(lat) & ~np.isnan(lon) & (lat != 0) & (lon != 0)
    if not valid.any():
        logger.error("Nessuna coordinata GPS valida")
        raise ValueError("Nessuna coordinata GPS valida nel file")
    
    fig = go.Figure()
    
    # Traccia principale - percorso completo in grigio
    step = max(1, len(lat[valid]) // 2000)
    fig.add_trace(go.Scattermapbox(
        lat=lat[valid][::step],
        lon=lon[valid][::step],
        mode='lines',
        line=dict(color='lightgray', width=2),
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
        
        color = get_zone_color(avg, ftp)
        
        duration = int(seg_time[-1] - seg_time[0] + 1)
        dist_tot = seg_dist[-1] - seg_dist[0]
        w_kg = avg / weight if weight > 0 else 0
        
        hover_text = [
            f"<b>Effort #{orig_idx + 1}</b><br>" +
            f"⚡ {avg:.0f} W ({w_kg:.2f} W/kg)<br>" +
            f"⏱️ {duration}s<br>" +
            f"📏 {dist_tot:.2f} km<br>" +
            f"⏰ {format_time_hhmmss(seg_time[0])}"
        ] * len(seg_lat)
        
        fig.add_trace(go.Scattermapbox(
            lat=seg_lat,
            lon=seg_lon,
            mode='lines',
            line=dict(color=color, width=6),
            name=f"Effort #{orig_idx + 1} ({avg:.0f}W)",
            text=hover_text,
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
            text=f"<b>Sprint #{i + 1}</b><br>⚡ {sprint['avg']:.0f} W (peak {seg_power.max():.0f}W)<br>⏰ {format_time_hhmmss(seg_time[0])}",
            hoverinfo='text',
            hoverlabel=dict(bgcolor='red', font=dict(color='white', size=12))
        ))
    
    # Layout mappa
    # Calcola centro mappa
    center_lat = np.nanmean(lat[valid])
    center_lon = np.nanmean(lon[valid])
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=13
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

