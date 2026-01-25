"""Visual Editor for Race Report GUI - Interactive layout controls"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QGroupBox, QGridLayout, QComboBox, QSpinBox,
    QFrame, QSizePolicy, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
import json


class LayoutPresetManager:
    """Manages layout presets for quick configuration"""
    
    PRESETS = {
        "Default": {
            "logo_frac": 0.03,
            "logo_margin_right": 0.03,
            "logo_margin_top": 0.018,
            "other_logo_frac": 0.05,
            "other_logo_margin_right": 0.015,
            "other_logo_margin_top": 0.01,
        },
        "Logo Grande": {
            "logo_frac": 0.08,
            "logo_margin_right": 0.02,
            "logo_margin_top": 0.015,
            "other_logo_frac": 0.10,
            "other_logo_margin_right": 0.02,
            "other_logo_margin_top": 0.015,
        },
        "Logo Piccolo": {
            "logo_frac": 0.02,
            "logo_margin_right": 0.01,
            "logo_margin_top": 0.01,
            "other_logo_frac": 0.03,
            "other_logo_margin_right": 0.01,
            "other_logo_margin_top": 0.008,
        },
        "Margini Larghi": {
            "logo_frac": 0.04,
            "logo_margin_right": 0.08,
            "logo_margin_top": 0.04,
            "other_logo_frac": 0.06,
            "other_logo_margin_right": 0.06,
            "other_logo_margin_top": 0.03,
        },
        "Centrato Alto": {
            "logo_frac": 0.05,
            "logo_margin_right": 0.475,  # Centered
            "logo_margin_top": 0.01,
            "other_logo_frac": 0.06,
            "other_logo_margin_right": 0.47,
            "other_logo_margin_top": 0.01,
        },
    }
    
    @classmethod
    def get_preset(cls, name):
        """Get preset configuration by name"""
        return cls.PRESETS.get(name, cls.PRESETS["Default"]).copy()
    
    @classmethod
    def get_preset_names(cls):
        """Get list of preset names"""
        return list(cls.PRESETS.keys())


class LogoPositionWidget(QWidget):
    """Visual widget showing logo position on page"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Logo position (0-1 normalized coordinates)
        self.logo_width = 0.03
        self.logo_margin_right = 0.03
        self.logo_margin_top = 0.018
        
        # Page aspect ratio (A4)
        self.page_aspect = 1.414
    
    def update_position(self, width, margin_right, margin_top):
        """Update logo position and redraw"""
        self.logo_width = width
        self.logo_margin_right = margin_right
        self.logo_margin_top = margin_top
        self.update()
    
    def paintEvent(self, event):
        """Draw the page with logo position"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate page dimensions to fit widget
        widget_w = self.width()
        widget_h = self.height()
        
        # Fit A4 page in widget
        if widget_w / widget_h > 1 / self.page_aspect:
            page_h = widget_h - 40
            page_w = page_h / self.page_aspect
        else:
            page_w = widget_w - 40
            page_h = page_w * self.page_aspect
        
        page_x = (widget_w - page_w) / 2
        page_y = (widget_h - page_h) / 2
        
        # Draw page background
        painter.setBrush(QBrush(QColor("#d9e8dd")))
        painter.setPen(QPen(QColor("#666666"), 2))
        painter.drawRect(int(page_x), int(page_y), int(page_w), int(page_h))
        
        # Calculate logo position
        logo_w_px = page_w * self.logo_width
        logo_h_px = logo_w_px  # Assume square for preview
        
        logo_right = page_x + page_w - (page_w * self.logo_margin_right)
        logo_top = page_y + (page_h * self.logo_margin_top)
        logo_left = logo_right - logo_w_px
        logo_bottom = logo_top + logo_h_px
        
        # Draw logo placeholder
        painter.setBrush(QBrush(QColor("#4CAF50")))
        painter.setPen(QPen(QColor("#2E7D32"), 2))
        painter.drawRect(int(logo_left), int(logo_top), int(logo_w_px), int(logo_h_px))
        
        # Draw logo label
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.drawText(
            int(logo_left), int(logo_top), int(logo_w_px), int(logo_h_px),
            Qt.AlignCenter, "LOGO"
        )
        
        # Draw dimension lines
        painter.setPen(QPen(QColor("#FF5722"), 1, Qt.DashLine))
        
        # Margin right
        painter.drawLine(int(logo_right), int(page_y), int(logo_right), int(page_y + page_h))
        painter.drawLine(int(page_x + page_w), int(page_y), int(page_x + page_w), int(page_y + page_h))
        
        # Margin top
        painter.drawLine(int(page_x), int(logo_top), int(page_x + page_w), int(logo_top))
        painter.drawLine(int(page_x), int(page_y), int(page_x + page_w), int(page_y))
        
        # Draw measurements
        painter.setPen(QPen(QColor("#000000")))
        painter.drawText(
            int(logo_right + 5), int(page_y + page_h / 2),
            f"{self.logo_margin_right:.3f}"
        )
        painter.drawText(
            int(page_x + page_w / 2), int(logo_top - 5),
            f"{self.logo_margin_top:.3f}"
        )


class VisualSlider(QWidget):
    """Enhanced slider with value display and live update"""
    
    def __init__(self, label, min_val, max_val, default_val, step=0.001, parent=None):
        super().__init__(parent)
        self.step = step
        self.min_val = min_val
        self.max_val = max_val
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(label)
        self.label.setMinimumWidth(120)
        layout.addWidget(self.label)
        
        # Slider (scaled to integer range)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_val / step))
        self.slider.setMaximum(int(max_val / step))
        self.slider.setValue(int(default_val / step))
        layout.addWidget(self.slider, stretch=1)
        
        # Value display
        self.value_label = QLabel(f"{default_val:.3f}")
        self.value_label.setMinimumWidth(50)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.value_label)
        
        # Connect slider
        self.slider.valueChanged.connect(self._on_slider_change)
    
    def _on_slider_change(self, value):
        """Update value label when slider changes"""
        real_value = value * self.step
        self.value_label.setText(f"{real_value:.3f}")
    
    def value(self):
        """Get current value"""
        return self.slider.value() * self.step
    
    def setValue(self, val):
        """Set slider value"""
        self.slider.setValue(int(val / self.step))


def create_visual_editor_tab(parent):
    """Create the visual editor tab with interactive controls"""
    widget = QWidget()
    main_layout = QHBoxLayout(widget)
    
    # LEFT SIDE: Visual Preview
    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    
    # Page selector
    page_selector_layout = QHBoxLayout()
    page_selector_layout.addWidget(QLabel("Modifica layout:"))
    parent.page_selector = QComboBox()
    parent.page_selector.addItems(["Pagina 1 (Tabella)", "Pagine 2-4 (Grafici)"])
    parent.page_selector.currentIndexChanged.connect(lambda: update_preview_from_page(parent))
    page_selector_layout.addWidget(parent.page_selector)
    page_selector_layout.addStretch()
    left_layout.addLayout(page_selector_layout)
    
    # Visual preview
    preview_label = QLabel("Anteprima Posizionamento Logo:")
    preview_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
    left_layout.addWidget(preview_label)
    
    parent.logo_preview = LogoPositionWidget()
    left_layout.addWidget(parent.logo_preview, stretch=1)
    
    # Info box
    info_frame = QFrame()
    info_frame.setFrameStyle(QFrame.StyledPanel)
    info_layout = QVBoxLayout(info_frame)
    info_label = QLabel(
        "💡 <b>Suggerimenti:</b><br>"
        "• Usa gli slider per posizionare il logo<br>"
        "• L'anteprima si aggiorna in tempo reale<br>"
        "• Prova i preset per configurazioni rapide<br>"
        "• Clicca 'Applica' per aggiornare il PDF"
    )
    info_label.setWordWrap(True)
    info_layout.addWidget(info_label)
    info_frame.setLayout(info_layout)
    left_layout.addWidget(info_frame)
    
    main_layout.addWidget(left_widget, stretch=2)
    
    # RIGHT SIDE: Controls
    right_widget = QWidget()
    right_layout = QVBoxLayout(right_widget)
    
    # Preset selector
    preset_group = QGroupBox("⚡ Preset Rapidi")
    preset_layout = QVBoxLayout()
    
    preset_combo_layout = QHBoxLayout()
    preset_combo_layout.addWidget(QLabel("Scegli preset:"))
    parent.preset_combo = QComboBox()
    parent.preset_combo.addItems(LayoutPresetManager.get_preset_names())
    parent.preset_combo.currentTextChanged.connect(lambda name: apply_preset(parent, name))
    preset_combo_layout.addWidget(parent.preset_combo)
    preset_layout.addLayout(preset_combo_layout)
    
    preset_group.setLayout(preset_layout)
    right_layout.addWidget(preset_group)
    
    # Slider controls
    controls_group = QGroupBox("🎯 Controlli Posizione Logo")
    controls_layout = QVBoxLayout()
    
    # Width slider
    parent.visual_width_slider = VisualSlider(
        "Larghezza:", 0.01, 0.20, parent.args.logo_frac
    )
    parent.visual_width_slider.slider.valueChanged.connect(
        lambda: on_visual_change(parent)
    )
    controls_layout.addWidget(parent.visual_width_slider)
    
    # Margin right slider
    parent.visual_margin_right_slider = VisualSlider(
        "Margine Destra:", 0.0, 0.50, parent.args.logo_margin_right
    )
    parent.visual_margin_right_slider.slider.valueChanged.connect(
        lambda: on_visual_change(parent)
    )
    controls_layout.addWidget(parent.visual_margin_right_slider)
    
    # Margin top slider
    parent.visual_margin_top_slider = VisualSlider(
        "Margine Alto:", 0.0, 0.20, parent.args.logo_margin_top
    )
    parent.visual_margin_top_slider.slider.valueChanged.connect(
        lambda: on_visual_change(parent)
    )
    controls_layout.addWidget(parent.visual_margin_top_slider)
    
    controls_group.setLayout(controls_layout)
    right_layout.addWidget(controls_group)
    
    # Quick position buttons
    quick_group = QGroupBox("📍 Posizionamento Rapido")
    quick_layout = QGridLayout()
    
    positions = [
        ("Alto Sx", 0.02, 0.02),
        ("Alto Centro", 0.475, 0.02),
        ("Alto Dx", 0.02, 0.02),
        ("Basso Sx", 0.02, 0.95),
        ("Basso Centro", 0.475, 0.95),
        ("Basso Dx", 0.02, 0.95),
    ]
    
    for i, (name, margin_right, margin_top) in enumerate(positions):
        btn = QPushButton(name)
        btn.clicked.connect(
            lambda checked, mr=margin_right, mt=margin_top: 
            quick_position(parent, mr, mt)
        )
        row = i // 3
        col = i % 3
        quick_layout.addWidget(btn, row, col)
    
    quick_group.setLayout(quick_layout)
    right_layout.addWidget(quick_group)
    
    # Auto-update toggle
    parent.auto_update_checkbox = QCheckBox("Aggiornamento Automatico Anteprima")
    parent.auto_update_checkbox.setChecked(False)
    right_layout.addWidget(parent.auto_update_checkbox)
    
    right_layout.addStretch()
    
    # Apply button
    btn_apply = QPushButton("✅ Applica Modifiche al Report")
    btn_apply.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            font-size: 11pt;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    btn_apply.clicked.connect(lambda: apply_visual_changes(parent))
    right_layout.addWidget(btn_apply)
    
    main_layout.addWidget(right_widget, stretch=1)
    
    # Initialize debounce timer for live updates
    parent.visual_update_timer = QTimer()
    parent.visual_update_timer.setSingleShot(True)
    parent.visual_update_timer.timeout.connect(lambda: update_live_preview(parent))
    
    return widget


def update_preview_from_page(parent):
    """Update preview when page selection changes"""
    page_index = parent.page_selector.currentIndex()
    
    if page_index == 0:  # Page 1
        parent.visual_width_slider.setValue(parent.args.logo_frac)
        parent.visual_margin_right_slider.setValue(parent.args.logo_margin_right)
        parent.visual_margin_top_slider.setValue(parent.args.logo_margin_top)
    else:  # Pages 2-4
        parent.visual_width_slider.setValue(parent.args.other_logo_frac)
        parent.visual_margin_right_slider.setValue(parent.args.other_logo_margin_right)
        parent.visual_margin_top_slider.setValue(parent.args.other_logo_margin_top)
    
    on_visual_change(parent)


def on_visual_change(parent):
    """Called when any visual control changes"""
    # Update preview immediately
    parent.logo_preview.update_position(
        parent.visual_width_slider.value(),
        parent.visual_margin_right_slider.value(),
        parent.visual_margin_top_slider.value()
    )
    
    # Debounce live preview generation (wait 500ms after last change)
    if parent.auto_update_checkbox.isChecked():
        parent.visual_update_timer.start(500)


def update_live_preview(parent):
    """Update the actual matplotlib preview (debounced)"""
    if parent.df is None:
        return
    
    # Temporarily update args
    page_index = parent.page_selector.currentIndex()
    
    if page_index == 0:
        parent.args.logo_frac = parent.visual_width_slider.value()
        parent.args.logo_margin_right = parent.visual_margin_right_slider.value()
        parent.args.logo_margin_top = parent.visual_margin_top_slider.value()
    else:
        parent.args.other_logo_frac = parent.visual_width_slider.value()
        parent.args.other_logo_margin_right = parent.visual_margin_right_slider.value()
        parent.args.other_logo_margin_top = parent.visual_margin_top_slider.value()
    
    # Regenerate only if auto-update is on
    parent.generate_visualizations()


def apply_preset(parent, preset_name):
    """Apply a preset configuration"""
    preset = LayoutPresetManager.get_preset(preset_name)
    
    # Update args
    parent.args.logo_frac = preset["logo_frac"]
    parent.args.logo_margin_right = preset["logo_margin_right"]
    parent.args.logo_margin_top = preset["logo_margin_top"]
    parent.args.other_logo_frac = preset["other_logo_frac"]
    parent.args.other_logo_margin_right = preset["other_logo_margin_right"]
    parent.args.other_logo_margin_top = preset["other_logo_margin_top"]
    
    # Update sliders based on current page
    update_preview_from_page(parent)
    
    # Update spinboxes in LAYOUT tab if they exist
    if hasattr(parent, 'logo_frac_spin'):
        parent.logo_frac_spin.setValue(preset["logo_frac"])
        parent.logo_margin_right_spin.setValue(preset["logo_margin_right"])
        parent.logo_margin_top_spin.setValue(preset["logo_margin_top"])
        parent.other_logo_frac_spin.setValue(preset["other_logo_frac"])
        parent.other_logo_margin_right_spin.setValue(preset["other_logo_margin_right"])
        parent.other_logo_margin_top_spin.setValue(preset["other_logo_margin_top"])


def quick_position(parent, margin_right, margin_top):
    """Quickly position logo at common locations"""
    parent.visual_margin_right_slider.setValue(margin_right)
    parent.visual_margin_top_slider.setValue(margin_top)
    on_visual_change(parent)


def apply_visual_changes(parent):
    """Apply visual editor changes to the report"""
    if parent.df is None:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(parent, "Avviso", "Carica prima i dati CSV")
        return
    
    # Get current page
    page_index = parent.page_selector.currentIndex()
    
    # Update appropriate args
    if page_index == 0:
        parent.args.logo_frac = parent.visual_width_slider.value()
        parent.args.logo_margin_right = parent.visual_margin_right_slider.value()
        parent.args.logo_margin_top = parent.visual_margin_top_slider.value()
    else:
        parent.args.other_logo_frac = parent.visual_width_slider.value()
        parent.args.other_logo_margin_right = parent.visual_margin_right_slider.value()
        parent.args.other_logo_margin_top = parent.visual_margin_top_slider.value()
    
    # Sync with LAYOUT tab spinboxes
    if hasattr(parent, 'logo_frac_spin'):
        parent.logo_frac_spin.setValue(parent.args.logo_frac)
        parent.logo_margin_right_spin.setValue(parent.args.logo_margin_right)
        parent.logo_margin_top_spin.setValue(parent.args.logo_margin_top)
        parent.other_logo_frac_spin.setValue(parent.args.other_logo_frac)
        parent.other_logo_margin_right_spin.setValue(parent.args.other_logo_margin_right)
        parent.other_logo_margin_top_spin.setValue(parent.args.other_logo_margin_top)
    
    # Invalidate cache and regenerate
    parent.invalidate_figure_cache()
    parent.generate_visualizations()
    
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.information(parent, "Successo", "Layout aggiornato con successo!")
