# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
OmniPD Plotting - Funzioni per creazione e aggiornamento grafici
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter

try:
    from .core_omniPD import ompd_power, ompd_power_short, w_eff, _format_time_label, TCPMAX
except ImportError:
    from omniPD_calculator.core_omniPD import ompd_power, ompd_power_short, w_eff, _format_time_label, TCPMAX


def format_plot(ax):
    """Formattazione comune per tutti i plot"""
    ax.set_facecolor('#061f17')
    ax.tick_params(colors='white')
    for s in ax.spines.values(): 
        s.set_color('#334155')
    ax.grid(True, alpha=0.1)


def plot_ompd_curve(ax, x_data, y_data, params):
    """
    Disegna il grafico OmPD principale
    
    Args:
        ax: Axes matplotlib
        x_data: array dei tempi (s)
        y_data: array delle potenze (W)
        params: tuple (CP, W_prime, Pmax, A)
    """
    ax.clear()
    format_plot(ax)
    
    CP, W_prime, Pmax, A = params
    
    # Dati inseriti
    ax.scatter(x_data, y_data, color='#4ade80', 
                    label='MMP Data', zorder=5, s=80, marker='x',
                    linewidths=1)

    # Range di tempo
    t_max = max(max(x_data) * 1.2, 3600)
    t_model = np.logspace(np.log10(1.0), np.log10(t_max), 500)
    
    # Curva completa
    p_model = ompd_power(t_model, CP, W_prime, Pmax, A)
    ax.plot(t_model, p_model, color='#7c3aed', 
                 linewidth=2.5, label='OmniPD')
    
    # Curva base
    t_short = t_model[t_model <= TCPMAX]
    p_short = ompd_power_short(t_short, CP, W_prime, Pmax)
    ax.plot(t_short, p_short, color='#3b82f6', 
                 linewidth=1.5, linestyle='--', alpha=0.7, 
                 label='Base curve (t ≤ TCPmax)')
    
    # Linee di riferimento
    ax.axhline(y=CP, color='red', linestyle='--', 
                    linewidth=1.0, alpha=0.8, zorder=1)
    ax.axvline(x=TCPMAX, color='blue', linestyle=':', 
                    linewidth=1.0, alpha=0.7, zorder=1)

    # Assi
    ax.set_xscale("log")
    ax.set_xlim(left=1, right=t_max)
    
    xticks = [5, 3*60, 5*60, 12*60, 20*60, 30*60, 40*60, 60*60]
    ax.xaxis.set_major_locator(FixedLocator(xticks))
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.set_xticklabels([_format_time_label(t) for t in xticks])
    
    ax.set_xlabel("Time", color='white')
    ax.set_ylabel("Power (W)", color='white')
    ax.set_title("OmniPD Curve", color='white', fontsize=14)
    
    # Griglia solo sui tick maggiori
    ax.grid(which='major', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.grid(which='minor', visible=False)
    
    # Parametri nel grafico
    textstr = f"CP={int(round(CP))} W\nW'={int(round(W_prime))} J\nPmax={int(round(Pmax))} W\nA={A:.2f}"
    ax.text(0.98, 0.98, textstr, transform=ax.transAxes, 
             fontsize=9, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    
    ax.legend(facecolor='#1e293b', edgecolor='none', 
               labelcolor='white', loc='lower left', fontsize=9)


def plot_residuals(ax, x_data, residuals, RMSE, MAE):
    """
    Disegna il grafico dei residui
    
    Args:
        ax: Axes matplotlib
        x_data: array dei tempi (s)
        residuals: array dei residui
        RMSE: errore quadratico medio
        MAE: errore medio assoluto
    """
    ax.clear()
    format_plot(ax)
    
    # Linea zero
    ax.axhline(0, color='white', linestyle='--', linewidth=1, alpha=0.5)
    
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
    
    ax.set_xlabel("Time", color='white')
    ax.set_ylabel("Residuals (W)", color='white')
    ax.set_title("OmPD Residuals", color='white', fontsize=14)
    
    # Griglia solo sui tick maggiori
    ax.grid(which='major', linestyle='-', linewidth=0.7, alpha=0.5)
    ax.grid(which='minor', visible=False)
    
    # Metriche
    metrics_text = f"RMSE = {RMSE:.2f} W\nMAE  = {MAE:.2f} W"
    ax.text(0.98, 0.98, metrics_text, transform=ax.transAxes,
             fontsize=9, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))


def plot_weff(ax, params, W_prime):
    """
    Disegna il grafico W'eff (Effective W')
    
    Args:
        ax: Axes matplotlib
        params: tuple (CP, W_prime, Pmax, A)
        W_prime: valore di W'
    """
    ax.clear()
    format_plot(ax)
    
    CP, _, Pmax, _ = params
    
    # Range di tempo per W'eff
    T_plot_w = np.linspace(1, 3*60, 500)
    Weff_plot = w_eff(T_plot_w, W_prime, CP, Pmax)
    
    # Curva W'eff
    ax.plot(T_plot_w, Weff_plot, color='#4ade80', linewidth=2.5)
    
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
                     fontsize=10, color='white')
    
    # Assi
    ax.set_xlim(0, 3*60)
    ax.set_ylim(0, np.max(Weff_plot) * 1.1)
    ax.set_xlabel("Time", color='white')
    ax.set_ylabel("W'eff (J)", color='white')
    ax.set_title("OmPD Effective W'", color='white', fontsize=14)
    
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
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
