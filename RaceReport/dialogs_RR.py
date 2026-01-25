# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""Dialog components for Race Report GUI"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox, QGroupBox
)


class TagEditorDialog(QDialog):
    """Dialog for adding/removing tags to a single row"""
    
    # Available tags organized by category
    RACE_TYPE_TAGS = {
        '#road': 'Road - Gara in linea',
        '#itt': 'ITT - Cronometro individuale',
        '#ttt': 'TTT - Cronometro a squadre',
    }
    
    INFO_TAGS = {
        '#dnf': 'DNF - Did Not Finish',
        '#almdnf': 'almDNF - Almost Did Not Finish (+)',
        '#errpwr': 'errPWR - Power Data Invalid',
        '#errhr': 'errHR - Heart Rate Data Invalid',
    }
    
    # Combined for backward compatibility
    AVAILABLE_TAGS = {**RACE_TYPE_TAGS, **INFO_TAGS}
    
    def __init__(self, row_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestione Tag")
        self.setGeometry(200, 200, 400, 300)
        
        # Extract existing tags from row
        self.row_data = row_data
        self.existing_tags = set()
        
        # First, check if there's a Tags column with explicit tags
        if 'Tags' in row_data.index:
            tags_str = str(row_data.get('Tags', ''))
            if tags_str and tags_str != 'nan':
                # Parse tags from the Tags column
                for tag in self.AVAILABLE_TAGS.keys():
                    if tag in tags_str.lower():
                        self.existing_tags.add(tag)
        
        # Also check other columns for any tags
        for val in row_data.values:
            if isinstance(val, str):
                val_lower = val.lower()
                for tag in self.AVAILABLE_TAGS.keys():
                    if tag in val_lower:
                        self.existing_tags.add(tag)
        
        self.selected_tags = set(self.existing_tags)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Seleziona i tag da applicare:"))
        
        self.tag_checkboxes = {}
        
        # Section 1: Tipo Gara
        race_type_group = QGroupBox("Tipo Gara")
        race_type_layout = QVBoxLayout()
        for tag, description in self.RACE_TYPE_TAGS.items():
            checkbox = QCheckBox(f"{tag} - {description}")
            checkbox.setChecked(tag in self.existing_tags)
            checkbox.stateChanged.connect(self._make_tag_handler(tag))
            self.tag_checkboxes[tag] = checkbox
            race_type_layout.addWidget(checkbox)
        race_type_group.setLayout(race_type_layout)
        layout.addWidget(race_type_group)
        
        # Section 2: Info
        info_group = QGroupBox("Info")
        info_layout = QVBoxLayout()
        for tag, description in self.INFO_TAGS.items():
            checkbox = QCheckBox(f"{tag} - {description}")
            checkbox.setChecked(tag in self.existing_tags)
            checkbox.stateChanged.connect(self._make_tag_handler(tag))
            self.tag_checkboxes[tag] = checkbox
            info_layout.addWidget(checkbox)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancella")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _make_tag_handler(self, tag):
        """Create a handler function for a specific tag"""
        def handler(state):
            self.on_tag_changed(tag, state)
        return handler
    
    def on_tag_changed(self, tag, state):
        """Update selected tags"""
        if state == 2:  # Checked
            self.selected_tags.add(tag)
        else:
            self.selected_tags.discard(tag)
    
    def get_tags(self):
        """Return selected tags"""
        return self.selected_tags
