# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
Omniselector Events - Handler per interazioni con i grafici (hover, click, ecc.)
"""

import numpy as np

from .core_omniselector import ompd_power, _format_time_label


class OmniSelectorEventHandler:
    """Gestore degli eventi di interazione per i grafici Omniselector"""
    
    def __init__(self, analyzer):
        """
        Inizializza l'event handler
        
        Args:
            analyzer: istanza di OmniSelectorAnalyzer
        """
        self.analyzer = analyzer
    
    def connect_ompd_hover(self):
        """Connette gli eventi di hover per il grafico Omniselector"""
        if self.analyzer.cid_ompd is not None:
            self.analyzer.canvas1.mpl_disconnect(self.analyzer.cid_ompd)
        
        self.analyzer.cid_ompd = self.analyzer.canvas1.mpl_connect(
            'motion_notify_event', self._on_ompd_hover
        )
    
    def _on_ompd_hover(self, event):
        """Gestisce il movimento del mouse sul grafico Omniselector"""
        if event.inaxes != self.analyzer.ax1 or self.analyzer.params is None:
            # Rimuovi annotazioni se fuori dall'asse - con proper error handling
            if self.analyzer.hover_ann_points is not None:
                try:
                    self.analyzer.hover_ann_points.remove()
                except Exception:
                    pass
                self.analyzer.hover_ann_points = None
            if self.analyzer.ann_curve is not None:
                try:
                    self.analyzer.ann_curve.remove()
                except Exception:
                    pass
                self.analyzer.ann_curve = None
            self.analyzer.canvas1.draw_idle()
            return
        
        # Ottieni coordinate mouse
        x_mouse = event.xdata
        if x_mouse is None:
            return
        
        CP, W_prime, Pmax, A = self.analyzer.params
        
        # Rimuovi vecchia annotazione sulla curva - safe removal
        if self.analyzer.ann_curve is not None:
            try:
                self.analyzer.ann_curve.remove()
            except Exception:
                pass
            self.analyzer.ann_curve = None
        
        # Aggiungi annotazione per la curva nel punto x_mouse
        try:
            y_curve = ompd_power(x_mouse, CP, W_prime, Pmax, A)
            self.analyzer.ann_curve = self.analyzer.ax1.annotate(
                f"{_format_time_label(x_mouse)}\n{int(y_curve)}W",
                xy=(x_mouse, y_curve),
                xytext=(5, 5),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#7c3aed', alpha=0.8, edgecolor='white', linewidth=1),
                fontsize=8,
                color='white',
                weight='bold'
            )
        except Exception:
            pass
        
        # Hover sui punti inseriti - safe removal
        if self.analyzer.hover_ann_points is not None:
            try:
                self.analyzer.hover_ann_points.remove()
            except Exception:
                pass
            self.analyzer.hover_ann_points = None
        
        # Trova il punto più vicino al mouse
        distances = np.abs(self.analyzer.x_data - x_mouse)
        closest_idx = np.argmin(distances)
        closest_dist = distances[closest_idx]
        
        # Se abbastanza vicino, mostra annotazione
        if closest_dist < max(self.analyzer.x_data) * 0.05:
            try:
                x_point = self.analyzer.x_data[closest_idx]
                y_point = self.analyzer.y_data[closest_idx]
                self.analyzer.hover_ann_points = self.analyzer.ax1.annotate(
                    f"MMP: {_format_time_label(x_point)} @ {int(y_point)}W",
                    xy=(x_point, y_point),
                    xytext=(5, -20),
                    textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#4ade80', alpha=0.8, edgecolor='white', linewidth=1),
                    fontsize=8,
                    color='black',
                    weight='bold'
                )
            except Exception:
                pass
        
        self.analyzer.canvas1.draw_idle()
    
    def connect_residuals_hover(self):
        """Connette gli eventi di hover per il grafico residui"""
        if self.analyzer.cid_residuals is not None:
            self.analyzer.canvas2.mpl_disconnect(self.analyzer.cid_residuals)
        
        self.analyzer.cid_residuals = self.analyzer.canvas2.mpl_connect(
            'motion_notify_event', self._on_residuals_hover
        )
    
    def _on_residuals_hover(self, event):
        """Gestisce il movimento del mouse sul grafico residui"""
        if event.inaxes != self.analyzer.ax2:
            if self.analyzer.hover_ann_residuals is not None:
                try:
                    self.analyzer.hover_ann_residuals.remove()
                except Exception:
                    pass
                self.analyzer.hover_ann_residuals = None
            self.analyzer.canvas2.draw_idle()
            return
        
        x_mouse = event.xdata
        if x_mouse is None:
            return
        
        if self.analyzer.hover_ann_residuals is not None:
            try:
                self.analyzer.hover_ann_residuals.remove()
            except Exception:
                pass
            self.analyzer.hover_ann_residuals = None
        
        # Trova il punto più vicino
        distances = np.abs(self.analyzer.x_data - x_mouse)
        closest_idx = np.argmin(distances)
        closest_dist = distances[closest_idx]
        
        if closest_dist < max(self.analyzer.x_data) * 0.05:
            try:
                x_point = self.analyzer.x_data[closest_idx]
                y_residual = self.analyzer.residuals[closest_idx]
                self.analyzer.hover_ann_residuals = self.analyzer.ax2.annotate(
                    f"{_format_time_label(x_point)}\nResidual: {int(y_residual)}W",
                    xy=(x_point, y_residual),
                    xytext=(5, 10),
                    textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='red', alpha=0.8, edgecolor='white', linewidth=1),
                    fontsize=8,
                    color='white',
                    weight='bold'
                )
            except Exception:
                pass
        
        self.analyzer.canvas2.draw_idle()
