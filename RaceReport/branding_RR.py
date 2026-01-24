import os
from PIL import Image


def add_branding_to_figure(fig, logo_path=None, bg_color='#d9e8dd',
                           logo_w_frac=0.03, margin_right=0.03, margin_top=0.018):
    """
    Aggiunge branding alla figura principale (pagina tabella) con parametri espliciti.
    Logica identica all'implementazione originale.
    """
    fig.patch.set_facecolor(bg_color)
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert('RGBA')
            img_w, img_h = logo.size
            fig_w, fig_h = fig.get_figwidth(), fig.get_figheight()
            logo_h_frac = logo_w_frac * (img_h / img_w) * (fig_w / fig_h)
            left = 1.0 - margin_right - logo_w_frac
            bottom = 1.0 - margin_top - logo_h_frac
            ax_logo = fig.add_axes([left, bottom, logo_w_frac, logo_h_frac], anchor='NE', zorder=100)
            ax_logo.imshow(logo)
            ax_logo.axis('off')
        except Exception as e:
            print(f"Avvertenza: impossibile caricare il logo '{logo_path}': {e}")


def add_branding_to_other_pages(fig, logo_path=None, bg_color='#d9e8dd',
                                logo_w_frac=0.05, margin_right=0.015, margin_top=0.01):
    """
    Aggiunge branding alle pagine successive (grafici) con parametri espliciti.
    Logica identica all'implementazione originale.
    """
    fig.patch.set_facecolor(bg_color)
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert('RGBA')
            img_w, img_h = logo.size
            fig_w, fig_h = fig.get_figwidth(), fig.get_figheight()
            logo_h_frac = logo_w_frac * (img_h / img_w) * (fig_w / fig_h)
            left = 1.0 - margin_right - logo_w_frac
            bottom = 1.0 - margin_top - logo_h_frac
            ax_logo = fig.add_axes([left, bottom, logo_w_frac, logo_h_frac], anchor='NE', zorder=100)
            ax_logo.imshow(logo)
            ax_logo.axis('off')
        except Exception as e:
            print(f"Avvertenza: impossibile caricare il logo '{logo_path}': {e}")
