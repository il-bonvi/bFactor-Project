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
    convert_time_minutes_to_seconds,
    apply_data_filters
)
from .widgets_omniselector import CSVColumnDialog, TimeWindowsDialog
from .plotting_omniselector import (
    plot_ompd_curve, 
    plot_residuals, 
    plot_weff,
    draw_time_windows,
    plot_raw_points
)
from .events_omniselector import OmniSelectorEventHandler
from .ui_builder_omniselector import (
    create_sidebar_widgets, create_ompd_tab, create_residuals_tab,
    create_weff_tab, create_theme_selector, apply_widget_styles
)

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
    'convert_time_minutes_to_seconds',
    'apply_data_filters',
    'CSVColumnDialog',
    'TimeWindowsDialog',
    'plot_ompd_curve',
    'plot_residuals',
    'plot_weff',
    'draw_time_windows',
    'plot_raw_points',
    'OmniSelectorEventHandler',
    'omniselector',
]
