from flask import Blueprint, render_template, request, jsonify
from compute import compute_all, build_tree_json
from tree_render import render_tree_png
from queueing import compute_queueing
from game_theory import compute_game_theory

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/compute', methods=['POST'])
def compute():
    data = request.get_json() or {}
    cfg = {
        'alt_names': data.get('alt_names', ['A1','A2','A3']),
        'state_names': data.get('state_names', ['S1','S2']),
        'payoffs': data.get('payoffs', [[8,7],[14,5],[20,-9]]),
        'P_S1': float(data.get('P_S1', 0.7)),
        'P_S2': float(1 - float(data.get('P_S1', 0.7))),
        'P_F_given_S1': float(data.get('P_F_given_S1', 0.9)),
        'P_F_given_S2': float(data.get('P_F_given_S2', 0.25)),
    }
    res = compute_all(cfg)
    tree_json = build_tree_json(cfg, res)
    res['tree'] = tree_json
    
    # Generar imagen del árbol
    tree_img_b64 = render_tree_png(cfg, res)
    res['tree_image'] = f"data:image/png;base64,{tree_img_b64}"
    
    return jsonify(res)


@bp.route('/compute_queueing', methods=['POST'])
def compute_queueing_route():
    data = request.get_json() or {}
    return jsonify(compute_queueing({
        'lam':           float(data.get('lam', 10)),
        'mu_mm1_actual': float(data.get('mu_mm1_actual', 12)),
        'mu_mm1_mejor':  float(data.get('mu_mm1_mejor', 18)),
        'mu_mm2':        float(data.get('mu_mm2', 12)),
    }))


@bp.route('/compute_game_theory', methods=['POST'])
def compute_game_theory_route():
    data = request.get_json() or {}
    return jsonify(compute_game_theory({
        'matrix':     data.get('matrix', [[10,30,25,15],[5,40,10,30],[15,25,5,10],[20,20,15,40]]),
        'row_labels': data.get('row_labels', ['E1', 'E2', 'E3', 'E4']),
        'col_labels': data.get('col_labels', ['U1', 'U2', 'U3', 'U4']),
    }))
