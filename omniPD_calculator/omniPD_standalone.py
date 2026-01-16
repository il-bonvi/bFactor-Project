# ==============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ==============================================================================

import os
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import math
from tkinter import ttk

# =========================
# Inserimento dati manuale con pulsante Importa Excel
# =========================
class ManualDataEntry:
    def __init__(self, master):
        self.master = master
        master.title("Data Entry")

        self.entries = []
        self.data = None

        # Testo informativo sopra le righe
        tk.Label(master, text="One must be sprint power (best 1-5s)\nMinimum 4 points!!", 
                 font=("Helvetica Neue", 12, "bold"), justify="center").grid(row=0, column=0, columnspan=2, pady=(5,2))
        
        # Testo informativo sotto le colonne
        durata_info = "3m=180 | 5m=300 | 12m=720 | 20m=1200\nby bonvi <3"
        tk.Label(master, text=durata_info,
                 font=("Arial", 9, "italic"), justify="center", fg="gray"
                 ).grid(row=2, column=0, columnspan=2, pady=(0,5))

        # Titoli colonne
        tk.Label(master, text="Time (s)").grid(row=3, column=0)
        tk.Label(master, text="Power (W)").grid(row=3, column=1)

        # Definisci la larghezza dei pulsanti
        btn_width = 15  

        # Pulsanti principali
        tk.Button(master, text="Add Row", command=self.add_row, width=btn_width).grid(row=2, column=2, padx=5, pady=2)
        tk.Button(master, text="Confirm", command=self.confirm, width=btn_width).grid(row=3, column=2, padx=5, pady=2)
        tk.Button(master, text="Import Excel", command=self.import_file, width=btn_width).grid(row=4, column=2, padx=5, pady=(10,5))

        # Inizia con 5 righe
        for _ in range(5):
            self.add_row()

        # Metti a fuoco e seleziona la prima cella appena aperta
        self.master.after(0, lambda: self.entries[0][0].focus_set())
        self.master.after(0, lambda: self.entries[0][0].select_range(0, tk.END))


        # Lega il tasto Enter al metodo confirm
        master.bind('<Return>', lambda event: self.confirm())


    def add_row(self):
        row = len(self.entries) + 4
        e1 = tk.Entry(self.master, width=10)
        e2 = tk.Entry(self.master, width=10)
        e1.grid(row=row, column=0, padx=5, pady=2)
        e2.grid(row=row, column=1, padx=5, pady=2)
        self.entries.append((e1, e2))

        def on_tab(event, entry=e2):
            if entry == self.entries[-1][1]:
                self.add_row()
                self.entries[-1][0].focus_set()
                return "break"
        e2.bind("<Tab>", on_tab)

    def remove_row(self):
        if self.entries:
            e1, e2 = self.entries.pop()
            e1.destroy()
            e2.destroy()

    def confirm(self):
        self.data = []
        for e1, e2 in self.entries:
            t_val = e1.get()
            p_val = e2.get()
            if t_val and p_val:
                try:
                    t_val = float(t_val)
                    p_val = float(p_val)
                    self.data.append((t_val, p_val))
                except ValueError:
                    messagebox.showerror("Errore", f"Valori non numerici: {t_val}, {p_val}")
                    return
        if len(self.data) < 4:
            messagebox.showerror("Errore", "Inserire almeno 4 punti dati")
            return
        self.master.destroy()

    def import_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona file",
            filetypes=[("Excel/CSV files", "*.xlsm *.xlsx *.csv")]
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".xlsm":
                try:
                    df = pd.read_excel(file_path, sheet_name="Summary Sheet", usecols="A:B", header=None)
                except ValueError:
                    df = pd.read_excel(file_path, sheet_name=0, usecols="A:B", header=None)
            elif ext == ".xlsx":
                df = pd.read_excel(file_path, usecols="A:B", header=None)
            elif ext == ".csv":
                df_csv = pd.read_csv(file_path, sep=None, engine="python")

                # =========================
                # Selector colonne CSV
                # =========================
                class CSVColumnSelector(tk.Toplevel):
                    def __init__(self, master, columns):
                        super().__init__(master)
                        self.title("Seleziona colonne CSV")
                        self.result = None
                        self.grab_set()

                        tk.Label(self, text="Colonna Tempo (s)").grid(row=0, column=0, padx=5, pady=5)
                        tk.Label(self, text="Colonna Potenza (W)").grid(row=1, column=0, padx=5, pady=5)

                        self.cb_t = ttk.Combobox(self, values=list(columns), state="readonly")
                        self.cb_p = ttk.Combobox(self, values=list(columns), state="readonly")
                        self.cb_t.grid(row=0, column=1, padx=5)
                        self.cb_p.grid(row=1, column=1, padx=5)

                        self.cb_t.current(0)
                        self.cb_p.current(1 if len(columns) > 1 else 0)

                        tk.Button(self, text="OK", command=self.ok).grid(row=2, column=0, columnspan=2, pady=10)

                    def ok(self):
                        self.result = (self.cb_t.current(), self.cb_p.current())
                        self.destroy()

                sel = CSVColumnSelector(self.master, df_csv.columns)
                self.master.wait_window(sel)
                if sel.result is None:
                    messagebox.showerror("Errore", "Selezione colonne annullata")
                    return
                col_time_idx, col_power_idx = sel.result
                df = df_csv.iloc[:, [col_time_idx, col_power_idx]]
            else:
                messagebox.showerror("Errore", "Formato file non supportato")
                return
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            return
        # Conversione valori numerici e rimozione NaN
        df.columns = ["t", "P"]
        df["t"] = pd.to_numeric(df["t"], errors="coerce")
        df["P"] = pd.to_numeric(df["P"], errors="coerce")
        df = df.dropna()
        if df.empty:
            messagebox.showerror("Errore", "File senza dati numerici validi")
            return

        self.data = df.values.tolist()
        self.master.destroy()

