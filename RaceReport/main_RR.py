

import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from .cli_args_RR import parse_args
from .data_prep_RR import read_and_prepare
from .naming_RR import compute_pdf_path_and_title
from .table_page_RR import build_table_figure
from .branding_RR import add_branding_to_figure, add_branding_to_other_pages
from .plots_RR import create_distance_figure, create_power_hr_figure, create_work_figure


def _run():
    args = parse_args()
    bg_color = args.bg_color
    print(f"Colore di sfondo impostato: {bg_color}")

    # Logo settings
    LOGO_W_FRAC_PAGE1 = args.logo_frac
    LOGO_MARGIN_RIGHT_PAGE1 = args.logo_margin_right
    LOGO_MARGIN_TOP_PAGE1 = args.logo_margin_top
    OTHER_LOGO_W_FRAC = args.other_logo_frac
    OTHER_LOGO_MARGIN_RIGHT = args.other_logo_margin_right
    OTHER_LOGO_MARGIN_TOP = args.other_logo_margin_top
    print(
        f"Logo page1 settings: width_frac={LOGO_W_FRAC_PAGE1}, "
        f"margin_right={LOGO_MARGIN_RIGHT_PAGE1}, margin_top={LOGO_MARGIN_TOP_PAGE1}"
    )
    print(
        f"Logo pages2-4 settings: width_frac={OTHER_LOGO_W_FRAC}, "
        f"margin_right={OTHER_LOGO_MARGIN_RIGHT}, margin_top={OTHER_LOGO_MARGIN_TOP}"
    )

    csv_dir = args.csv_dir or os.getcwd()
    df, raw_df, csv_files, single_csv = read_and_prepare(csv_dir)

    # Prompt title only when multiple CSVs and no custom title provided
    if not single_csv and not args.custom_title:
        print("\nSono presenti più file CSV.")
        user_title = input(
            "Desideri aggiungere un titolo al report? (Premi INVIO per saltare, altrimenti scrivi il titolo): "
        ).strip()
        if user_title:
            args.custom_title = user_title
            print(f"Titolo impostato: {args.custom_title}")
        else:
            print("Nessun titolo impostato.")

    # Cerca sempre il logo nella cartella del modulo Python
    logo_file = os.path.join(os.path.dirname(__file__), 'LOGO.png')
    pdf_path, title_text = compute_pdf_path_and_title(
        csv_dir, csv_files, single_csv, df, raw_df, args.custom_title
    )
    args.custom_title = title_text

    # Build table page
    fig, _df_table = build_table_figure(df, raw_df, args, logo_file, bg_color)

    with PdfPages(pdf_path) as pdf:
        # Branding page 1
        add_branding_to_figure(
            fig,
            logo_path=logo_file,
            bg_color=bg_color,
            logo_w_frac=LOGO_W_FRAC_PAGE1,
            margin_right=LOGO_MARGIN_RIGHT_PAGE1,
            margin_top=LOGO_MARGIN_TOP_PAGE1,
        )
        pdf.savefig(fig, bbox_inches=None, pad_inches=0.1)
        plt.close(fig)

        # Distance + time
        fig2 = create_distance_figure(df, bg_color, logo_file)
        if fig2 is not None:
            add_branding_to_other_pages(
                fig2,
                logo_path=logo_file,
                bg_color=bg_color,
                logo_w_frac=OTHER_LOGO_W_FRAC,
                margin_right=OTHER_LOGO_MARGIN_RIGHT,
                margin_top=OTHER_LOGO_MARGIN_TOP,
            )
            pdf.savefig(fig2)
            plt.close(fig2)

        # Power + HR
        fig3 = create_power_hr_figure(df, bg_color, logo_file)
        if fig3 is not None:
            add_branding_to_other_pages(
                fig3,
                logo_path=logo_file,
                bg_color=bg_color,
                logo_w_frac=OTHER_LOGO_W_FRAC,
                margin_right=OTHER_LOGO_MARGIN_RIGHT,
                margin_top=OTHER_LOGO_MARGIN_TOP,
            )
            pdf.savefig(fig3)
            plt.close(fig3)

        # Work pages
        fig4 = create_work_figure(df, bg_color, logo_file)
        if fig4 is not None:
            add_branding_to_other_pages(
                fig4,
                logo_path=logo_file,
                bg_color=bg_color,
                logo_w_frac=OTHER_LOGO_W_FRAC,
                margin_right=OTHER_LOGO_MARGIN_RIGHT,
                margin_top=OTHER_LOGO_MARGIN_TOP,
            )
            pdf.savefig(fig4)
            plt.close(fig4)

        print(f"Report PDF generato: {os.path.abspath(pdf_path)}")


if __name__ == "__main__":
    _run()
    raise SystemExit(0)