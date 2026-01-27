# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
INSPECTION BUILDER (MATPLOTLIB) - Generazione grafico interattivo con Matplotlib
Permette visual inspection e modifica manuale dei bordi degli effort
"""

from typing import List, Tuple, Any, Dict
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

logger = logging.getLogger(__name__)


def plot_inspection_figure(fig: Figure,
                           df: pd.DataFrame, 
                           efforts: List[Tuple[int, int, float]],
                           sprints: List[Dict[str, Any]],
                           ftp: float,
                           weight: float,
                           zoom_level: float = 1.0) -> None:
    """
    Disegna il grafico di ispezione su una figura Matplotlib esistente
    
    Args:
        fig: Figura Matplotlib su cui disegnare
        df: DataFrame con dati FIT (power, time_sec, etc.)
        efforts: Lista di tuple (start_idx, end_idx, avg_power)
        sprints: Lista di dict con dati sprint
        ftp: Soglia funzionale
        weight: Peso atleta
        zoom_level: Livello di zoom (non usato, ma per coerenza API)
    """
    fig.patch.set_facecolor('#0f172a')
    
    # Layout: 2 subplot in colonna con margini ridotti
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.25, left=0.08, right=0.95, top=0.95, bottom=0.08)
    ax1 = fig.add_subplot(gs[0])  # Power raw
    ax2 = fig.add_subplot(gs[1], sharex=ax1)  # 30s average
    
    time_sec = df['time_sec'].values
    power = df['power'].values
    
    # ============ SUBPLOT 1: POWER RAW ============
    ax1.plot(time_sec, power, color='#3b82f6', linewidth=0.8, label='Power', zorder=2)
    ax1.fill_between(time_sec, power, alpha=0.2, color='#3b82f6', zorder=1)
    ax1.set_ylabel('Power (W)', fontsize=11, color='#e2e8f0', fontweight='bold')
    ax1.set_title('Raw Power Signal', fontsize=12, color='#e2e8f0', fontweight='bold', pad=10)
    ax1.grid(True, color='#475569', linewidth=0.5, alpha=0.5)
    ax1.set_facecolor('#1e293b')
    ax1.tick_params(colors='#cbd5e1', labelsize=9)
    ax1.spines['bottom'].set_color('#475569')
    ax1.spines['left'].set_color('#475569')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # ============ SUBPLOT 2: 30-SECOND AVERAGE ============
    # Calcola media mobile 30-secondi
    window_size = max(1, int(30 / (time_sec[1] - time_sec[0])) if len(time_sec) > 1 else 1)
    rolling_avg = pd.Series(power).rolling(window=window_size, center=True).mean().values
    
    ax2.plot(time_sec, rolling_avg, color='#f59e0b', linewidth=1.2, label='30s Average', zorder=2)
    ax2.fill_between(time_sec, rolling_avg, alpha=0.2, color='#f59e0b', zorder=1)
    ax2.set_xlabel('Time (s)', fontsize=11, color='#e2e8f0', fontweight='bold')
    ax2.set_ylabel('Power (W)', fontsize=11, color='#e2e8f0', fontweight='bold')
    ax2.set_title('30-Second Rolling Average', fontsize=12, color='#e2e8f0', fontweight='bold', pad=10)
    ax2.grid(True, color='#475569', linewidth=0.5, alpha=0.5)
    ax2.set_facecolor('#1e293b')
    ax2.tick_params(colors='#cbd5e1', labelsize=9)
    ax2.spines['bottom'].set_color('#475569')
    ax2.spines['left'].set_color('#475569')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # ============ EVIDENZIA GLI EFFORT ============
    colors_effort = plt.cm.tab10(np.linspace(0, 1, len(efforts)))
    
    for idx, (start_idx, end_idx, avg) in enumerate(efforts):
        if start_idx >= len(time_sec) or end_idx <= start_idx or end_idx > len(time_sec):
            continue
        
        start_time = time_sec[start_idx]
        end_time = time_sec[end_idx - 1]
        
        color = colors_effort[idx % len(colors_effort)]
        
        # Rettangolo di background sugli effort
        rect1 = Rectangle((start_time, ax1.get_ylim()[0]), 
                         end_time - start_time, 
                         ax1.get_ylim()[1] - ax1.get_ylim()[0],
                         linewidth=2, 
                         edgecolor=color, 
                         facecolor=color, 
                         alpha=0.15,
                         zorder=3)
        ax1.add_patch(rect1)
        
        rect2 = Rectangle((start_time, ax2.get_ylim()[0]), 
                         end_time - start_time, 
                         ax2.get_ylim()[1] - ax2.get_ylim()[0],
                         linewidth=2, 
                         edgecolor=color, 
                         facecolor=color, 
                         alpha=0.15,
                         zorder=3)
        ax2.add_patch(rect2)
        
        # Linee di bordo
        ax1.axvline(x=start_time, color=color, linestyle='--', linewidth=2, alpha=0.7, zorder=4)
        ax1.axvline(x=end_time, color=color, linestyle='--', linewidth=2, alpha=0.7, zorder=4)
        ax2.axvline(x=start_time, color=color, linestyle='--', linewidth=2, alpha=0.7, zorder=4)
        ax2.axvline(x=end_time, color=color, linestyle='--', linewidth=2, alpha=0.7, zorder=4)
        
        # Label effort
        mid_time = (start_time + end_time) / 2
        ax1.text(mid_time, ax1.get_ylim()[1] * 0.95, 
                f'#{idx+1}', 
                fontsize=10, 
                color=color, 
                fontweight='bold',
                ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#0f172a', edgecolor=color, alpha=0.8),
                zorder=5)
    
    # Imposta limiti assi
    ax2.set_xlim(time_sec[0], time_sec[-1])
    ax1.set_xlim(time_sec[0], time_sec[-1])
    
    # Imposta i limiti Y per avere spazio per le labels
    y1_max = max(power) if len(power) > 0 else 100
    y2_max = max(rolling_avg[~np.isnan(rolling_avg)]) if len(rolling_avg[~np.isnan(rolling_avg)]) > 0 else 100
    ax1.set_ylim(0, y1_max * 1.1)
    ax2.set_ylim(0, y2_max * 1.1)
    
    logger.debug(f"Grafico inspection completato: {len(efforts)} efforts visualizzati")
