# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
EXPORTER STREAM - Generazione grafico potenza vs tempo per stream
Vista stream potenza nel tempo senza GPS/altimetria
"""

from typing import List, Tuple, Dict, Any
import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .peffort_engine import format_time_hhmmss, format_time_mmss, get_zone_color

logger = logging.getLogger(__name__)


def plot_stream_html(df: pd.DataFrame, efforts: List[Tuple[int, int, float]], 
                     sprints: List[Dict[str, Any]], ftp: float, weight: float) -> str:
    """
    Genera grafico stream HTML con potenza vs tempo e efforts evidenziati.
    
    Args:
        df: DataFrame con dati attività
        efforts: Lista efforts (start, end, avg_power)
        sprints: Lista sprints {start, end, avg}
        ftp: Functional Threshold Power
        weight: Peso atleta
        
    Returns:
        HTML string con grafico Plotly interattivo
    """
    logger.info("Generazione grafico stream...")
    
    power = df["power"].values
    time_sec = df["time_sec"].values
    hr = df["heartrate"].values
    cadence = df["cadence"].values
    
    # Crea figura con subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=("Potenza & Efforts", "Frequenza Cardiaca & Cadenza")
    )
    
    # Converti tempo in minuti per asse x
    time_min = time_sec / 60
    
    # SUBPLOT 1: Potenza
    step = max(1, len(power) // 2000)
    
    # Traccia potenza base
    hover_power_text = []
    for i in range(0, len(power), step):
        t = time_sec[i]
        if t >= 3600:
            time_str = format_time_hhmmss(t)
        else:
            time_str = format_time_mmss(t)
        hover_power_text.append(
            f"⏱️ {time_str}<br>⚡ {power[i]:.0f} W<br>❤️ {hr[i]:.0f} bpm<br>🦵 {cadence[i]:.0f} rpm"
        )
    
    fig.add_trace(go.Scatter(
        x=time_min[::step],
        y=power[::step],
        mode='lines',
        name='Potenza',
        line=dict(color='lightgray', width=1),
        text=hover_power_text,
        hoverinfo='text',
        hoverlabel=dict(bgcolor='gray', font=dict(color='white', size=11)),
        showlegend=True
    ), row=1, col=1)
    
    # Linea FTP
    fig.add_trace(go.Scatter(
        x=[time_min[0], time_min[-1]],
        y=[ftp, ftp],
        mode='lines',
        name=f'FTP ({ftp:.0f}W)',
        line=dict(color='orange', width=2, dash='dash'),
        hoverinfo='skip',
        showlegend=True
    ), row=1, col=1)
    
    # EFFORTS - segmenti evidenziati
    efforts_with_idx = [(i, eff) for i, eff in enumerate(efforts)]
    sorted_efforts = sorted(efforts_with_idx, key=lambda x: x[1][2], reverse=True)
    
    for idx, (orig_idx, (s, e, avg)) in enumerate(sorted_efforts):
        seg_power = power[s:e]
        seg_time_min = time_min[s:e]
        seg_time = time_sec[s:e]
        
        color = get_zone_color(avg, ftp)
        
        duration = int(seg_time[-1] - seg_time[0] + 1)
        w_kg = avg / weight if weight > 0 else 0
        
        # Calcola energia
        energy_j = 0
        for j in range(s, min(e-1, len(time_sec)-1)):
            dt = time_sec[j+1] - time_sec[j]
            if dt > 0 and dt < 30:
                energy_j += power[j] * dt
        energy_kj = energy_j / 1000
        
        hover_text = [
            f"<b>Effort #{orig_idx + 1}</b><br>" +
            f"⚡ {avg:.0f} W ({w_kg:.2f} W/kg)<br>" +
            f"⏱️ {duration}s<br>" +
            f"⚙️ {energy_kj:.1f} kJ<br>" +
            f"⏰ {format_time_hhmmss(seg_time[0])}"
        ] * len(seg_power)
        
        fig.add_trace(go.Scatter(
            x=seg_time_min,
            y=seg_power,
            mode='lines',
            name=f"Effort #{orig_idx + 1} ({avg:.0f}W)",
            line=dict(color=color, width=4),
            text=hover_text,
            hoverinfo='text',
            hoverlabel=dict(bgcolor=color, font=dict(color='white', size=12)),
            showlegend=True
        ), row=1, col=1)
    
    # SPRINTS - markers
    for i, sprint in enumerate(sprints):
        start, end = sprint['start'], sprint['end']
        mid = (start + end) // 2
        
        seg_power = power[start:end]
        seg_time = time_sec[start:end]
        
        fig.add_trace(go.Scatter(
            x=[time_min[mid]],
            y=[power[mid]],
            mode='markers',
            name=f"Sprint #{i + 1}",
            marker=dict(
                size=12,
                color='red',
                symbol='star',
                line=dict(color='white', width=2)
            ),
            text=f"<b>Sprint #{i + 1}</b><br>⚡ {sprint['avg']:.0f} W (peak {seg_power.max():.0f}W)<br>⏰ {format_time_hhmmss(seg_time[0])}",
            hoverinfo='text',
            hoverlabel=dict(bgcolor='red', font=dict(color='white', size=12)),
            showlegend=True
        ), row=1, col=1)
    
    # SUBPLOT 2: HR e Cadenza
    hr_step = max(1, len(hr) // 2000)
    
    fig.add_trace(go.Scatter(
        x=time_min[::hr_step],
        y=hr[::hr_step],
        mode='lines',
        name='Heart Rate',
        line=dict(color='#e74c3c', width=1.5),
        yaxis='y2',
        showlegend=True
    ), row=2, col=1)
    
    fig.add_trace(go.Scatter(
        x=time_min[::hr_step],
        y=cadence[::hr_step],
        mode='lines',
        name='Cadence',
        line=dict(color='#3498db', width=1.5),
        yaxis='y3',
        showlegend=True
    ), row=2, col=1)
    
    # Layout
    fig.update_xaxes(title_text="Tempo (min)", row=2, col=1)
    fig.update_yaxes(title_text="Potenza (W)", row=1, col=1)
    fig.update_yaxes(title_text="HR (bpm)", row=2, col=1, side='left', color='#e74c3c')
    
    # Secondary y-axis per cadenza
    fig.update_layout(
        yaxis3=dict(
            title="Cadenza (rpm)",
            overlaying='y2',
            side='right',
            color='#3498db'
        )
    )
    
    fig.update_layout(
        autosize=True,
        margin=dict(l=40, r=40, t=80, b=40),
        title=dict(
            text="STREAM ANALYSIS - Stream Potenza & Effort",
            font=dict(size=20, color='#333'),
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
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Helvetica, Arial, sans-serif")
    )
    
    # Grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    html = fig.to_html(config={'displayModeBar': True, 'responsive': True})
    logger.info("Grafico stream generato")
    return html
