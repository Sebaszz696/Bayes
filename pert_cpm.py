from collections import deque


def compute_pert_cpm(cfg):
    activities_input = cfg.get('activities', [])

    acts = {a['id']: {
        'id':           a['id'],
        'desc':         a.get('desc', ''),
        'predecessors': [p.strip() for p in a.get('predecessors', []) if p.strip()],
        'duration':     int(a.get('duration', 0)),
        'IP': 0, 'TP': 0, 'IL': 0, 'TL': 0,
        'holgura': 0, 'critica': False,
    } for a in activities_input}

    ids = list(acts.keys())

    # Build successor map
    successors = {i: [] for i in ids}
    for i in ids:
        for p in acts[i]['predecessors']:
            if p in successors:
                successors[p].append(i)

    # Topological sort (Kahn)
    in_degree = {i: len(acts[i]['predecessors']) for i in ids}
    queue = deque(i for i in ids if in_degree[i] == 0)
    topo_order = []
    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for s in successors[node]:
            in_degree[s] -= 1
            if in_degree[s] == 0:
                queue.append(s)

    # Forward Pass
    for i in topo_order:
        preds = acts[i]['predecessors']
        if not preds:
            acts[i]['IP'] = 0
        else:
            acts[i]['IP'] = max(acts[p]['TP'] for p in preds if p in acts)
        acts[i]['TP'] = acts[i]['IP'] + acts[i]['duration']

    project_duration = max(acts[i]['TP'] for i in ids) if ids else 0

    # Backward Pass
    for i in ids:
        acts[i]['TL'] = project_duration  # initialize all to project end

    for i in reversed(topo_order):
        succs = successors[i]
        if not succs:
            acts[i]['TL'] = project_duration
        else:
            acts[i]['TL'] = min(acts[s]['IL'] for s in succs)
        acts[i]['IL'] = acts[i]['TL'] - acts[i]['duration']

    # Holgura and critical path
    for i in ids:
        acts[i]['holgura'] = acts[i]['IL'] - acts[i]['IP']
        acts[i]['critica'] = acts[i]['holgura'] == 0

    critical_path = [i for i in topo_order if acts[i]['critica']]

    path_str = ' → '.join(critical_path)
    conclusion = (
        f"La ruta crítica es {path_str} con una duración total de {project_duration} días. "
        f"Cualquier retraso en estas actividades impacta directamente la fecha de finalización del proyecto. "
        f"Las demás actividades presentan holgura y pueden reprogramarse sin afectar el plazo."
    )

    return {
        'activities': [acts[i] for i in topo_order],
        'project_duration': project_duration,
        'critical_path': critical_path,
        'conclusion': conclusion,
    }
