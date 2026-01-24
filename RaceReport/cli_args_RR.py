import argparse


def parse_args(args=None):
    """
    Definisce e parsea gli argomenti CLI esattamente come in race.py.
    Se args è None, usa sys.argv. Se args è una lista vuota, restituisce defaults (utile per GUI).
    """
    parser = argparse.ArgumentParser(
        description='Genera report dalle gare leggendo tutti i CSV in una cartella'
    )
    parser.add_argument('-d', '--dir', dest='csv_dir', default=None,
                        help='Cartella contenente i CSV (default: cartella corrente)')
    parser.add_argument('-t', '--title', dest='custom_title', default=None,
                        help='Titolo personalizzato per il report (utilizzato quando sono presenti più CSV)')
    parser.add_argument('-c', '--color', dest='bg_color', default='#d9e8dd',
                        help='Colore di sfondo del report in formato esadecimale (default: #d9e8dd)')

    # Opzioni CLI per controllare dimensione e margini del logo (pagina 1)
    group_page1 = parser.add_argument_group(
        'Logo Page 1 options',
        'Opzioni per dimensione e margini del logo sulla pagina 1 (tabella)'
    )
    group_page1.add_argument('--logo-frac', dest='logo_frac', type=float, default=0.03,
                             help='Larghezza logo pagina 1 come frazione della larghezza figura (default: 0.04)')
    group_page1.add_argument('--logo-margin-right', dest='logo_margin_right', type=float, default=0.03,
                             help='Margine destro logo pagina 1 come frazione figura (default: 0.03)')
    group_page1.add_argument('--logo-margin-top', dest='logo_margin_top', type=float, default=0.018,
                             help='Margine superiore logo pagina 1 come frazione figura (default: 0.018)')

    # Gruppo per le altre pagine (grafici)
    group_other = parser.add_argument_group(
        'Logo Pages 2-4 options',
        'Opzioni per dimensione e margini del logo sulle pagine 2-4 (grafici)'
    )
    group_other.add_argument('--other-logo-frac', dest='other_logo_frac', type=float, default=0.05,
                             help='Larghezza logo altre pagine come frazione della larghezza figura (default: 0.08)')
    group_other.add_argument('--other-logo-margin-right', dest='other_logo_margin_right', type=float, default=0.015,
                             help='Margine destro logo altre pagine come frazione figura (default: 0.03)')
    group_other.add_argument('--other-logo-margin-top', dest='other_logo_margin_top', type=float, default=0.01,
                             help='Margine superiore logo altre pagine come frazione figura (default: 0.03)')

    return parser.parse_args(args)
