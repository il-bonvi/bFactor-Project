# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
omniPD_calculator - Modulo di calcolo potenza-durata per bFactor
"""

from .gui_omniPD import OmniPDAnalyzer
from .core_omniPD import (
    calculate_omnipd_model,
    ompd_power,
    ompd_power_short,
    w_eff,
    load_data_from_file,
    extract_data_from_rows,
    convert_time_minutes_to_seconds
)
from .widgets_omniPD import CSVColumnDialog, MmpRow
from .plotting_omniPD import plot_ompd_curve, plot_residuals, plot_weff
from .events_omniPD import OmniPDEventHandler

__all__ = [
    'OmniPDAnalyzer',
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
    'OmniPDEventHandler',
]
