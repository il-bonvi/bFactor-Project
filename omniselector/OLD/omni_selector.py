import os
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.optimize import curve_fit

# =========================
# Costanti
# =========================
TCPMAX = 1800

# =========================
# Modello OmPD
# =========================
def ompd_power(t, CP, Wp, Pmax, A):
    t = np.asarray(t, dtype=float)
    base = (Wp / t) * (1 - np.exp(-t * (Pmax - CP) / Wp)) + CP
    return np.where(t <= TCPMAX, base, base - A * np.log(t / TCPMAX))

# =========================
# Finestra selezione colonne CSV
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

# =========================
# Finestra selezione finestre temporali (multilinea)
# =========================
class WindowSelector(tk.Toplevel):
    def __init__(self, master, defaults):
        super().__init__(master)
        self.title("Finestre temporali (secondi)")
        self.result = None
        self.grab_set()

        w, h = 400, 300
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(350, 250)
        self.resizable(True, True)

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Inserisci finestre temporali (una per riga, formato: tmin,tmax)\n(es: 120,300)",
            font=("Helvetica", 10, "bold")
        ).pack(pady=(0, 10))

        # Textbox multilinea
        self.text = tk.Text(main, height=10)
        self.text.pack(fill="both", expand=True)
        # Inserisco i default come testo iniziale
        default_text = "\n".join(f"{t1},{t2}" for t1, t2 in defaults)
        self.text.insert("1.0", default_text)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="left", padx=5)

    def on_ok(self):
        windows = []
        try:
            # prendo tutte le righe della textbox
            lines = self.text.get("1.0", "end").strip().splitlines()
            for line in lines:
                if line.strip():
                    parts = line.split(",")
                    if len(parts) != 2:
                        raise ValueError(f"Riga non valida: {line}")
                    t1 = float(parts[0].strip())
                    t2 = float(parts[1].strip())
                    if t2 <= t1:
                        raise ValueError(f"tmax deve essere maggiore di tmin: {line}")
                    windows.append((t1, t2))

            if not windows:
                raise ValueError("Nessuna finestra valida inserita")

            self.result = windows
            self.destroy()
        except Exception as e:
            messagebox.showerror("Errore", str(e))

# =========================
# Finestra selezione percentile
# =========================
class PercentileSelector(tk.Toplevel):
    def __init__(self, master, default=80):
        super().__init__(master)
        self.title("Percentile selezione punti")
        self.result = None
        self.grab_set()

        tk.Label(self, text="Percentile residui (es. 80)").pack(pady=10)
        self.entry = ttk.Entry(self, width=10)
        self.entry.pack(pady=5)
        self.entry.insert(0, str(default))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="left", padx=5)

    def on_ok(self):
        try:
            val = float(self.entry.get())
            if not 0 < val < 100:
                raise ValueError
            self.result = val
            self.destroy()
        except:
            messagebox.showerror("Errore", "Inserisci un numero tra 0 e 100")

# =========================
# Finestra selezione durata sprint
# =========================
class SprintSelector(tk.Toplevel):
    def __init__(self, master, default="2"):
        super().__init__(master)
        self.title("Selezione durata sprint (s)")
        self.result = None
        self.grab_set()

        tk.Label(self, text="Durata dello sprint (s)\nPuoi inserire più valori separati da virgola, es: 2,30").pack(pady=10)
        self.entry = ttk.Entry(self, width=20)
        self.entry.pack(pady=5)
        self.entry.insert(0, default)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Annulla", command=self.destroy).pack(side="left", padx=5)

    def on_ok(self):
        try:
            vals = [float(v.strip()) for v in self.entry.get().split(",") if v.strip()]
            if not vals:
                raise ValueError
            self.result = vals
            self.destroy()
        except:
            messagebox.showerror("Errore", "Inserisci valori numerici separati da virgola")

# =========================
# Import dati
# =========================
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    filetypes=[("CSV / Excel", "*.csv *.xlsx *.xlsm")]
)
if not file_path:
    raise SystemExit

ext = os.path.splitext(file_path)[1].lower()
if ext == ".csv":
    df_csv = pd.read_csv(file_path)
    sel = CSVColumnSelector(root, df_csv.columns)
    sel.wait_window()
    tcol, pcol = sel.result
    df = df_csv.iloc[:, [tcol, pcol]]
else:
    df = pd.read_excel(file_path, usecols=[0, 1], header=None)

df.columns = ["t", "P"]
df = df.apply(pd.to_numeric, errors="coerce").dropna()
df = df[df["t"] > 0]

# =========================
# Selezione finestre temporali
# =========================
default_windows = [
    (120, 240),
    (240, 480),
    (480, 900),
    (900, 1800),
    (1800, 2700),
    (2700, 4500)
]

ws = WindowSelector(root, default_windows)
ws.wait_window()
windows = ws.result

