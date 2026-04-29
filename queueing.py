from typing import Optional


def mm1_metrics(lam: float, mu: float) -> dict:
    rho = lam / mu
    if rho >= 1.0:
        return {"rho": rho, "P0": None, "L": None, "Lq": None,
                "W": None, "Wq": None, "valid": False,
                "error": f"Sistema inestable: ρ = {rho:.4f} ≥ 1"}
    P0 = 1 - rho
    L  = rho / (1 - rho)
    Lq = rho ** 2 / (1 - rho)
    W  = L / lam
    Wq = Lq / lam
    return {"rho": rho, "P0": P0, "L": L, "Lq": Lq,
            "W": W, "Wq": Wq, "valid": True, "error": None}


def mm2_metrics(lam: float, mu: float) -> dict:
    c = 2
    rho = lam / (c * mu)
    if rho >= 1.0:
        return {"rho": rho, "P0": None, "L": None, "Lq": None,
                "W": None, "Wq": None, "valid": False,
                "error": f"Sistema inestable: ρ/c = {rho:.4f} ≥ 1"}
    r = lam / mu
    P0 = 1.0 / (1 + r + (r ** 2) / (2 * (1 - rho)))
    Lq = P0 * (r ** 2) * rho / (2 * (1 - rho) ** 2)
    L  = Lq + r
    W  = L / lam
    Wq = Lq / lam
    return {"rho": rho, "P0": P0, "L": L, "Lq": Lq,
            "W": W, "Wq": Wq, "valid": True, "error": None}


def _best_per_metric(scenarios: list) -> dict:
    best = {}
    for m in ("rho", "L", "Lq", "W", "Wq"):
        candidates = [(i, s[m]) for i, s in enumerate(scenarios)
                      if s.get("valid") and s[m] is not None]
        if candidates:
            best[m] = min(candidates, key=lambda x: x[1])[0]
    # P0: higher is better
    p0_candidates = [(i, s["P0"]) for i, s in enumerate(scenarios)
                     if s.get("valid") and s["P0"] is not None]
    if p0_candidates:
        best["P0"] = max(p0_candidates, key=lambda x: x[1])[0]
    return best


def _generate_conclusion(scenarios: list, best: dict) -> str:
    valid = [s for s in scenarios if s.get("valid")]
    if not valid:
        return "Ningún escenario es estable. Ajuste los parámetros."
    best_w_idx = best.get("W")
    if best_w_idx is not None:
        w = scenarios[best_w_idx]
        return (
            f"El escenario '{w['label']}' es el más eficiente: "
            f"W = {w['W']:.4f} h ({w['W']*60:.1f} min) por vehículo, "
            f"con L = {w['L']:.4f} vehículos en el sistema y "
            f"ρ = {w['rho']:.4f}. "
            f"Se recomienda su implementación para el horizonte PETI 2025-2028."
        )
    return "Revise la estabilidad de los escenarios."


def compute_queueing(cfg: dict) -> dict:
    lam       = float(cfg.get("lam", 10))
    mu_actual = float(cfg.get("mu_mm1_actual", 12))
    mu_mejor  = float(cfg.get("mu_mm1_mejor", 18))
    mu_mm2    = float(cfg.get("mu_mm2", 12))

    scenarios = [
        {"label": "Canal Simple",   "type": "mm1", "lam": lam, "mu": mu_actual, "c": 1,
         **mm1_metrics(lam, mu_actual)},
        {"label": "Canal Mejorado", "type": "mm1", "lam": lam, "mu": mu_mejor,  "c": 1,
         **mm1_metrics(lam, mu_mejor)},
        {"label": "Canal Múltiple", "type": "mm2", "lam": lam, "mu": mu_mm2,    "c": 2,
         **mm2_metrics(lam, mu_mm2)},
    ]

    best       = _best_per_metric(scenarios)
    conclusion = _generate_conclusion(scenarios, best)
    return {"scenarios": scenarios, "best": best, "conclusion": conclusion}