# =========================
# Esecuzione finestra
# =========================
root_input = tk.Tk()
entry_window = ManualDataEntry(root_input)
root_input.mainloop()

if not entry_window.data:
    raise ValueError("Nessun dato inserito o selezionato")

# Trasforma in DataFrame
df = pd.DataFrame(entry_window.data, columns=["t", "P"])




# =========================
# Costante di modello
# =========================
TCPMAX = 1800  # secondi

# =========================
# Funzioni comuni
# =========================
def ompd_power(t, CP, W_prime, Pmax, A):
    t = np.array(t, dtype=float)
    base = (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP
    P = np.where(t <= TCPMAX, base, base - A * np.log(t / TCPMAX))
    return P

def ompd_power_short(t, CP, W_prime, Pmax):
    t = np.array(t, dtype=float)
    return (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP

def w_eff(t, W_prime, CP, Pmax):
    return W_prime * (1 - np.exp(-t * (Pmax - CP) / W_prime))

def _format_time_label_custom(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m{secs}s"

def _format_time_label_custom_residuals(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes >= 60:
        h = minutes // 60
        m = minutes % 60
        return f"{h}h" if m == 0 else f"{h}h{m}m"
    return f"{minutes}m" if secs == 0 else f"{minutes}m{secs}s"

# Fit OmPD standard
initial_guess = [np.percentile(df["P"], 30), 20000, df["P"].max(), 5]
params, _ = curve_fit(ompd_power, df["t"].values, df["P"].values, p0=initial_guess, maxfev=20000)
CP, W_prime, Pmax, A = params

# Calcolo errori
P_pred = ompd_power(df["t"].values, CP, W_prime, Pmax, A)
residuals = df["P"].values - P_pred
RMSE = np.sqrt(np.mean(residuals**2))
MAE  = np.mean(np.abs(residuals))

# W' efficace
T_plot_w = np.linspace(1, 3*60, 500)
Weff_plot = w_eff(T_plot_w, W_prime, CP, Pmax)
W_99 = 0.99 * W_prime
t_99_idx = np.argmin(np.abs(Weff_plot - W_99))
t_99 = T_plot_w[t_99_idx]
w_99 = Weff_plot[t_99_idx]

# =========================
# Finestra principale Tkinter con Notebook
# =========================
root_tab = tk.Tk()
root_tab.title("OmPD MultiTab Viewer")
notebook = ttk.Notebook(root_tab)
notebook.pack(fill='both', expand=True)

# =========================
# Tab 1: OmPD
# =========================
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="OmPD")

fig1, ax1 = plt.subplots(figsize=(10,6))
T_plot = np.logspace(np.log10(1.0), np.log10(max(max(df["t"])*1.1, 180*60)), 500)

# Marker styling
max_annotations = 8
marker_lw = 1 if len(df)<=max_annotations else 0.5
marker_size = 40 if len(df)<=max_annotations else 20

ax1.scatter(df["t"], df["P"], label="Dati reali", color="black", marker="x", s=marker_size, linewidths=marker_lw, zorder=3)
ax1.plot(T_plot, ompd_power(T_plot, *params), label="OmPD", zorder=2)
ax1.plot(T_plot[T_plot<=TCPMAX], ompd_power_short(T_plot[T_plot<=TCPMAX], CP, W_prime, Pmax), linestyle='--', color='blue', linewidth=1, label='Curva base t ≤ TCPmax')

# Assi e griglie
ax1.set_xscale("log")
ax1.set_xlim(left=1, right=180*60)
xticks = [5, 3*60, 5*60, 12*60, 20*60, 30*60, 40*60, 60*60]
ax1.xaxis.set_major_locator(FixedLocator(xticks))
ax1.xaxis.set_minor_locator(plt.NullLocator())
ax1.set_xticklabels([f"{int(t/60)}m" if t>=60 else f"{int(t)}s" for t in xticks])
ax1.set_xlabel("Time")
ax1.set_ylabel("Power (W)")
ax1.set_title("OmniPD Curve")
y_min = 50
y_max = math.ceil(max(Pmax, df["P"].max()) / 50) * 50
major_ticks = np.arange(y_min, y_max + 1, 50)
minor_ticks = np.arange(y_min, y_max + 1, 10)
ax1.set_yticks(major_ticks)
ax1.set_yticks(minor_ticks, minor=True)
ax1.set_ylim(bottom=y_min, top=y_max)
ax1.grid(which='major', linestyle='-', linewidth=0.8, alpha=0.7)
ax1.grid(which='minor', linestyle='--', linewidth=0.5, alpha=0.4)

# Riquadro parametri stimati
textstr = f"CP={int(round(CP))} W\nW'={int(round(W_prime))} J\nPmax={int(round(Pmax))} W\nA={A:.2f}"
ax1.text(0.98, 0.98, textstr, transform=ax1.transAxes, fontsize=9,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# Annotazioni interattive
ann_curve = ax1.annotate('', xy=(0,0), xytext=(15,15), textcoords='offset points',
                        bbox=dict(boxstyle='round', fc='w'), arrowprops=dict(arrowstyle='->'))
ann_curve.set_visible(False)
cursor_point, = ax1.plot([], [], marker='o', color='red', markersize=2, zorder=5, visible=False)

def on_move_tab1_smooth(event):
    if event.inaxes != ax1 or event.xdata is None or event.xdata <= 0:
        ann_curve.set_visible(False)
        cursor_point.set_visible(False)
        fig1.canvas.draw_idle()
        return
    x = event.xdata
    y_curve = ompd_power(np.array([x]), *params)[0]  # modello continuo
    ann_curve.xy = (x, y_curve)
    ann_curve.set_text(f"{_format_time_label_custom(x)} ({int(round(x))}s)\n{int(round(y_curve))} W")
    ann_curve.set_visible(True)
    cursor_point.set_data([x], [y_curve])
    cursor_point.set_visible(True)
    fig1.canvas.draw_idle()

fig1.canvas.mpl_connect('motion_notify_event', on_move_tab1_smooth)

# Hover o annotazioni fisse
hover_ann1 = ax1.annotate('', xy=(0, 0), xytext=(15, 15), textcoords='offset points',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), arrowprops=dict(arrowstyle='->'))
hover_ann1.set_visible(False)

if len(df) <= max_annotations:
    for i in range(len(df)):
        ax1.annotate(
            f"{_format_time_label_custom(df['t'].iloc[i])} ({int(round(df['t'].iloc[i]))}s)\n{int(round(df['P'].iloc[i]))} W",
            xy=(df['t'].iloc[i], df['P'].iloc[i]),
            xytext=(-50, -50),
            textcoords='offset points',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            arrowprops=dict(arrowstyle='-', linewidth=1, color='gray', shrinkA=1, shrinkB=3),
            fontsize=10
        )
else:
    def on_hover_points_tab1(event):
        if event.inaxes != ax1 or event.xdata is None:
            hover_ann1.set_visible(False)
            fig1.canvas.draw_idle()
            return
        x, y = event.xdata, event.ydata
        dx = np.abs(np.log10(df['t']) - np.log10(x))
        dy = np.abs(df['P'] - y)
        dist = np.sqrt(dx**2 + (dy / 100)**2)
        idx = np.argmin(dist)
        if dist.iloc[idx] < 0.1:
            hover_ann1.xy = (df['t'].iloc[idx], df['P'].iloc[idx])
            hover_ann1.set_text(f"{_format_time_label_custom(df['t'].iloc[idx])} ({int(round(df['t'].iloc[idx]))}s)\n{int(round(df['P'].iloc[idx]))} W")
            hover_ann1.set_visible(True)
        else:
            hover_ann1.set_visible(False)
        fig1.canvas.draw_idle()
    fig1.canvas.mpl_connect('motion_notify_event', on_hover_points_tab1)

# Linee CP e TCPMAX
ax1.axhline(y=CP, color='red', linestyle='--', linewidth=1.0, alpha=0.8, zorder=1)
ax1.axvline(x=TCPMAX, color='blue', linestyle=':', linewidth=1.0, alpha=0.7, zorder=1)

# Mini-leggenda
custom_lines = [Line2D([0],[0],color='red',linestyle='--',linewidth=1.0),
                Line2D([0],[0],color='blue',linestyle=':',linewidth=1.0)]
ax1.legend(custom_lines, ['CP','TCPmax'], loc='lower left', fontsize=9, framealpha=0.9)

# Canvas Matplotlib
canvas1 = FigureCanvasTkAgg(fig1, master=tab1)
canvas1.get_tk_widget().pack(fill='both', expand=True)

# Toolbar standard
toolbar1 = NavigationToolbar2Tk(canvas1, tab1)
toolbar1.update()

# Forza il salvataggio dello stato originale come home
canvas1.draw_idle()         # disegna la figura
toolbar1.push_current()     # salva lo stato corrente come home

# =========================
# ZOOM MANUALE + PRESET X
# =========================

class ZoomDialogCustom(tk.Toplevel):
    def __init__(self, master, labels=None, units=None, title="Manual Zoom"):
        super().__init__(master)
        self.title(title)
        self.result = None
        self.grab_set()  # modale

        if labels is None:
            labels = ["X min", "X max", "Y min", "Y max"]
        if units is None:
            units = ["", "", "", ""]

        self.entries = []

        for i, label in enumerate(labels):
            frame = tk.Frame(self)
            frame.grid(row=i, column=0, padx=6, pady=5)

            tk.Label(frame, text=label, width=14, anchor="w").pack(side="left")

            e = tk.Entry(frame, width=10)
            e.pack(side="left")

            if units[i]:
                tk.Label(frame, text=units[i]).pack(side="left", padx=(5, 0))

            self.entries.append(e)

        # focus automatico sulla prima cella
        self.after(50, lambda: self.entries[0].focus_set())
        self.after(50, lambda: self.entries[0].select_range(0, tk.END))

        tk.Button(self, text="OK", width=10, command=self.on_ok)\
            .grid(row=len(labels), column=0, pady=10)

        # ENTER = OK
        self.bind("<Return>", lambda event: self.on_ok())

    def on_ok(self):
        try:
            self.result = [float(e.get()) for e in self.entries]
            self.destroy()
        except ValueError:
            messagebox.showerror("Errore", "Inserisci solo numeri validi")


# Funzione zoom manuale completo
def manual_zoom_custom(ax, canvas, master, labels=None, units=None):
    dialog = ZoomDialogCustom(master, labels=labels, units=units)
    master.wait_window(dialog)
    if dialog.result:
        x_min, x_max, y_min, y_max = dialog.result
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        canvas.draw_idle()


# =========================
# PULSANTI ZOOM + PRESET X/Y
# =========================

def zoom_x_preset(ax, canvas, x_max, x_min=1):
    ax.set_xlim(x_min, x_max)
    canvas.draw_idle()

def zoom_y_preset(ax, canvas, y_min=None, y_max=None):
    if y_min is not None and y_max is not None:
        ax.set_ylim(y_min, y_max)
    canvas.draw_idle()



zoom_frame1 = tk.Frame(tab1)
zoom_frame1.pack(side="bottom", pady=5)

# Manual Zoom
tk.Button(
    zoom_frame1,
    text="Manual Zoom",
    command=lambda: manual_zoom_custom(
        ax1, canvas1, root_tab,
        labels=["Time min", "Time max", "Power min", "Power max"],
        units=["s", "s", "W", "W"]
    )
).pack(side="left", padx=6)

# Presets
tk.Button(
    zoom_frame1,
    text="Fit Data X",
    command=lambda: zoom_x_preset(ax1, canvas1, x_min=df["t"].min(), x_max=df["t"].max())
).pack(side="left", padx=6)

tk.Button(
    zoom_frame1,
    text="60m",
    command=lambda: zoom_x_preset(ax1, canvas1, x_max=3600)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame1,
    text="2m→30m",
    command=lambda: zoom_x_preset(ax1, canvas1, x_max=1800, x_min=120)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame1,
    text="3m→20m",
    command=lambda: zoom_x_preset(ax1, canvas1, x_max=1200, x_min=180)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame1,
    text="1000W",
    command=lambda: zoom_y_preset(ax1, canvas1, y_max=1000)
).pack(side="left", padx=6)


# =========================
# Tab 2: Residuals
# =========================
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Residuals")

fig2, ax2 = plt.subplots(figsize=(10,4))
ax2.axhline(0, color='black', linestyle='--', linewidth=1)
ax2.plot(df["t"], residuals, linestyle='-', color='red', linewidth=1,
         marker='x', markerfacecolor='black', markeredgecolor='black', markersize=5)

hover_ann2 = ax2.annotate('', xy=(0,0), xytext=(15,15), textcoords='offset points',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), arrowprops=dict(arrowstyle='->'))
hover_ann2.set_visible(False)

def on_hover_tab2(event):
    if event.inaxes != ax2 or event.xdata is None:
        hover_ann2.set_visible(False)
        fig2.canvas.draw_idle()
        return
    x = event.xdata
    idx = np.argmin(np.abs(df["t"].values - x))
    hover_ann2.xy = (df["t"].iloc[idx], residuals[idx])
    hover_ann2.set_text(f"{_format_time_label_custom_residuals(df['t'].iloc[idx])} ({int(df['t'].iloc[idx])} s)\n{residuals[idx]:.2f} W")
    hover_ann2.set_visible(True)
    fig2.canvas.draw_idle()

fig2.canvas.mpl_connect("motion_notify_event", on_hover_tab2)

# Tick e griglia
xticks2 = [5,30,60,3*60,5*60,6*60,10*60,12*60,15*60,20*60,30*60,60*60]  # lascia tutti i valori, non filtrare
ax2.set_xscale("log")  # scala log
ax2.xaxis.set_major_locator(FixedLocator(xticks2))
ax2.xaxis.set_major_formatter(FuncFormatter(lambda x,pos:_format_time_label_custom_residuals(x)))
ax2.tick_params(axis='x', which='both', length=0)
ax2.set_xlabel("Time")
ax2.set_ylabel("Residuals (W)")
ax2.set_title("OmPD Residuals")


# Griglia secondaria
sec_ticks = np.concatenate([
    np.arange(1,6,1),
    np.arange(5,31,5),
    np.arange(40,61,10),
    np.arange(60,12*60+1,30),
    np.arange(12*60+60,20*60+1,60),
    np.arange(20*60+5*60,60*60+1,5*60)
])
sec_ticks = sec_ticks[sec_ticks<=60*60]
for t in sec_ticks:
    ax2.axvline(x=t,color='gray',linestyle=':',linewidth=0.5,alpha=0.5,zorder=0)
ax2.grid(which='major', linestyle='-', linewidth=0.7, alpha=0.7)
ax2.grid(which='minor', linestyle='--', linewidth=0.4, alpha=0.4)

# Riquadro metriche
metrics_text = f"RMSE = {RMSE:.2f} W\nMAE  = {MAE:.2f} W"
ax2.text(0.98,0.98,metrics_text, transform=ax2.transAxes, fontsize=9,
         verticalalignment='top', horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

canvas2 = FigureCanvasTkAgg(fig2, master=tab2)
canvas2.get_tk_widget().pack(fill='both', expand=True)

toolbar2 = NavigationToolbar2Tk(canvas2, tab2)
toolbar2.update()

# Salva lo stato iniziale come home
canvas2.draw_idle()
toolbar2.push_current()


# =========================
# PULSANTI ZOOM - TAB 2
# =========================
zoom_frame2 = tk.Frame(tab2)
zoom_frame2.pack(side="bottom", pady=5)

# Manual Zoom
tk.Button(
    zoom_frame2,
    text="Manual Zoom",
    command=lambda: manual_zoom_custom(
        ax2, canvas2, root_tab,
        labels=["Time min", "Time max", "Residual min", "Residual max"],
        units=["s","s","W","W"]
    )
).pack(side="left", padx=6)

# Presets
tk.Button(
    zoom_frame2,
    text="Fit Data X",
    command=lambda: zoom_x_preset(ax2, canvas2, x_min=df["t"].min(), x_max=df["t"].max())
).pack(side="left", padx=6)

tk.Button(
    zoom_frame2,
    text="2m",
    command=lambda: zoom_x_preset(ax2, canvas2, x_max=120)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame2,
    text="6m",
    command=lambda: zoom_x_preset(ax2, canvas2, x_max=360)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame2,
    text="60m",
    command=lambda: zoom_x_preset(ax2, canvas2, x_max=3600)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame2,
    text="2m->30m",
    command=lambda: zoom_x_preset(ax2, canvas2, x_max=1800, x_min=120)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame2,
    text="-10 + 10",
    command=lambda: zoom_y_preset(ax2, canvas2, y_min=-10, y_max=10)
).pack(side="left", padx=6)

tk.Button(
    zoom_frame2,
    text="-50 + 50",
    command=lambda: zoom_y_preset(ax2, canvas2, y_min=-50, y_max=50)
).pack(side="left", padx=6)

tk.Button(
    zoom_frame2,
    text="-100 + 100",
    command=lambda: zoom_y_preset(ax2, canvas2, y_min=-100, y_max=100)
).pack(side="left", padx=6)


# =========================
# Tab 3: W'eff
# =========================
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="W'eff")

fig3, ax3 = plt.subplots(figsize=(10,6))
ax3.set_title("OmPD Effective W'")
ax3.plot(T_plot_w, Weff_plot, color='green', linewidth=2)
ax3.axhline(y=w_99,color='blue',linestyle='--',linewidth=1,alpha=0.8,zorder=2)
ax3.axvline(x=t_99,color='blue',linestyle='--',linewidth=1,alpha=0.8,zorder=2)
minutes = int(t_99//60)
seconds = int(t_99%60)
ax3.annotate(f"99% W'eff at {minutes}m{seconds}s ({int(t_99)}s)",
             xy=(t_99,W_99), xytext=(10,-18), textcoords='offset points',
             bbox=dict(boxstyle='round', facecolor='blue', alpha=0.2), fontsize=10)

# Marker interattivo
marker_line, = ax3.plot([], [], marker='o', color='red', zorder=5, visible=False)
marker_text = ax3.annotate('', xy=(0,0), xytext=(10,-30), textcoords='offset points',
                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
marker_text.set_visible(False)

def on_move_tab3(event):
    if event.inaxes != ax3 or event.xdata is None:
        marker_line.set_visible(False)
        marker_text.set_visible(False)
        fig3.canvas.draw_idle()
        return
    x = event.xdata
    if x<1 or x>T_plot_w[-1]:
        marker_line.set_visible(False)
        marker_text.set_visible(False)
        fig3.canvas.draw_idle()
        return
    y = w_eff(np.array([x]), W_prime, CP, Pmax)[0]
    marker_line.set_data([x],[y])
    marker_line.set_visible(True)
    marker_text.xy = (x,y)
    marker_text.set_text(f"{_format_time_label_custom(x)} | {int(y)} J")
    marker_text.set_visible(True)
    fig3.canvas.draw_idle()

fig3.canvas.mpl_connect('motion_notify_event', on_move_tab3)

# Assi, griglia, riquadro
ax3.set_xlim(0,3*60)
ax3.set_ylim(0,np.max(Weff_plot)*1.1)
ax3.set_xlabel("Time")
ax3.set_ylabel("W'eff (J)")
x_ticks = list(range(0,181,30))
ax3.set_xticks(x_ticks)
ax3.set_xticklabels([f"{int(t//60)}m{int(t%60)}s" if t>=60 else f"{int(t)}s" for t in x_ticks])
ax3.set_xticks(np.arange(0,3*60+10,10), minor=True)
ax3.grid(which='minor', linestyle='--', linewidth=0.5, alpha=0.4)
ax3.grid(which='major', linestyle='-', linewidth=0.8, alpha=0.7)
ax3.text(0.98,0.98,f"W' = {int(W_prime)} J", transform=ax3.transAxes,
         fontsize=10, verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

canvas3 = FigureCanvasTkAgg(fig3, master=tab3)
canvas3.get_tk_widget().pack(fill='both', expand=True)
toolbar3 = NavigationToolbar2Tk(canvas3, tab3)
toolbar3.update()
canvas3.draw_idle()
toolbar3.push_current()  # salva lo stato iniziale come home

# =========================
# PULSANTI ZOOM - TAB 3
# =========================
zoom_frame3 = tk.Frame(tab3)
zoom_frame3.pack(side="bottom", pady=5)

# Manual Zoom
tk.Button(
    zoom_frame3,
    text="Manual Zoom",
    command=lambda: manual_zoom_custom(
        ax3, canvas3, root_tab,
        labels=["Time min", "Time max", "Joule min", "Joule max"],
        units=["s","s","J","J"]
    )
).pack(side="left", padx=6)

# Presets
tk.Button(
    zoom_frame3,
    text="Fit Data X",
    command=lambda: zoom_x_preset(ax3, canvas3, x_min=df["t"].min(), x_max=df["t"].max())
).pack(side="left", padx=6)

tk.Button(
    zoom_frame3,
    text="120s",
    command=lambda: zoom_x_preset(ax3, canvas3, x_max=120)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame3,
    text="300s",
    command=lambda: zoom_x_preset(ax3, canvas3, x_max=300)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame3,
    text="750s",
    command=lambda: zoom_x_preset(ax3, canvas3, x_max=750)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame3,
    text="3m→20m",
    command=lambda: zoom_x_preset(ax3, canvas3, x_min=180, x_max=1200)
).pack(side="left", padx=3)

tk.Button(
    zoom_frame3,
    text="30000J",
    command=lambda: zoom_y_preset(ax3, canvas3, y_max=30000)
).pack(side="left", padx=6)




# =========================
# Avvio finestra
# =========================
root_tab.mainloop()
