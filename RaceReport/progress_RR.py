"""Progress and performance utilities for Race Report GUI"""

from PySide6.QtWidgets import QProgressDialog, QApplication
from PySide6.QtCore import Qt


class ProgressContext:
    """Context manager for progress dialogs"""
    
    def __init__(self, parent, title="Caricamento...", max_value=100):
        self.parent = parent
        self.dialog = QProgressDialog(title, "Annulla", 0, max_value, parent)
        self.dialog.setWindowModality(Qt.WindowModal)
        self.dialog.setCancelButton(None)  # Disable cancel for now
        self.dialog.show()
    
    def set_value(self, value):
        """Update progress value"""
        self.dialog.setValue(value)
        QApplication.processEvents()
    
    def set_label(self, text):
        """Update progress label"""
        self.dialog.setLabelText(text)
        QApplication.processEvents()
    
    def close(self):
        """Close progress dialog"""
        self.dialog.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
