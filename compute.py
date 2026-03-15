import numpy as np

def compute_all(cfg):
    """Compute all decision-theory metrics and return serializable results."""
    V = np.array(cfg["payoffs"], dtype=float)
    n_alt, n_states = V.shape
    PS = np.array([cfg["P_S1"], cfg["P_S2"]])

    optimist  = V.max(axis=1)
    conserv   = V.min(axis=1)
    best_col  = V.max(axis=0)
    regret    = np.abs(best_col - V)
    max_regret= regret.max(axis=1)

    EV = V @ PS
    best_per_state = V.max(axis=0)
    EV_perfect = float(np.dot(PS, best_per_state))
    VEIP = EV_perfect - float(EV.max())

    PF_S1 = cfg.get("P_F_given_S1", 0.0)
    PF_S2 = cfg.get("P_F_given_S2", 0.0)
    PU_S1 = 1 - PF_S1
    PU_S2 = 1 - PF_S2

    P_F = float(PS[0]*PF_S1 + PS[1]*PF_S2)
    P_U = float(PS[0]*PU_S1 + PS[1]*PU_S2)

    PS1_F = (PS[0]*PF_S1) / P_F if P_F>0 else 0
    PS2_F = (PS[1]*PF_S2) / P_F if P_F>0 else 0
    PS1_U = (PS[0]*PU_S1) / P_U if P_U>0 else 0
    PS2_U = (PS[1]*PU_S2) / P_U if P_U>0 else 0

    EV_F = V @ np.array([PS1_F, PS2_F])
    EV_U = V @ np.array([PS1_U, PS2_U])

    best_F_idx = int(np.argmax(EV_F))
    best_U_idx = int(np.argmax(EV_U))

    best_F = float(EV_F.max())
    best_U = float(EV_U.max())

    EV_sample_strategy = P_F * best_F + P_U * best_U
    EVSI = EV_sample_strategy - float(EV.max())
    efficiency = (EVSI / VEIP * 100) if VEIP > 0 else 0

    # EV sensitivity lines for plotting
    p = np.linspace(0, 1, 200)
    EV_lines = []
    for i in range(n_alt):
        ev_line = V[i, 0] * p + V[i, 1] * (1 - p)
        EV_lines.append(ev_line.tolist())

    return {
        "V": V.tolist(),
        "alt_names": cfg.get("alt_names"),
        "state_names": cfg.get("state_names"),
        "PS": PS.tolist(),
        "optimist": optimist.tolist(),
        "conserv": conserv.tolist(),
        "regret": regret.tolist(),
        "max_regret": max_regret.tolist(),
        "EV": EV.tolist(),
        "EV_perfect": EV_perfect,
        "VEIP": VEIP,
        "PF_S1": PF_S1, "PF_S2": PF_S2, "PU_S1": PU_S1, "PU_S2": PU_S2,
        "P_F": P_F, "P_U": P_U,
        "PS1_F": PS1_F, "PS2_F": PS2_F,
        "PS1_U": PS1_U, "PS2_U": PS2_U,
        "EV_F": EV_F.tolist(), "EV_U": EV_U.tolist(),
        "best_F_idx": best_F_idx, "best_U_idx": best_U_idx,
        "best_F": best_F, "best_U": best_U,
        "EV_sample_strategy": EV_sample_strategy,
        "EVSI": EVSI,
        "efficiency": efficiency,
        "p": p.tolist(),
        "EV_lines": EV_lines,
    }

def build_tree_json(cfg, res):
    """Build decision tree as hierarchical JSON for D3 visualization."""
    V = res["V"]
    alt_names = cfg.get("alt_names", ["A1", "A2", "A3"])
    state_names = cfg.get("state_names", ["S1", "S2"])
    
    best_no_idx = int(np.argmax(res["EV"]))
    best_f_idx = res["best_F_idx"]
    best_u_idx = res["best_U_idx"]
    
    ps = res.get('PS', [0,0])
    PS1 = ps[0]
    PS2 = ps[1]

    def ev_formula_for_alt(idx, prior=True, posterior=None):
        v0 = V[idx][0]
        v1 = V[idx][1]
        if prior:
            return f"EV = {PS1:.4f}*{v0} + {PS2:.4f}*{v1}"
        else:
            p1, p2 = posterior
            return f"EV = {p1:.4f}*{v0} + {p2:.4f}*{v1}"

    root = {
        "id": "root",
        "label": "Decisión",
        "type": "decision",
        "children": [
            {
                "id": "no-study",
                "label": "Sin estudio",
                "type": "chance",
                "prob": 1.0,
                "children": [
                    {
                        "id": "outcome-no-study",
                        "label": alt_names[best_no_idx],
                        "type": "outcome",
                        "ev": res["EV"][best_no_idx],
                        "payoffs": [V[best_no_idx][0], V[best_no_idx][1]],
                        "states": state_names,
                        "formula": ev_formula_for_alt(best_no_idx, prior=True),
                    }
                ]
            },
            {
                "id": "study",
                "label": "Hacer estudio",
                "type": "chance",
                "prob": 1.0,
                "children": [
                    {
                        "id": "favorable",
                        "label": f"Favorable (p={res['P_F']:.4f})",
                        "type": "chance",
                        "prob": res["P_F"],
                        "children": [
                                    {
                                        "id": "outcome-favorable",
                                        "label": alt_names[best_f_idx],
                                        "type": "outcome",
                                        "ev": res["best_F"],
                                        "payoffs": [V[best_f_idx][0], V[best_f_idx][1]],
                                        "states": state_names,
                                        "formula": ev_formula_for_alt(best_f_idx, prior=False, posterior=(res.get('PS1_F',0), res.get('PS2_F',0)))
                                    }
                        ]
                    },
                    {
                        "id": "unfavorable",
                        "label": f"Desfavorable (p={res['P_U']:.4f})",
                        "type": "chance",
                        "prob": res["P_U"],
                        "children": [
                            {
                                "id": "outcome-unfavorable",
                                "label": alt_names[best_u_idx],
                                "type": "outcome",
                                "ev": res["best_U"],
                                "payoffs": [V[best_u_idx][0], V[best_u_idx][1]],
                                "states": state_names,
                                "formula": ev_formula_for_alt(best_u_idx, prior=False, posterior=(res.get('PS1_U',0), res.get('PS2_U',0)))
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    return root
