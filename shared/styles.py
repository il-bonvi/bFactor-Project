"""
SHARED STYLES - Temi e stili centralizzati per la suite bFactor
"""

# =====================
# TEMI PROFESSIONALI
# =====================
TEMI = {
    "Forest Green": {
        "bg": "#061f17", 
        "sidebar": "#0b2e24", 
        "accent": "#4ade80", 
        "btn": "#16a34a", 
        "input": "#0d3a2f", 
        "text": "#f1f5f9"
    },
    "Deep Ocean": {
        "bg": "#0f172a", 
        "sidebar": "#1e293b", 
        "accent": "#38bdf8", 
        "btn": "#2563eb", 
        "input": "#1e293b", 
        "text": "#f1f5f9"
    },
    "***Comal": {
        "bg": "#f8fafc", 
        "sidebar": "#e0e7ff", 
        "accent": "#1e40af", 
        "btn": "#1e40af", 
        "input": "#ffffff", 
        "text": "#0f172a" 
    },
    "***VO2": {
        "bg": "#000000", 
        "sidebar": "#111111", 
        "accent": "#ffed00", 
        "btn": "#ffed00", 
        "input": "#222222", 
        "text": "#ffffff" 
    },
    "***ABCoaching": {
        "bg": "#f2f7f2", 
        "sidebar": "#e4efe5", 
        "accent": "#17423b", 
        "btn": "#2d6a4f", 
        "input": "#ffffff", 
        "text": "#0b201c" 
    },
}


def get_style(tema_name):
    """Genera CSS per il tema selezionato"""
    t = TEMI[tema_name]
    return f"""
    QWidget {{ background-color: {t['bg']}; color: #f1f5f9; font-family: 'Segoe UI', system-ui, sans-serif; }}
    QFrame#Sidebar {{ background-color: {t['sidebar']}; border-right: 1px solid #334155; }}
    QLabel#Header {{ font-size: 22px; font-weight: 800; color: {t['accent']}; padding: 10px 0px; margin-bottom: 5px; }}
    QLabel#SectionTitle {{ font-size: 10px; font-weight: bold; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 5px; margin-bottom: 5px; }}
    QLabel {{ font-size: 12px; color: #94a3b8; font-weight: 500; background: transparent; }}
    QLineEdit {{ background-color: {t['input']}; border: 2px solid #334155; border-radius: 12px; padding: 8px 15px; color: white; font-size: 14px; selection-background-color: {t['accent']}; }}
    QLineEdit:focus {{ border: 2px solid {t['accent']}; background-color: {t['bg']}; }}
    QPushButton {{ background-color: {t['btn']}; color: white; border-radius: 15px; padding: 12px; font-weight: bold; border: none; }}
    QPushButton:hover {{ background-color: {t['accent']}; color: {t['bg']}; }}
    QComboBox {{ background-color: {t['input']}; border: 2px solid #334155; border-radius: 10px; padding: 2px 10px; font-size: 11px; min-height: 25px; }}
    QComboBox::drop-down {{ border: none; }}
    QTableWidget {{ background-color: {t['bg']}; alternate-background-color: {t['sidebar']}; gridline-color: #334155; }}
    QHeaderView::section {{ background-color: {t['sidebar']}; color: {t['accent']}; padding: 5px; border: none; }}
    QTableWidget::item {{ padding: 5px; color: #f1f5f9; }}
    """
