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
    {id:'tab-summary-pane', title:'Resumen'}
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