# =========================
# Percentile selezione punti
# =========================
ps = PercentileSelector(root, default=80)
ps.wait_window()
percentile_value = ps.result if ps.result else 80

# =========================
# Fit OmPD
# =========================
p0 = [np.percentile(df["P"], 30), 20000, df["P"].max(), 5]
params, _ = curve_fit(ompd_power, df["t"], df["P"], p0=p0, maxfev=20000)
CP, Wp, Pmax, A = params

# =========================
# Residuals & selezione punti filtrati (percentile globale)
# =========================
pred = ompd_power(df["t"], CP, Wp, Pmax, A)
res = df["P"] - pred
cut_global = np.percentile(res[df["t"] > 120], percentile_value)
df_sel = df[(res >= cut_global) & (df["t"] > 120)]

# =========================
# Seleziona massimo residuo per finestra
# =========================
df_max_per_window = pd.DataFrame(columns=df.columns)

for t1, t2 in windows:
    df_window = df[(df["t"] >= t1) & (df["t"] <= t2)]
    if not df_window.empty:
        res_window = df_window["P"] - ompd_power(df_window["t"], CP, Wp, Pmax, A)
        idx_max_res = res_window.idxmax()
        # mantiene solo se sopra percentile globale
        if res_window[idx_max_res] >= cut_global:
            df_max_per_window = pd.concat([df_max_per_window, df_window.loc[[idx_max_res]]])

df_max_per_window = df_max_per_window.sort_values("t")

# =========================
# GUI Plot
# =========================
root_plot = tk.Tk()
root_plot.title("OmPD")

fig, ax = plt.subplots(figsize=(10, 6))
T = np.logspace(np.log10(1), np.log10(df["t"].max() * 1.1), 500)

sc_all = ax.scatter(df["t"], df["P"], c="black", s=25, zorder=3, picker=5)
ax.plot(T, ompd_power(T, CP, Wp, Pmax, A), lw=2)
sc_sel = ax.scatter(df_max_per_window["t"], df_max_per_window["P"], s=90, facecolors="none",
                    edgecolors="red", linewidths=2, zorder=4)

for t1, t2 in windows:
    ax.axvspan(t1, t2, color="dodgerblue", alpha=0.08)
    ax.text((t1 + t2) / 2, ax.get_ylim()[1] * 0.98, f"{int(t1)}–{int(t2)}s",
            ha="center", va="top", fontsize=8)

ax.axhline(CP, color="red", ls="--")
ax.axvline(TCPMAX, color="blue", ls=":")

xticks = [5, 180, 300, 720, 1200, 1800, 3600]
ax.set_xscale("log")
ax.xaxis.set_major_locator(FixedLocator(xticks))
ax.set_xticklabels([f"{t}s" if t < 60 else f"{t // 60}m" for t in xticks])
ax.minorticks_off()

ax.set_xlabel("Time")
ax.set_ylabel("Power (W)")
ax.grid(True)

ax.text(0.98, 0.98,
        f"CP={int(CP)} W\nW'={int(Wp)} J\nPmax={int(Pmax)} W\nA={A:.2f}",
        transform=ax.transAxes, ha="right", va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9))

canvas = FigureCanvasTkAgg(fig, root_plot)
canvas.get_tk_widget().pack(fill="both", expand=True)
NavigationToolbar2Tk(canvas, root_plot)
canvas.draw()

hover = ax.annotate(
    "", xy=(0, 0), xytext=(12, 12),
    textcoords="offset points",
    bbox=dict(boxstyle="round", fc="white", alpha=0.9),
    arrowprops=dict(arrowstyle="->")
)
hover.set_visible(False)

def on_hover(event):
    if event.inaxes != ax:
        hover.set_visible(False)
        fig.canvas.draw_idle()
        return
    contains, info = sc_all.contains(event)
    if contains:
        i = info["ind"][0]
        t = df.iloc[i]["t"]
        P = df.iloc[i]["P"]
        hover.xy = (t, P)
        r = res.iloc[i]
        perc = 100 * np.mean(res <= r)
        hover.set_text(
        f"{int(t)} s\n"
        f"{int(P)} W\n"
        f"{perc:.0f} pctl"
    )

        hover.set_visible(True)
    else:
        hover.set_visible(False)
    fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", on_hover)

def export_csv():
    ss = SprintSelector(root_plot)
    ss.wait_window()
    sprint_durations = ss.result if ss.result else []

    df_export = df_max_per_window.copy()
    for s in sprint_durations:
        closest_idx = (df["t"] - s).abs().idxmin()
        df_export = pd.concat([df_export, df.iloc[[closest_idx]]])

    df_export = df_export.drop_duplicates().sort_values("t")
    path = filedialog.asksaveasfilename(defaultextension=".csv")
    if path:
        df_export.to_csv(path, index=False, sep=';')

tk.Button(root_plot, text="Export selected CSV", command=export_csv).pack(pady=5)
root_plot.mainloop()