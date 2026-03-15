from flask import Blueprint, render_template, request, jsonify
from compute import compute_all, build_tree_json
from tree_render import render_tree_png

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
