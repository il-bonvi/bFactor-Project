# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

"""
SHARED STYLES - Temi e stili centralizzati per la suite bFactor
"""

# =====================
# TEMI PROFESSIONALI
# =====================
TEMI = {
    # --- TEMI SCURI (Dark Mode) ---
    "Forest Green": {
        "bg": "#061f17",
        "sidebar": "#0b2e24",
        "accent": "#4ade80",
        "btn": "#16a34a",
        "input": "#0d3a2f",
        "text": "#f1f5f9",
        "border": "#1f4b3a",
        "btn_text": "#ffffff"
    },
    "Deep Ocean": {
        "bg": "#0f172a",
        "sidebar": "#1e293b",
        "accent": "#38bdf8",
        "btn": "#2563eb",
        "input": "#1e293b",
        "text": "#f1f5f9",
        "border": "#334155",
        "btn_text": "#ffffff"
    },
    "VO2": {  
        "bg": "#0a0a0a",
        "sidebar": "#171717",
        "accent": "#ffe600",    
        "btn": "#ffe600",       
        "input": "#262626",
        "text": "#ededed",
        "border": "#404040",
        "btn_text": "#000000"   
    },
    "Red Zone": {  
        "bg": "#1a0505",
        "sidebar": "#2b0a0a",
        "accent": "#ff4d4d",
        "btn": "#dc2626",
        "input": "#450a0a",
        "text": "#fee2e2",
        "border": "#7f1d1d",
        "btn_text": "#ffffff"
    },
    
    
    # --- TEMI CHIARI (Light Mode) ---
    "Comal Light": { 
        "bg": "#f9fbfc",         
        "sidebar": "#d0dffe",    
        "accent": "#2C3FD1",     
        "btn": "#081791",       
        "input": "#ffd6f3",      
        "text": "#0f1d77",      
        "border": "#354d90",    
        "btn_text": "#ffffff",
        "placeholder": "#354d90" #aggiunto (perchè?)
    },
    "Comal Pro": { 
        "bg": "#f9fbfc",          
        "sidebar": "#d2e0fe",     
        "accent": "#f736b8",     
        "btn": "#0a178f",       
        "input": "#ffffff", 
        "text": "#0a178f",      
        "border": "#324a8e",     
        "btn_text": "#ffffff",
        "secondary_accent": "#d96bc2"
    },
    "ABCoaching": {   
        "bg": "#e6f0e6",        
        "sidebar": "#e5f0e4",     
        "accent": "#417b2d",      
        "btn": "#18413b",         
        "input": "#dceddc",       
        "text": "#18413b",       
        "border": "#8bb0a1",     
        "btn_text": "#ffffff",
        "placeholder": "#8bb0a1"
    },
    "Giro Pink": {    
        "bg": "#fff0f5",         
        "sidebar": "#fce7f3",
        "accent": "#db2777",    
        "btn": "#db2777",
        "input": "#ffeef7",
        "text": "#831843",       
        "border": "#fbcfe8",
        "btn_text": "#ffffff"
    },
    "Prossimo": {
        "bg": "#ffffff",
        "sidebar": "#f1f5f9",
        "accent": "#475569",     
        "btn": "#0f172a",       
        "input": "#f8fafc",
        "text": "#334155",
        "border": "#e2e8f0",
        "btn_text": "#ffffff"
    },
}


def get_style(tema_name):
    """Genera CSS per il tema selezionato, supportando temi chiari e scuri"""
    # Fallback al primo tema se il nome non esiste
    if tema_name not in TEMI:
        tema_name = "Forest Green"
        
    t = TEMI[tema_name]
    
    # Assicuriamo che esistano chiavi opzionali per compatibilità
    border_col = t.get('border', '#334155')
    btn_txt_col = t.get('btn_text', '#ffffff')

    return f"""
    /* Main Widget & Global Font */
    QWidget {{ 
        background-color: {t['bg']}; 
        color: {t['text']}; 
        font-family: 'Segoe UI', system-ui, sans-serif; 
    }}

    /* Sidebar Styling */
    QFrame#Sidebar {{ 
        background-color: {t['sidebar']}; 
        border-right: 1px solid {border_col}; 
    }}

    /* Headers & Labels */
    QLabel#Header {{ 
        font-size: 22px; 
        font-weight: 800; 
        color: {t['accent']}; 
        padding: 10px 0px; 
        margin-bottom: 5px; 
    }}
    QLabel#SectionTitle {{ 
        font-size: 10px; 
        font-weight: bold; 
        color: {t['accent']}; /* Usa accent per visibilità su temi chiari */
        opacity: 0.8;
        text-transform: uppercase; 
        letter-spacing: 1.5px; 
        margin-top: 5px; 
        margin-bottom: 5px; 
    }}
    QLabel {{ 
        font-size: 12px; 
        color: {t['text']}; /* Colore dinamico */
        font-weight: 500; 
        background: transparent; 
    }}

    /* Inputs (LineEdit, etc) */
    QLineEdit {{ 
        background-color: {t['input']}; 
        border: 2px solid {border_col}; 
        border-radius: 12px; 
        padding: 8px 15px; 
        color: {t['text']}; /* Fondamentale per temi chiari */
        font-size: 14px; 
        selection-background-color: {t['accent']};
        selection-color: {t['bg']};
    }}
    QLineEdit:focus {{ 
        border: 2px solid {t['accent']}; 
        background-color: {t['bg']}; 
    }}

    /* Buttons */
    QPushButton {{ 
        background-color: {t['btn']}; 
        color: {btn_txt_col}; 
        border-radius: 15px; 
        padding: 12px; 
        font-weight: bold; 
        border: none; 
    }}
    QPushButton:hover {{ 
        background-color: {t['accent']}; 
        color: {t['bg']}; 
        border: 1px solid {t['text']};
    }}

    /* Dropdowns (ComboBox) */
    QComboBox {{ 
        background-color: {t['input']}; 
        color: {t['text']};
        border: 2px solid {border_col}; 
        border-radius: 10px; 
        padding: 2px 10px; 
        font-size: 11px; 
        min-height: 25px; 
    }}
    QComboBox::drop-down {{ border: none; }}
    QComboBox QAbstractItemView {{
        background-color: {t['input']};
        color: {t['text']};
        selection-background-color: {t['accent']};
        selection-color: {t['bg']};
    }}

    /* Tables */
    QTableWidget {{ 
        background-color: {t['bg']}; 
        alternate-background-color: {t['sidebar']}; 
        gridline-color: {border_col}; 
        color: {t['text']};
    }}
    QHeaderView::section {{ 
        background-color: {t['sidebar']}; 
        color: {t['accent']}; 
        padding: 5px; 
        border: none; 
        font-weight: bold;
    }}
    QTableWidget::item {{ 
        padding: 5px; 
        color: {t['text']}; 
    }}
    QTableWidget::item:selected {{
        background-color: {t['accent']};
        color: {t['bg']};
    }}
    """