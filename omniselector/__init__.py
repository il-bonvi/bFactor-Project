# ============================================================================== 
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ============================================================================== 

"""
omniselector - Modulo selector per bFactor
"""

from .gui_omniselector import OmniSelectorAnalyzer
from .core_omniselector import (
    calculate_omnipd_model,
    ompd_power,
    ompd_power_short,
    w_eff,
    load_data_from_file,
    extract_data_from_rows,
    convert_time_minutes_to_seconds
)
from .widgets_omniselector import CSVColumnDialog, MmpRow
from .plotting_omniselector import plot_ompd_curve, plot_residuals, plot_weff
from .events_omniselector import OmniSelectorEventHandler

def omniselector(theme=None):
    """Apre la finestra Omniselector"""
    win = OmniSelectorAnalyzer(theme=theme)
    win.show()
    return win

__all__ = [
    'OmniSelectorAnalyzer',
    'calculate_omnipd_model',
    'ompd_power',
    'ompd_power_short',
    'w_eff',
    'load_data_from_file',
    'extract_data_from_rows',
    'convert_time_minutes_to_seconds',
    'CSVColumnDialog',
    'MmpRow',
    'plot_ompd_curve',
    'plot_residuals',
    'plot_weff',
    'OmniSelectorEventHandler',
    'omniselector',
]
