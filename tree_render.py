"""Render decision tree as matplotlib figure."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import io
import base64

# Palette
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
    "axes.facecolor":    C["bg"],
    "axes.edgecolor":    C["border"],
    "axes.labelcolor":   C["white"],
    "text.color":        C["white"],
    "font.family":       "monospace",
})

def draw_square(ax, x, y, label, color=C["panel"], size=0.38, fontsize=9):
    box = FancyBboxPatch((x-size/2, y-size/3), size, size*0.67,
                         boxstyle="round,pad=0.04",
                         facecolor=color, edgecolor=C["teal"], lw=1.5)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=C["white"])

def draw_circle(ax, x, y, label, color=C["panel"], r=0.22, fontsize=9):
    circ = plt.Circle((x, y), r, facecolor=color, edgecolor=C["purple"], lw=1.5)
    ax.add_patch(circ)
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize, fontweight="bold", color=C["white"])

def arrow(ax, x0, y0, x1, y1, color=C["dim"], lw=1.2):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=10))

def leaf(ax, x, y, val, color=None):
    c = C["green"] if val >= 0 else C["red"]
    if color: c = color
    box = FancyBboxPatch((x-0.35, y-0.15), 0.72, 0.30,
                         boxstyle="round,pad=0.03",
                         facecolor=c+"44", edgecolor=c, lw=1.2)
    ax.add_patch(box)
    sign = "+" if val >= 0 else ""
    ax.text(x, y, f"{sign}{val:.1f}", ha="center", va="center",
            fontsize=8, fontweight="bold", color=c)

def render_tree_png(cfg, res):
    """Render decision tree to PNG (base64) or bytes."""
    V = res["V"]
    alt_names = cfg.get("alt_names", ["A1", "A2", "A3"])
    state_names = cfg.get("state_names", ["S1", "S2"])
    
    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor(C["bg"])
    
    fig.text(0.5, 0.97, "ÁRBOL DE DECISIÓN (CON ESTUDIO vs SIN ESTUDIO)",
             ha="center", fontsize=14, fontweight="bold", color=C["teal"])
    
    ax = fig.add_axes([0, 0, 1, 0.94])
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 16)
    ax.axis("off")
    ax.set_facecolor(C["bg"])
    
    # colors for alternatives (extendable)
    palette = [C["orange"], C["teal"], C["purple"], C["yellow"], C["green"], C["blue"]]
    n_alt = len(V)
    alt_colors = [palette[i % len(palette)] for i in range(n_alt)]

    # ─── ÁRBOL CON ESTUDIO (izquierda) ───
    # Nodo raíz
    draw_square(ax, 1.2, 8, "1", color="#1A2A3A", size=0.5, fontsize=11)
    ax.text(1.2, 7.35, "Estudio", ha="center", fontsize=7, color=C["dim"])
    
    # Rama a nodo de azar
    arrow(ax, 1.45, 8, 2.8, 8, color=C["teal"], lw=1.5)
    ax.text(2.1, 8.15, "Hacer\nestudio", fontsize=7, color=C["teal"], ha="center")
    
    draw_circle(ax, 3.0, 8, "2", color="#1A1D27", r=0.28)
    
    P_F_val = res["P_F"]
    P_U_val = res["P_U"]
    
    # Rama Favorable
    arrow(ax, 3.0, 8.28, 4.2, 11.2, color=C["green"], lw=1.5)
    ax.text(3.3, 10.0, f"Favorable\nP(F)={P_F_val:.4f}", fontsize=7, color=C["green"], ha="center")
    
    draw_square(ax, 4.4, 11.2, "3", color="#1A2A1A", size=0.5)
    ax.text(4.4, 10.55, "Fav.", ha="center", fontsize=6.5, color=C["green"])
    
    # Rama Desfavorable
    arrow(ax, 3.0, 7.72, 4.2, 4.8, color=C["red"], lw=1.5)
    ax.text(3.3, 6.1, f"Desfav.\nP(U)={P_U_val:.4f}", fontsize=7, color=C["red"], ha="center")
    
    draw_square(ax, 4.4, 4.8, "4", color="#2A1A1A", size=0.5)
    ax.text(4.4, 4.15, "Desfav.", ha="center", fontsize=6.5, color=C["red"])
    
    # Sub-árbol Favorable (position dynamically based on number of alternatives)
    top_fav = 13.0
    bottom_fav = 9.0
    if n_alt > 1:
        step_fav = (top_fav - bottom_fav) / (n_alt - 1)
        y_fav = [top_fav - k * step_fav for k in range(n_alt)]
    else:
        y_fav = [(top_fav + bottom_fav) / 2]
    for k, y_c in enumerate(y_fav):
        arrow(ax, 4.65, 11.2, 5.8, y_c, color=alt_colors[k], lw=1.3)
        ax.text(5.1, (11.2 + y_c)/2 + 0.15, alt_names[k].split(":")[0], fontsize=6.5, color=alt_colors[k], ha="center")
        draw_circle(ax, 6.0, y_c, str(6+k), r=0.22)
        
        # S1 y S2 (positions handled after computing compacted leaf positions)
        pass
        
        ev_val = res["EV_F"][k]
        is_best = (k == res["best_F_idx"])
        ev_color = C["yellow"] if is_best else C["white"]
        badge = " ★" if is_best else ""
        ax.text(6.0, y_c - 0.42, f"EV={ev_val:.2f}{badge}", fontsize=6, color=ev_color, ha="center", fontweight="bold" if is_best else "normal")
    
    # Sub-árbol Desfavorable (dynamic)
    top_des = 6.5
    bottom_des = 3.1
    if n_alt > 1:
        step_des = (top_des - bottom_des) / (n_alt - 1)
        y_des = [top_des - k * step_des for k in range(n_alt)]
    else:
        y_des = [(top_des + bottom_des) / 2]
    for k, y_c in enumerate(y_des):
        arrow(ax, 4.65, 4.8, 5.8, y_c, color=alt_colors[k], lw=1.3)
        ax.text(5.1, (4.8 + y_c)/2 + 0.15, alt_names[k].split(":")[0], fontsize=6.5, color=alt_colors[k], ha="center")
        draw_circle(ax, 6.0, y_c, str(9+k), r=0.22)
        
        # S1 y S2 (positions handled after computing compacted leaf positions)
        pass
        
        ev_val = res["EV_U"][k]
        is_best = (k == res["best_U_idx"])
        ev_color = C["yellow"] if is_best else C["white"]
        badge = " ★" if is_best else ""
        ax.text(6.0, y_c - 0.42, f"EV={ev_val:.2f}{badge}", fontsize=6, color=ev_color, ha="center", fontweight="bold" if is_best else "normal")
    
    # EVSI box
    ax.text(1.2, 14.8,
            f"EV = P(F)·EV_F* + P(U)·EV_U*\n"
            f"= {P_F_val:.4f}·{res['best_F']:.2f} + {P_U_val:.4f}·{res['best_U']:.2f}\n"
            f"= {res['EV_sample_strategy']:.4f}",
            fontsize=8, color=C["teal"],
            bbox=dict(facecolor=C["panel"], edgecolor=C["teal"], boxstyle="round,pad=0.5", lw=1.2))
    
    # ─── ÁRBOL SIN ESTUDIO (derecha) ───
    x_off = 11.5
    draw_square(ax, x_off + 1.0, 8, "1", color="#1A2A3A", size=0.5, fontsize=11)
    ax.text(x_off + 1.0, 7.35, "Sin Est.", ha="center", fontsize=7, color=C["dim"])
    
    # ─── ÁRBOL SIN ESTUDIO (derecha) ───
    # positions for no-study alternatives (dynamic)
    top_se = 11.2
    bottom_se = 4.8
    if n_alt > 1:
        step_se = (top_se - bottom_se) / (n_alt - 1)
        y_se = [top_se - k * step_se for k in range(n_alt)]
    else:
        y_se = [(top_se + bottom_se) / 2]
    for k, y_c in enumerate(y_se):
        arrow(ax, x_off + 1.25, 8, x_off + 2.4, y_c, color=alt_colors[k], lw=1.3)
        ax.text(x_off + 1.75, (8 + y_c)/2 + 0.2, alt_names[k].split(":")[0], fontsize=6.5, color=alt_colors[k], ha="center")
        draw_circle(ax, x_off + 2.6, y_c, str(12+k), r=0.22)
        # register desired leaf positions for no-study (draw later to avoid overlaps)
        num_states = len(V[0]) if (len(V) and len(V[0])) else 2
        leaf_sep = 0.9
        offsets = [((num_states - 1) / 2.0 - i) * leaf_sep for i in range(num_states)]
        if 'no_study_leaves' not in locals():
            no_study_leaves = []
        for s_idx in range(num_states):
            dy = offsets[s_idx]
            ps_val = None
            if 'PS' in res and len(res['PS']) > s_idx:
                ps_val = res['PS'][s_idx]
            y_leaf_desired = y_c + dy
            # store tuple (x_parent, y_parent, x_mid, desired_y, x_leaf, payoff, ps_val)
            no_study_leaves.append((x_off + 2.82, y_c, x_off + 3.9, y_leaf_desired, x_off + 4.5, V[k][s_idx], ps_val))
        
        ev_val = res["EV"][k]
        is_best = (k == int(max(range(len(res["EV"])), key=lambda i: res["EV"][i])))
        ev_color = C["yellow"] if is_best else C["white"]
        badge = " ★" if is_best else ""
        ax.text(x_off + 2.6, y_c - 0.42, f"EV={ev_val:.2f}{badge}", fontsize=6.5, color=ev_color, ha="center", fontweight="bold" if is_best else "normal")
    
    # Convert to base64
    # --- compact centers to avoid overlaps and prevent crossing arrows ---
    def compact_centers(desired_centers, half_span=1.0, min_sep=0.9):
        """Pack parent centers so sibling pairs don't cross with other parents.
        Ensures distance between centers >= 2*half_span + min_sep.
        Returns adjusted centers in original order.
        """
        if not desired_centers:
            return []
        pairs = sorted([(i, desired_centers[i]) for i in range(len(desired_centers))], key=lambda x: x[1])
        placed = []
        for idx, val in pairs:
            if not placed:
                cur = val
            else:
                prev = placed[-1][1]
                cur = max(val, prev + 2 * half_span + min_sep)
            placed.append((idx, cur))
        res = [0] * len(desired_centers)
        for idx, cur in placed:
            res[idx] = cur
        return res

    # Favorable leaves: handle arbitrary number of states, pack parent centers and place leaves symmetrically
    num_states = len(V[0]) if (len(V) and len(V[0])) else 2
    leaf_sep = 0.8
    offsets = [((num_states - 1) / 2.0 - i) * leaf_sep for i in range(num_states)]
    half_span = abs(offsets[0]) if offsets else 0.6
    fav_centers = list(y_fav)
    fav_centers_adj = compact_centers(fav_centers, half_span=half_span, min_sep=0.4)
    for k, center in enumerate(fav_centers_adj):
        y_parent = y_fav[k]
        for s_idx in range(num_states):
            y_leaf = center + offsets[s_idx]
            # posterior probability label if available (PS1_F, PS2_F ...)
            ps_key = f"PS{ s_idx + 1 }_F"
            ps_val = res.get(ps_key, None)
            arrow(ax, 6.22, y_parent, 7.3, y_leaf, color=C['dim'], lw=1.0)
            if ps_val is not None:
                ax.text(6.6, (y_parent + y_leaf) / 2, f"{ps_val:.3f}", fontsize=5.5, color=C['dim'], ha='center')
            leaf(ax, 7.85, y_leaf, V[k][s_idx])

    # Unfavorable leaves: same dynamic handling
    des_centers = list(y_des)
    des_centers_adj = compact_centers(des_centers, half_span=half_span, min_sep=0.4)
    for k, center in enumerate(des_centers_adj):
        y_parent = y_des[k]
        for s_idx in range(num_states):
            y_leaf = center + offsets[s_idx]
            ps_key = f"PS{ s_idx + 1 }_U"
            ps_val = res.get(ps_key, None)
            arrow(ax, 6.22, y_parent, 7.3, y_leaf, color=C['dim'], lw=1.0)
            if ps_val is not None:
                ax.text(6.6, (y_parent + y_leaf) / 2, f"{ps_val:.3f}", fontsize=5.5, color=C['dim'], ha='center')
            leaf(ax, 7.85, y_leaf, V[k][s_idx])

    # No-study leaves: group per parent (two leaves each), pack centers to avoid crossings
    if 'no_study_leaves' in locals() and len(no_study_leaves) > 0:
        parents = []
        # no_study_leaves stored two entries per parent in insertion order
        for i in range(0, len(no_study_leaves), 2):
            l1 = no_study_leaves[i]
            l2 = no_study_leaves[i + 1]
            x_parent, y_parent, x_mid, _desired1, x_leaf, payoff1, ps1 = l1
            _, _, _, _desired2, _, payoff2, ps2 = l2
            parents.append((x_parent, y_parent, x_mid, x_leaf, payoff1, payoff2, ps1, ps2))
        centers = [p[1] for p in parents]
        centers_adj = compact_centers(centers, half_span=0.9, min_sep=0.6)
        for idx, parent in enumerate(parents):
            x_parent, y_parent, x_mid, x_leaf, pay1, pay2, ps1, ps2 = parent
            center_adj = centers_adj[idx]
            y_leaf_up = center_adj + 0.9
            y_leaf_down = center_adj - 0.9
            # upper leaf (s_idx 0)
            arrow(ax, x_parent, y_parent, x_mid, y_leaf_up, color=C['dim'], lw=1.0)
            ax.text(x_mid - 0.55, (y_parent + y_leaf_up) / 2, f"{ps1:.3f}", fontsize=6, color=C['dim'], ha='center')
            leaf(ax, x_leaf, y_leaf_up, pay1)
            # lower leaf (s_idx 1)
            arrow(ax, x_parent, y_parent, x_mid, y_leaf_down, color=C['dim'], lw=1.0)
            ax.text(x_mid - 0.55, (y_parent + y_leaf_down) / 2, f"{ps2:.3f}", fontsize=6, color=C['dim'], ha='center')
            leaf(ax, x_leaf, y_leaf_down, pay2)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor=C["bg"])
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    
    return img_b64
