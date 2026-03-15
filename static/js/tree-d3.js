// D3 interactive decision tree renderer
// - horizontal layout
// - zoom & pan
// - draggable nodes (manual re-layout)
// - HTML tooltip showing formula (uses node.data.formula when present)

// Render a two-panel decision tree similar to the reference image
function renderTreeD3(treeData, containerId){
  const container = document.getElementById(containerId);
  if(!container || !treeData) return;
  container.innerHTML = '';

  // tooltip element
  const tooltip = document.createElement('div');
  tooltip.className = 'd3-tooltip';
  Object.assign(tooltip.style, {position:'absolute', pointerEvents:'none', background:'#fff', border:'1px solid #cfcfcf', padding:'8px', borderRadius:'6px', boxShadow:'0 4px 12px rgba(0,0,0,0.08)', display:'none', zIndex:1000, fontSize:'13px'});
  container.appendChild(tooltip);

  const width = Math.max(1000, container.clientWidth || 1000);
  const height = Math.max(520, container.clientHeight || 520);
  const svg = d3.select(container).append('svg').attr('width','100%').attr('height',height).attr('viewBox',[0,0,width,height]);
  const g = svg.append('g').attr('class','root-g');
  svg.call(d3.zoom().scaleExtent([0.5,2]).on('zoom', (event)=> g.attr('transform', event.transform)));

  // two columns: left = study subtree, right = no-study subtree
  const padding = 40;
  const midX = 260; // left column width
  const gap = 60; // gap between columns
  const rightX = midX + gap + 420; // start of right column (EV boxes area)

  // helper to layout a subtree vertically
  function layoutSubtree(node, xBase, xSpacing){
    const root = d3.hierarchy(node);
    const leaves = root.leaves().length || 1;
    const h = Math.max(220, leaves * 80);
    const tree = d3.tree().size([h, xSpacing]);
    tree(root);
    // translate coordinates so leftmost top is at xBase
    root.each(d=> { d.x = d.x + padding; d.y = d.y + xBase; });
    return root;
  }

  // find study and no-study branches
  const children = treeData.children || [];
  let noStudy = null, study = null;
  for(const c of children){ if(c.id && c.id.toLowerCase().includes('no')) noStudy = c; if(c.id && c.id.toLowerCase().includes('study')) study = c; }
  if(!noStudy) noStudy = children[0];
  if(!study) study = children[1] || children[0];

  // layout both subtrees
  const leftRoot = layoutSubtree(study, 20, midX - 80);
  const rightRoot = layoutSubtree(noStudy, rightX, 240);

  // combine nodes and links for drawing
  const leftNodes = leftRoot.descendants();
  const leftLinks = leftRoot.links();
  const rightNodes = rightRoot.descendants();
  const rightLinks = rightRoot.links();

  // dashed vertical separator
  svg.append('line').attr('x1', rightX-40).attr('x2', rightX-40).attr('y1', 0).attr('y2', height).attr('stroke','#ddd').attr('stroke-dasharray','6 6');

  // draw links with colored strokes (green for favorable, purple for unfavorable)
  function drawLinks(linkData){
    return g.selectAll(null).data(linkData).enter().append('path')
      .attr('d', d=> `M${d.source.y},${d.source.x} C${d.source.y+40},${d.source.x} ${d.target.y-40},${d.target.x} ${d.target.y},${d.target.x}`)
      .attr('fill','none')
      .attr('stroke', d=> {
        const lab = (d.target && d.target.data && d.target.data.label||'').toLowerCase();
        if(lab.includes('fav')||lab.includes('favorable')) return '#00C9A7';
        if(lab.includes('desf')||lab.includes('unf')) return '#9B59F5';
        return '#7f8c8d';
      })
      .attr('stroke-width',2)
      .attr('marker-end','url(#arrow)');
  }

  // arrow marker
  svg.append('defs').append('marker').attr('id','arrow').attr('markerWidth',8).attr('markerHeight',8).attr('refX',8).attr('refY',4).attr('orient','auto')
    .append('path').attr('d','M0,0 L8,4 L0,8 Z').attr('fill','#667');

  drawLinks(leftLinks);
  drawLinks(rightLinks);

  // draw link labels (probabilities)
  function drawLinkLabels(linkData){
    g.selectAll(null).data(linkData).enter().append('text')
      .attr('x', d=> (d.source.y + d.target.y)/2)
      .attr('y', d=> (d.source.x + d.target.x)/2 - 8)
      .attr('text-anchor','middle')
      .attr('font-size',11)
      .attr('fill','#666')
      .text(d => (d.target.data && d.target.data.prob!==undefined) ? `p=${Number(d.target.data.prob).toFixed(3)}` : '');
  }
  drawLinkLabels(leftLinks);
  drawLinkLabels(rightLinks);

  // node renderer (only draws node shapes and labels)
  function renderNodes(nodes){
    const ng = g.selectAll(null).data(nodes).enter().append('g').attr('transform', d=> `translate(${d.y},${d.x})`).attr('class','node-g');
    ng.each(function(d){
      const el = d3.select(this);
      if(d.data.type === 'decision'){
        el.append('rect').attr('x',-26).attr('y',-26).attr('width',52).attr('height',52).attr('rx',6).attr('fill','#223');
        el.append('text').attr('text-anchor','middle').attr('dy',6).attr('fill','#fff').attr('font-weight','700').text(d.data.label||'');
      } else if(d.data.type === 'chance'){
        el.append('circle').attr('r',18).attr('fill','#ffffff').attr('stroke','#223').attr('stroke-width',2);
        el.append('text').attr('text-anchor','middle').attr('dy',4).attr('fill','#223').attr('font-weight','600').text(d.data.label||'');
      } else {
        // outcome boxes smaller
        el.append('rect').attr('x',-48).attr('y',-14).attr('width',96).attr('height',28).attr('rx',6).attr('fill','#fff3cd').attr('stroke','#e0c080');
        el.append('text').attr('text-anchor','middle').attr('dy',3).attr('fill','#333').text(d.data.label||'');
      }

      // EV small badge to the right for outcomes
      // outcome boxes handled later to avoid overlaps

      // draggable
      el.call(d3.drag().on('drag', function(event, nd){ nd.x += event.dy; nd.y += event.dx; d3.select(this).attr('transform', `translate(${nd.y},${nd.x})`); g.selectAll('path.link').remove(); g.selectAll('text.link-label').remove(); drawLinks(leftLinks); drawLinks(rightLinks); drawLinkLabels(leftLinks); drawLinkLabels(rightLinks); }))
        .on('mouseover', function(event, nd){
          tooltip.style.display = 'block';
          tooltip.innerHTML = `<b>${nd.data.label||''}</b><div style="white-space:pre-wrap;margin-top:6px">${nd.data.formula|| (nd.data.payoffs? ('Payoffs: ' + (nd.data.states? nd.data.states.join(', '):'') + ' => ' + nd.data.payoffs.join(', ')) : '')}</div>`;
        }).on('mousemove', function(event){ const r = container.getBoundingClientRect(); tooltip.style.left = (event.clientX - r.left + 12) + 'px'; tooltip.style.top = (event.clientY - r.top + 12) + 'px'; })
        .on('mouseout', function(){ tooltip.style.display = 'none'; });
    });
  }

  renderNodes(leftNodes);
  renderNodes(rightNodes);

  // Place EV boxes in columns and avoid overlaps by sorting and compacting vertically
  function placeBoxesForNodes(nodes, bx){
    const outcomes = nodes.filter(d => d.data && d.data.type === 'outcome' && d.data.ev !== undefined);
    if(outcomes.length === 0) return;
    const boxW = 160, boxH = 28, gap = 6;
    // desired top positions
    const items = outcomes.map(d => ({d, desiredTop: d.x - boxH/2}));
    // sort by desiredTop to place from top to bottom
    items.sort((a,b)=> a.desiredTop - b.desiredTop);
    const placed = [];
    for(const it of items){
      let top = it.desiredTop;
      // if overlaps previous placed, move below
      for(let i=0;i<placed.length;i++){
        const r = placed[i];
        if(!(top + boxH + 0.5 < r.top || top > r.top + boxH + 0.5)){
          top = r.top + boxH + gap;
        }
      }
      placed.push({top});
      // draw box and label
      g.append('rect').attr('x',bx).attr('y',top).attr('width',boxW).attr('height',boxH).attr('rx',6).attr('fill','#fff9e6').attr('stroke','#d9b86b');
      g.append('text').attr('x',bx+8).attr('y',top+18).attr('fill','#333').attr('font-weight','700').text(`EV(${it.d.data.label}) = ${Number(it.d.data.ev).toFixed(2)}`);
    }
  }

  const boxesXLeft = 20 + (midX - 80) + 120; // xBase + xSpacing + offset
  const boxesXRight = rightX + 240 + 120;
  placeBoxesForNodes(leftNodes, boxesXLeft);
  placeBoxesForNodes(rightNodes, boxesXRight);

}

function renderTreeD3Simple(data, containerId){ if(data && data.tree) renderTreeD3(data.tree, containerId); }
