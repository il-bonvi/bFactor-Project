# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
PEFFORT (Project Effort) Module - Analisi avanzata di file FIT
Main exports: EffortAnalyzer GUI, engine functions, configuration classes
"""

from .peffort_gui import EffortAnalyzer
from .peffort_engine import parse_fit, create_efforts, detect_sprints, merge_extend, split_included
from .peffort_config import AnalysisConfig, AthleteProfile, EffortConfig, SprintConfig
from .peffort_exporter import create_pdf_report, plot_unified_html

__all__ = [
    'EffortAnalyzer',
    'parse_fit',
    'create_efforts', 
    'detect_sprints',
    'merge_extend',
    'split_included',
    'AnalysisConfig',
    'AthleteProfile',
    'EffortConfig',
    'SprintConfig',
    'create_pdf_report',
    'plot_unified_html'
]
