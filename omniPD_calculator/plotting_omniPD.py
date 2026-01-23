# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
OmniPD Plotting - Funzioni per creazione e aggiornamento grafici
"""

import logging
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import FixedLocator, FuncFormatter
from numpy.typing import NDArray

logger = logging.getLogger(__name__)

try:
    from .core_omniPD import ompd_power, ompd_power_short, w_eff, _format_time_label, TCPMAX
    from shared.styles import TEMI
except ImportError:
    from omniPD_calculator.core_omniPD import ompd_power, ompd_power_short, w_eff, _format_time_label, TCPMAX
    from shared.styles import TEMI


def format_plot(ax: Axes, theme: str = "Forest Green") -> None:
    """
    Formattazione comune per tutti i plot.
    
    Args:
        ax: Matplotlib Axes object
        theme: Nome del tema da applicare
    """
    colors = TEMI.get(theme, TEMI["Forest Green"])
    
    bg_color = colors.get("bg", "#061f17")
    border_color = colors.get("border", "#334155")
    text_color = colors.get("text", "#f1f5f9")
    
    ax.set_facecolor(bg_color)
    ax.tick_params(colors=text_color)
    for s in ax.spines.values(): 
        s.set_color(border_color)
    ax.grid(True, alpha=0.1)


def plot_ompd_curve(ax: Axes, x_data: NDArray[np.float64], y_data: NDArray[np.float64], 
                    params: Tuple[float, float, float, float], theme: str = "Forest Green") -> None:
    """
    Disegna il grafico OmPD principale con curve e dati inseriti.
    
    Args:
        ax: Matplotlib Axes object
        x_data: Array dei tempi in secondi
        y_data: Array delle potenze in Watt
        params: Tuple (CP, W_prime, Pmax, A)
        theme: Nome del tema da applicare
    """
    ax.clear()
    format_plot(ax, theme)
    
    colors = TEMI.get(theme, TEMI["Forest Green"])
    accent_color = colors.get("accent", "#4ade80")
    btn_color = colors.get("btn", "#16a34a")
    text_color = colors.get("text", "#f1f5f9")
    sidebar_color = colors.get("sidebar", "#0b2e24")
    
    CP, W_prime, Pmax, A = params
    
    # Dati inseriti - usa colore accent (senza label)
    ax.scatter(x_data, y_data, color=accent_color, 
                    zorder=5, s=80, marker='x',
                    linewidths=1)

    # Range di tempo
    t_max = max(max(x_data) * 1.2, 5400)
    t_model = np.logspace(np.log10(1.0), np.log10(t_max), 500)
    
    # Curva completa - usa btn_color (senza label)
    p_model = ompd_power(t_model, CP, W_prime, Pmax, A)
    ax.plot(t_model, p_model, color=btn_color, 
                 linewidth=2.5)
    
    # Curva base - colore secondario (senza label)
    t_short = t_model[t_model <= TCPMAX]
    p_short = ompd_power_short(t_short, CP, W_prime, Pmax)
    ax.plot(t_short, p_short, color='#3b82f6', 
                 linewidth=1.5, linestyle='--', alpha=0.7)
    
    # Linee di riferimento con label per legenda
    ax.axhline(y=CP, color='red', linestyle='--', 
                    linewidth=1.0, alpha=0.8, zorder=1, label='CP')
    ax.axvline(x=TCPMAX, color='blue', linestyle=':', 
                    linewidth=2.0, alpha=0.7, zorder=1, label='TCPMAX')

    # Assi
    ax.set_xscale("log")
    ax.set_xlim(left=1, right=t_max)
    
    xticks = [5, 3*60, 5*60, 12*60, 20*60, 30*60, 40*60, 60*60]
    ax.xaxis.set_major_locator(FixedLocator(xticks))
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.set_xticklabels([_format_time_label(t) for t in xticks])
    
    ax.set_xlabel("Time", color=text_color)
    ax.set_ylabel("Power (W)", color=text_color)
    ax.set_title("OmniPD Curve", color=text_color, fontsize=14)
    
    # Griglia solo sui tick maggiori
    ax.grid(which='major', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.grid(which='minor', visible=False)
    
    # Parametri nel grafico
    textstr = f"CP={int(round(CP))} W\nW'={int(round(W_prime))} J\nPmax={int(round(Pmax))} W\nA={A:.2f}"
    ax.text(0.98, 0.98, textstr, transform=ax.transAxes, 
             fontsize=9, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor=text_color, alpha=0.9))
    
    ax.legend(facecolor=sidebar_color, edgecolor='none', 
               labelcolor=text_color, loc='lower left', fontsize=9)


def plot_residuals(ax: Axes, x_data: NDArray[np.float64], residuals: NDArray[np.float64], 
                   RMSE: float, MAE: float, theme: str = "Forest Green") -> None:
    """
    Disegna il grafico dei residui con metriche.
    
    Args:
        ax: Matplotlib Axes object
        x_data: Array dei tempi in secondi
        residuals: Array dei residui
        RMSE: Errore quadratico medio
        MAE: Errore medio assoluto
        theme: Nome del tema da applicare
    """
    ax.clear()
    format_plot(ax, theme)
    ax.set_ylim(-50, 50)
    
    colors = TEMI.get(theme, TEMI["Forest Green"])
    text_color = colors.get("text", "#f1f5f9")
    
    # Linea zero
    ax.axhline(0, color=text_color, linestyle='--', linewidth=1, alpha=0.5)
    
    # Residui
    ax.plot(x_data, residuals, linestyle='-', 
             color='red', linewidth=1, marker='x', 
             markerfacecolor='black', markeredgecolor='black', 
             markersize=5)
    
    # Assi
    ax.set_xscale("log")
    xticks = [5, 30, 60, 3*60, 5*60, 6*60, 10*60, 12*60, 15*60, 20*60, 30*60, 60*60]
    ax.xaxis.set_major_locator(FixedLocator(xticks))
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x,pos: _format_time_label(x)))
    
    ax.set_xlabel("Time", color=text_color)
    ax.set_ylabel("Residuals (W)", color=text_color)
    ax.set_title("OmPD Residuals", color=text_color, fontsize=14)
    
    # Griglia solo sui tick maggiori
    ax.grid(which='major', linestyle='-', linewidth=0.7, alpha=0.5)
    ax.grid(which='minor', visible=False)
    
    # Metriche
    metrics_text = f"RMSE = {RMSE:.2f} W\nMAE  = {MAE:.2f} W"
    ax.text(0.98, 0.98, metrics_text, transform=ax.transAxes,
             fontsize=9, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor=text_color, alpha=0.9))


def plot_weff(ax: Axes, params: Tuple[float, float, float, float], W_prime: float, 
              theme: str = "Forest Green") -> None:
    """
    Disegna il grafico W'eff (Capacità anaerobica effettiva utilizzata nel tempo).
    
    Args:
        ax: Matplotlib Axes object
        params: Tuple (CP, W_prime, Pmax, A)
        W_prime: Valore di W' (ridondante in params ma esplicito)
        theme: Nome del tema da applicare
    """
    ax.clear()
    format_plot(ax, theme)
    
    colors = TEMI.get(theme, TEMI["Forest Green"])
    accent_color = colors.get("accent", "#4ade80")
    text_color = colors.get("text", "#f1f5f9")
    
    CP, _, Pmax, _ = params
    
    # Range di tempo per W'eff
    T_plot_w = np.linspace(1, 3*60, 500)
    Weff_plot = w_eff(T_plot_w, W_prime, CP, Pmax)
    
    # Curva W'eff - usa colore accent
    ax.plot(T_plot_w, Weff_plot, color=accent_color, linewidth=2.5)
    
    # Punto 99% W'
    W_99 = 0.99 * W_prime
    t_99_idx = np.argmin(np.abs(Weff_plot - W_99))
    t_99 = T_plot_w[t_99_idx]
    w_99 = Weff_plot[t_99_idx]
    
    ax.axhline(y=w_99, color='blue', linestyle='--', linewidth=1, alpha=0.8)
    ax.axvline(x=t_99, color='blue', linestyle='--', linewidth=1, alpha=0.8)
    
    minutes = int(t_99 // 60)
    seconds = int(t_99 % 60)
    ax.annotate(f"99% W'eff at {minutes}m{seconds}s ({int(t_99)}s)",
                     xy=(t_99, W_99), xytext=(10, -18), 
                     textcoords='offset points',
                     bbox=dict(boxstyle='round', facecolor='blue', alpha=0.2),
                     fontsize=10, color=text_color)
    
    # Assi
    ax.set_xlim(0, 3*60)
    ax.set_ylim(0, np.max(Weff_plot) * 1.1)
    ax.set_xlabel("Time", color=text_color)
    ax.set_ylabel("W'eff (J)", color=text_color)
    ax.set_title("OmPD Effective W'", color=text_color, fontsize=14)
    
    x_ticks = list(range(0, 181, 30))
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([_format_time_label(t) for t in x_ticks])
    ax.set_xticks([], minor=True)
    
    # Griglia pulita
    ax.grid(which='major', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.grid(which='minor', visible=False)
    
    # Info W'
    ax.text(0.98, 0.98, f"W' = {int(W_prime)} J", 
             transform=ax.transAxes, fontsize=10,
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor=text_color, alpha=0.9))
