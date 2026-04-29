from typing import Optional
import numpy as np


def find_dominated_column(matrix: np.ndarray) -> Optional[int]:
    """Return index of a column dominated (for minimizer sindicato) by another, or None."""
    n_cols = matrix.shape[1]
    for b in range(n_cols):
        for a in range(n_cols):
            if a == b:
                continue
            # column a dominates b: a[i] <= b[i] for all rows (sindicato prefers lower values)
            if np.all(matrix[:, a] <= matrix[:, b]):
                return b
    return None


def find_dominated_row(matrix: np.ndarray) -> Optional[int]:
    """Return index of a row dominated (for maximizer JW) by another, or None."""
    n_rows = matrix.shape[0]
    for b in range(n_rows):
        for a in range(n_rows):
            if a == b:
                continue
            # row a dominates b: a[j] >= b[j] for all cols (JW prefers higher values)
            if np.all(matrix[a, :] >= matrix[b, :]):
                return b
    return None


def iterated_dominance(matrix: np.ndarray, row_labels: list, col_labels: list) -> dict:
    steps = []
    active_rows = list(range(matrix.shape[0]))
    active_cols = list(range(matrix.shape[1]))

    for _ in range(200):
        sub = matrix[np.ix_(active_rows, active_cols)]

        col_elim = find_dominated_column(sub)
        if col_elim is not None:
            dominator_local = next(
                a for a in range(sub.shape[1])
                if a != col_elim and np.all(sub[:, a] <= sub[:, col_elim])
            )
            elim_orig = active_cols[col_elim]
            dom_orig  = active_cols[dominator_local]
            steps.append({
                "type": "column",
                "eliminated": col_labels[elim_orig],
                "dominated_by": col_labels[dom_orig],
                "reason": (
                    f"Columna '{col_labels[elim_orig]}' dominada por "
                    f"'{col_labels[dom_orig]}': "
                    f"{sub[:, dominator_local].tolist()} ≤ "
                    f"{sub[:, col_elim].tolist()} para todos los renglones"
                ),
            })
            active_cols.pop(col_elim)
            continue

        row_elim = find_dominated_row(sub)
        if row_elim is not None:
            dominator_local = next(
                a for a in range(sub.shape[0])
                if a != row_elim and np.all(sub[a, :] >= sub[row_elim, :])
            )
            elim_orig = active_rows[row_elim]
            dom_orig  = active_rows[dominator_local]
            steps.append({
                "type": "row",
                "eliminated": row_labels[elim_orig],
                "dominated_by": row_labels[dom_orig],
                "reason": (
                    f"Renglón '{row_labels[elim_orig]}' dominado por "
                    f"'{row_labels[dom_orig]}': "
                    f"{sub[dominator_local, :].tolist()} ≥ "
                    f"{sub[row_elim, :].tolist()} para todas las columnas"
                ),
            })
            active_rows.pop(row_elim)
            continue

        break

    reduced = matrix[np.ix_(active_rows, active_cols)]
    return {
        "steps": steps,
        "reduced_matrix": reduced.tolist(),
        "remaining_rows": active_rows,
        "remaining_cols": active_cols,
    }


def solve_2x2_mixed(matrix: np.ndarray) -> dict:
    a, b = float(matrix[0, 0]), float(matrix[0, 1])
    c, d = float(matrix[1, 0]), float(matrix[1, 1])
    denom = a - b - c + d
    if abs(denom) < 1e-9:
        return {"error": "Denominador cero: el juego es degenerado o tiene solución en estrategias puras.", "valid": False}
    q = (d - b) / denom   # sindicato prob for col 0
    p = (d - c) / denom   # JW prob for row 0
    V = a * p + c * (1 - p)   # sindicato plays col 0; equals game value
    return {
        "p_row0": round(p, 6),
        "p_row1": round(1 - p, 6),
        "q_col0": round(q, 6),
        "q_col1": round(1 - q, 6),
        "value": round(V, 6),
        "valid": True,
        "error": None,
    }


def _game_conclusion(mixed: Optional[dict], row_labels: list, col_labels: list) -> str:
    if not mixed or not mixed.get("valid"):
        return "No se pudo calcular la estrategia mixta óptima."
    V  = mixed["value"]
    p0 = mixed.get("p_row0", 0)
    p1 = mixed.get("p_row1", 0)
    r0 = mixed.get("label_row0", "")
    r1 = mixed.get("label_row1", "")
    q0 = mixed.get("q_col0", 0)
    q1 = mixed.get("q_col1", 0)
    c0 = mixed.get("label_col0", "")
    c1 = mixed.get("label_col1", "")
    return (
        f"El valor del juego es V = {V:.2f} M COP. "
        f"JW debe mezclar: {r0} con probabilidad {p0:.2f} y {r1} con probabilidad {p1:.2f}. "
        f"El Sindicato debe mezclar: {c0} con probabilidad {q0:.2f} y {c1} con probabilidad {q1:.2f}. "
        f"Ningún jugador puede mejorar su resultado si el otro juega óptimamente. "
        f"Esta negociación estratégica con el sindicato es clave para la implementación exitosa de la inversión tecnológica "
        f"seleccionada en el PETI 2025-2028. El resultado de la negociación afecta directamente la adopción digital y la "
        f"viabilidad de la alternativa B (Inversión Media - Proyecto TI-01)."
    )


def compute_game_theory(cfg: dict) -> dict:
    _default_matrix = [[10,30,25,15],[5,40,10,30],[15,25,5,10],[20,20,15,40]]
    matrix     = np.array(cfg.get("matrix", _default_matrix), dtype=float)
    row_labels = list(cfg.get("row_labels", [f"E{i+1}" for i in range(matrix.shape[0])]))
    col_labels = list(cfg.get("col_labels", [f"U{i+1}" for i in range(matrix.shape[1])]))

    dom     = iterated_dominance(matrix, row_labels, col_labels)
    reduced = np.array(dom["reduced_matrix"])

    mixed = None
    note  = None

    if reduced.shape == (2, 2):
        mixed = solve_2x2_mixed(reduced)
        if mixed.get("valid"):
            mixed["label_row0"] = row_labels[dom["remaining_rows"][0]]
            mixed["label_row1"] = row_labels[dom["remaining_rows"][1]]
            mixed["label_col0"] = col_labels[dom["remaining_cols"][0]]
            mixed["label_col1"] = col_labels[dom["remaining_cols"][1]]
    elif reduced.shape[0] == 1 and reduced.shape[1] == 1:
        note  = "Solución en estrategias puras."
        mixed = {
            "valid": True, "value": float(reduced[0, 0]),
            "p_row0": 1.0, "p_row1": 0.0,
            "q_col0": 1.0, "q_col1": 0.0,
            "label_row0": row_labels[dom["remaining_rows"][0]],
            "label_row1": "",
            "label_col0": col_labels[dom["remaining_cols"][0]],
            "label_col1": "",
        }
    else:
        note = (
            f"Matriz reducida {reduced.shape[0]}×{reduced.shape[1]}: "
            "la solución de mezcla requiere programación lineal (fuera del alcance de este módulo)."
        )

    conclusion = _game_conclusion(mixed, row_labels, col_labels)

    return {
        "original_matrix": matrix.tolist(),
        "row_labels": row_labels,
        "col_labels": col_labels,
        "dominance_steps": dom["steps"],
        "reduced_matrix": dom["reduced_matrix"],
        "remaining_rows": dom["remaining_rows"],
        "remaining_cols": dom["remaining_cols"],
        "mixed_strategy": mixed,
        "note": note,
        "conclusion": conclusion,
    }
