function getTableData(){
  const tbl = document.getElementById('payTable');
  const alts = [];
  const pays = [];
  const rows = tbl.querySelectorAll('tbody tr');
  rows.forEach(r=>{
    const alt = r.querySelector('.alt-name').value.trim();
    const s1 = parseFloat(r.querySelector('.pay-s1').value)||0;
    const s2 = parseFloat(r.querySelector('.pay-s2').value)||0;
    alts.push(alt);
    pays.push([s1,s2]);
  });
  return {alts, pays};
}

let lastData = null;
let computeTimeout = null;
function debounceCompute(){
  if(computeTimeout) clearTimeout(computeTimeout);
  computeTimeout = setTimeout(()=>{ computeAndRender(); }, 350);
}

async function computeAndRender(){
  const tableData = getTableData();
  const payload = {
    payoffs: tableData.pays,
    alt_names: tableData.alts,
    state_names: [document.getElementById('state1_name').value, document.getElementById('state2_name').value],
    P_S1: parseFloat(document.getElementById('p_s1').value),
    P_F_given_S1: parseFloat(document.getElementById('pf_s1').value),
    P_F_given_S2: parseFloat(document.getElementById('pf_s2').value),
  };

  const res = await fetch('/compute', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await res.json();
  console.log('compute: tree_image present?', !!data.tree_image, 'length=', data.tree_image ? data.tree_image.length : 0);
  lastData = data;
  renderQuickMetrics(data);
  renderTables(data);
  renderTree(data);
  renderChart(data);
}

function renderTables(data){
  const div = document.getElementById('tablesArea');
  div.innerHTML = '';
  // compute best/worst indices
  const best_opt_idx = data.optimist.indexOf(Math.max(...data.optimist));
  const best_cons_idx = data.conserv.indexOf(Math.min(...data.conserv));
  const best_ev_idx = data.EV.indexOf(Math.max(...data.EV));
  const best_ev_f_idx = data.best_F_idx;
  const best_ev_u_idx = data.best_U_idx;

  // Tabla de pagos
  let html = '<h5>Tabla de Pagos</h5>';
  html += '<table class="table table-sm table-bordered"><thead><tr><th>Alternativa</th>' +
         `<th>${escapeHtml(data.state_names[0])}</th><th>${escapeHtml(data.state_names[1])}</th></tr></thead><tbody>`;
  for(let i=0;i<data.V.length;i++){
    html += `<tr><td>${escapeHtml(data.alt_names[i]||('A'+(i+1)))}</td><td>${data.V[i][0]}</td><td>${data.V[i][1]}</td></tr>`;
  }
  html += '</tbody></table>';

  // Enfoque optimista
  html += '<h5>Enfoque Optimista (MAXIMAX)</h5>';
  html += '<table class="table table-sm table-bordered"><thead><tr><th>Alternativa</th><th>Máx</th></tr></thead><tbody>';
  data.optimist.forEach((v,i)=> html += `<tr${i===best_opt_idx? ' class="best-optimist"':''}><td>${escapeHtml(data.alt_names[i]||('A'+(i+1)))}</td><td>${v}</td></tr>`);
  html += '</tbody></table>';

  // Enfoque conservador
  html += '<h5>Enfoque Conservador (MAXIMIN)</h5>';
  html += '<table class="table table-sm table-bordered"><thead><tr><th>Alternativa</th><th>Mín</th></tr></thead><tbody>';
  data.conserv.forEach((v,i)=> html += `<tr${i===best_cons_idx? ' class="best-conserv"':''}><td>${escapeHtml(data.alt_names[i]||('A'+(i+1)))}</td><td>${v}</td></tr>`);
  html += '</tbody></table>';

  // Arrepentimiento
  html += '<h5>Máx Arrepentimiento (Regret)</h5>';
  html += '<table class="table table-sm table-bordered"><thead><tr><th>Alternativa</th><th>R(S1)</th><th>R(S2)</th><th>Máx</th></tr></thead><tbody>';
  for(let i=0;i<data.regret.length;i++){
    html += `<tr${i===best_ev_idx? ' class="best-ev"':''}><td>${escapeHtml(data.alt_names[i]||('A'+(i+1)))}</td><td>${data.regret[i][0]}</td><td>${data.regret[i][1]}</td><td>${data.max_regret[i]}</td></tr>`;
  }
  html += '</tbody></table>';

  // Valor Esperado
  html += '<h5>Valor Esperado (EV)</h5>';
  html += '<table class="table table-sm table-bordered"><thead><tr><th>Alternativa</th><th>EV</th></tr></thead><tbody>';
  data.EV.forEach((v,i)=> html += `<tr${i===best_ev_idx? ' class="best-ev"':''}><td>${escapeHtml(data.alt_names[i]||('A'+(i+1)))}</td><td>${v.toFixed(4)}</td></tr>`);
  html += '</tbody></table>';

  // Probabilidades Bayesianas
  html += '<h5>Probabilidades Bayesianas</h5>';
  html += `<ul class="list-group mb-3"><li class="list-group-item">P(F|${escapeHtml(data.state_names[0])}) = ${data.PF_S1}</li><li class="list-group-item">P(U|${escapeHtml(data.state_names[0])}) = ${data.PU_S1}</li><li class="list-group-item">P(F|${escapeHtml(data.state_names[1])}) = ${data.PF_S2}</li><li class="list-group-item">P(U|${escapeHtml(data.state_names[1])}) = ${data.PU_S2}</li><li class="list-group-item">P(F) = ${data.P_F.toFixed(4)}</li><li class="list-group-item">P(U) = ${data.P_U.toFixed(4)}</li><li class="list-group-item">P(${escapeHtml(data.state_names[0])}|F) = ${data.PS1_F.toFixed(4)}</li><li class="list-group-item">P(${escapeHtml(data.state_names[1])}|F) = ${data.PS2_F.toFixed(4)}</li></ul>`;

  // EV Muestral
  html += '<h5>EV Muestral (EV|F, EV|U)</h5>';
  html += '<table class="table table-sm table-bordered"><thead><tr><th>Alternativa</th><th>EV|F</th><th>EV|U</th></tr></thead><tbody>';
  for(let i=0;i<data.EV_F.length;i++){
    const clsF = (i===best_ev_f_idx)? ' class="best-ev"':'';
    const clsU = (i===best_ev_u_idx)? ' class="best-ev"':'';
    html += `<tr><td>${escapeHtml(data.alt_names[i]||('A'+(i+1)))}</td><td${clsF}>${data.EV_F[i].toFixed(4)}</td><td${clsU}>${data.EV_U[i].toFixed(4)}</td></tr>`;
  }
  html += '</tbody></table>';

  div.innerHTML = html;
}

function escapeHtml(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function renderTree(data){
  // New image-based renderer: wrapper (relative) + absolutely positioned draggable image + outcomes panel
  const containerIdCandidates = ['treeArea','tree','tree-container','treeAreaContainer','tab-arbol-pane'];
  let div = null;
  for(const id of containerIdCandidates){
    div = document.getElementById(id);
    if(div) break;
  }
  if(!div){
    console.warn('No tree container found. Expected one of: ' + containerIdCandidates.join(','));
    return;
  }
  div.innerHTML = '';

  // If there's no tree image, keep previous fallback message
  if(!data || !data.tree_image){
    div.innerHTML = '<p>No se pudo generar el árbol.</p>';
    return;
  }

  // wrapper with position:relative
  const wrapper = document.createElement('div');
  wrapper.style.position = 'relative';
  wrapper.style.width = '100%';
  // make wrapper occupy most of the viewport so the tree image is much larger
  wrapper.style.height = 'calc(100vh - 140px)';
  wrapper.style.minHeight = '480px';
  // allow scrolling if image is larger than viewport
  wrapper.style.overflow = 'auto';
  wrapper.style.boxSizing = 'border-box';
  div.appendChild(wrapper);

  // no outcomes panel: image can use full width
  const panelWidth = 0;

  // tooltip element
  const tooltip = document.createElement('div');
  tooltip.style.position = 'absolute';
  tooltip.style.pointerEvents = 'none';
  tooltip.style.background = 'rgba(0,0,0,0.85)';
  tooltip.style.color = '#fff';
  tooltip.style.padding = '6px 8px';
  tooltip.style.borderRadius = '4px';
  tooltip.style.fontSize = '12px';
  tooltip.style.display = 'none';
  tooltip.style.zIndex = '9999';
  wrapper.appendChild(tooltip);

  // image: absolutely positioned within wrapper (left area)
  const img = document.createElement('img');
  // force reload: set empty src first, then assign the data URI
  img.src = '';
  // small timeout ensures DOM updated before assigning large data URI
  setTimeout(()=> { try{ img.src = data.tree_image; } catch(e){ console.error('img set src error', e); } }, 8);
  // make image fill width and respect wrapper height
  img.style.position = 'relative';
  img.style.left = '0px';
  img.style.top = '0px';
  img.style.width = '100%';
  img.style.maxWidth = 'none';
  img.style.maxHeight = '100%';
  img.style.height = 'auto';
  img.style.objectFit = 'contain';
  img.style.cursor = 'grab';
  img.style.userSelect = 'none';
  img.style.touchAction = 'none';
  img.draggable = false;
  wrapper.appendChild(img);

  // no separate outcomes list; tooltip is available for future use

  // Drag + zoom implementation for desktop and touch
  let dragging = false;
  let startX = 0, startY = 0;
  let imgX = 0, imgY = 0;
  let scale = 1;

  function setImgTransform(x,y){
    img.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
  }

  img.addEventListener('mousedown', (e)=>{
    e.preventDefault();
    dragging = true;
    img.style.cursor = 'grabbing';
    startX = e.clientX;
    startY = e.clientY;
    // extract current transform
    const m = img.style.transform.match(/translate\((-?\d+)px,\s*(-?\d+)px\)/);
    if(m){
      imgX = parseInt(m[1],10);
      imgY = parseInt(m[2],10);
    } else { imgX = 0; imgY = 0; }
  });
  document.addEventListener('mousemove', (e)=>{
    if(!dragging) return;
    e.preventDefault();
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    setImgTransform(imgX + dx, imgY + dy);
  });
  document.addEventListener('mouseup', ()=>{
    if(dragging){
      dragging = false;
      img.style.cursor = 'grab';
      // store final position
      const m = img.style.transform.match(/translate\((-?\d+)px,\s*(-?\d+)px\)/);
      if(m){ imgX = parseInt(m[1],10); imgY = parseInt(m[2],10); }
    }
  });

  // touch equivalents
  img.addEventListener('touchstart', (e)=>{
    if(e.touches.length !== 1) return;
    const t = e.touches[0];
    dragging = true;
    startX = t.clientX;
    startY = t.clientY;
    const m = img.style.transform.match(/translate\((-?\d+)px,\s*(-?\d+)px\)/);
    if(m){ imgX = parseInt(m[1],10); imgY = parseInt(m[2],10); } else { imgX = 0; imgY = 0; }
  }, {passive:true});
  img.addEventListener('touchmove', (e)=>{
    if(!dragging) return;
    const t = e.touches[0];
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;
    setImgTransform(imgX + dx, imgY + dy);
  }, {passive:true});
  img.addEventListener('touchend', ()=>{ dragging = false; });

  // --- Zoom controls ---
  const controls = document.createElement('div');
  controls.style.position = 'absolute';
  controls.style.top = '12px';
  controls.style.right = '12px';
  controls.style.zIndex = 10001;
  controls.style.display = 'flex';
  controls.style.flexDirection = 'column';
  controls.style.gap = '6px';

  function makeBtn(label, title){
    const b = document.createElement('button');
    b.className = 'btn btn-sm btn-outline-secondary';
    b.textContent = label;
    b.title = title || label;
    b.style.width = '44px';
    b.style.height = '36px';
    return b;
  }

  const btnZoomIn = makeBtn('+', 'Zoom in');
  const btnZoomOut = makeBtn('−', 'Zoom out');
  const btnReset = makeBtn('⟲', 'Reset zoom');

  btnZoomIn.addEventListener('click', ()=>{ scale = Math.min(scale * 1.2, 8); setImgTransform(imgX, imgY); });
  btnZoomOut.addEventListener('click', ()=>{ scale = Math.max(scale / 1.2, 0.125); setImgTransform(imgX, imgY); });
  btnReset.addEventListener('click', ()=>{ scale = 1; imgX = 0; imgY = 0; setImgTransform(imgX, imgY); });

  controls.appendChild(btnZoomIn);
  controls.appendChild(btnZoomOut);
  controls.appendChild(btnReset);
  wrapper.appendChild(controls);
}

function renderQuickMetrics(data){
  const q = document.getElementById('quickMetrics');
  q.innerHTML = '';
  const items = [
    {k:'EV_opt', v:`$${Math.max(...data.EV).toFixed(2)}M`, c:'bg-dark text-white'},
    {k:'EV_est', v:`$${data.EV_sample_strategy.toFixed(2)}M`, c:'bg-success text-white'},
    {k:'EVSI', v:`$${data.EVSI.toFixed(2)}M`, c:'bg-info text-dark'},
  ];
  items.forEach(it=>{
    const div = document.createElement('div'); div.className = `p-2 rounded ${it.c}`; div.textContent = it.v; q.appendChild(div);
  });
}

function renderChart(data){
  const el = document.getElementById('chartArea');
  el.innerHTML = '';
  const traces = [];
  // add line traces for each alternative
  for(let i=0;i<data.EV_lines.length;i++){
    traces.push({x:data.p, y:data.EV_lines[i], mode:'lines', name:`${data.alt_names[i]||('A'+(i+1))}`, line:{width:2}});
  }

  // compute intersection points between pairs of EV lines
  const interX = [];
  const interY = [];
  const interLabels = [];
  const V = data.V; // payoff matrix
  for(let i=0;i<V.length;i++){
    for(let j=i+1;j<V.length;j++){
      const a1 = V[i][0] - V[i][1];
      const a2 = V[j][0] - V[j][1];
      const denom = a1 - a2;
      if(Math.abs(denom) < 1e-9) continue;
      const p_int = (V[j][1] - V[i][1]) / denom;
      if(p_int >= 0 && p_int <= 1){
        const ev = V[i][0]*p_int + V[i][1]*(1-p_int);
        interX.push(p_int);
        interY.push(ev);
        interLabels.push(`p=${p_int.toFixed(3)}\nEV=${ev.toFixed(2)}`);
      }
    }
  }

  // marker trace for intersections
  if(interX.length){
    traces.push({x:interX, y:interY, mode:'markers', name:'Intersecciones', marker:{size:8, color:'#ffffff', line:{color:'#000', width:1}}, hoverinfo:'text', text:interLabels});
  }

  // vertical line at current P(S1) and marker for best alt at that P
  const p_cur = parseFloat(document.getElementById('p_s1').value) || data.p[Math.floor(data.p.length/2)];
  // compute ev at p_cur per alt
  const ev_at_p = [];
  for(let i=0;i<V.length;i++) ev_at_p.push(V[i][0]*p_cur + V[i][1]*(1-p_cur));
  const maxIdx = ev_at_p.indexOf(Math.max(...ev_at_p));
  const ev_max = ev_at_p[maxIdx];
  // marker for best at current p
  traces.push({x:[p_cur], y:[ev_max], mode:'markers', name:'P(S1) actual', marker:{size:10, color:'#ffffff', line:{color:'#000', width:1}}, hoverinfo:'none'});

  // build annotations for intersections and current p
  const annotations = [];
  for(let k=0;k<interX.length;k++){
    annotations.push({ x: interX[k], y: interY[k], xanchor:'left', yanchor:'bottom', text: interLabels[k].replace('\n','<br>'), showarrow:true, arrowhead:2, ax:10, ay:-10, font:{size:11, color:'#ffffff'}, bgcolor:'rgba(0,0,0,0.6)'});
  }
  annotations.push({ x: p_cur, y: ev_max, xanchor:'left', yanchor:'bottom', text:`p=${p_cur.toFixed(3)}<br>EV=${ev_max.toFixed(2)}`, showarrow:true, arrowhead:2, ax:10, ay:-10, font:{size:11, color:'#ffffff'}, bgcolor:'rgba(0,0,0,0.6)'});

  // determine y-range for vertical line
  const allYs = data.EV_lines.flat();
  const yMin = Math.min(...allYs) - 2;
  const yMax = Math.max(...allYs) + 2;

  const layout = {template:'plotly_dark', xaxis:{title:'Probabilidad P(S1)', range:[0,1]}, yaxis:{title:'Valor Esperado (M$)', range:[yMin,yMax]}, shapes:[{type:'line', x0:p_cur, x1:p_cur, y0:yMin, y1:yMax, line:{color:'#FFD166', width:2, dash:'dash'}}], annotations:annotations, title:{text:'ANÁLISIS GRÁFICO DE SENSIBILIDAD', x:0.5, font:{color:'#00C9A7'}}};

  Plotly.newPlot(el, traces, layout, {responsive:true});
}

function renderSummary(data){
  const el = document.getElementById('summaryArea');
  el.innerHTML = '';
  if(!data) { el.innerHTML = '<p>No hay datos.</p>'; return; }

  // Prepare values
  const P_S = (data.PS && data.PS.length)? data.PS : [ (parseFloat(document.getElementById('p_s1').value)||0.7), 1-(parseFloat(document.getElementById('p_s1').value)||0.7) ];
  const alt_names = data.alt_names || [];
  const state_names = data.state_names || ['S1','S2'];
  const V = data.V || [];
  const n_alt = V.length;
  const n_states = (V[0] || []).length;

  // helpers
  const fmt = (v,dec=4)=> (typeof v === 'number')? v.toFixed(dec): v;

  // Compute summary values to avoid undefined references
  const EVs = data.EV || [];
  const best_ev_val = EVs.length ? Math.max(...EVs) : 0;
  const best_ev_idx = EVs.length ? EVs.indexOf(best_ev_val) : 0;
  const EV_sample = data.EV_sample_strategy || 0;
  const EV_F = data.EV_F || [];
  const EV_U = data.EV_U || [];
  const best_f_val = EV_F.length ? Math.max(...EV_F) : 0;
  const best_f_i = EV_F.length ? EV_F.indexOf(best_f_val) : 0;
  const best_u_val = EV_U.length ? Math.max(...EV_U) : 0;
  const best_u_i = EV_U.length ? EV_U.indexOf(best_u_val) : 0;
  const EV_perfect = (typeof data.EV_perfect !== 'undefined') ? data.EV_perfect : 0;
  const VEIP = (typeof data.VEIP !== 'undefined') ? data.VEIP : (EV_perfect - best_ev_val);
  const EVSI = (typeof data.EVSI !== 'undefined') ? data.EVSI : (EV_sample - best_ev_val);
  const efficiency = (typeof data.efficiency !== 'undefined') ? data.efficiency : (VEIP? (EVSI/VEIP*100):0);

  // Header / authors
  let html = `<div class="report">
    <h3 style="color:#333;">Autores</h3>
    <p>Sebastian Velasquez<br/>Camila Bermudez<br/>Diego Zabaleta<br/>Simon Cortes<br/>Sara Patiño</p>
    <hr/>
  `;

  

  // Section 9: Resumen
  html += `<h4>Resumen</h4>`;
  html += `<table class="table table-sm"><tbody>`;
  html += `<tr><td>VE (Valor Esperado) óptimo sin info</td><td>$${fmt(best_ev_val,4)} M$</td><td>A${best_ev_idx+1}: ${escapeHtml(alt_names[best_ev_idx]||'')}</td></tr>`;
  html += `<tr><td>VE (Valor Esperado) con estudio</td><td>$${fmt(EV_sample,4)} M$</td><td>Si se usa el estudio esta seria la ganacia </td></tr>`;
  html += `<tr><td>Alternativa óptima (si estudio = Favorable)</td><td>$${fmt(best_f_val,4)} M$</td><td>A${best_f_i+1}: ${escapeHtml(alt_names[best_f_i]||'')}</td></tr>`;
  html += `<tr><td>Alternativa óptima (si estudio = Desfavorable)</td><td>$${fmt(best_u_val,4)} M$</td><td>A${best_u_i+1}: ${escapeHtml(alt_names[best_u_i]||'')}</td></tr>`;
  html += `<tr><td>EVwPI (Valor Esperado con Información Perfecta)</td><td>$${fmt(EV_perfect,4)} M$</td><td>Max. valor teórico alcanzable</td></tr>`;
  html += `<tr><td>EVPI (Valor Esperado de la Información Perfecta)</td><td>$${fmt(VEIP,4)} M$</td><td>Max. a pagar por info perfecta</td></tr>`;
  html += `<tr><td>EVSI (Valor Esperado de la Información de la Muestra)</td><td>$${fmt(EVSI,4)} M$</td><td>Max. a pagar por el estudio</td></tr>`;
  html += `<tr><td>Eficiencia del estudio</td><td>${fmt(efficiency,1)}%</td><td>EVSI / EVPI</td></tr>`;
  html += `</tbody></table>`;

  html += `</tbody></table>`;

  // Conclusion section added per user request
  html += `<h4>Conclusión</h4>`;
  html += `<p>Recomendación: seleccionar <strong>A${best_ev_idx+1}</strong> (${escapeHtml(alt_names[best_ev_idx]||'')}) como alternativa óptima sin información adicional, con VE = ${fmt(best_ev_val,4)} M$. El análisis con el estudio eleva el valor esperado a ${fmt(EV_sample,4)} M$ (EVSI = ${fmt(EVSI,4)} M$). El valor máximo teórico con información perfecta es ${fmt(EV_perfect,4)} M$ (EVPI = ${fmt(VEIP,4)} M$). </p>`;

  html += `</div>`;

  el.innerHTML = html;
}

// ensure summary renders when tab shown
document.getElementById('nav-summary').addEventListener('shown.bs.tab', (ev)=>{ if(!lastData) computeAndRender(); else renderSummary(lastData); });

// Re-render when tab becomes visible (fix hidden-container rendering issues)
document.querySelectorAll('[data-bs-toggle="list"]').forEach(el=>{
  el.addEventListener('shown.bs.tab', (ev)=>{
    const target = ev.target.getAttribute('href') || ev.target.dataset.bsTarget;
    if(!lastData){ computeAndRender(); return; }
    if(target && target.includes('tables')) renderTables(lastData);
    if(target && target.includes('tree')) renderTree(lastData);
    if(target && target.includes('charts')) renderChart(lastData);
  });
});

document.getElementById('computeBtn').addEventListener('click', computeAndRender);
document.getElementById('addAltBtn').addEventListener('click', ()=>{ addAltRow(); computeAndRender(); });

function addAltRow(name='', s1=0, s2=0){
  const tbody = document.querySelector('#payTable tbody');
  const tr = document.createElement('tr');
  tr.innerHTML = `<td><input class="form-control alt-name" value="${name}"/></td><td><input type="number" class="form-control pay-s1" value="${s1}"/></td><td><input type="number" class="form-control pay-s2" value="${s2}"/></td><td><button class="btn btn-sm btn-outline-danger rm-row">✕</button></td>`;
  tbody.appendChild(tr);
  // remove row and trigger recompute
  tr.querySelector('.rm-row').addEventListener('click', ()=>{ tr.remove(); debounceCompute(); });
  // trigger recompute when editing any input in the row
  const inputs = tr.querySelectorAll('.alt-name, .pay-s1, .pay-s2');
  inputs.forEach(inp => inp.addEventListener('input', debounceCompute));
}

function buildInitialTable(){
  const altText = document.getElementById('alt_names').value.trim();
  const altLines = altText.split('\n').map(s=>s.trim()).filter(s=>s.length>0);
  // default payoffs if missing
  const defaults = [[8,7],[14,5],[20,-9]];
  let html = '<table id="payTable" class="table table-sm table-bordered"><thead><tr><th>Alternativa</th><th>' + document.getElementById('state1_name').value + '</th><th>' + document.getElementById('state2_name').value + '</th><th></th></tr></thead><tbody></tbody></table>';
  document.getElementById('payTableContainer').innerHTML = html;
  altLines.forEach((name,i)=>{
    const p = defaults[i]||[0,0];
    addAltRow(name, p[0], p[1]);
  });
  // attach listeners to existing table inputs (for rows added by defaults)
  attachTableListeners();
}

function attachTableListeners(){
  const tbl = document.getElementById('payTable');
  if(!tbl) return;
  tbl.querySelectorAll('.alt-name, .pay-s1, .pay-s2').forEach(inp => {
    // avoid duplicate listeners by removing and re-adding
    inp.removeEventListener('input', debounceCompute);
    inp.addEventListener('input', debounceCompute);
  });
  tbl.querySelectorAll('.rm-row').forEach(btn => {
    btn.removeEventListener('click', ()=>{});
    btn.addEventListener('click', ()=>{ debounceCompute(); });
  });
}

// build table on load
buildInitialTable();
// rebuild table when alt names or state names change
document.getElementById('alt_names').addEventListener('change', ()=>{ buildInitialTable(); computeAndRender(); });
document.getElementById('state1_name').addEventListener('change', ()=>{ buildInitialTable(); computeAndRender(); });
document.getElementById('state2_name').addEventListener('change', ()=>{ buildInitialTable(); computeAndRender(); });

// initial compute
computeAndRender();

// Attach download buttons to each main tab pane so user can export any section
function attachSectionDownloadButtons(){
  const panes = [
    {id:'tab-vars-pane', title:'Variables'},
    {id:'tab-tables-pane', title:'Tablas'},
    {id:'tab-tree-pane', title:'Arbol'},
    {id:'tab-charts-pane', title:'Graficas'},
    {id:'tab-summary-pane', title:'Resumen'},
    {id:'tab-queueing-pane', title:'Lineas_Espera'},
    {id:'tab-game-pane', title:'Teoria_Juegos'}
  ];
  panes.forEach((p, idx)=>{
    const pane = document.getElementById(p.id);
    if(!pane) return;
    // avoid duplicate button
    if(pane.querySelector('.download-section-btn')) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'd-flex justify-content-end mb-2';
    const btn = document.createElement('button');
    btn.className = 'btn btn-sm btn-outline-primary download-section-btn';
    btn.textContent = 'Descargar PDF';
    btn.title = `Descargar sección: ${p.title}`;
    wrapper.appendChild(btn);
    // insert at top of pane
    pane.insertBefore(wrapper, pane.firstChild);
    btn.addEventListener('click', ()=>{
      const nodeToExport = (p.id==='tab-summary-pane') ? pane.querySelector('.report') || pane : pane;
      if(!nodeToExport){ alert('No hay contenido para exportar en esta sección.'); return; }
      if(typeof html2pdf === 'undefined'){ alert('html2pdf no está disponible.'); return; }
      const filename = `seccion_${idx+1}_${p.title.replace(/\s+/g,'_')}.pdf`;
      const opt = { margin:0.5, filename, image:{type:'jpeg',quality:0.98}, html2canvas:{scale:2,useCORS:true}, jsPDF:{unit:'in', format:'a4', orientation:'portrait'} };
      html2pdf().set(opt).from(nodeToExport).save();
    });
  });
}

// call it once now (panes are present in DOM)
attachSectionDownloadButtons();

// ============================================================
// MODULE 6: LÍNEAS DE ESPERA (Queueing Theory)
// ============================================================

let lastQueueingData = null;

async function computeQueueing() {
  const payload = {
    lam:           parseFloat(document.getElementById('q_lam').value)       || 10,
    mu_mm1_actual: parseFloat(document.getElementById('q_mu_actual').value) || 12,
    mu_mm1_mejor:  parseFloat(document.getElementById('q_mu_mejor').value)  || 18,
    mu_mm2:        parseFloat(document.getElementById('q_mu_mm2').value)    || 12,
  };
  const res  = await fetch('/compute_queueing', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await res.json();
  lastQueueingData = data;
  renderQueueingResults(data);
}

function renderQueueingResults(data) {
  const area = document.getElementById('queueingResultsArea');
  if (!area) return;

  const metrics = [
    { key:'rho', label:'ρ (Utilización)',           fmt: v => v.toFixed(3) },
    { key:'P0',  label:'P₀ (Prob. sistema vacío)',  fmt: v => v.toFixed(3) },
    { key:'L',   label:'L (Clientes en sistema)',    fmt: v => v.toFixed(4) },
    { key:'Lq',  label:'Lq (Clientes en cola)',      fmt: v => v.toFixed(4) },
    { key:'W',   label:'W (Tiempo en sistema, h)',   fmt: v => v.toFixed(4) },
    { key:'Wq',  label:'Wq (Tiempo en cola, h)',     fmt: v => v.toFixed(4) },
  ];
  const best = data.best || {};

  let html = '<table class="table table-bordered table-sm">';
  html += '<thead class="table-dark"><tr><th>Indicador</th>';
  data.scenarios.forEach(s => { html += `<th>${escapeHtml(s.label)}</th>`; });
  html += '</tr></thead><tbody>';

  metrics.forEach(m => {
    html += `<tr><td><strong>${m.label}</strong></td>`;
    data.scenarios.forEach((s, idx) => {
      if (!s.valid || s[m.key] === null) {
        html += '<td class="text-danger fw-bold">Inestable</td>';
      } else {
        const isBest = best[m.key] === idx;
        const cls    = isBest ? ' class="best-ev"' : '';
        html += `<td${cls}>${m.fmt(s[m.key])}${isBest ? ' ★' : ''}</td>`;
      }
    });
    html += '</tr>';
  });
  html += '</tbody></table>';

  data.scenarios.forEach(s => {
    if (!s.valid) {
      html += `<div class="alert alert-danger py-1 mb-1"><strong>${escapeHtml(s.label)}:</strong> ${escapeHtml(s.error)}</div>`;
    }
  });

  if (data.conclusion) {
    html += `<div class="alert alert-info mt-2"><strong>Conclusión:</strong> ${escapeHtml(data.conclusion)}</div>`;
  }

  area.innerHTML = html;
}

document.getElementById('queueingComputeBtn').addEventListener('click', computeQueueing);
document.getElementById('nav-queueing').addEventListener('shown.bs.tab', () => {
  if (!lastQueueingData) computeQueueing();
  else renderQueueingResults(lastQueueingData);
});

// ============================================================
// MODULE 7: TEORÍA DE JUEGOS (Game Theory)
// ============================================================

let lastGameData   = null;
let gameMatrix     = [[10,30,25,15],[5,40,10,30],[15,25,5,10],[20,20,15,40]];
let gameRowLabels  = ['E1','E2','E3','E4'];
let gameColLabels  = ['U1','U2','U3','U4'];

function buildGameMatrix() {
  const container = document.getElementById('gameMatrixContainer');
  if (!container) return;

  let html = '<table id="gameTable" class="table table-bordered table-sm align-middle">';
  html += '<thead class="table-dark"><tr><th></th>';
  gameColLabels.forEach((cl, j) => {
    html += `<th><input class="form-control form-control-sm game-col-label" data-col="${j}" value="${escapeHtml(cl)}" style="width:72px;display:inline-block">` +
            `<button class="btn btn-sm btn-outline-danger ms-1 rm-col" data-col="${j}" title="Eliminar columna">✕</button></th>`;
  });
  html += '</tr></thead><tbody>';

  gameMatrix.forEach((row, i) => {
    html += '<tr>';
    html += `<td><input class="form-control form-control-sm game-row-label" data-row="${i}" value="${escapeHtml(gameRowLabels[i])}" style="width:56px;display:inline-block">` +
            `<button class="btn btn-sm btn-outline-danger ms-1 rm-row" data-row="${i}" title="Eliminar fila">✕</button></td>`;
    row.forEach((cell, j) => {
      html += `<td><input type="number" class="form-control form-control-sm game-cell" data-row="${i}" data-col="${j}" value="${cell}" style="width:68px"></td>`;
    });
    html += '</tr>';
  });

  html += '</tbody></table>';
  container.innerHTML = html;

  container.querySelectorAll('.game-col-label').forEach(inp => {
    inp.addEventListener('change', e => { gameColLabels[+e.target.dataset.col] = e.target.value; });
  });
  container.querySelectorAll('.game-row-label').forEach(inp => {
    inp.addEventListener('change', e => { gameRowLabels[+e.target.dataset.row] = e.target.value; });
  });
  container.querySelectorAll('.game-cell').forEach(inp => {
    inp.addEventListener('change', e => { gameMatrix[+e.target.dataset.row][+e.target.dataset.col] = parseFloat(e.target.value) || 0; });
  });
  container.querySelectorAll('.rm-col').forEach(btn => {
    btn.addEventListener('click', e => {
      const j = +e.target.dataset.col;
      gameColLabels.splice(j, 1);
      gameMatrix.forEach(r => r.splice(j, 1));
      buildGameMatrix();
    });
  });
  container.querySelectorAll('.rm-row').forEach(btn => {
    btn.addEventListener('click', e => {
      const i = +e.target.dataset.row;
      gameRowLabels.splice(i, 1);
      gameMatrix.splice(i, 1);
      buildGameMatrix();
    });
  });
}

function addGameRow() {
  gameRowLabels.push(`E${gameMatrix.length + 1}`);
  gameMatrix.push(Array(gameColLabels.length).fill(0));
  buildGameMatrix();
}

function addGameCol() {
  gameColLabels.push(`U${gameColLabels.length + 1}`);
  gameMatrix.forEach(r => r.push(0));
  buildGameMatrix();
}

function syncGameStateFromDOM() {
  document.querySelectorAll('.game-cell').forEach(inp => {
    gameMatrix[+inp.dataset.row][+inp.dataset.col] = parseFloat(inp.value) || 0;
  });
  document.querySelectorAll('.game-col-label').forEach(inp => {
    gameColLabels[+inp.dataset.col] = inp.value;
  });
  document.querySelectorAll('.game-row-label').forEach(inp => {
    gameRowLabels[+inp.dataset.row] = inp.value;
  });
}

async function computeGame() {
  syncGameStateFromDOM();
  const payload = {matrix: gameMatrix, row_labels: gameRowLabels, col_labels: gameColLabels};
  const res  = await fetch('/compute_game_theory', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await res.json();
  lastGameData = data;
  renderGameResults(data);
}

function renderGameResults(data) {
  const area = document.getElementById('gameResultsArea');
  if (!area) return;

  const remainingRows = new Set(data.remaining_rows);
  const remainingCols = new Set(data.remaining_cols);

  // Texto introductorio
  let html = `<div class="alert alert-secondary mb-3">
    
  </div>`;

  // 1. Original matrix with strikethrough on eliminated strategies
  html += '<h6 class="mt-2">Matriz Original de Pagos</h6>';
  html += '<table class="table table-bordered table-sm"><thead class="table-secondary"><tr><th></th>';
  data.col_labels.forEach((cl, j) => {
    const elim = !remainingCols.has(j);
    html += `<th${elim ? ' class="gt-eliminated"' : ''}>${escapeHtml(cl)}</th>`;
  });
  html += '</tr></thead><tbody>';
  data.original_matrix.forEach((row, i) => {
    const rowElim = !remainingRows.has(i);
    html += `<tr>`;
    html += `<td${rowElim ? ' class="gt-eliminated"' : ''}><strong>${escapeHtml(data.row_labels[i])}</strong></td>`;
    row.forEach((cell, j) => {
      const colElim = !remainingCols.has(j);
      html += `<td${(rowElim || colElim) ? ' class="gt-eliminated"' : ''}>${cell}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';

  // 3. Reduced matrix
  const rRows = data.remaining_rows.map(i => data.row_labels[i]);
  const rCols = data.remaining_cols.map(j => data.col_labels[j]);
  html += '<h6>Matriz Reducida</h6>';
  html += '<table class="table table-bordered table-sm table-success"><thead><tr><th></th>';
  rCols.forEach(cl => { html += `<th>${escapeHtml(cl)}</th>`; });
  html += '</tr></thead><tbody>';
  data.reduced_matrix.forEach((row, i) => {
    html += `<tr><td><strong>${escapeHtml(rRows[i])}</strong></td>`;
    row.forEach(cell => { html += `<td>${cell}</td>`; });
    html += '</tr>';
  });
  html += '</tbody></table>';

  // 4. Mixed strategy solution
  const ms = data.mixed_strategy;
  if (ms && ms.valid) {
    html += '<h6>Estrategia Mixta Óptima</h6>';
    html += '<table class="table table-sm table-bordered"><tbody>';
    html += `<tr class="best-ev"><td colspan="2"><strong>Valor del juego V = ${ms.value.toFixed(4)} M COP</strong></td></tr>`;
    html += `<tr><td>JW — ${escapeHtml(ms.label_row0 || rRows[0])}</td><td>p = ${ms.p_row0.toFixed(4)}</td></tr>`;
    if (ms.label_row1) {
      html += `<tr><td>JW — ${escapeHtml(ms.label_row1)}</td><td>p = ${ms.p_row1.toFixed(4)}</td></tr>`;
    }
    html += `<tr><td>Sindicato — ${escapeHtml(ms.label_col0 || rCols[0])}</td><td>q = ${ms.q_col0.toFixed(4)}</td></tr>`;
    if (ms.label_col1) {
      html += `<tr><td>Sindicato — ${escapeHtml(ms.label_col1)}</td><td>q = ${ms.q_col1.toFixed(4)}</td></tr>`;
    }
    html += '</tbody></table>';
  } else if (ms && ms.error) {
    html += `<div class="alert alert-warning">${escapeHtml(ms.error)}</div>`;
  }

  if (data.note) {
    html += `<div class="alert alert-info py-1">${escapeHtml(data.note)}</div>`;
  }

  // Chart goes above the conclusion
  html += '<div id="gameDomChart" style="height:360px;margin:16px 0 8px;"></div>';

  if (data.conclusion) {
    html += `<div class="alert alert-success mt-2"><strong>Conclusión:</strong> ${escapeHtml(data.conclusion)}</div>`;
  }

  area.innerHTML = html;
  renderDominanceChart(data);
}

function renderDominanceChart(data) {
  const el = document.getElementById('gameDomChart');
  if (!el || !data.original_matrix) return;
  if (!data.mixed_strategy || !data.mixed_strategy.valid) return;
  if (data.remaining_rows.length < 2 || data.remaining_cols.length < 2) return;

  const ms  = data.mixed_strategy;
  const rc  = data.remaining_cols;    // e.g. [U1_idx, U3_idx]
  const rr  = data.remaining_rows;    // e.g. [E1_idx, E4_idx]
  const mat = data.original_matrix;
  const CL  = data.col_labels;
  const RL  = data.row_labels;
  const xs  = Array.from({length: 101}, (_, k) => k / 100);

  // ── BLUE LINES: Sindicato's columns as function of p = P(JW plays rr[1]) ──
  // f(p) = val_at_rr0*(1-p) + val_at_rr1*p
  const bA0 = mat[rr[0]][rc[0]], bA1 = mat[rr[1]][rc[0]];  // col rc[0]: U1: 10→20
  const bB0 = mat[rr[0]][rc[1]], bB1 = mat[rr[1]][rc[1]];  // col rc[1]: U3: 25→15
  const blueA_ys = xs.map(p => bA0*(1-p) + bA1*p);
  const blueB_ys = xs.map(p => bB0*(1-p) + bB1*p);

  // ── OTHER LINES: JW's rows as function of q = P(Sindicato plays rc[1]) ──
  // g(q) = val_at_rc0*(1-q) + val_at_rc1*q
  const oA0 = mat[rr[0]][rc[0]], oA1 = mat[rr[0]][rc[1]];  // row rr[0]: E1: 10→25
  const oB0 = mat[rr[1]][rc[0]], oB1 = mat[rr[1]][rc[1]];  // row rr[1]: E4: 20→15
  const otherA_ys = xs.map(q => oA0*(1-q) + oA1*q);
  const otherB_ys = xs.map(q => oB0*(1-q) + oB1*q);

  // ── Intersection of blue lines: p* where bA(p) = bB(p) ──
  const pDenom = (bA1 - bA0) - (bB1 - bB0);
  const p_star = Math.abs(pDenom) > 1e-9 ? (bB0 - bA0) / pDenom : null;
  const V_blue = p_star !== null ? bA0*(1-p_star) + bA1*p_star : null;

  // ── Intersection of other lines: q* where oA(q) = oB(q) ──
  const qDenom = (oA1 - oA0) - (oB1 - oB0);
  const q_star = Math.abs(qDenom) > 1e-9 ? (oB0 - oA0) / qDenom : null;
  const V_other = q_star !== null ? oA0*(1-q_star) + oA1*q_star : null;

  const traces = [
    // Blue: col rc[1] (U3): 25→15
    {x:xs, y:blueB_ys, mode:'lines', name:`${CL[rc[1]]} (Sindicato)`,
     line:{color:'#1d4ed8', width:2.5},
     hovertemplate:`${CL[rc[1]]}: %{y:.1f}<extra></extra>`},
    // Blue: col rc[0] (U1): 10→20
    {x:xs, y:blueA_ys, mode:'lines', name:`${CL[rc[0]]} (Sindicato)`,
     line:{color:'#60a5fa', width:2.5},
     hovertemplate:`${CL[rc[0]]}: %{y:.1f}<extra></extra>`},
    // Other: row rr[1] (E4): 20→15
    {x:xs, y:otherB_ys, mode:'lines', name:`${RL[rr[1]]} (JW)`,
     line:{color:'#7c3aed', width:2.5},
     hovertemplate:`${RL[rr[1]]}: %{y:.1f}<extra></extra>`},
    // Other: row rr[0] (E1): 10→25
    {x:xs, y:otherA_ys, mode:'lines', name:`${RL[rr[0]]} (JW)`,
     line:{color:'#c026d3', width:2.5},
     hovertemplate:`${RL[rr[0]]}: %{y:.1f}<extra></extra>`},
  ];

  // Intersection marker traces
  const mkr = (x, y, label, color) => ({
    x:[x], y:[y], mode:'markers', showlegend:false,
    marker:{size:11, color, line:{color:'#fff', width:2}},
    hovertemplate:`${label}<extra></extra>`,
  });
  if (p_star !== null && p_star >= 0 && p_star <= 1)
    traces.push(mkr(p_star, V_blue, `p*=${p_star.toFixed(2)}, V=${V_blue.toFixed(1)}`, '#1d4ed8'));
  if (q_star !== null && q_star >= 0 && q_star <= 1)
    traces.push(mkr(q_star, V_other, `q*=${q_star.toFixed(2)}, V=${V_other.toFixed(1)}`, '#7c3aed'));

  // Shapes: vertical dashed at each intersection + horizontal at V
  const V = ms.value;
  const shapes = [
    {type:'line', xref:'paper', yref:'y', x0:0, x1:1, y0:V, y1:V,
     line:{color:'#dc2626', dash:'dot', width:1}},
  ];
  if (p_star !== null && p_star >= 0 && p_star <= 1)
    shapes.push({type:'line', xref:'x', yref:'paper', x0:p_star, x1:p_star, y0:0, y1:1,
      line:{color:'#1d4ed8', dash:'dash', width:1}});
  if (q_star !== null && q_star >= 0 && q_star <= 1)
    shapes.push({type:'line', xref:'x', yref:'paper', x0:q_star, x1:q_star, y0:0, y1:1,
      line:{color:'#7c3aed', dash:'dash', width:1}});

  // Right-side value labels at x=1 (paper coords = 1, data y = terminal value)
  const annotations = [];
  const rightVals = [
    {y: bB1, color:'#1d4ed8'}, // U3 at p=1
    {y: bA1, color:'#60a5fa'}, // U1 at p=1
    {y: oB1, color:'#7c3aed'}, // E4 at q=1
    {y: oA1, color:'#c026d3'}, // E1 at q=1
  ];
  rightVals.forEach(({y, color}) => {
    annotations.push({
      x:1.01, y, xref:'paper', yref:'y', xanchor:'left', yanchor:'middle',
      text:`${y}`, showarrow:false, font:{color, size:11, weight:'bold'},
    });
  });
  // V label on left
  annotations.push({
    x:0, y:V, xref:'paper', yref:'y', xanchor:'right', yanchor:'middle',
    text:`V=${V}`, showarrow:false, font:{color:'#dc2626', size:10},
    bgcolor:'rgba(255,255,255,0.8)',
  });
  // p* and q* labels below x-axis
  if (p_star !== null && p_star >= 0 && p_star <= 1)
    annotations.push({x:p_star, y:0, xref:'x', yref:'paper', xanchor:'center', yanchor:'top',
      text:`p*=${p_star.toFixed(2)}`, showarrow:false, font:{color:'#1d4ed8', size:10}});
  if (q_star !== null && q_star >= 0 && q_star <= 1)
    annotations.push({x:q_star, y:0, xref:'x', yref:'paper', xanchor:'center', yanchor:'top',
      text:`q*=${q_star.toFixed(2)}`, showarrow:false, font:{color:'#7c3aed', size:10}});

  Plotly.newPlot(el, traces, {
    title: {text:'GRÁFICA DOMINACIÓN — Estrategias Mixtas Óptimas', font:{size:13, weight:'bold'}},
    xaxis: {
      title:{text:`p = P(JW juega ${RL[rr[1]]})  |  q = P(Sindicato juega ${CL[rc[1]]})`, font:{size:10}},
      range:[0,1], tickvals:[0,0.25,0.5,0.75,1], gridcolor:'#e5e7eb',
    },
    yaxis: {title:{text:'Pago esperado (M COP)', font:{size:10}}, gridcolor:'#e5e7eb'},
    legend:{orientation:'h', x:0, y:-0.18, font:{size:10}},
    margin:{t:50, b:80, l:60, r:55},
    shapes, annotations,
    height:360,
    paper_bgcolor:'#fff', plot_bgcolor:'#f9fafb',
    hovermode:'x unified',
  }, {responsive:true, displayModeBar:false});
}

document.getElementById('gameComputeBtn').addEventListener('click', computeGame);
document.getElementById('gameAddRowBtn').addEventListener('click', addGameRow);
document.getElementById('gameAddColBtn').addEventListener('click', addGameCol);
document.getElementById('nav-game').addEventListener('shown.bs.tab', () => {
  if (!lastGameData) computeGame();
  else renderGameResults(lastGameData);
});

buildGameMatrix();
