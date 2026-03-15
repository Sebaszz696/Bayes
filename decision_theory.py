#!/usr/bin/env python3
"""
Teoría de Decisiones - Análisis Completo
Empresa: Optimización de Entrega de Productos
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import warnings
warnings.filterwarnings('ignore')
import os
os.makedirs("outputs", exist_ok=True)

# ============================================================
#  SECCIÓN DE VARIABLES — MODIFICA AQUÍ
# ============================================================
CONFIG = {
    # Alternativas (nombres)
    "alt_names": ["A1: Empresa externa", "A2: Vehículos", "A3: Procesos"],

    # Estados de naturaleza
    "state_names": ["S1: Demanda sostenible", "S2: Baja demanda"],

    # Tabla de pagos [alternativa][estado]  (millones $)
    #         S1   S2
    "payoffs": [
        [8,   7],   # A1
        [14,  5],   # A2
        [20, -9],   # A3
    ],

    # Probabilidades previas
    "P_S1": 0.70,   # P(S1)
    "P_S2": 0.30,   # P(S2)

    # Probabilidades históricas (condicionales)
    "P_F_given_S1": 0.90,   # P(F | S1)
    "P_F_given_S2": 0.25,   # P(F | S2)
    # P(U|S1) = 1 - P(F|S1),  P(U|S2) = 1 - P(F|S2)  (se calculan automáticamente)
}
# ============================================================

# ── Paleta de colores ──────────────────────────────────────
C = {
    "bg":       "#0F1117",
    "panel":    "#1A1D27",
    "border":   "#2D3148",
    "teal":     "#00C9A7",
    "purple":   "#9B59F5",
    "orange":   "#FF6B35",
    "yellow":   "#FFD166",
    "red":      "#EF4444",
    "green":    "#22C55E",
    "blue":     "#3B82F6",
    "gray":     "#6B7280",
    "white":    "#F1F5F9",
    "dim":      "#94A3B8",
}

plt.rcParams.update({
    "figure.facecolor":  C["bg"],
    "axes.facecolor":    C["panel"],
    "axes.edgecolor":    C["border"],
    "axes.labelcolor":   C["white"],
    "xtick.color":       C["dim"],
    "ytick.color":       C["dim"],
    "text.color":        C["white"],
    "grid.color":        C["border"],
    "grid.alpha":        0.5,
    "font.family":       "monospace",
})

# ═══════════════════════════════════════════════════════════
#  CÁLCULOS PRINCIPALES
# ═══════════════════════════════════════════════════════════

def compute_all(cfg):
    V = np.array(cfg["payoffs"], dtype=float)
    n_alt, n_states = V.shape
    PS = np.array([cfg["P_S1"], cfg["P_S2"]])

    # ── 1. Decisión sin probabilidad ──────────────────────
    optimist  = V.max(axis=1)          # max por fila
    conserv   = V.min(axis=1)          # min por fila
    best_col  = V.max(axis=0)          # mejor pago por columna
    regret    = np.abs(best_col - V)
    max_regret= regret.max(axis=1)

    # ── 2. Valor esperado con probabilidades previas ──────
    EV = V @ PS                         # EV[i] = Σ PS[j]*V[i,j]

    # ── 3. Valor esperado con información perfecta (VEIP) ─
    # Para cada estado, elijo la mejor alternativa
    best_per_state = V.max(axis=0)
    EV_perfect = np.dot(PS, best_per_state)
    VEIP = EV_perfect - EV.max()

    # ── 4. Probabilidades muestrales (Bayes) ──────────────
    PF_S1 = cfg["P_F_given_S1"]
    PF_S2 = cfg["P_F_given_S2"]
    PU_S1 = 1 - PF_S1
    PU_S2 = 1 - PF_S2

    P_F = PS[0]*PF_S1 + PS[1]*PF_S2
    P_U = PS[0]*PU_S1 + PS[1]*PU_S2

    # Probabilidades posteriores (Bayes)
    PS1_F = (PS[0]*PF_S1) / P_F
    PS2_F = (PS[1]*PF_S2) / P_F
    PS1_U = (PS[0]*PU_S1) / P_U
    PS2_U = (PS[1]*PU_S2) / P_U

    # EV de cada alternativa dado Favorable / Desfavorable
    EV_F = V @ np.array([PS1_F, PS2_F])
    EV_U = V @ np.array([PS1_U, PS2_U])

    best_F = EV_F.max()
    best_U = EV_U.max()

    # Valor esperado de la estrategia óptima (EVSI base)
    EV_sample_strategy = P_F * best_F + P_U * best_U
    EVSI = EV_sample_strategy - EV.max()

    efficiency = (EVSI / VEIP * 100) if VEIP > 0 else 0

    return {
        "V": V, "PS": PS, "n_alt": n_alt, "n_states": n_states,
        "optimist": optimist, "conserv": conserv,
        "max_regret": max_regret, "regret": regret,
        "EV": EV,
        "EV_perfect": EV_perfect, "VEIP": VEIP,
        "PF_S1": PF_S1, "PF_S2": PF_S2, "PU_S1": PU_S1, "PU_S2": PU_S2,
        "P_F": P_F, "P_U": P_U,
        "PS1_F": PS1_F, "PS2_F": PS2_F,
        "PS1_U": PS1_U, "PS2_U": PS2_U,
        "EV_F": EV_F, "EV_U": EV_U,
        "best_F": best_F, "best_U": best_U,
        "EV_sample_strategy": EV_sample_strategy,
        "EVSI": EVSI,
        "efficiency": efficiency,
    }

R = compute_all(CONFIG)
ALT  = CONFIG["alt_names"]
STAT = CONFIG["state_names"]
V    = R["V"]

# ═══════════════════════════════════════════════════════════
#  FIGURA 1 — TABLERO DE ANÁLISIS + ANÁLISIS GRÁFICO
# ═══════════════════════════════════════════════════════════

def draw_panel(ax, title, rows, highlight=None, col_headers=None):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.96, title, ha="center", va="top",
            fontsize=9, fontweight="bold", color=C["teal"])
    n = len(rows)
    row_h = 0.80 / (n + (1 if col_headers else 0))
    y0 = 0.88
    if col_headers:
        for ci, ch in enumerate(col_headers):
            ax.text(0.05 + ci*0.30, y0, ch, ha="left", va="top",
                    fontsize=7, color=C["yellow"], fontweight="bold")
        y0 -= row_h
    for i, row in enumerate(rows):
        y = y0 - i*row_h
        bg = C["border"] if i % 2 == 0 else C["panel"]
        if highlight is not None and i == highlight:
            bg = "#1A3A2A"
        ax.add_patch(FancyBboxPatch((0.01, y-row_h*0.85), 0.98, row_h*0.82,
                     boxstyle="round,pad=0.01", facecolor=bg,
                     edgecolor=C["border"], linewidth=0.5))
        for ci, cell in enumerate(row):
            color = C["white"]
            if highlight is not None and i == highlight:
                color = C["green"]
            if isinstance(cell, float) and cell < 0:
                color = C["red"]
            ax.text(0.05 + ci*0.30, y - row_h*0.3, str(cell),
                    ha="left", va="center", fontsize=7.5, color=color)


fig1 = plt.figure(figsize=(20, 14))
fig1.patch.set_facecolor(C["bg"])

# Title
fig1.text(0.5, 0.97, "TEORÍA DE DECISIONES — ANÁLISIS COMPLETO",
          ha="center", fontsize=16, fontweight="bold", color=C["teal"])
fig1.text(0.5, 0.945, "Optimización de entrega de productos",
          ha="center", fontsize=10, color=C["dim"])

gs = gridspec.GridSpec(3, 4, figure=fig1,
                       top=0.92, bottom=0.06,
                       hspace=0.55, wspace=0.35)

# ── Panel 1: Tabla de Pagos ───────────────────────────────
ax_p = fig1.add_subplot(gs[0, 0])
rows_p = []
for i, a in enumerate(ALT):
    rows_p.append([a.split(":")[0], f"${V[i,0]:.0f}M", f"${V[i,1]:.0f}M"])
draw_panel(ax_p, "TABLA DE PAGOS (M$)",
           rows_p,
           col_headers=["Alt", "S1", "S2"])

# ── Panel 2: Enfoque Optimista ────────────────────────────
ax_opt = fig1.add_subplot(gs[0, 1])
rows_opt = [[ALT[i].split(":")[0], f"${R['optimist'][i]:.0f}M"]
            for i in range(R["n_alt"])]
draw_panel(ax_opt, "ENFOQUE OPTIMISTA (MAXIMAX)",
           rows_opt,
           highlight=int(R["optimist"].argmax()),
           col_headers=["Alt", "Máx Pago"])

# ── Panel 3: Enfoque Conservador ──────────────────────────
ax_con = fig1.add_subplot(gs[0, 2])
rows_con = [[ALT[i].split(":")[0], f"${R['conserv'][i]:.0f}M"]
            for i in range(R["n_alt"])]
draw_panel(ax_con, "ENFOQUE CONSERVADOR (MAXIMIN)",
           rows_con,
           highlight=int(R["conserv"].argmax()),
           col_headers=["Alt", "Mín Pago"])

# ── Panel 4: Arrepentimiento ──────────────────────────────
ax_reg = fig1.add_subplot(gs[0, 3])
rows_reg = [[ALT[i].split(":")[0],
             f"${R['regret'][i,0]:.0f}M", f"${R['regret'][i,1]:.0f}M",
             f"${R['max_regret'][i]:.0f}M"]
            for i in range(R["n_alt"])]
draw_panel(ax_reg, "MÁX ARREPENTIMIENTO (MINIMAX)",
           rows_reg,
           highlight=int(R["max_regret"].argmin()),
           col_headers=["Alt", "R(S1)", "R(S2)", "Máx"])

# ── Panel 5: Valor Esperado ───────────────────────────────
ax_ev = fig1.add_subplot(gs[1, 0])
rows_ev = []
for i in range(R["n_alt"]):
    rows_ev.append([ALT[i].split(":")[0], f"${R['EV'][i]:.2f}M"])
draw_panel(ax_ev, "VALOR ESPERADO (EV)",
           rows_ev,
           highlight=int(R["EV"].argmax()),
           col_headers=["Alt", "EV"])

# ── Panel 6: Bayes ────────────────────────────────────────
ax_bay = fig1.add_subplot(gs[1, 1])
rows_bay = [
    ["P(F|S1)", f"{R['PF_S1']:.2f}"],
    ["P(U|S1)", f"{R['PU_S1']:.2f}"],
    ["P(F|S2)", f"{R['PF_S2']:.2f}"],
    ["P(U|S2)", f"{R['PU_S2']:.2f}"],
    ["P(F)",    f"{R['P_F']:.4f}"],
    ["P(U)",    f"{R['P_U']:.4f}"],
    ["P(S1|F)", f"{R['PS1_F']:.4f}"],
    ["P(S2|F)", f"{R['PS2_F']:.4f}"],
    ["P(S1|U)", f"{R['PS1_U']:.4f}"],
    ["P(S2|U)", f"{R['PS2_U']:.4f}"],
]
draw_panel(ax_bay, "PROBABILIDADES BAYESIANAS",
           rows_bay, col_headers=["Variable", "Valor"])

# ── Panel 7: EV Muestral ──────────────────────────────────
ax_evs = fig1.add_subplot(gs[1, 2])
rows_evs = []
for i in range(R["n_alt"]):
    rows_evs.append([ALT[i].split(":")[0],
                     f"${R['EV_F'][i]:.2f}M",
                     f"${R['EV_U'][i]:.2f}M"])
draw_panel(ax_evs, "EV MUESTRAL (FAVORABLE/DESFAV.)",
           rows_evs, col_headers=["Alt", "EV|F", "EV|U"])

# ── Panel 8: Resumen Final ────────────────────────────────
ax_res = fig1.add_subplot(gs[1, 3])
ax_res.set_xlim(0, 1); ax_res.set_ylim(0, 1)
ax_res.axis("off")
ax_res.text(0.5, 0.96, "RESUMEN FINAL", ha="center", va="top",
            fontsize=9, fontweight="bold", color=C["teal"])
best_alt_idx = int(R["EV"].argmax())
summary = [
    ("EV óptimo sin info",       f"${R['EV'].max():.4f}M",  C["white"]),
    ("Alt óptima sin estudio",   ALT[best_alt_idx].split(":")[0], C["yellow"]),
    ("EV con estudio (EVSI+)",   f"${R['EV_sample_strategy']:.4f}M", C["green"]),
    ("Mejor si Favorable",       ALT[int(R['EV_F'].argmax())].split(":")[0], C["teal"]),
    ("Mejor si Desfavorable",    ALT[int(R['EV_U'].argmax())].split(":")[0], C["teal"]),
    ("EV con info perfecta",     f"${R['EV_perfect']:.4f}M", C["purple"]),
    ("VEIP",                     f"${R['VEIP']:.4f}M",      C["orange"]),
    ("EVSI",                     f"${R['EVSI']:.4f}M",      C["blue"]),
    ("Eficiencia del estudio",   f"{R['efficiency']:.1f}%",  C["yellow"]),
]
for k, (label, val, col) in enumerate(summary):
    y = 0.86 - k * 0.09
    ax_res.text(0.04, y, label + ":", fontsize=7, color=C["dim"])
    ax_res.text(0.96, y, val, fontsize=7.5, fontweight="bold",
                color=col, ha="right")

# ── Análisis Gráfico (ocupa toda la fila inferior) ────────
ax_gr = fig1.add_subplot(gs[2, :])
p = np.linspace(0, 1, 300)
colors_lines = [C["orange"], C["teal"], C["purple"]]
EV_lines = []
for i in range(R["n_alt"]):
    ev_line = V[i, 0] * p + V[i, 1] * (1 - p)
    EV_lines.append(ev_line)
    ax_gr.plot(p, ev_line, color=colors_lines[i], lw=2.2,
               label=f"{ALT[i].split(':')[0]}: {V[i,0]}·p + {V[i,1]}·(1-p)")

# Región óptima (upper envelope)
env = np.array(EV_lines).max(axis=0)
ax_gr.fill_between(p, env - 0.3, env, alpha=0.12, color=C["yellow"])

# Línea de probabilidad actual
p0 = CONFIG["P_S1"]
ax_gr.axvline(p0, color=C["yellow"], ls="--", lw=1.5, alpha=0.8,
              label=f"P(S1) actual = {p0}")

# Puntos de corte
from itertools import combinations
cuts = []
for (i, j) in combinations(range(R["n_alt"]), 2):
    # V[i,0]*p + V[i,1]*(1-p) = V[j,0]*p + V[j,1]*(1-p)
    # (V[i,0]-V[i,1])*p + V[i,1] = (V[j,0]-V[j,1])*p + V[j,1]
    a = (V[i,0]-V[i,1]) - (V[j,0]-V[j,1])
    b = V[j,1] - V[i,1]
    if abs(a) > 1e-9:
        px = b / a
        if 0 <= px <= 1:
            py = V[i,0]*px + V[i,1]*(1-px)
            cuts.append((px, py, i, j))
            ax_gr.scatter([px], [py], color=C["white"], s=60, zorder=5)
            ax_gr.annotate(f"p={px:.3f}\nEV={py:.2f}",
                           xy=(px, py), xytext=(px+0.03, py+0.5),
                           fontsize=6.5, color=C["white"],
                           arrowprops=dict(arrowstyle="-", color=C["dim"], lw=0.8))

ax_gr.set_xlabel("Probabilidad P(S1)", fontsize=9)
ax_gr.set_ylabel("Valor Esperado (M$)", fontsize=9)
ax_gr.set_title("ANÁLISIS GRÁFICO DE SENSIBILIDAD", fontsize=10,
                fontweight="bold", color=C["teal"], pad=8)
ax_gr.legend(fontsize=7.5, loc="upper left",
             facecolor=C["panel"], edgecolor=C["border"])
ax_gr.grid(True, alpha=0.3)
ax_gr.set_xlim(0, 1)

plt.savefig("outputs/fig1_analisis_tablero.png",
            dpi=150, bbox_inches="tight", facecolor=C["bg"])
print("✓ Figura 1 guardada en outputs/fig1_analisis_tablero.png")


# ═══════════════════════════════════════════════════════════
#  FIGURA 2 — ÁRBOL DE DECISIÓN (sin estudio + con estudio)
# ═══════════════════════════════════════════════════════════

def draw_square(ax, x, y, label, color=C["panel"], size=0.38, fontsize=9):
    box = FancyBboxPatch((x-size/2, y-size/3), size, size*0.67,
                         boxstyle="round,pad=0.04",
                         facecolor=color, edgecolor=C["teal"], lw=1.5)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=C["white"])

def draw_circle(ax, x, y, label, color=C["panel"], r=0.22, fontsize=9):
    circ = plt.Circle((x, y), r, facecolor=color,
                       edgecolor=C["purple"], lw=1.5)
    ax.add_patch(circ)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=C["white"])

def arrow(ax, x0, y0, x1, y1, color=C["dim"], lw=1.2):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>",
                                color=color, lw=lw,
                                mutation_scale=10))

def leaf(ax, x, y, val, color=None):
    c = C["green"] if val >= 0 else C["red"]
    if color: c = color
    box = FancyBboxPatch((x-0.35, y-0.15), 0.72, 0.30,
                         boxstyle="round,pad=0.03",
                         facecolor=c+"22", edgecolor=c, lw=1.2)
    ax.add_patch(box)
    sign = "+" if val >= 0 else ""
    ax.text(x, y, f"{sign}{val:.0f}M", ha="center", va="center",
            fontsize=8, fontweight="bold", color=c)

fig2 = plt.figure(figsize=(22, 16))
fig2.patch.set_facecolor(C["bg"])
fig2.text(0.5, 0.97, "ÁRBOLES DE DECISIÓN",
          ha="center", fontsize=15, fontweight="bold", color=C["teal"])
fig2.text(0.5, 0.945,
          "Izquierda: Con Estudio de Mercado (Bayesiano)  |  Derecha: Sin Estudio",
          ha="center", fontsize=9, color=C["dim"])

ax_tree = fig2.add_axes([0, 0, 1, 0.92])
ax_tree.set_xlim(0, 22)
ax_tree.set_ylim(0, 16)
ax_tree.axis("off")
ax_tree.set_facecolor(C["bg"])

# ── Colores por alternativa ────────────────────────────────
alt_colors = [C["orange"], C["teal"], C["purple"]]

# ══════════════════════════════════════════════════════
#  ÁRBOL CON ESTUDIO (izquierda, x ∈ [0,11])
# ══════════════════════════════════════════════════════
# Nodo 1 (decisión raíz)
draw_square(ax_tree, 1.2, 8, "1", color="#1A2A3A", size=0.5, fontsize=11)
ax_tree.text(1.2, 7.35, "Estudio", ha="center", fontsize=7, color=C["dim"])

# Rama ESTUDIO
arrow(ax_tree, 1.45, 8, 2.8, 8, color=C["teal"], lw=1.5)
ax_tree.text(2.1, 8.15, "Estudio", fontsize=7, color=C["teal"])

# Nodo 2 (azar — resultado del estudio)
draw_circle(ax_tree, 3.0, 8, "2", color="#1A1D27", r=0.28)

# Probabilidades de las ramas del nodo 2
P_F_val = R["P_F"]
P_U_val = R["P_U"]

# Rama Favorable
arrow(ax_tree, 3.0, 8.28, 4.2, 11.2, color=C["green"], lw=1.5)
ax_tree.text(3.3, 10.0, f"Favorable\nP(F)={P_F_val:.3f}", fontsize=7,
             color=C["green"], ha="center")

# Nodo 3 (decisión dado Favorable)
draw_square(ax_tree, 4.4, 11.2, "3", color="#1A2A1A", size=0.5)
ax_tree.text(4.4, 10.55, "Favorable", ha="center", fontsize=6.5,
             color=C["green"])

# Rama Desfavorable
arrow(ax_tree, 3.0, 7.72, 4.2, 4.8, color=C["red"], lw=1.5)
ax_tree.text(3.3, 6.1, f"Desfav.\nP(U)={P_U_val:.3f}", fontsize=7,
             color=C["red"], ha="center")

# Nodo 4 (decisión dado Desfavorable)
draw_square(ax_tree, 4.4, 4.8, "4", color="#2A1A1A", size=0.5)
ax_tree.text(4.4, 4.15, "Desfav.", ha="center", fontsize=6.5, color=C["red"])

# ── Sub-árbol FAVORABLE ───────────────────────────────────
y_fav_centers = [13.0, 11.2, 9.4]
node_nums_fav = [6, 7, 8]
for k, (y_c, nn) in enumerate(zip(y_fav_centers, node_nums_fav)):
    arrow(ax_tree, 4.65, 11.2, 5.8, y_c, color=alt_colors[k], lw=1.3)
    ax_tree.text(5.1, (11.2 + y_c)/2 + 0.15,
                 ALT[k].split(":")[0], fontsize=6.5,
                 color=alt_colors[k], ha="center")
    draw_circle(ax_tree, 6.0, y_c, str(nn), r=0.22)

    # S1 y S2 desde cada nodo de azar
    for s_idx, (dy, ps_label, ps_val) in enumerate([
        (+1.0, f"P(S1|F)\n={R['PS1_F']:.4f}", R["PS1_F"]),
        (-1.0, f"P(S2|F)\n={R['PS2_F']:.4f}", R["PS2_F"]),
    ]):
        y_leaf = y_c + dy
        arrow(ax_tree, 6.22, y_c, 7.3, y_leaf,
              color=C["dim"], lw=1.0)
        ax_tree.text(6.6, y_c + dy*0.55, f"{ps_val:.4f}",
                     fontsize=5.5, color=C["dim"], ha="center")
        leaf(ax_tree, 7.85, y_leaf, V[k, s_idx])

    # EV del nodo de azar
    ev_val = R["EV_F"][k]
    is_best = (k == int(R["EV_F"].argmax()))
    ev_color = C["yellow"] if is_best else C["white"]
    badge = " ★ÓPTIMA" if is_best else ""
    ax_tree.text(6.0, y_c - 0.38,
                 f"EV={ev_val:.2f}M{badge}",
                 fontsize=6, color=ev_color, ha="center",
                 fontweight="bold" if is_best else "normal")

# ── Sub-árbol DESFAVORABLE ────────────────────────────────
y_des_centers = [6.5, 4.8, 3.1]
node_nums_des = [9, 10, 11]
for k, (y_c, nn) in enumerate(zip(y_des_centers, node_nums_des)):
    arrow(ax_tree, 4.65, 4.8, 5.8, y_c, color=alt_colors[k], lw=1.3)
    ax_tree.text(5.1, (4.8 + y_c)/2 + 0.15,
                 ALT[k].split(":")[0], fontsize=6.5,
                 color=alt_colors[k], ha="center")
    draw_circle(ax_tree, 6.0, y_c, str(nn), r=0.22)

    for s_idx, (dy, ps_val) in enumerate([
        (+1.0, R["PS1_U"]),
        (-1.0, R["PS2_U"]),
    ]):
        y_leaf = y_c + dy
        arrow(ax_tree, 6.22, y_c, 7.3, y_leaf, color=C["dim"], lw=1.0)
        ax_tree.text(6.6, y_c + dy*0.55, f"{ps_val:.4f}",
                     fontsize=5.5, color=C["dim"], ha="center")
        leaf(ax_tree, 7.85, y_leaf, V[k, s_idx])

    ev_val = R["EV_U"][k]
    is_best = (k == int(R["EV_U"].argmax()))
    ev_color = C["yellow"] if is_best else C["white"]
    badge = " ★ÓPTIMA" if is_best else ""
    ax_tree.text(6.0, y_c - 0.38,
                 f"EV={ev_val:.2f}M{badge}",
                 fontsize=6, color=ev_color, ha="center",
                 fontweight="bold" if is_best else "normal")

# EVSI box
ax_tree.text(1.2, 14.6,
             f"EV con estudio = P(F)·EV_F* + P(U)·EV_U*\n"
             f"= {P_F_val:.3f}·{R['best_F']:.2f} + {P_U_val:.3f}·{R['best_U']:.2f}\n"
             f"= {R['EV_sample_strategy']:.4f} M$",
             fontsize=7.5, color=C["teal"],
             bbox=dict(facecolor=C["panel"], edgecolor=C["teal"],
                       boxstyle="round,pad=0.4", lw=1.2))

# ══════════════════════════════════════════════════════
#  ÁRBOL SIN ESTUDIO (derecha, x ∈ [11,22])
# ══════════════════════════════════════════════════════
x_off = 11.5

draw_square(ax_tree, x_off + 1.0, 8, "1", color="#1A2A3A", size=0.5, fontsize=11)
ax_tree.text(x_off + 1.0, 7.35, "Sin Est.", ha="center",
             fontsize=7, color=C["dim"])

y_centers_se = [11.2, 8.0, 4.8]
node_nums_se = [12, 13, 14]

for k, (y_c, nn) in enumerate(zip(y_centers_se, node_nums_se)):
    arrow(ax_tree, x_off + 1.25, 8, x_off + 2.4, y_c,
          color=alt_colors[k], lw=1.3)
    ax_tree.text(x_off + 1.75, (8 + y_c)/2 + 0.2,
                 ALT[k].split(":")[0], fontsize=6.5,
                 color=alt_colors[k], ha="center")
    draw_circle(ax_tree, x_off + 2.6, y_c, str(nn), r=0.22)

    for s_idx, (dy, ps_val) in enumerate([
        (+1.3, R["PS"][0]),
        (-1.3, R["PS"][1]),
    ]):
        y_leaf = y_c + dy
        arrow(ax_tree, x_off + 2.82, y_c,
              x_off + 3.9, y_leaf, color=C["dim"], lw=1.0)
        ax_tree.text(x_off + 3.25, y_c + dy*0.55,
                     f"{ps_val:.2f}", fontsize=6,
                     color=C["dim"], ha="center")
        leaf(ax_tree, x_off + 4.5, y_leaf, V[k, s_idx])

    ev_val = R["EV"][k]
    is_best = (k == int(R["EV"].argmax()))
    ev_color = C["yellow"] if is_best else C["white"]
    badge = " ★MEJOR" if is_best else ""
    ax_tree.text(x_off + 2.6, y_c - 0.42,
                 f"EV={ev_val:.2f}M{badge}",
                 fontsize=6.5, color=ev_color, ha="center",
                 fontweight="bold" if is_best else "normal")

# EV sin estudio
ax_tree.text(x_off + 1.0, 14.6,
             f"EV sin estudio = ${R['EV'].max():.4f}M\n"
             f"(Alt óptima: {ALT[int(R['EV'].argmax())]})",
             fontsize=7.5, color=C["yellow"],
             bbox=dict(facecolor=C["panel"], edgecolor=C["yellow"],
                       boxstyle="round,pad=0.4", lw=1.2))

# ── Leyenda ────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor=C["panel"], edgecolor=C["teal"],
                   label="= Nodo de decisión (□)"),
    mpatches.Patch(facecolor=C["panel"], edgecolor=C["purple"],
                   label="= Nodo de azar (○)"),
] + [
    Line2D([0],[0], color=alt_colors[k], lw=2,
           label=ALT[k]) for k in range(R["n_alt"])
]
ax_tree.legend(handles=legend_items, loc="lower left",
               fontsize=7, facecolor=C["panel"],
               edgecolor=C["border"], framealpha=0.9)

# ── Separador ─────────────────────────────────────────────
ax_tree.axvline(11.0, color=C["border"], lw=1.5, ls=":")
ax_tree.text(11.0, 15.5, "────────────────────────────",
             ha="center", fontsize=8, color=C["border"])

plt.savefig("outputs/fig2_arbol_decision.png",
            dpi=150, bbox_inches="tight", facecolor=C["bg"])
print("✓ Figura 2 guardada en outputs/fig2_arbol_decision.png")

# ═══════════════════════════════════════════════════════════
#  FIGURA 3 — ÁRBOL BAYESIANO + MÉTRICAS FINALES
# ═══════════════════════════════════════════════════════════

fig3, axes = plt.subplots(1, 2, figsize=(18, 9))
fig3.patch.set_facecolor(C["bg"])
fig3.suptitle("ÁRBOL BAYESIANO & MÉTRICAS CLAVE",
              fontsize=14, fontweight="bold", color=C["teal"], y=0.97)

# ── Árbol Bayesiano (diagrama de flujo probabilístico) ────
ax_b = axes[0]
ax_b.set_xlim(0, 10); ax_b.set_ylim(0, 10)
ax_b.axis("off")
ax_b.set_facecolor(C["bg"])
ax_b.set_title("ÁRBOL DE PROBABILIDADES BAYESIANO",
               fontsize=9, color=C["teal"], pad=6)

# Nodo raíz
draw_circle(ax_b, 1.2, 5, "Estudio", r=0.45, fontsize=7.5)

# P(F) y P(U)
arrow(ax_b, 1.65, 5, 3.5, 7.5, color=C["green"], lw=1.8)
ax_b.text(2.3, 6.8, f"P(F)={R['P_F']:.4f}", fontsize=8, color=C["green"])

arrow(ax_b, 1.65, 5, 3.5, 2.5, color=C["red"], lw=1.8)
ax_b.text(2.3, 3.2, f"P(U)={R['P_U']:.4f}", fontsize=8, color=C["red"])

# Nodo F
draw_circle(ax_b, 3.8, 7.5, "F", color="#0A2A0A", r=0.35)
# Nodo U
draw_circle(ax_b, 3.8, 2.5, "U", color="#2A0A0A", r=0.35)

# Desde F
arrow(ax_b, 4.15, 7.5, 5.8, 8.8, color=C["teal"], lw=1.3)
ax_b.text(4.9, 8.65, f"P(S1|F)={R['PS1_F']:.4f}", fontsize=7.5, color=C["teal"])
draw_circle(ax_b, 6.4, 8.9, "S1|F", color="#0A1A2A", r=0.4, fontsize=7)
ax_b.text(7.1, 8.9, f"= P(S1)·P(F|S1)/P(F)\n= {CONFIG['P_S1']}·{R['PF_S1']}/{R['P_F']:.4f}",
          fontsize=6, color=C["teal"], va="center")

arrow(ax_b, 4.15, 7.5, 5.8, 6.2, color=C["orange"], lw=1.3)
ax_b.text(4.9, 6.7, f"P(S2|F)={R['PS2_F']:.4f}", fontsize=7.5, color=C["orange"])
draw_circle(ax_b, 6.4, 6.1, "S2|F", color="#1A0A0A", r=0.4, fontsize=7)
ax_b.text(7.1, 6.1, f"= P(S2)·P(F|S2)/P(F)\n= {CONFIG['P_S2']}·{R['PF_S2']}/{R['P_F']:.4f}",
          fontsize=6, color=C["orange"], va="center")

# Desde U
arrow(ax_b, 4.15, 2.5, 5.8, 3.8, color=C["teal"], lw=1.3)
ax_b.text(4.9, 3.6, f"P(S1|U)={R['PS1_U']:.4f}", fontsize=7.5, color=C["teal"])
draw_circle(ax_b, 6.4, 3.9, "S1|U", color="#0A1A2A", r=0.4, fontsize=7)

arrow(ax_b, 4.15, 2.5, 5.8, 1.2, color=C["orange"], lw=1.3)
ax_b.text(4.9, 1.65, f"P(S2|U)={R['PS2_U']:.4f}", fontsize=7.5, color=C["orange"])
draw_circle(ax_b, 6.4, 1.1, "S2|U", color="#1A0A0A", r=0.4, fontsize=7)

# Fórmula de Bayes
ax_b.text(0.5, 0.3,
          "Teorema de Bayes:  P(Sj|Info) = P(Sj) · P(Info|Sj) / P(Info)",
          fontsize=7, color=C["dim"],
          bbox=dict(facecolor=C["border"], boxstyle="round,pad=0.3"))

# ── Métricas Finales (barras) ─────────────────────────────
ax_m = axes[1]
ax_m.set_facecolor(C["panel"])
ax_m.set_title("COMPARATIVA DE MÉTRICAS (M$)",
               fontsize=9, color=C["teal"], pad=6)

metrics_labels = [
    "EV sin info\n(mejor alt)",
    "EV con\nestudio (EVSI)",
    "EV con info\nperfecta",
    "VEIP\n(valor info)",
    "EVSI\n(valor estudio)",
]
metrics_vals = [
    R["EV"].max(),
    R["EV_sample_strategy"],
    R["EV_perfect"],
    R["VEIP"],
    R["EVSI"],
]
bar_colors = [C["yellow"], C["green"], C["purple"], C["orange"], C["blue"]]
bars = ax_m.barh(metrics_labels, metrics_vals,
                  color=bar_colors, edgecolor=C["border"],
                  height=0.55, alpha=0.85)
for bar, val in zip(bars, metrics_vals):
    ax_m.text(val + 0.05, bar.get_y() + bar.get_height()/2,
              f"${val:.4f}M", va="center", fontsize=8,
              color=C["white"], fontweight="bold")
ax_m.set_xlabel("Valor Esperado (M$)", fontsize=8)
ax_m.tick_params(labelsize=8)
ax_m.grid(axis="x", alpha=0.3)
ax_m.spines["top"].set_visible(False)
ax_m.spines["right"].set_visible(False)

# Eficiencia
ax_m.text(0.98, 0.04,
          f"Eficiencia del estudio: {R['efficiency']:.1f}%\n"
          f"EVSI/VEIP × 100",
          transform=ax_m.transAxes, ha="right", va="bottom",
          fontsize=8.5, color=C["yellow"],
          bbox=dict(facecolor=C["panel"], edgecolor=C["yellow"],
                    boxstyle="round,pad=0.4"))

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("/mnt/user-data/outputs/fig3_bayes_metricas.png",
            dpi=150, bbox_inches="tight", facecolor=C["bg"])
print("✓ Figura 3 guardada")

# ═══════════════════════════════════════════════════════════
#  IMPRIMIR REPORTE EN CONSOLA
# ═══════════════════════════════════════════════════════════

print("\n" + "═"*60)
print("       REPORTE COMPLETO — TEORÍA DE DECISIONES")
print("═"*60)

print("\n── TABLA DE PAGOS ──────────────────────────────────")
header = f"{'':20s}" + "".join(f"{s:>15s}" for s in STAT)
print(header)
for i, a in enumerate(ALT):
    row = f"{a:20s}" + "".join(f"{V[i,j]:>15.1f}" for j in range(R["n_states"]))
    print(row)

print(f"\nProbabilidades previas: P(S1)={CONFIG['P_S1']}, P(S2)={CONFIG['P_S2']}")

print("\n── DECISIONES SIN PROBABILIDAD ─────────────────────")
print(f"  Optimista (MAXIMAX): {ALT[int(R['optimist'].argmax())]}  → ${R['optimist'].max():.1f}M")
print(f"  Conservador (MAXIMIN): {ALT[int(R['conserv'].argmax())]}  → ${R['conserv'].max():.1f}M")
print(f"  Min Arrepentimiento: {ALT[int(R['max_regret'].argmin())]}  → ${R['max_regret'].min():.1f}M")

print("\n── VALOR ESPERADO ───────────────────────────────────")
for i, a in enumerate(ALT):
    mark = " ← ÓPTIMA" if i == int(R["EV"].argmax()) else ""
    print(f"  EV({a.split(':')[0]}) = {R['EV'][i]:.4f}M{mark}")

print("\n── PROBABILIDADES BAYESIANAS ────────────────────────")
print(f"  P(F|S1)={R['PF_S1']:.2f}  P(U|S1)={R['PU_S1']:.2f}")
print(f"  P(F|S2)={R['PF_S2']:.2f}  P(U|S2)={R['PU_S2']:.2f}")
print(f"  P(F)   = {CONFIG['P_S1']}·{R['PF_S1']} + {CONFIG['P_S2']}·{R['PF_S2']} = {R['P_F']:.4f}")
print(f"  P(U)   = {CONFIG['P_S1']}·{R['PU_S1']} + {CONFIG['P_S2']}·{R['PU_S2']} = {R['P_U']:.4f}")
print(f"  P(S1|F)= {R['PS1_F']:.4f}  P(S2|F)= {R['PS2_F']:.4f}")
print(f"  P(S1|U)= {R['PS1_U']:.4f}  P(S2|U)= {R['PS2_U']:.4f}")

print("\n── EV MUESTRAL ──────────────────────────────────────")
for i, a in enumerate(ALT):
    print(f"  EV({a.split(':')[0]}|F) = {R['EV_F'][i]:.4f}M   "
          f"EV({a.split(':')[0]}|U) = {R['EV_U'][i]:.4f}M")
print(f"  → Favorable: MEJOR = {ALT[int(R['EV_F'].argmax())]} = ${R['best_F']:.4f}M")
print(f"  → Desfav:    MEJOR = {ALT[int(R['EV_U'].argmax())]} = ${R['best_U']:.4f}M")

print("\n── RESUMEN FINAL ────────────────────────────────────")
print(f"  EV óptimo sin info        = ${R['EV'].max():.4f}M")
print(f"  EV con estudio (estrategia óptima) = ${R['EV_sample_strategy']:.4f}M")
print(f"  EVSI (valor estudio)      = ${R['EVSI']:.4f}M")
print(f"  EV con info perfecta      = ${R['EV_perfect']:.4f}M")
print(f"  VEIP (valor info perf.)   = ${R['VEIP']:.4f}M")
print(f"  Eficiencia del estudio    = {R['efficiency']:.2f}%")
print("═"*60)

print("\n✓ Todos los archivos guardados en /mnt/user-data/outputs/")
