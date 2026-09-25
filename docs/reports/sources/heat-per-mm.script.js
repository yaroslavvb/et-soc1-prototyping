/* Heat per millimetre. D is report.json (tools/ettelem/build_wire_report.py); every number on the page is computed
   from it. Charts use the shared toolkit CK (docs/reports/sources/chartkit.js): responsive frames, tooltips that work by
   pointer, touch and keyboard, HTML legends, template colour tokens only. */
const W_=D.wire, IN=D.inputs, HD=D.headline;
const SET=(W_.model.v2&&W_.model.v2.board&&W_.model.v2.board.toggle_fj_per_bit_transition_hop)?'v2':'v1';
const HB=HD[`${SET}/board`], HN=HD[`${SET}/noc_rail`], UB=HD['uncontended/board'], UN=HD['uncontended/noc_rail'];
const f0=v=>v.toFixed(0),f1=v=>v.toFixed(1),f2=v=>v.toFixed(2),f3=v=>v.toFixed(3);
const bar=(p,fn)=>p?`<b>${fn(p.mean)}</b> <span class="small">[${fn(p.lo)}–${fn(p.hi)}]</span>`:'—';
const cards=(p,fn)=>p&&p.per_card?Object.keys(p.per_card).sort().map(h=>`a${h.slice(-1)} ${fn(typeof p.per_card[h]==='number'?p.per_card[h]:p.per_card[h].mean)}`).join(' · '):'';
function setText(id,html){const e=document.getElementById(id);if(e)e.innerHTML=html;}
const NK='noc_pj_per_byte', BK='pj_per_byte';
const METERS=[[NK,'mesh rail'],[BK,'board power']];   // every meter toggle opens on the mesh rail, the page's primary meter
const meterName=k=>k===NK?'mesh rail':'board power', srcOf=k=>k===NK?'noc_rail':'board';
const HOP=IN.hop_mm.value;
const sty=(n,o)=>{for(const k in o)n.style[k]=o[k];return n;};
const halo=n=>sty(n,{paintOrder:'stroke',stroke:'var(--page)',strokeWidth:'3px',strokeLinejoin:'round'});   // keeps a label legible where a line crosses it
function whisker(g,x,y1,y2,col){[[x,x,y1,y2],[x-3,x+3,y1,y1],[x-3,x+3,y2,y2]].forEach(q=>sty(CK.el('line',{x1:q[0],x2:q[1],y1:q[2],y2:q[3]},g),{stroke:col,strokeWidth:'1.4px'}));}
const meanOf=v=>v.reduce((a,b)=>a+b,0)/v.length;
/* per-pattern slopes from a model's per-pass points, pooled over passes and cards (pJ per byte per hop) */
function pooled(set,src){const m=W_.model[set]&&W_.model[set][src], acc={}; if(!m||!m.per_pass)return acc;
 for(const h in m.per_pass)m.per_pass[h].forEach(f=>f.points.forEach(q=>{(acc[q.pattern]=acc[q.pattern]||{t:q.toggle,o:q.ones,v:[]}).v.push(q.slope);}));
 for(const k in acc){const a=acc[k];a.mean=meanOf(a.v);a.lo=Math.min(...a.v);a.hi=Math.max(...a.v);a.n=a.v.length;}
 return acc;}
/* the 16-128 B blocks (first run, d = 1, 3, 6) against the no-transition prediction compared like for like: the first
   run's all-zeros and all-ones averaged, (s(P = 0) + s(P = 1))/2, with every slope over the same d = 1, 3, 6. Pooled
   and per card; `below` is the blocks' shortfall as a fraction of the prediction (pJ per byte per hop). */
function blocksLFL(k){
 const ds=[1,3,6], C=W_.configs, ok=pre=>ds.every(d=>C[pre+d]&&C[pre+d][k]);
 if(![16,32,64,128].every(n=>ok(`walt/n${n}/hop`))||!ok('wbern/p0/hop')||!ok('wbern/p1/hop'))return null;
 const lsq=ys=>{const mx=meanOf(ds),my=meanOf(ys);let a=0,b=0;ds.forEach((x,i)=>{a+=(x-mx)*(ys[i]-my);b+=(x-mx)*(x-mx);});return a/b;};
 const sl=(pre,h)=>lsq(ds.map(d=>{const c=C[pre+d][k];return h?c.per_card[h].mean:c.mean;}));
 const one=h=>{const blk=meanOf([16,32,64,128].map(n=>sl(`walt/n${n}/hop`,h))), nt=(sl('wbern/p0/hop',h)+sl('wbern/p1/hop',h))/2;return {blk,nt,below:1-blk/nt};};
 const out=one(null); out.per_card={}; W_.hosts.forEach(h=>{out.per_card[h]=one(h);}); return out;}
/* de-collide end-of-line labels: keep at least `gap` px between them, inside [top, bottom] */
function spread(items,gap,top,bottom){items.sort((a,b)=>a.y-b.y);for(let i=1;i<items.length;i++)items[i].y=Math.max(items[i].y,items[i-1].y+gap);
 const over=items.length?items[items.length-1].y-bottom:0; if(over>0)items.forEach(it=>it.y-=over);
 for(let i=items.length-2;i>=0;i--)items[i].y=Math.min(items[i].y,items[i+1].y-gap); if(items.length&&items[0].y<top){const d=top-items[0].y;items.forEach(it=>it.y+=d);} return items;}

/* ---------- KPIs ---------- */
(function(){
 setText('k-hop',`${f2(HOP)} mm`);
 setText('k-noc',`${f1(UN.random_bit_data.mean)} + ${f1(UN.fixed_per_bit.mean)} fJ`);
 setText('k-noc-sub',`data-dependent + fixed, 0.485 V, fitted over 1–4 hops; loaded mesh ${f1(HN.random_bit_data.mean)} + ${f1(HN.fixed_per_bit.mean)} (the model, 1–6 hops)`);
 setText('k-one',`${f0(HN.per_one.mean)} vs ${f0(HN.per_transition.mean)} fJ`);
 const s09=D.scaled['0.9'];
 setText('k-09',`${f0(UN.random_bit_data.mean*s09)}–${f0(HN.random_bit_data.mean*s09)} fJ`);
})();

/* ---------- 2. the die and the mesh ---------- */
(function(){
 const dw=IN.die_w_mm.value, dh=IN.die_h_mm.value, px=IN.pitch_x_mm.value, py=IN.pitch_y_mm.value, MS=IN.memshire_w_mm;
 CK.frame('mesh',{label:'The ET-SoC-1 die drawn to scale: 8 by 6 mesh stops',minW:300,maxW:640,
  height:W=>Math.round((W-24)/dw*dh+62),
  draw(f){
   const sc=(f.W-24)/dw, ox=12, oy=24, X=v=>ox+v*sc, Y=v=>oy+v*sc, svg=f.svg, tiles=[];
   sty(CK.el('rect',{x:X(0),y:Y(0),width:dw*sc,height:dh*sc,rx:3},svg),{fill:'none',stroke:'var(--ink-2)',strokeWidth:'1.5px'});
   const gx0=(dw-6*px)/2, gy0=(dh-6*py)/2, mw=gx0;   // drawn at six full tile periods (see the caption)
   for(let r=0;r<6;r++)for(let c=0;c<8;c++){
    const isMem=(c===0||c===7); if(isMem&&(r===0||r===5))continue;
    const x0=isMem?(c===0?0:dw-mw):gx0+(c-1)*px, w=isMem?mw:px, y0=gy0+r*py, top=(r===0&&(c===5||c===6));
    const fill=isMem?'var(--c4)':top?'var(--c5)':'var(--c1)', g=CK.el('g',{},svg);
    sty(CK.el('rect',{x:X(x0)+1,y:Y(y0)+1,width:w*sc-2,height:py*sc-2},g),{fill,fillOpacity:isMem||top?0.35:0.18,stroke:fill,strokeWidth:'1px'});
    sty(CK.el('circle',{cx:X(x0+w/2),cy:Y(y0+py/2),r:3.2},g),{fill:'var(--ink)'});
    CK.tip(f,g,isMem?`memory shire + LPDDR4x PHY strip, about ${f2(MS.range[0])}–${f2(MS.range[1])} mm wide on the die plot`:top?(c===5?'I/O or PCIe shire (the two sources disagree on the order)':'PCIe or I/O shire'):`minion shire tile, ${f2(px)} × ${f2(py)} mm (column ${c} of 8, row ${r+1} of 6)`);
    tiles.push(g);
   }
   const ln=(x1,x2,y1,y2)=>sty(CK.el('line',{x1,x2,y1,y2},svg),{stroke:'var(--ink-2)',strokeWidth:'1px'});
   for(let c=1;c<7;c++)for(let r=0;r<6;r++){const cx=X(gx0+(c-1)*px+px/2), cy=Y(gy0+r*py+py/2);
    if(c<6)ln(cx+3,X(gx0+c*px+px/2)-3,cy,cy); if(r<5)ln(cx,cx,cy+3,Y(gy0+(r+1)*py+py/2)-3);}
   for(let r=1;r<5;r++){const yy=Y(gy0+r*py+py/2); ln(X(mw/2)+3,X(gx0+px/2)-3,yy,yy); ln(X(dw-mw/2)-3,X(gx0+5*px+px/2)+3,yy,yy);}
   const yb=Y(dh)+16; sty(CK.el('line',{x1:X(gx0),x2:X(gx0+px),y1:yb,y2:yb},svg),{stroke:'var(--c2)',strokeWidth:'2px'});
   CK.txt(svg,X(gx0+px/2),yb+15,`one hop ≈ ${f2(HOP)} mm`,'lab-strong','middle');
   CK.txt(svg,X(dw/2),Y(0)-8,`≈ ${f1(dw)} × ${f1(dh)} mm, ${IN.die_mm2.value} mm²`,'lab','middle');
   CK.keynav(f,tiles);
  }});
 setText('meshcap',`Drawn to scale from the pitch measured on Esperanto's published die plot. 8 × 6 mesh stops: 34 minion shires (blue) — the 32 compute shires (1,024 minions) that the other reports count, plus the master shire, which runs the firmware, and a spare — the PCIe and I/O shires (pink, top row), and four memory shires with their LPDDR4x PHYs down each side (amber); the corners are empty. The 6 × 6 grid of the other reports is the inner six columns. Dots are mesh stops, lines the links between neighbours. Tiles are drawn at the ${f2(px)} mm period, so the grid looks slightly wider than the 86% its outlines span. Hover, tap or tab to a tile.`);
})();

/* ---------- 4. energy against distance ---------- */
(function(){
 const pre=SET==='v2'?'wu/p':'wbern/p', Ps=SET==='v2'?['0','0.25','0.5','0.75','1']:['0','0.1','0.25','0.5','0.75','0.9','1'];
 const C=W_.configs, ds=[0,1,2,3,4,6]; let key=NK;
 // density of ones is ordered: one hue, from a visible floor (P = 0) to full strength and past it towards the ink (P = 1)
 const col=p=>p<=0.5?`color-mix(in srgb, var(--c1) ${f0(45+110*p)}%, var(--surface))`:`color-mix(in srgb, var(--c1) ${f0(100-130*(p-0.5))}%, var(--ink))`;
 const frac={'0':'0','0.1':'0.1','0.25':'¼','0.5':'½','0.75':'¾','0.9':'0.9','1':'1'};
 CK.legend('dist-leg',Ps.map(p=>({key:p,label:`P = ${frac[p]}`,mark:'line',color:col(+p)})));
 const f=CK.frame('dist',{label:'Energy per payload byte against hop distance, one line per density of ones',height:W=>W<600?300:340,draw(f){
  const L=46,R=f.narrow?48:62,T=26,B=40;
  let mx=0; Ps.forEach(p=>ds.forEach(d=>{const c=C[`${pre}${p}/hop${d}`]; if(c&&c[key])mx=Math.max(mx,c[key].hi);})); mx*=1.06;
  const x=CK.lin(-0.2,6.15,L,f.W-R), y=CK.lin(0,mx,f.H-B,T);
  CK.axes(f,{x,y,L,R,T,B,xt:ds,xl:'hops to the scratchpad read (0 = the shire’s own)',yl:`${meterName(key)}: pJ per payload byte above idle`});
  const ends=[];
  Ps.forEach(p=>{const c0=col(+p), g=CK.el('g',{'data-series':p},f.svg), pts=[], nodes=[];
   ds.forEach(d=>{const c=C[`${pre}${p}/hop${d}`]; if(c&&c[key])pts.push([d,c[key].mean]);});
   if(pts.length>1)sty(CK.el('path',{d:CK.path(pts,x,y)},g),{fill:'none',stroke:c0,strokeWidth:'2px',strokeLinejoin:'round'});
   ds.forEach(d=>{const c=C[`${pre}${p}/hop${d}`]; if(!c||!c[key])return; const q=c[key], m=CK.el('g',{},g);
    whisker(m,x(d),y(q.hi),y(q.lo),c0); sty(CK.el('circle',{cx:x(d),cy:y(q.mean),r:4},m),{fill:c0,stroke:'var(--surface)',strokeWidth:'1.5px'});
    CK.tip(f,m,`<b>P(one) = ${p}</b>, ${d} hop${d===1?'':'s'}, ${meterName(key)}<br>${f2(q.mean)} pJ/B [${f2(q.lo)}–${f2(q.hi)}], n = ${q.n}<br>${c.participants} minions reading (${Math.round(c.participants/32)} shires), ${f0(c.gb_s)} GB/s`);
    nodes.push(m);});
   CK.keynav(f,nodes);
   if(pts.length)ends.push({y:y(pts[pts.length-1][1]),p,x:x(pts[pts.length-1][0])});});
  spread(ends,14,T,f.H-B).forEach(e=>CK.txt(f.svg,e.x+8,e.y+4,`P = ${frac[e.p]}`,'lab'));
 }});
 CK.seg('distbtn',{label:'Meter',options:METERS,value:key,onChange:v=>{key=v;f.redraw();}});
})();

/* ---------- 5. what a bit costs per hop: ones and differences ---------- */
(function(){
 let key=NK;
 const SETS=[['v1','var(--c1)','first run: one 512 B image'],['v2','var(--c2)','second run: lines unique']];
 CK.legend('model-leg',[{key:'v1',label:'first run: one 512 B image',mark:'dot',color:'var(--c1)'},{key:'v2',label:'second run: lines unique',mark:'dot',color:'var(--c2)'},
  {key:'frz',label:'second run: frozen line',mark:'box',color:'var(--c3)'},{key:'fit',label:'ones + differences (the fit)',mark:'line',color:'var(--ink)'},
  {key:'tog',label:'differences only (best fit)',mark:'dash',color:'var(--ref)'}]);
 const f=CK.frame('model',{label:'Cost of one hop against the density of ones, with the two-term fit and the best differences-only curve',height:W=>W<600?300:340,draw(f){
  const L=46,R=14,T=26,B=40, src=srcOf(key), pts=[];
  let mx=0;
  SETS.forEach(s=>{const acc=pooled(s[0],src); for(const k in acc){const a=acc[k]; pts.push(Object.assign({set:s,k},a)); mx=Math.max(mx,a.hi);}});
  mx*=1.1;
  const x=CK.lin(-0.04,1.04,L,f.W-R), y=CK.lin(0,mx,f.H-B,T);
  CK.axes(f,{x,y,L,R,T,B,xt:[0,0.25,0.5,0.75,1],xl:'density of ones in the data, P',yl:`${meterName(key)}: pJ per payload byte per hop (slope)`});
  const M=W_.model[SET][src], a=M.toggle_fj_per_bit_transition_hop.mean*8/1000, b=M.ones_fj_per_one_bit_hop.mean*8/1000, s0=M.s0_pj_per_byte_hop.mean;
  const curve=[],tog=[]; for(let p=0;p<=1.0001;p+=0.02)curve.push([p,s0+a*2*p*(1-p)+b*p]);
  // the best pure-difference model (no ones term), fitted to the same points: the fair test of "only differences cost"
  const pp=pts.filter(q=>q.set[0]===SET&&!q.k.startsWith('wfrz')); let sxx=0,sx=0,sy=0,sxy=0,n=0; pp.forEach(q=>{sxx+=q.t*q.t;sx+=q.t;sy+=q.mean;sxy+=q.t*q.mean;n++;});
  const aT=(n*sxy-sx*sy)/(n*sxx-sx*sx), bT=(sy-aT*sx)/n; for(let p=0;p<=1.0001;p+=0.02)tog.push([p,bT+aT*2*p*(1-p)]);
  sty(CK.el('path',{d:CK.path(tog,x,y)},f.svg),{fill:'none',stroke:'var(--ref)',strokeWidth:'1.5px',strokeDasharray:'5 4'});
  sty(CK.el('path',{d:CK.path(curve,x,y)},f.svg),{fill:'none',stroke:'var(--ink)',strokeWidth:'1.6px'});
  const groups={v1:[],v2:[],frz:[]};
  pts.forEach(q=>{const frz=q.k.startsWith('wfrz'), g=CK.el('g',{},f.svg), xx=x(q.o)+(q.set[0]==='v1'?-3:3), col=frz?'var(--c3)':q.set[1];
   whisker(g,xx,y(q.hi),y(q.lo),col);
   sty(frz?CK.el('rect',{x:xx-4.5,y:y(q.mean)-4.5,width:9,height:9},g):CK.el('circle',{cx:xx,cy:y(q.mean),r:4.5},g),{fill:col,stroke:'var(--surface)',strokeWidth:'1.5px'});
   CK.tip(f,g,`<b>${q.k.replace(/\/$/,'')}</b> (${frz?'second run: frozen line':q.set[2]})<br>ones ${f3(q.o)}, bits differing from the previous flit ${f3(q.t)}<br>${f3(q.mean)} pJ/B per hop [${f3(q.lo)}–${f3(q.hi)}], n = ${q.n}<br>the fit: ${f3(s0+a*q.t+b*q.o)}`);
   groups[frz?'frz':q.set[0]].push(g);});
  Object.values(groups).forEach(g=>CK.keynav(f,g.sort((p,q)=>p.getBBox().x-q.getBBox().x)));
 }});
 CK.seg('modelbtn',{label:'Meter',options:METERS,value:key,onChange:v=>{key=v;f.redraw();}});
})();

/* ---------- the model table ---------- */
(function(){
 const rows=[['<i>a</i>: per flit-to-flit difference','per_transition'],['<i>b</i>: per one carried','per_one'],['random bit, data part (½<i>a</i> + ½<i>b</i>)','random_bit_data'],['per bit, data-independent','fixed_per_bit']];
 const t=document.getElementById('modeltab'); if(!t)return;
 t.innerHTML='<thead><tr><th>At 0.485 V, 400 MHz; the model on the loaded mesh</th><th class="num">mesh rail, fJ per hop</th><th class="num">fJ per mm</th><th class="num">board power, fJ per hop</th><th class="num">fJ per mm</th></tr></thead><tbody>'+
  rows.map(r=>`<tr><td>${r[0]}</td><td class="num">${bar(HN.per_hop[r[1]],f0)}</td><td class="num">${bar(HN[r[1]],f1)}</td><td class="num">${bar(HB.per_hop[r[1]],f0)}</td><td class="num">${bar(HB[r[1]],f1)}</td></tr>`).join('')+
  `<tr><td colspan="5"><b>With every flow on its own links</b>, fitted over 1–4 hops (only random and zeros were run this way)</td></tr>`+
  // board power resolves the free-link total but not its split into a data and a fixed part: those cells say so (§10 has the numbers)
  `<tr><td>random bit, data part</td><td class="num">${bar(UN.per_hop.random_bit_data,f0)}</td><td class="num">${bar(UN.random_bit_data,f1)}</td><td class="num small">not resolved</td><td class="num small">not resolved</td></tr>`+
  `<tr><td>per bit, data-independent</td><td class="num">${bar(UN.per_hop.fixed_per_bit,f0)}</td><td class="num">${bar(UN.fixed_per_bit,f1)}</td><td class="num small">not resolved</td><td class="num small">not resolved</td></tr>`+
  `<tr><td><b>A random bit, everything, free links</b></td><td class="num">—</td><td class="num"><b>${f1(UN.random_bit_total.mean)}</b> <span class="small">[${f1(UN.random_bit_total.lo)}–${f1(UN.random_bit_total.hi)}]</span></td><td class="num">—</td><td class="num"><b>${f1(UB.random_bit_total.mean)}</b> <span class="small">[${f1(UB.random_bit_total.lo)}–${f1(UB.random_bit_total.hi)}]</span></td></tr>`+
  `<tr><td colspan="5"><b>On the loaded mesh</b> (all pairs, sections 4–5; the model fitted over 1–6 hops)</td></tr>`+
  `<tr><td><b>A random bit, everything, loaded mesh</b></td><td class="num">—</td><td class="num"><b>${f1(HN.random_bit_total.mean)}</b> <span class="small">[${f1(HN.random_bit_total.lo)}–${f1(HN.random_bit_total.hi)}]</span></td><td class="num">—</td><td class="num"><b>${f1(HB.random_bit_total.mean)}</b> <span class="small">[${f1(HB.random_bit_total.lo)}–${f1(HB.random_bit_total.hi)}]</span></td></tr>`+
  `<tr><td colspan="5" class="small">Fit per card and pass over ${SET==='v2'?'five bit densities and the frozen line':'seven bit densities'}, then pooled: bold is the mean, brackets the range over passes and cards, with the hop length’s range (${IN.hop_mm.range[0]}–${IN.hop_mm.range[1]} mm) folded into the per-mm bars. Residual of the fit: ${f3(HN.rms_pj_per_byte_hop)} pJ/B/hop on the mesh rail, ${f3(HB.rms_pj_per_byte_hop)} on board power. Over the same 1–4 hops as the free-link rows, the loaded mesh rail gives ${f0(W_.disjoint_flows.noc_pj_per_byte.wu.random_minus_zeros_fj_per_bit_hop.mean/HOP)} + ${f0(W_.disjoint_flows.noc_pj_per_byte.wu.zeros_fj_per_bit_hop.mean/HOP)} fJ/mm (section 6). On board power the free-link total is resolved on both cards but its split into a data part and a data-independent part is not (<a href="#limits">§10</a>).</td></tr></tbody>`;
 CK.stackTable(t);
})();

/* ---------- 5b. what any bit pattern would cost: the plane of the second run's model ---------- */
(function(){
 if(!(W_.model.v2&&W_.model.v2.noc_rail))return;
 let key=NK, P=0.5, t=0.5, preset='random', comp=null;
 const coef=k=>{const M=W_.model.v2[srcOf(k)];return {a:M.toggle_fj_per_bit_transition_hop.mean,b:M.ones_fj_per_one_bit_hop.mean,s0:M.s0_pj_per_byte_hop.mean*1000/8,s0pj:M.s0_pj_per_byte_hop.mean};};
 const E=(c,p,q)=>c.s0+c.a*q+c.b*p, tmax=p=>2*Math.min(p,1-p), r2=v=>Math.round(v*100)/100;
 function meas(k){   // measured cost per bit per hop (fJ), pooled over passes and cards
  const acc=pooled('v2',srcOf(k)), out={}, al=n=>W_.patterns[`alt:${n}`][k].slope, fj=v=>v*1000/8;
  for(const p in acc){const a=acc[p]; out[p]={P:a.o,t:a.t,mean:fj(a.mean),lo:fj(a.lo),hi:fj(a.hi),n:a.n};}
  const bl=[16,32,64,128].map(n=>fj(al(n).mean));
  out.blocks={P:0.5,t:0,mean:meanOf(bl),lo:Math.min(...bl),hi:Math.max(...bl),n:4,sizes:true};   // first run; t = 0 by the lane rule
  const s=al(256); out.b256={P:0.5,t:1,mean:fj(s.mean),lo:fj(s.lo),hi:fj(s.hi),n:s.n};            // first run; t = 1 by the lane rule
  return out;}
 const PRE=[['zeros','all zeros','wu/p0/'],['p25','P = ¼','wu/p0.25/'],['random','random','wu/p0.5/'],['p75','P = ¾','wu/p0.75/'],['ones','all ones','wu/p1/'],
            ['frozen','frozen line','wfrz/'],['blocks','16–128 B blocks','blocks'],['b256','256 B blocks','b256']];
 const preOf=id=>PRE.find(p=>p[0]===id);
 const pb=document.getElementById('plane-presets');
 pb.innerHTML=PRE.map(p=>`<button type="button" data-p="${p[0]}" aria-pressed="false">${p[1]}</button>`).join('');
 pb.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>pick(b.dataset.p)));
 const quiet=(rng,v)=>{rng.input.value=v;const s=f2(v);rng.el.querySelector('output').textContent=s;rng.input.setAttribute('aria-valuetext',s);};
 const rP=CK.range('plane-P',{label:'Ones, P',min:0,max:1,step:0.01,value:P,fmt:f2,onInput:v=>{P=v;t=Math.min(t,tmax(P));quiet(rT,t);preset=null;comp=null;update();}});
 const rT=CK.range('plane-t',{label:'Differences, t',min:0,max:1,step:0.01,value:t,fmt:f2,onInput:v=>{t=Math.min(v,tmax(P));if(t!==v)quiet(rT,t);preset=null;comp=null;update();}});
 function pick(id){const m=meas(key)[preOf(id)[2]]; P=m.P; t=m.t; preset=id; comp=null; quiet(rP,P); quiet(rT,t); update();}
 document.getElementById('plane-comp').addEventListener('click',()=>{const c=coef(key), from={P,t,e:E(c,P,t),name:preset?preOf(preset)[1]:`P = ${f2(P)}`};
  P=r2(1-P); quiet(rP,P); const back=PRE.find(p=>{const m=meas(key)[p[2]];return m&&!m.sizes&&p[2]!=='b256'&&Math.abs(m.P-P)<1e-6&&Math.abs(m.t-t)<1e-6;});
  preset=back?back[0]:null; comp=from; update();});
 CK.legend('plane-leg',[{key:'m',label:'measured, second run',mark:'dot',color:'var(--c2)'},{key:'f',label:'frozen line',mark:'box',color:'var(--c3)'},
  {key:'bk',label:'blocks, first run (t from the lane rule, §9)',mark:'ring',color:'var(--c3)'},{key:'par',label:'independent bits: t = 2P(1−P)',mark:'dash',color:'var(--ref)'},
  {key:'iso',label:'equal cost, fJ per bit per hop (the model; extrapolated away from the points)',mark:'line',color:'var(--ink-2)'}]);
 let F=null;
 const f=CK.frame('plane',{label:'The plane of bit patterns: density of ones across, flit-to-flit differences up, with lines of equal cost',minW:300,maxW:560,height:W=>Math.round(W*0.9),draw(f){
  F=f; const L=44,R=16,T=24,B=44, c=coef(key), M=meas(key), svg=f.svg, small=f.W<460;
  const x=CK.lin(0,1,L,f.W-R), y=CK.lin(0,1,f.H-B,T); f.x=x; f.y=y;
  const ax=CK.axes(f,{x,y,L,R,T,B,grid:false,xt:[0,0.25,0.5,0.75,1],yt:[0,0.25,0.5,0.75,1],xl:'density of ones, P',yl:'fraction of bits that differ from the previous flit, t'});
  ax.querySelectorAll('text').forEach(n=>{if(+n.getAttribute('y')===f.H-B+16)n.setAttribute('y',f.H-B+20);});   // x ticks 4 px lower, clear of the markers on t = 0
  sty(CK.el('polygon',{points:[[0,0],[0.5,1],[1,0]].map(q=>`${x(q[0])},${y(q[1])}`).join(' ')},svg),{fill:'var(--grid)',fillOpacity:0.5,stroke:'var(--axis)',strokeWidth:'1px'});
  if(small){CK.txt(svg,x(0.03),y(0.95),'no pattern','tick'); CK.txt(svg,x(0.03),y(0.95)+14,'reaches here','tick');} else CK.txt(svg,x(0.03),y(0.93),'no pattern reaches here','tick');
  // lines of equal cost: t = (k - s0 - bP)/a inside the feasible triangle; labelled where they meet its left edge t = 2P
  const Emax=E(c,0.5,1), step=25, iso=CK.el('g',{'aria-hidden':'true'},svg); let lab=0;
  for(let k=Math.ceil((c.s0+1)/step)*step;k<Emax;k+=step){const seg=[];
   for(let p=0;p<=1.00001;p+=0.0025){const q=(k-c.s0-c.b*p)/c.a; if(q>=-1e-9&&q<=tmax(p)+1e-9)seg.push([p,q]);}
   if(seg.length<2)continue; const a0=seg[0], a1=seg[seg.length-1]; if(Math.hypot(x(a1[0])-x(a0[0]),y(a1[1])-y(a0[1]))<16)continue;
   sty(CK.el('line',{x1:x(a0[0]),y1:y(a0[1]),x2:x(a1[0]),y2:y(a1[1])},iso),{stroke:'var(--ink-2)',strokeWidth:'1px',strokeOpacity:0.55});
   const pl=(k-c.s0)/(2*c.a+c.b); if(!small||lab++%2===0)CK.txt(iso,x(pl)-5,y(2*pl)+4,`${k}`,'tick','end');}
  const par=[]; for(let p=0;p<=1.0001;p+=0.02)par.push([p,2*p*(1-p)]);
  sty(CK.el('path',{d:CK.path(par,x,y)},svg),{fill:'none',stroke:'var(--ref)',strokeWidth:'1.5px',strokeDasharray:'5 4'});
  // markers: the measured patterns, each with its tooltip; Enter picks it
  const marks=[], tipOf=(id,m)=>{const e=E(c,m.P,m.t);return `<b>${preOf(id)[1]}</b>${m.sizes?' (16, 32, 64 and 128 B; first run)':id==='b256'?' (first run)':''}: P ${f2(m.P)}, t ${f2(m.t)}<br>measured ${f0(m.mean)} fJ per bit per hop${m.sizes?' (the four sizes: '+f0(m.lo)+'–'+f0(m.hi)+')':' ['+f0(m.lo)+'–'+f0(m.hi)+'], n = '+m.n}<br>the plane: ${f0(e)}, ${meterName(key)}`;};
  PRE.forEach(p=>{const m=M[p[2]]; if(!m)return; const g=CK.el('g',{'data-pre':p[0]},svg), cx=x(m.P), cy=y(m.t);
   if(p[0]==='blocks')sty(CK.el('circle',{cx,cy,r:7},g),{fill:'none',stroke:'var(--c3)',strokeWidth:'2px'});   // rings, as in the legend
   else if(p[0]==='b256')sty(CK.el('circle',{cx,cy,r:6},g),{fill:'var(--surface)',stroke:'var(--c3)',strokeWidth:'2px'});
   else if(p[0]==='frozen')sty(CK.el('rect',{x:cx-4,y:cy-4,width:8,height:8},g),{fill:'var(--c3)',stroke:'var(--surface)',strokeWidth:'1.5px'});
   else sty(CK.el('circle',{cx,cy,r:5.5},g),{fill:'var(--c2)',stroke:'var(--surface)',strokeWidth:'1.5px'});
   CK.tip(f,g,tipOf(p[0],m)); marks.push(g);});
  // the frozen line (P 0.48, t 0) sits beside the 16–128 B blocks (P 0.5, t 0): paint it last so it stays on top (keyboard order unchanged)
  const fz=svg.querySelector('[data-pre="frozen"]'); if(fz)svg.appendChild(fz);
  // where the 256 B blocks' measured cost sits on the plane (same P), shown when that pattern is picked
  const m256=M.b256; if(m256){const te=(m256.mean-c.s0-c.b*0.5)/c.a; if(te>=0&&te<1){
   const gr=CK.el('g',{'aria-hidden':'true',id:'plane-b256'},svg); gr.style.display=preset==='b256'?'':'none';
   sty(CK.el('line',{x1:x(0.5),x2:x(0.5),y1:y(1)+9,y2:y(te)+7},gr),{stroke:'var(--c3)',strokeWidth:'1.5px',strokeDasharray:'3 3'});
   sty(CK.el('circle',{cx:x(0.5),cy:y(te),r:6},gr),{fill:'none',stroke:'var(--c3)',strokeWidth:'2px'});
   const halo=n=>sty(n,{paintOrder:'stroke',stroke:'var(--surface)',strokeWidth:'3px',strokeLinejoin:'round'});
   if(small){halo(CK.txt(gr,x(0.5)-10,y(te)-2,'measured cost:','lab','end')); halo(CK.txt(gr,x(0.5)-10,y(te)+12,`as if t ≈ ${f2(te)}`,'lab','end'));}
   else halo(CK.txt(gr,x(0.5)+10,y(te)+16,`measured: costs what t ≈ ${f2(te)} would`,'lab'));}}
  CK.keynav(f,marks,{onEnter:n=>pick(n.getAttribute('data-pre'))});
  // the cursor
  const cur=CK.el('g',{'aria-hidden':'true',id:'plane-cursor'},svg);
  sty(CK.el('line',{class:'gx'},cur),{stroke:'var(--ink)',strokeWidth:'1px',strokeDasharray:'2 3'});
  sty(CK.el('line',{class:'gy'},cur),{stroke:'var(--ink)',strokeWidth:'1px',strokeDasharray:'2 3'});
  sty(CK.el('circle',{r:9},cur),{fill:'none',stroke:'var(--ink)',strokeWidth:'2px'});   // wider than every marker, so a ring under it still shows
  place();
 }});
 (function(svg){   // drag or tap anywhere on the plane (listeners attached once; the frame redraws the svg's children only)
  let drag=false; const at=ev=>{const b=svg.getBoundingClientRect(), p=Math.max(0,Math.min(1,F.x.inv(ev.clientX-b.left))), q=Math.max(0,F.y.inv(ev.clientY-b.top));
   P=r2(p); t=r2(Math.min(q,tmax(P))); quiet(rP,P); quiet(rT,t); preset=null; comp=null; update();};
  svg.addEventListener('pointerdown',ev=>{if(ev.target.closest('[data-pre]'))return; drag=true; try{svg.setPointerCapture(ev.pointerId);}catch(_){} at(ev);});
  svg.addEventListener('pointermove',ev=>{if(drag)at(ev);});
  ['pointerup','pointercancel'].forEach(e=>svg.addEventListener(e,()=>{drag=false;}));
  svg.style.touchAction='pan-y';   // a vertical swipe still scrolls the page on a phone; a tap or a sideways drag moves the cursor
 })(f.svg);
 function place(){if(!F)return; const cur=F.svg.querySelector('#plane-cursor'); if(!cur)return; const x=F.x,y=F.y, cx=x(P), cy=y(t);
  const [gx,gy]=cur.querySelectorAll('line'); Object.entries({x1:cx,x2:cx,y1:cy+9,y2:y(0)}).forEach(([k,v])=>gx.setAttribute(k,v)); Object.entries({x1:x(0),x2:cx-9,y1:cy,y2:cy}).forEach(([k,v])=>gy.setAttribute(k,v));
  const c0=cur.querySelector('circle'); c0.setAttribute('cx',cx); c0.setAttribute('cy',cy);}
 const out=CK.readout('plane-readout');
 function update(){
  place(); const g256=F&&F.svg.querySelector('#plane-b256'); if(g256)g256.style.display=preset==='b256'?'':'none';
  pb.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.p===preset)));
  const c=coef(key), M=meas(key), e=E(c,P,t), parts=[[c.s0,'var(--ref)','fixed, s<sub>0</sub>'],[c.a*t,'var(--c1)','differences, <i>a·t</i>'],[c.b*P,'var(--c2)','ones, <i>b·P</i>']];
  const top=Math.max(E(c,0.5,1),E(c,1,0),...Object.values(M).map(m=>m.hi))*1.04, m=preset?M[preOf(preset)[2]]:null;
  let h=`<b>${preset?preOf(preset)[1]:'your pattern'}</b>: P ${f2(P)}, t ${f2(t)}, ${meterName(key)}`+
   `<div class="hv-bar" role="img" aria-label="${f0(c.s0)} fixed, ${f0(c.a*t)} for differences and ${f0(c.b*P)} for ones, fJ per bit per hop${m?'; measured '+f0(m.mean):''}">`+
   parts.map(q=>`<span style="width:${(100*q[0]/top).toFixed(2)}%;background:${q[1]}"></span>`).join('')+(m?`<i style="left:${(100*m.mean/top).toFixed(2)}%"></i>`:'')+`</div>`+
   `<div class="hv-key">${parts.map(q=>`<span><u style="background:${q[1]}"></u>${q[2]} <b>${f0(q[0])}</b></span>`).join('')}${m?'<span>▮ measured</span>':''}</div>`+
   `<p style="margin:6px 0 0">The plane: <b>${f0(e)} fJ per bit per hop</b> = ${f1(e/HOP)} fJ per bit·mm = ${f2(e*8192/1e6)} nJ per 1 KB tensor load per hop.</p>`;
  if(m&&m.sizes){   // the blocks were measured over d = 1, 3, 6 only: compared with the plane (fitted over 1-6 hops) they would
   // seem to fall short; compared like for like (blocksLFL) they sit on the no-transition prediction
   const lf=blocksLFL(key), dev=lf?Math.max(...Object.values(lf.per_card).map(c=>Math.abs(c.below))):null;
   h+=`<p style="margin:4px 0 0">Measured: <b>${f0(m.mean)}</b> fJ (four block sizes, ${f0(m.lo)}–${f0(m.hi)}): a first-run pattern the model was not fitted to, measured over 1, 3 and 6 hops`+
    (lf?`; against the first run's all-zeros and all-ones over the same hops it sits on the no-transition prediction ${key===NK?`within about ${Math.max(1,Math.round(100*dev))}% on both cards`:'within the noise'}`:'')+`.</p>`;}
  else if(m){const d=1-m.mean/e, word=preset==='b256'&&key===BK?'below':d>0.1?'far below':d>0.005?'slightly below':d<-0.005?'above':'on';   // board power does not resolve the 256 B pattern from a full flip
   h+=`<p style="margin:4px 0 0">Measured: <b>${f0(m.mean)}</b> fJ [${f0(m.lo)}–${f0(m.hi)}], n = ${m.n}: ${word==='on'?'on the plane':`${word} the plane (${f0(100*Math.abs(d))}%)`}${preset==='b256'?'; a first-run pattern the model was not fitted to'+(key===BK?', and on board power not resolved from a full flip on either card':''):''}.</p>`;}
  if(comp){const d=1-e/comp.e; h+=`<p style="margin:4px 0 0">Sent complemented (P → 1 − P), ${comp.name} goes from ${f0(comp.e)} to ${f0(e)} fJ per bit per hop: ${f0(100*Math.abs(d))}% ${d>=0?'less':'more'}.</p>`;}
  out.set(h);}
 CK.seg('plane-meter',{label:'Meter',options:METERS,value:key,onChange:v=>{key=v;f.redraw();update();}});
 const cN=coef(NK), cB=coef(BK);
 setText('planecap',`The plane is the second run's fit, E = s<sub>0</sub> + <i>a·t</i> + <i>b·P</i>: on the mesh rail s<sub>0</sub> = ${f3(cN.s0pj)} pJ/B per hop (${f0(cN.s0)} fJ per bit), <i>a</i> = ${f1(cN.a)} fJ per bit that differs and <i>b</i> = ${f1(cN.b)} fJ per one carried (board power: ${f3(cB.s0pj)} pJ/B, ${f1(cB.a)} and ${f1(cB.b)}). Because <i>b</i> > <i>a</i>, all ones (${f0(E(cN,1,0))} fJ) cost more than random data (${f0(E(cN,0.5,0.5))} fJ) on the mesh rail. Only the points are measured; the lines of equal cost between them are the model's extrapolation, and the feasible triangle is every pattern whose ones and differences can coexist (t ≤ 2·min(P, 1 − P)).`);
 update();
})();

/* ---------- 6. contention, and the link-sharing map ---------- */
const MAPBUS=CK.bus('heat-map-d');
(function(){
 const C=W_.configs; let key=NK, sel=null;
 const series=[['wu/p0.5/hop',[1,2,3,4,6],'var(--c2)','loaded mesh, random',''],['wsep/p0.5/hop',[1,2,3,4,5],'var(--c1)','own links, random',''],
               ['wu/p0/hop',[1,2,3,4,6],'var(--c4)','loaded mesh, zeros','5 3'],['wsep/p0/hop',[1,2,3,4,5],'var(--c3)','own links, zeros','5 3']];
 CK.legend('cont-leg',series.map((s,i)=>({key:String(i),label:s[3],mark:s[4]?'dash':'line',color:s[2]})));
 const f=CK.frame('cont',{label:'Energy per payload byte against distance, with every flow on its own links and on a loaded mesh',height:W=>W<600?300:330,draw(f){
  const L=46,R=14,T=26,B=40;
  let mx=0; series.forEach(sr=>sr[1].forEach(d=>{const c=C[sr[0]+d]; if(c&&c[key])mx=Math.max(mx,c[key].hi);})); mx*=1.08;
  const x=CK.lin(0.6,6.3,L,f.W-R), y=CK.lin(0,mx,f.H-B,T);
  CK.axes(f,{x,y,L,R,T,B,xt:[1,2,3,4,5,6],xl:'hops',yl:`${meterName(key)}: pJ per payload byte above idle`});
  series.forEach((sr,i)=>{const pts=[],nodes=[],g=CK.el('g',{'data-series':String(i)},f.svg);
   sr[1].forEach(d=>{const c=C[sr[0]+d]; if(c&&c[key])pts.push([d,c[key].mean]);});
   sty(CK.el('path',{d:CK.path(pts,x,y)},g),{fill:'none',stroke:sr[2],strokeWidth:'1.8px',strokeDasharray:sr[4]||'none'});
   sr[1].forEach(d=>{const c=C[sr[0]+d]; if(!c||!c[key])return; const q=c[key], m=CK.el('g',{},g);
    whisker(m,x(d),y(q.hi),y(q.lo),sr[2]); sty(CK.el('circle',{cx:x(d),cy:y(q.mean),r:4},m),{fill:sr[2],stroke:'var(--surface)',strokeWidth:'1.5px'});
    if(sel===d)sty(CK.el('circle',{cx:x(d),cy:y(q.mean),r:8},m),{fill:'none',stroke:'var(--ink)',strokeWidth:'1.5px'});
    CK.tip(f,m,`<b>${sr[3]}</b>, ${d} hop${d>1?'s':''}<br>${f2(q.mean)} pJ/B [${f2(q.lo)}–${f2(q.hi)}], ${meterName(key)}<br>${Math.round(c.participants/32)} reader shires, ${f0(c.gb_s)} GB/s`);
    nodes.push(m);});
   CK.keynav(f,nodes);});
  const dj=W_.disjoint_flows[key]; if(dj&&dj.wsep_d1_4&&dj.wu){const u=dj.wsep_d1_4.random_minus_zeros_fj_per_bit_hop, l=dj.wu.random_minus_zeros_fj_per_bit_hop, uz=dj.wsep_d1_4.zeros_fj_per_bit_hop, lz=dj.wu.zeros_fj_per_bit_hop;
   // board power resolves only the total per card, not its split into a data and a fixed part (§10)
   const body=key===NK?`the data-dependent part costs ${f0(u.mean)} fJ with every flow on its own links against ${f0(l.mean)} on the loaded mesh, the data-independent part ${f0(uz.mean)} against ${f0(lz.mean)}`
    :`a random bit costs ${f0(dj.wsep_d1_4.random_fj_per_bit_hop.mean)} fJ with every flow on its own links against ${f0(dj.wu.random_fj_per_bit_hop.mean)} on the loaded mesh; on this meter the split into a data-dependent and a fixed part is not resolved (<a href="#limits">§10</a>)`;
   setText('contcap',`Per bit per hop over 1–4 hops, ${meterName(key)}: ${body}. Solid: random data; dashed: zeros; bars: the range over six passes${sel?`; rings: the ${sel}-hop points, the distance on the map`:''}.`);}
 }});
 CK.seg('contbtn',{label:'Meter',options:METERS,value:key,onChange:v=>{key=v;f.redraw();}});
 MAPBUS.on(d=>{sel=d;f.redraw();});
})();
(function(){
 const MX=IN.mesh_xy&&IN.mesh_xy.value, LS=W_.checks.link_sharing, C=W_.configs; if(!MX)return;
 const SETS={wu:{pre:'wu/p0.5/hop',label:'loaded mesh (all pairs)',short:'loaded mesh'},wsep:{pre:'wsep/p0.5/hop',label:'own links',short:'own links'}};
 const has=(s,d)=>!!(LS[SETS[s].pre+d]&&LS[SETS[s].pre+d].target_map);
 let d=4, set='wu', order='xy';
 const XY=s=>MX[String(s)];
 function route(tg,rd,ord){let [x,y]=XY(tg); const [x1,y1]=XY(rd), out=[];   // as analyze_wire.route(): data flow target -> reader
  for(const ax of ord){if(ax==='x')while(x!==x1){const nx=x+(x1>x?1:-1);out.push([x,y,nx,y]);x=nx;} else while(y!==y1){const ny=y+(y1>y?1:-1);out.push([x,y,x,ny]);y=ny;}}
  return out;}
 function flows(s,dd,ord){const tm=(LS[SETS[s].pre+dd]||{}).target_map||'', fl=[], use=new Map();
  tm.split(',').filter(Boolean).forEach(it=>{const [rs,ts]=it.split('>'), r=+rs, tg=+ts.split('/')[0]; if(r===tg||!XY(r)||!XY(tg))return;
   const links=route(tg,r,ord); const fo={r,t:tg,links}; fl.push(fo); links.forEach(l=>{const k=l.join(','); if(!use.has(k))use.set(k,[]); use.get(k).push(fo);});});
  let tot=0,sh=0; fl.forEach(fo=>fo.links.forEach(l=>{tot++; if(use.get(l.join(',')).length>1)sh++;}));
  return {fl,use,shared:tot?sh/tot:0,busiest:Math.max(0,...[...use.values()].map(v=>v.length)),readers:new Set(fl.map(fo=>fo.r)).size};}
 const loadCol=n=>n<=1?'var(--c1)':n===2?'var(--c4)':'var(--c2)', loadW=n=>n<=1?1.6:n===2?2.6:3.6;
 CK.legend('map-leg',[{key:'1',label:'1 flow',mark:'line',color:'var(--c1)'},{key:'2',label:'2 flows',mark:'line',color:'var(--c4)'},{key:'3',label:'3–4 flows',mark:'line',color:'var(--c2)'},
  {key:'s',label:'compute shire',mark:'dot',color:'var(--ink)'},{key:'e',label:'empty position',mark:'ring',color:'var(--ref)'}]);
 const out=CK.readout('map-readout');
 const f=CK.frame('linkmap',{label:'Logical mesh map with the directed links the flows use, coloured by how many flows share each',minW:280,maxW:420,height:W=>Math.round(W*0.92),draw(f){
  const svg=f.svg, pad=22, s=(Math.min(f.W,f.H)-2*pad)/5, ox=(f.W-5*s)/2, oy=pad-4, P=([x,y])=>[ox+x*s,oy+y*s];
  const occ=new Set(Object.values(MX).map(v=>v.join(',')));
  const grid=CK.el('g',{'aria-hidden':'true'},svg);
  for(let x=0;x<6;x++)for(let y=0;y<6;y++){[[1,0],[0,1]].forEach(([dx,dy])=>{const a=[x,y],b=[x+dx,y+dy]; if(b[0]>5||b[1]>5||!occ.has(a.join(','))||!occ.has(b.join(',')))return;
   const [x1,y1]=P(a),[x2,y2]=P(b); sty(CK.el('line',{x1,y1,x2,y2},grid),{stroke:'var(--grid)',strokeWidth:'5px',strokeLinecap:'round'});});}
  const R=flows(set,d,order), lg=CK.el('g',{},svg), linkNodes=[], byLink=new Map();
  [...R.use.entries()].sort((a,b)=>a[1].length-b[1].length).forEach(([k,fl])=>{const [x0,y0,x1,y1]=k.split(',').map(Number), a=P([x0,y0]), b=P([x1,y1]);
   const dx=Math.sign(x1-x0), dy=Math.sign(y1-y0), off=3.2, nx=-dy*off, ny=dx*off, sh=9;   // offset to the right of travel; shorten at both ends
   const ax=a[0]+dx*sh+nx, ay=a[1]+dy*sh+ny, bx=b[0]-dx*sh+nx, by=b[1]-dy*sh+ny, n=fl.length, c=loadCol(n), g=CK.el('g',{'data-link':k},lg);
   sty(CK.el('line',{x1:ax,y1:ay,x2:bx-dx*4,y2:by-dy*4},g),{stroke:c,strokeWidth:loadW(n)+'px',strokeLinecap:'round'});
   sty(CK.el('polygon',{points:`${bx},${by} ${bx-dx*6-dy*3.5},${by-dy*6+dx*3.5} ${bx-dx*6+dy*3.5},${by-dy*6-dx*3.5}`},g),{fill:c});
   sty(CK.el('line',{x1:ax,y1:ay,x2:bx,y2:by,class:'ck-hit'},g),{strokeWidth:'12px',pointerEvents:'stroke'});
   CK.tip(f,g,`link (${x0}, ${y0}) → (${x1}, ${y1}): <b>${n} flow${n>1?'s':''}</b><br>${fl.map(fo=>`shire ${fo.t} → ${fo.r}`).join(', ')}`);
   linkNodes.push(g); byLink.set(k,g);});
  const dim=fo=>{lg.querySelectorAll('[data-link]').forEach(g=>{g.style.opacity=!fo||fo.links.some(l=>l.join(',')===g.getAttribute('data-link'))?'1':'0.18';});};
  const nodes=CK.el('g',{},svg), readerNodes=[], fByR=new Map(R.fl.map(fo=>[fo.r,fo]));
  (IN.mesh_xy.empty||[]).forEach(e=>{const [cx,cy]=P(e); sty(CK.el('circle',{cx,cy,r:4.5},nodes),{fill:'none',stroke:'var(--ref)',strokeWidth:'1.5px'});});
  Object.keys(MX).map(Number).sort((a,b)=>XY(a)[1]-XY(b)[1]||XY(a)[0]-XY(b)[0]).forEach(sh=>{const [cx,cy]=P(XY(sh)), fo=fByR.get(sh), g=CK.el('g',{},nodes);
   sty(CK.el('circle',{cx,cy,r:fo?5:3.5},g),{fill:'var(--ink)',stroke:'var(--surface)',strokeWidth:'1.5px'});
   if(fo){const nsh=fo.links.filter(l=>R.use.get(l.join(',')).length>1).length;
    CK.tip(f,g,`<b>shire ${sh}</b> at (${XY(sh).join(', ')}) reads shire ${fo.t}'s scratchpad, ${fo.links.length} hop${fo.links.length>1?'s':''} away<br>its data crosses ${fo.links.length} link${fo.links.length>1?'s':''}, ${nsh} shared with another flow`);
    g.addEventListener('pointerenter',()=>dim(fo)); g.addEventListener('pointerleave',()=>dim(null)); g.addEventListener('focus',()=>dim(fo)); g.addEventListener('blur',()=>dim(null));
    readerNodes.push(g);}});
  CK.keynav(f,readerNodes); CK.keynav(f,linkNodes);
 }});
 const segD=CK.seg('map-d',{label:'Distance',options:[1,2,3,4,5,6].map(v=>[v,`${v}`]),value:d,onChange:v=>{d=v;fix('d');}});
 const segS=CK.seg('map-set',{label:'Flows',options:[['wu','loaded mesh'],['wsep','own links']],value:set,onChange:v=>{set=v;fix('set');}});
 CK.seg('map-order',{label:'Route',options:[['xy','x first (as the analysis assumes)'],['yx','y first']],value:order,onChange:v=>{order=v;fix();}});
 function fix(what){   // a distance that one set did not run: keep the choice and switch the other
  if(!has(set,d)){if(what==='set'){const ds=[1,2,3,4,5,6].filter(q=>has(set,q)); d=ds.reduce((b,q)=>Math.abs(q-d)<Math.abs(b-d)?q:b,ds[0]); segD.set(d); return;} set=set==='wu'?'wsep':'wu'; segS.set(set); return;}
  segD.el.querySelectorAll('[role=radio]').forEach((b,i)=>b.setAttribute('aria-label',`${i+1} hop${i?'s':''}${has(set,i+1)?'':' (not run for this set)'}`));
  f.redraw(); MAPBUS.emit(d); readout();}
 function readout(){
  const col=s=>{if(!has(s,d))return null; const cfg=SETS[s].pre+d, l=LS[cfg], R=flows(s,d,order);
   return {flows:l.flows,readers:l.reader_shires,shared:order==='xy'?l.shared_link_hop_fraction:l.shared_link_hop_fraction_yx,busy:R.busiest,pj:C[cfg][NK].mean,check:R.shared};};
  const a=col('wu'), b=col('wsep'), cell=(o,fn)=>o?fn(o):'not run', pc=v=>`${f0(100*v)}%`;
  const rows=[['flows',o=>o.flows],['reader shires',o=>o.readers],['link-hops on shared links',o=>pc(o.shared)],['busiest link, flows',o=>o.busy],['mesh rail, random data, pJ/B',o=>f2(o.pj)]];
  out.set(`<table><thead><tr><th>${d} hop${d>1?'s':''}, ${order==='xy'?'x':'y'} first</th><th class="num">loaded mesh</th><th class="num">own links</th></tr></thead><tbody>`+
   rows.map(r=>`<tr><td>${r[0]}</td><td class="num">${cell(a,r[1])}</td><td class="num">${cell(b,r[1])}</td></tr>`).join('')+'</tbody></table>');}
 fix();
 const sx=dd=>LS[`wu/p0.5/hop${dd}`];
 setText('mapcap',`The map is the logical 6 × 6 grid of the 32 compute shires (marty1885's coordinates, as in on-chip communication; it appears to be the die turned a quarter), and each arrow a directed link that carries data from a target's scratchpad to its reader. Routes are drawn dimension-ordered, as the analysis assumes; the chip's routing order is not measured, so the map can route y first too, and the shares hardly change (3 hops: ${f0(100*sx(3).shared_link_hop_fraction)}% x first, ${f0(100*sx(3).shared_link_hop_fraction_yx)}% y first; 6 hops: ${f0(100*sx(6).shared_link_hop_fraction)}% and ${f0(100*sx(6).shared_link_hop_fraction_yx)}%). The own-links pairs use only straight paths, so both orders give the same routes. That set also has fewer flows at long distances (${LS['wsep/p0.5/hop4'].flows} against ${LS['wu/p0.5/hop4'].flows} at four hops), so the energy gap between the sets is not sharing alone. Hover, tap or tab to a reader shire to see its route, or to a link to list its flows.`);
})();

/* ---------- 9. lanes and flit width ---------- */
(function(){
 const Ns=[16,32,64,128,256], PT=W_.patterns; let key=NK;
 if(!Ns.some(n=>PT[`alt:${n}`]))return;
 CK.legend('alt-leg',[{key:'s',label:'blocks of 16–128 B',mark:'box',color:'var(--c1)'},{key:'l',label:'256 B blocks',mark:'box',color:'var(--c2)'},{key:'p',label:'predicted over the same hops, with 0 or 1 difference per bit',mark:'dash',color:'var(--ink)'}]);
 const f=CK.frame('alt',{label:'Cost per hop of blocks of N bytes alternately all-zero and all-one',height:W=>W<600?260:280,draw(f){
  const L=46,R=14,T=26,B=40, M=W_.model.v1[srcOf(key)], a=M.toggle_fj_per_bit_transition_hop.mean*8/1000, b=M.ones_fj_per_one_bit_hop.mean*8/1000, s0=M.s0_pj_per_byte_hop.mean;
  // like for like: the blocks' slopes are over d = 1, 3, 6, so the no-difference level is the first run's all-zeros and
  // all-ones averaged over the same hops (the model's s0 + b/2 is fitted over 1-6 hops, which the raised four-hop point
  // steepens); a full flip adds the first run's cost per difference, a
  const lf=blocksLFL(key), lvl=lf?lf.nt:s0+b*0.5;
  const pred=n=>lvl+a*(n===256?1:0);
  // top of the axis rounded up to a labelled tick, so the 256 B prediction (2.7 pJ/B on board power) sits under a gridline
  const mx=Math.ceil(2*1.1*Math.max(...Ns.filter(n=>PT[`alt:${n}`]).map(n=>Math.max(PT[`alt:${n}`][key].slope.hi,pred(n)))))/2;
  const bw=(f.W-L-R)/Ns.length, xc=i=>L+bw*i+bw/2, y=CK.lin(0,mx,f.H-B,T);
  CK.axes(f,{x:CK.lin(0,1,L,f.W-R),y,L,R,T,B,xt:[],yt:[0,0.5,1,1.5,2,2.5,3,3.5].filter(q=>q<=mx),xl:'block size N (half the pattern period)',yl:`${meterName(key)}: pJ per payload byte per hop`});
  const nodes=[];
  Ns.forEach((n,i)=>{const e=PT[`alt:${n}`]; if(!e)return; const s=e[key].slope, g=CK.el('g',{},f.svg), tl=n===256?1:0;
   sty(CK.el('rect',{x:xc(i)-bw*0.28,y:y(s.mean),width:bw*0.56,height:y(0)-y(s.mean),rx:3},g),{fill:n===256?'var(--c2)':'var(--c1)',fillOpacity:0.85});
   whisker(g,xc(i),y(s.hi),y(s.lo),'var(--ink)');
   sty(CK.el('line',{x1:xc(i)-bw*0.36,x2:xc(i)+bw*0.36,y1:y(pred(n)),y2:y(pred(n))},f.svg),{stroke:'var(--ink)',strokeDasharray:'4 3',strokeWidth:'1.5px'});
   CK.txt(f.svg,xc(i),f.H-B+16,`${n} B`,'tick','middle');
   CK.tip(f,g,`<b>blocks of ${n} B</b>, alternately all-0 and all-1, ${meterName(key)}<br>${f3(s.mean)} pJ/B per hop [${f3(s.lo)}–${f3(s.hi)}]<br>on one lane consecutive lines are i and i+4: ${n<=128?'the same block value, no differences':'opposite values, every bit differs'}<br>dashed: predicted with ${tl} difference${tl?'':'s'} per bit over the same hops, ${f3(pred(n))}`);
   nodes.push(g);});
  CK.keynav(f,nodes);
 }});
 CK.seg('altbtn',{label:'Meter',options:METERS,value:key,onChange:v=>{key=v;f.redraw();}});
})();

/* ---------- 7. against the rule of thumb: the voltage explorer ---------- */
(function(){
 const V0=IN.noc_v.value, sq=V=>(V/V0)*(V/V0), cross=e=>V0*Math.sqrt(100/e);
 const W485=D.first_principles.at_0485.per_random_bit_fj_mm;   // plain 7 nm repeated wire [lo, mid, hi] at 0.485 V
 const CUR=[{key:'df',label:'data, free links',p:UN.random_bit_data,color:'var(--c1)',dash:null},{key:'dl',label:'data, loaded mesh',p:HN.random_bit_data,color:'var(--c1)',dash:'7 4'},
            {key:'af',label:'everything, free links',p:UN.random_bit_total,color:'var(--c7)',dash:null},{key:'al',label:'everything, loaded mesh',p:HN.random_bit_total,color:'var(--c7)',dash:'7 4'}];
 const kek=D.literature.find(l=>/^Keckler/.test(l.who)), d14=D.literature.find(l=>l.v&&l.v<0.8&&/Dally/.test(l.who));
 const litV=D.literature.filter(l=>l.v&&l.v<=1.0), litN=D.literature.filter(l=>!l.v);
 let V=0.9, FV=null;
 const LG=CK.legend('volt-leg',[...CUR.map(c=>({key:c.key,label:c.key[0]==='a'?c.label+' (assumes the fixed part also scales as CV²)':c.label,mark:c.dash?'dash':'line',color:c.color})),
  {key:'wire',label:'plain 7 nm wire, first principles',mark:'box',color:'var(--c3)'},{key:'kek',label:'Keckler 2011, scaled as CV²',mark:'dash',color:'var(--c2)'},
  {key:'refs',label:`no voltage stated: ${[...new Set(litN.map(l=>l.fj_bit_mm))].sort((a,b)=>b-a).map(v=>{const r=litN.find(l=>l.fj_bit_mm===v&&l.range);return r?r.range.join('–')+' and '+v:'~'+v;}).join('; ')} fJ`,mark:'dash',color:'var(--ref)'}],
  {toggle:true,onChange:on=>CK.showSeries(f,on)});
 const short=l=>{const w=l.who, yr=(w.match(/(19|20)\d\d/)||[''])[0]; return `${w.split(/[ ,(]/)[0]}${/CACM/.test(w)?' CACM':/VLSI/.test(w)?' VLSI':''} ${yr}`;};
 const f=CK.frame('volt',{label:'Energy per random bit per millimetre against supply voltage: the measured values scaled as CV², a plain wire, and the literature',height:W=>W<600?360:420,draw(f){
  const L=40,R=f.narrow?12:168,T=26,B=40, svg=f.svg;
  const x=CK.lin(0.40,1.00,L,f.W-R), y=CK.lin(0,240,f.H-B,T); f.x=x; f.y=y;
  CK.axes(f,{x,y,L,R,T,B,xt:[0.4,0.5,0.6,0.7,0.8,0.9,1.0],yt:[0,50,100,150,200],xfmt:v=>f1(v),xl:'supply voltage, V',yl:'fJ per random bit per mm'});
  const Vs=[]; for(let v=0.40;v<=1.0001;v+=0.005)Vs.push(+v.toFixed(3));
  const band=(lo,hi)=>CK.path(Vs.map(v=>[v,Math.min(240,lo*sq(v))]),x,y)+' '+CK.path(Vs.slice().reverse().map(v=>[v,Math.min(240,hi*sq(v))]),x,y).replace(/^M/,'L')+' Z';
  // voltage-less literature: horizontal references (grouped by value); VLSI 2018's 20-40 as a band
  const ref=CK.el('g',{'aria-hidden':'true','data-series':'refs'},svg);
  const rng=litN.find(l=>l.range); if(rng)sty(CK.el('rect',{x:x(0.4),y:y(rng.range[1]),width:x(1)-x(0.4),height:y(rng.range[0])-y(rng.range[1])},ref),{fill:'var(--ref)',fillOpacity:0.12});
  const byV={}; litN.forEach(l=>{(byV[l.fj_bit_mm]=byV[l.fj_bit_mm]||[]).push(l);});
  Object.keys(byV).forEach(k=>sty(CK.el('line',{x1:x(0.4),x2:x(1),y1:y(+k),y2:y(+k)},ref),{stroke:'var(--ref)',strokeWidth:'1.5px',strokeDasharray:'2 4'}));
  const refLabels=g=>Object.keys(byV).map(Number).sort((a,b)=>b-a).forEach((k,i)=>{const ls=byV[k], r0=ls.find(l=>l.range), lab=`${r0?r0.range.join('–')+', ':'~'}${k} (no voltage): ${ls.map(short).join(', ')}`;
   if(i===0)halo(CK.txt(g,x(0.4)+4,y(k)-5,lab,'tick')); else halo(CK.txt(g,x(1)-4,y(rng?rng.range[0]:k)+14,lab,'tick','end'));});   // drawn over the curves and the cursor (below)
  // the plain wire and the four measured curves, each with its lo-hi band
  const gw=CK.el('g',{'data-series':'wire','aria-hidden':'true'},svg);
  sty(CK.el('path',{d:band(W485[0],W485[2])},gw),{fill:'var(--c3)',fillOpacity:0.14,stroke:'var(--c3)',strokeWidth:'1px',strokeOpacity:0.6});
  if(!f.narrow)CK.txt(gw,x(1)+6,y(W485[1]*sq(1))+4,'plain 7 nm wire','lab');
  if(kek){const gk=CK.el('g',{'data-series':'kek','aria-hidden':'true'},svg); sty(CK.el('path',{d:CK.path(Vs.map(v=>[v,kek.fj_bit_mm*(v/kek.v)**2]),x,y)},gk),{fill:'none',stroke:'var(--c2)',strokeWidth:'1.2px',strokeDasharray:'2 3'});}
  const ends=[];
  CUR.forEach(c=>{const g=CK.el('g',{'data-series':c.key,'aria-hidden':'true'},svg);
   sty(CK.el('path',{d:band(c.p.lo,c.p.hi)},g),{fill:c.color,fillOpacity:0.13,stroke:'none'});
   sty(CK.el('path',{d:CK.path(Vs.map(v=>[v,c.p.mean*sq(v)]),x,y)},g),{fill:'none',stroke:c.color,strokeWidth:'2px',strokeDasharray:c.dash||'none'});
   ends.push({y:y(c.p.mean*sq(1)),t:c.label,g});});
  if(!f.narrow)spread(ends,14,T,f.H-B).forEach(e=>CK.txt(e.g,x(1)+6,e.y+4,e.t,'lab'));
  // where the chip runs
  const g0=CK.el('g',{'aria-hidden':'true'},svg);
  sty(CK.el('line',{x1:x(V0),x2:x(V0),y1:T-4,y2:f.H-B},g0),{stroke:'var(--ink-2)',strokeWidth:'1px',strokeDasharray:'1 3'});
  halo(CK.txt(g0,x(V0)+4,T+6,`ET-SoC-1 runs here, ${V0} V`,'lab'));
  // the voltage cursor, with one focusable dot per curve that reads its value; drawn before the literature and board
  // points so that snapping to 0.7 or 0.9 V does not cover Dally's or Keckler's point
  const cur=CK.el('g',{id:'volt-cursor'},svg);
  sty(CK.el('line',{y1:T-4,y2:f.H-B,class:'vl'},cur),{stroke:'var(--ink)',strokeWidth:'1.2px'});
  const dots=CUR.map(c=>{const g=CK.el('g',{'data-series':c.key,'data-k':c.key},cur); sty(CK.el('circle',{r:4.5},g),{fill:c.color,stroke:'var(--surface)',strokeWidth:'1.5px'}); CK.tip(f,g,()=>`<b>${c.label}</b> at ${f3(V)} V: ${f0(c.p.mean*sq(V))} fJ per bit·mm [${f0(c.p.lo*sq(V))}–${f0(c.p.hi*sq(V))}]`); return g;});
  if(!f.narrow)refLabels(CK.el('g',{'aria-hidden':'true','data-series':'refs'},svg));   // phones: the legend names them
  // marks with tooltips: literature at its own voltage, board power (not scaled)
  const marks=[];
  litV.forEach(l=>{const g=CK.el('g',{},svg), cx=x(l.v), cy=y(l.fj_bit_mm);
   if(l.range)whisker(g,cx,y(l.range[1]),y(l.range[0]),'var(--c2)');
   sty(CK.el('circle',{cx,cy,r:6},g),{fill:'var(--c2)',stroke:'var(--surface)',strokeWidth:'1.5px'});
   halo(CK.txt(g,cx+(l.v>0.85?-9:9),cy-8,short(l),'lab',l.v>0.85?'end':'start'));
   CK.tip(f,g,`<b>${l.who}</b><br>${l.what}: ${l.fj_bit_mm} fJ per bit·mm<br>${l.conditions}`); marks.push(g);});
  [['free links',UB],['loaded mesh',HB]].forEach(([w,h])=>{const g=CK.el('g',{},svg), cy=y(h.random_bit_total.mean);
   sty(CK.el('circle',{cx:x(V0),cy,r:5},g),{fill:'var(--surface)',stroke:'var(--ink-2)',strokeWidth:'2px'});
   CK.tip(f,g,`<b>board power, everything, ${w}</b>: ${f1(h.random_bit_total.mean)} fJ per bit·mm [${f1(h.random_bit_total.lo)}–${f1(h.random_bit_total.hi)}] at ${V0} V<br>includes the regulator's loss; not scaled`); marks.push(g);});
  CK.keynav(f,marks);
  CK.keynav(f,dots);
  FV=f; moveCursor();
 }});
 (function(svg){   // drag or tap across the chart to set the voltage (listeners attached once)
  let drag=false; const at=ev=>{const b=svg.getBoundingClientRect(); setV(Math.round(Math.max(0.4,Math.min(1,FV.x.inv(ev.clientX-b.left)))*200)/200);};
  svg.addEventListener('pointerdown',ev=>{if(ev.target.closest('[tabindex]'))return; drag=true; try{svg.setPointerCapture(ev.pointerId);}catch(_){} at(ev);});
  svg.addEventListener('pointermove',ev=>{if(drag)at(ev);}); ['pointerup','pointercancel'].forEach(e=>svg.addEventListener(e,()=>{drag=false;}));
  svg.style.touchAction='pan-y';
 })(f.svg);
 LG.set(['df','dl','af','al','wire','refs']); CK.showSeries(f,[...LG.on]);   // the Keckler curve starts hidden: it runs almost on top of 'everything, free links'
 function moveCursor(){const cur=FV&&FV.svg.querySelector('#volt-cursor'); if(!cur)return; const x=FV.x,y=FV.y, vl=cur.querySelector('.vl'); vl.setAttribute('x1',x(V)); vl.setAttribute('x2',x(V));
  CUR.forEach(c=>{const g=cur.querySelector(`[data-k="${c.key}"]`), e=c.p.mean*sq(V); const k=g.querySelector('circle'); k.setAttribute('cx',x(V)); k.setAttribute('cy',y(Math.min(240,e)));
   g.setAttribute('aria-label',`${c.label} at ${f3(V)} V: ${f0(e)} fJ per bit·mm`);});}
 const rv=CK.range('volt-v',{label:'Supply voltage',min:0.4,max:1.0,step:0.005,value:V,fmt:v=>`${f3(v)} V`,onInput:v=>{V=v;update();}});
 const SNAP=[[V0,`${V0} V (as run)`],[d14?d14.v:0.7,`${d14?d14.v:0.7} V (Dally 2014)`],[kek?kek.v:0.9,`${kek?kek.v:0.9} V (Keckler)`]];
 const sb=document.getElementById('volt-snap');
 sb.innerHTML=SNAP.map(s=>`<button type="button" data-v="${s[0]}" aria-pressed="false">${s[1]}</button>`).join('');
 sb.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>setV(+b.dataset.v)));
 function setV(v){V=v; rv.input.value=v; const s=`${f3(v)} V`; rv.el.querySelector('output').textContent=s; rv.input.setAttribute('aria-valuetext',s); update();}
 const out=CK.readout('volt-readout');
 function update(){moveCursor(); sb.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(Math.abs(+b.dataset.v-V)<1e-9)));
  const r=v=>f2(v/100), rows=CUR.map(c=>[c.key[0]==='a'?c.label+' (fixed part scaled too)':c.label,f0(c.p.mean*sq(V)),r(c.p.mean*sq(V))]);
  rows.push(['plain 7 nm wire',`${f0(W485[0]*sq(V))}–${f0(W485[2]*sq(V))}`,`${r(W485[0]*sq(V))}–${r(W485[2]*sq(V))}`]);
  if(kek)rows.push([`Keckler 2011 (${kek.fj_bit_mm} at ${kek.v} V), scaled`,f0(kek.fj_bit_mm*(V/kek.v)**2),r(kek.fj_bit_mm*(V/kek.v)**2)]);
  out.set(`<table><thead><tr><th>At ${f3(V)} V</th><th class="num">fJ per random bit·mm</th><th class="num">÷ Dally's 100</th></tr></thead><tbody>`+rows.map(q=>`<tr><td>${q[0]}</td><td class="num">${q[1]}</td><td class="num">${q[2]}</td></tr>`).join('')+'</tbody></table>');}
 setText('volttext',`Each measured value is scaled from ${V0} V as CV² (bands: the range over passes, cards and the hop length); the "everything" curves assume that the data-independent part scales the same way, and board power (hollow circles) is not scaled because it carries the regulator's loss. `+
  `<b>The data-dependent part reaches 100 fJ at ${f2(cross(HN.random_bit_data.mean))} V</b> on the loaded mesh and ${f2(cross(UN.random_bit_data.mean))} V on free links; everything included, at ${f2(cross(HN.random_bit_total.mean))}–${f2(cross(UN.random_bit_total.mean))} V; a plain 7 nm wire only at ${f1(cross(W485[2]))}–${f1(cross(W485[0]))} V. `+
  (d14?`At Dally's 2014 ${d14.v} V this mesh's data cost is ${f0(UN.random_bit_data.mean*sq(d14.v))}–${f0(HN.random_bit_data.mean*sq(d14.v))} fJ against his ${d14.fj_bit_mm}. `:'')+`Drag across the chart, use the slider or the buttons; hover, tap or tab to a point for its source.`);
 update();
})();

/* ---------- table of contents (anchors are in the template) ---------- */
(function(){const ol=document.getElementById('toclist'); if(!ol)return;
 ol.innerHTML=[...document.querySelectorAll('main h2')].map(h=>{if(!h.id)h.id=h.textContent.toLowerCase().replace(/^\d+\.\s*/,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,50);return `<li><a href="#${h.id}">${h.textContent.replace(/^\d+\.\s*/,'')}</a></li>`;}).join('');})();

/* ---------- the numeric sentences: every number below is computed from D ---------- */
(function(){
 const s09=D.scaled['0.9'], s05=D.scaled['0.5'], L=HOP, X=D.context||{}, C=W_.configs, CHK=W_.checks||{};
 const v=(cfg,key)=>C[cfg]&&C[cfg][key]?C[cfg][key].mean:null;
 const vc=(cfg,key,h)=>C[cfg]&&C[cfg][key]&&C[cfg][key].per_card[h]?C[cfg][key].per_card[h].mean:null;
 const pc=x=>`${f0(100*x)}%`;
 const span=(xs,fn)=>{const lo=Math.min(...xs),hi=Math.max(...xs);return fn(lo)===fn(hi)?fn(lo):`${fn(lo)}–${fn(hi)}`;};
 const pcs=xs=>`${span(xs.map(x=>100*x),f0)}%`;
 const sg=x=>`${x<0?'−':'+'}${Math.abs(x).toFixed(1)}`;
 const r5=x=>Math.round(20*x)*5, pc5=xs=>{const a=r5(Math.min(...xs)),b=r5(Math.max(...xs));return a===b?`about ${a}%`:`${a}–${b}%`;};
 function line(xs,ys){const n=xs.length,mx=xs.reduce((a,b)=>a+b,0)/n,my=ys.reduce((a,b)=>a+b,0)/n;let sxy=0,sxx=0;xs.forEach((x,i)=>{sxy+=(x-mx)*(ys[i]-my);sxx+=(x-mx)*(x-mx);});const s=sxy/sxx;return {slope:s,intercept:my-s*mx};}
 const slope=(pre,key,ds)=>line(ds,ds.map(d=>v(`${pre}${d}`,key))).slope;
 const slopeC=(pre,key,ds,h)=>line(ds,ds.map(d=>vc(`${pre}${d}`,key,h))).slope;   // the same on one card's means
 // how far the four-hop point sits off the line through the other distances `ref`, on one card
 const off4=(pre,ref,key,h)=>{const q=line(ref,ref.map(d=>vc(`${pre}${d}`,key,h)));return vc(`${pre}4`,key,h)/(q.slope*4+q.intercept)-1;};
 const byCard=xs=>xs.map((x,i)=>`${x} on ${W_.hosts[i]}`).join(' and ');   // "5% on aifoundry2 and 9% on aifoundry3"
 const kek=D.literature.find(l=>l.who.startsWith('Keckler')), KEK=kek?kek.fj_bit_mm:121;
 const dn=W_.disjoint_flows.noc_pj_per_byte, db=W_.disjoint_flows.pj_per_byte;
 const sh=c=>CHK.link_sharing&&CHK.link_sharing[c]?CHK.link_sharing[c].shared_link_hop_fraction:0;
 const hosts=W_.hosts;
 const D6=[1,2,3,4,6];

 /* the lede */
 setText('l-hop',`${f2(L)} mm`);
 setText('l-hoprange',`${f2(IN.hop_mm.range[0])}–${f2(IN.hop_mm.range[1])} mm`);
 setText('l-unc',`${f0(UN.random_bit_total.mean)} fJ`);
 setText('l-uncd',`${f0(UN.random_bit_data.mean)}`);
 setText('l-uncb',`${f0(UB.random_bit_total.mean)} fJ`);
 setText('l-load',`${f0(HN.random_bit_total.mean)} fJ on the mesh rail and ${f0(HB.random_bit_total.mean)} on board power`);
 const contN=[HN.random_bit_total.mean/UN.random_bit_total.mean-1, dn.wu.random_fj_per_bit_hop.mean/dn.wsep_d1_4.random_fj_per_bit_hop.mean-1];
 const contB=[HB.random_bit_total.mean/UB.random_bit_total.mean-1, db.wu.random_fj_per_bit_hop.mean/db.wsep_d1_4.random_fj_per_bit_hop.mean-1];
 setText('l-cont',`contention adds ${pc5(contN)} per millimetre on the mesh rail, and ${pc5(contB)} on board power`);
 // all ones against random data, per hop, per card: the mesh rail agrees on the two cards; board power is given per card
 const onesMoreC=k=>hosts.map(h=>slopeC('wu/p1/hop',k,D6,h)/slopeC('wu/p0.5/hop',k,D6,h)-1);
 const onesN=onesMoreC(NK), onesB=onesMoreC(BK);
 const onesTxt=`${pcs(onesN)} more on the mesh rail; on board power ${byCard(onesB.map(x=>pc(x)))}`;
 const onesLess1=[NK,BK].map(k=>1-v('wu/p1/hop1',k)/v('wu/p0.5/hop1',k));
 setText('l-ones',onesTxt);
 setText('l-ones1',pcs(onesLess1));
 setText('l-09',`${f0(UN.random_bit_data.mean*s09)}–${f0(HN.random_bit_data.mean*s09)} fJ per bit·mm`);
 setText('l-05',`${span([100/(UN.random_bit_data.mean*s05),100/(HN.random_bit_data.mean*s05)],f1)} times`);
 const drops=[].concat(...Object.values(W_.dropped||{}));
 const why=[...new Set(drops.map(x=>x.why))];
 setText('l-drop',`${drops.length} bursts${why.length===1&&why[0]==='service processor starved'?' (a starved meter)':''}`);

 /* 4. distance */
 const null0=(v('wu/p0.5/hop0',NK)-v('wu/p0/hop0',NK))/(v('wu/p0.5/hop1',NK)-v('wu/p0/hop1',NK));
 const d4=q=>[NK,BK].map(k=>CHK.d4_off_line[`wu/p${q}/${k}`]);
 const ex=k=>CHK.exit_step_hops[k];
 // per-hop increments on the mesh rail, per card (fJ per bit): the data-dependent part, and the data-independent part
 // (zeros) whose step from three to four hops stands out
 const incr=h=>{const dp=d=>(vc(`wu/p0.5/hop${d}`,NK,h)-vc(`wu/p0/hop${d}`,NK,h))*1000/8, z=d=>vc(`wu/p0/hop${d}`,NK,h)*1000/8;
  return {data:[dp(2)-dp(1),dp(3)-dp(2),dp(4)-dp(3),(dp(6)-dp(4))/2], zs:[z(2)-z(1),z(3)-z(2),(z(6)-z(4))/2], z34:z(4)-z(3)};};
 const INC=hosts.map(incr), incD=[].concat(...INC.map(q=>q.data)), incZ=[].concat(...INC.map(q=>q.zs)), incZ34=INC.map(q=>q.z34);
 const sepOff=hosts.map(h=>Math.abs(off4('wsep/p0.5/hop',[1,2,3,5],NK,h)));   // link-disjoint, random data, mesh rail
 setText('disttext',
  `On the mesh rail the data-dependent energy is zero at <i>d</i> = 0 (${f1(100*Math.abs(null0))}% of its one-hop value: the shire's own scratchpad does not use the mesh) and grows with every hop out to 6, by ${span(incD,f0)} fJ per bit per hop. `+
  `On this loaded mesh the step from three to four hops is larger, most clearly in the data-independent part (${span(incZ34,f0)} fJ per bit against ${span(incZ,f0)} for the other steps): on the mesh rail the four-hop point sits ${pcs([d4('0.5')[0],d4('0')[0]])} above the straight line through the others for random data and zeros, and ${pcs(d4('1'))} for all ones on both meters; on board power only the all-ones point is resolved from the line on both cards. `+
  `The step comes at the same distance as a jump in link sharing, from ${pc(sh('wu/p0.5/hop3'))} to ${pc(sh('wu/p0.5/hop4'))} of link-hops on shared links, but these runs do not show that one causes the other (<a href="#limits">§10</a>). With link-disjoint flows (section 6) the mesh rail grows linearly within the noise: its four-hop point sits ${pcs(sepOff)} off the line through the others for random data. `+
  `Leaving the shire adds a step of its own (the mesh-stop crossings) whose size depends on the data and the meter: about ${f1(ex('wu/p0.5/pj_per_byte'))} hops' worth for random data on board power, ${span([ex('wu/p0.5/noc_pj_per_byte'),ex('wu/random_minus_zeros/noc_pj_per_byte')],f2)} of a hop on the mesh rail in this sweep (${f1(ex('wsep/p0.5/noc_pj_per_byte'))} with link-disjoint flows), and almost nothing for all-ones data (${sg(Math.min(ex('wu/p1/pj_per_byte'),ex('wu/p1/noc_pj_per_byte')))} to ${sg(Math.max(ex('wu/p1/pj_per_byte'),ex('wu/p1/noc_pj_per_byte')))} hops). `+
  `The lines fan out with the density of ones; the all-ones line (<i>P</i> = 1) starts ${pcs(onesLess1)} below the random one at one hop but climbs faster (<a href="#ones">§5</a>).`);

 /* 5. ones */
 setText('onestext',
  `If the mesh's wires held their value between flits and only transitions cost energy, the per-hop cost would rise and fall as 2<i>P</i>(1−<i>P</i>): the same for all-zeros and all-ones, highest at <i>P</i> = ½, symmetric about it (dashed: the best fit of that shape, which misses both ends). `+
  `It does not: all-ones costs about as much per hop as random data (${onesTxt}, in the second run; the excess is resolved on both cards and both meters once the first run's passes are added), <i>P</i> = ¾ more than <i>P</i> = ¼, and the frozen line — half ones, no differences between flits at all — sits halfway up. `+
  `Two terms fit every bit density and the frozen line — <i>a</i>, an energy per bit that differs from the previous flit, and <i>b</i>, an energy per one carried — on both cards and both meters, to ${f2(HN.rms_pj_per_byte_hop)} pJ/B per hop on the mesh rail and ${f2(HB.rms_pj_per_byte_hop)} on board power (the block patterns of <a href="#lanes">§9</a> were not fitted: compared over the same hops, the 16–128 B blocks sit on its no-transition prediction, and on the mesh rail the 256 B blocks come in far below a full flip):`);
 const M=W_.model[SET].noc_rail, aN=M.toggle_fj_per_bit_transition_hop.mean, bN=M.ones_fj_per_one_bit_hop.mean, s0N=M.s0_pj_per_byte_hop.mean*1000/8;
 const fb=2*aN/(2*aN+bN), Et=aN/fb, Cmm=2*(Et/L)/(IN.noc_v.value*IN.noc_v.value);
 const onesToZeros=s0N/(s0N+bN);
 const dP=Math.sqrt(2*512*0.25/Math.PI)/512, save=bN*dP/(s0N+0.5*aN+0.5*bN);   // per-flit inversion of 512 random bits
 setText('modeltext',
  `On the mesh rail, on the loaded mesh, the fit gives <b>${f0(HN.per_transition.mean)} fJ per mm</b> per flit-to-flit difference and <b>${f0(HN.per_one.mean)}</b> per one carried, with no difference between the cards beyond the noise (per difference: ${cards(HN.per_transition,f0)}; per one: ${cards(HN.per_one,f0)}). `+
  `A cost per one-bit that does not need the bit to differ from the previous flit needs wires or nodes that rest at 0. The simplest case is ordinary logic whose output goes to 0 when no flit is present — a crossbar output with no grant, or data gated by valid. `+
  `Then each one rises and falls at the ends of a train of flits, and <i>a</i> and <i>b</i> are the same energy per transition, <i>E</i><sub>t</sub>, split by how often flits come back to back: if a fraction <i>f</i> of flits is followed directly by another, <i>a</i> = <i>f</i>·<i>E</i><sub>t</sub> and <i>b</i> = 2(1−<i>f</i>)·<i>E</i><sub>t</sub>, and the fitted <i>b</i>/<i>a</i> = ${f2(bN/aN)} gives <i>f</i> ≈ ${f1(fb)}. A transition then costs about ${f0(Et)} fJ per hop: ½<i>CV</i>² at ${IN.noc_v.value} V with <i>C</i> = ${f0(Cmm)} fF/mm, ordinary wire capacitance. `+
  `Precharged structures, such as buffer arrays with precharged read lines, would also do it. The fit cannot say which circuit it is — slowing the flows at a fixed distance would; it can say that the effect is the mesh's own: it is on the mesh rail, it grows with every hop, and it is absent at <i>d</i> = 0.`);
 setText('modeltext2',
  `Either way it matters for anyone encoding data for this mesh: <b>zeros are cheap to move, ones are not</b>. `+
  `Storing or sending ones-dense data complemented would make it cost what its complement costs: all-ones data would then cost what zeros cost per hop, ${pc(1-onesToZeros)} less; the data-independent part remains (the plane above has a button for it). For random data a per-flit inversion code would save about ${Math.max(1,Math.round(100*save))}%. On this chip the mesh is fixed, so only software can choose the representation.`);

 /* 6. contention */
 // one hop, all pairs against link-disjoint, mesh rail, per card: the totals' offsets (resolved on aifoundry3 only)
 const agR=hosts.map(h=>vc('wu/p0.5/hop1',NK,h)/vc('wsep/p0.5/hop1',NK,h)-1), agZ=hosts.map(h=>vc('wu/p0/hop1',NK,h)/vc('wsep/p0/hop1',NK,h)-1);
 const agUp=[...agR,...agZ].every(x=>x>0)?'higher':[...agR,...agZ].every(x=>x<0)?'lower':'different';
 const uD=dn.wu.random_minus_zeros_fj_per_bit_hop.mean, sD=dn.wsep_d1_4.random_minus_zeros_fj_per_bit_hop.mean;
 const uZ=dn.wu.zeros_fj_per_bit_hop.mean, sZ=dn.wsep_d1_4.zeros_fj_per_bit_hop.mean;
 const bwd=Math.max(...[1,2,3,4].map(d=>Math.abs(CHK.per_reader_gb_s[`wu/p0.5/hop${d}`]/CHK.per_reader_gb_s[`wsep/p0.5/hop${d}`]-1)));
 const rd=d=>CHK.link_sharing[`wsep/p0.5/hop${d}`].reader_shires;
 const xa=W_.axes['x/noc_pj_per_byte/random_bit_fj_per_bit_hop_d1_3'];
 const xz=line([1,2,3],[1,2,3].map(d=>v(`waxis/x/hop${d}/p0`,NK))).slope*1000/8;
 const bD=db.wsep_d1_4.random_minus_zeros_fj_per_bit_hop;
 setText('conttext',
  `In the all-pairs traffic of sections 4 and 5, flows share links more as the distance grows (none at one hop, ${pcs([sh('wu/p0.5/hop2'),sh('wu/p0.5/hop3')])} of link-hops at two and three, ${pc(sh('wu/p0.5/hop4'))} at four, ${pc(sh('wu/p0.5/hop6'))} at six, with dimension-ordered routing). `+
  `The second run added pairs chosen so that no two flows share a link and every scratchpad has one reader. At one hop, where neither set shares a link, the data-dependent parts agree within the noise; the totals on the mesh rail come out ${pcs(agR.map(Math.abs))} (random data) and ${pcs(agZ.map(Math.abs))} (zeros) ${agUp} for the all-pairs set, an offset resolved on aifoundry3 only (the all-pairs one-hop map puts two readers on some targets). `+
  `Beyond one hop the loaded mesh climbs faster: over the same one to four hops, <b>${f0(uD)} against ${f0(sD)} fJ per bit per hop</b> for the data-dependent part and ${f0(uZ)} against ${f0(sZ)} for the rest, on the mesh rail.`);
 setText('conttext2',
  `That is energy the loaded mesh spends beyond carrying the bits, most likely buffer writes and arbitration where flows meet; flits are not held long, since each reader's bandwidth is within ${Math.ceil(100*bwd)}% of what it gets on free links. It raises the data-independent part proportionally more (+${f0(100*(uZ/sZ-1))}% against +${f0(100*(uD/sD-1))}%). `+
  `The link-disjoint set also has only straight paths, one reader per target and fewer readers at long distances (${rd(1)} shires at one hop, ${rd(5)} at five), but straight x-only flows that do share links (the first run, one to three hops: ${span(Object.values(xa.per_card).map(c=>c.mean),f0)} and ${f0(xz)} fJ) cost about as much as the loaded mesh, which points to sharing rather than turns. `+
  `On board power only the total contrast is resolved: over one to four hops a random bit costs more per hop on the loaded mesh than on free links by ${byCard(hosts.map(h=>pc(db.wu.random_fj_per_bit_hop.per_card[h].mean/db.wsep_d1_4.random_fj_per_bit_hop.per_card[h].mean-1)))}; its split into a data-dependent and a fixed part is not resolved on that meter (<a href="#limits">§10</a>).`);

 /* 9. the block patterns */
 const A2=CHK.alt256||{}, ab=A2.board, an=A2.noc_rail;
 // the 16-128 B blocks against the no-transition prediction, like for like over the same d = 1, 3, 6 (blocksLFL)
 const lfN=blocksLFL(NK), lfDev=lfN?Math.max(...Object.values(lfN.per_card).map(c=>Math.abs(c.below))):null;
 const blk=lfN?` The 16–128 B blocks, a first-run pattern the model was not fitted to, sit on the no-transition prediction (all-zeros and all-ones averaged, over the same one, three and six hops) within about ${Math.max(1,Math.round(100*lfDev))}% on the mesh rail on both cards, and within the noise on board power.`:'';
 // the 256 B pattern's extra cost per hop as a fraction of a full flip, per card: (its slope - the 16-128 B level) / a
 const flip256=k=>{const src=srcOf(k), M1=W_.model.v1[src].toggle_fj_per_bit_transition_hop, P=W_.patterns;
  return hosts.map(h=>{const lv=meanOf([16,32,64,128].map(n=>P[`alt:${n}`][k].slope.per_card[h].mean)), a=M1.per_card[h];
   return (P['alt:256'][k].slope.per_card[h].mean-lv)/((typeof a==='number'?a:a.mean)*8/1000);});};
 if(ab&&an){
  const v1a=W_.model.v1.noc_rail.toggle_fj_per_bit_transition_hop.mean, v2a=W_.model.v2.noc_rail.toggle_fj_per_bit_transition_hop.mean;
  setText('alttext',
   `On the mesh rail the 256-byte pattern costs less than a full flip, every bit differing on every flit (dashed): its extra cost per hop is ${pcs(flip256(NK))} of that on both cards (on board power ${byCard(flip256(BK).map(x=>pc(x)))}, not resolved from a full flip), and it does not fall as more of the links are shared: `+
   `on the mesh rail it adds ${f2(an.increment_1_to_3)} pJ/B per hop from one to three hops, where ${pcs([sh('walt/n256/hop1'),sh('walt/n256/hop3')])} of link-hops are shared, and ${f2(an.increment_3_to_6)} from three to six, where ${pcs([sh('walt/n256/hop3'),sh('walt/n256/hop6')])} are. `+
   `So it is not other flows slipping in between, and the other in-flight load is unlikely too: in the first run its lines are identical to the first load's, yet the first run's cost per difference equals the second's (${f0(v1a)} against ${f0(v2a)} fJ per hop on the mesh rail). `+
   `Why is open; one possibility is that when all wires flip the same way together, the capacitance between neighbours is not charged. Most of the excess is paid on leaving the shire (${f2(an.excess_pj_per_byte_at_d['1'])} pJ/B at one hop on the mesh rail, ${f2(an.excess_per_hop)} per further hop).`+blk);
 } else if(blk) setText('alttext',blk.trim());

 /* 7. against the rule of thumb */
 const fp=D.first_principles, w485=fp.at_0485.per_random_bit_fj_mm, w09=fp.at_09.per_random_bit_fj_mm;
 const n09=[UN.random_bit_data.mean*s09,HN.random_bit_data.mean*s09];
 const tot=[UN.random_bit_total.mean,UB.random_bit_total.mean,HN.random_bit_total.mean,HB.random_bit_total.mean];
 const brk=Math.min(...n09)<100&&Math.max(...n09)>100?"brackets Dally's 100":(Math.max(...n09)<=100?"is below Dally's 100":"is above Dally's 100");
 const a09=[UN.random_bit_total.mean*s09,HN.random_bit_total.mean*s09];
 setText('comparetext',
  `At the voltage it runs at, the ET-SoC-1's mesh moves a random bit a millimetre on free links for <b>${f0(UN.random_bit_total.mean)}–${f0(UB.random_bit_total.mean)} fJ</b> in all (mesh rail to board), <b>${f0(UN.random_bit_data.mean)} fJ</b> of it data-dependent heat on the mesh rail (board power does not resolve that split on free links), and on the loaded mesh for ${f0(HN.random_bit_total.mean)}–${f0(HB.random_bit_total.mean)} fJ, ${f0(HN.random_bit_data.mean)}–${f0(HB.random_bit_data.mean)} of it data-dependent: in all, ${f2(Math.min(...tot)/100)}–${f2(Math.max(...tot)/100)} of Dally's 100 taken literally. `+
  `But 0.485 V is low: the same capacitance at 0.9 V would cost ${f2(s09)}× more, <b>${f0(n09[0])}–${f0(n09[1])} fJ</b> per random bit·mm for the mesh rail's data-dependent part (free links to loaded), which ${brk} and is ${f1(n09[0]/KEK)}–${f1(n09[1]/KEK)} of Keckler's ${KEK} (40 nm, 0.9 V). `+
  `Counting the data-independent part too, and assuming it also scales as CV², the figure at 0.9 V is ${f0(a09[0])}–${f0(a09[1])} fJ, ${Math.min(...a09)>100?"above Dally's 100":Math.max(...a09)<100?"below Dally's 100":"around Dally's 100"}. `+
  `Board power would say up to ${f0(HB.random_bit_data.mean*s09)} for the data-dependent part, but it carries the regulator's loss, which is not switched capacitance on the die.`);
 // 'at' the top of the plain-wire range when that top lies inside each card's 99% interval (t over passes) of the
 // free-link data cost; otherwise above or below it
 const T99={1:63.657,2:9.925,3:5.841,4:4.604,5:4.032,6:3.707};
 const wireIn=hosts.every(h=>{const c=UN.per_hop.random_bit_data.per_card[h], t=T99[c.n-1]||2.576, lo=(c.mean-t*c.se)/L, hi=(c.mean+t*c.se)/L;return w485[2]>=lo&&w485[2]<=hi;});
 const wireTop=wireIn?'at':UN.random_bit_data.mean>w485[2]?'above':'below';
 setText('comparetext2',
  `Being ${f1(n09[0]/KEK)}–${f1(n09[1]/KEK)} of Keckler's wire figure with the routers included is roughly what one would expect: wire capacitance per mm barely changes between process nodes (Dally 2018: "about 200fF/mm and independent of scaling"), and <b>the mesh's advantage over the 0.9 V literature is mostly V²</b>. `+
  `A plain repeated wire estimated from a predictive 7 nm kit (ASAP7) with Ho's repeater factors would cost ${f0(w485[0])}–${f0(w485[2])} fJ per random bit·mm at 0.485 V (${f0(w09[0])}–${f0(w09[2])} at 0.9 V, ${f1(w09[0]/KEK)}–${f1(w09[2]/KEK)} of Keckler's figure, which therefore holds more than an ideal wire or counts differently). The free-link mesh-rail data cost, ${f0(UN.random_bit_data.mean)}, is ${wireTop} the top of that range; these data cannot say how much the routers add.`);

 /* 8. in practice: every comparison on board power, the energy manual's meter */
 if(X.tload_dram_random_pj_per_byte){
  const perN=HN.random_bit_total.mean*8*L/1000, perB=HB.random_bit_total.mean*8*L/1000;   // pJ per byte per hop, loaded mesh
  const diag=10, ln=64, lb=line(D6,D6.map(d=>v(`wu/p0.5/hop${d}`,BK)));
  const hand=lb.intercept+diag*lb.slope;   // pJ per byte: the far scratchpad read, leaving the shire, ten hops
  const DR=X.tload_dram_random_pj_per_byte;   // like for like with the own-scratchpad figure: both are random-data tensor loads
  const FADDS=X.fadd_s_random_pj;   // scalar fadd.s on random data (energy manual §3.1), carried in report.json context
  const opB=32*HB.random_bit_total.mean*L/1000, opN=32*HN.random_bit_total.mean*L/1000, lane=X.fadd_ps_random_pj/8, lanes=opB/lane;
  const addMm=L/lanes, dallyX=Math.round(addMm/0.010/10)*10;   // Dally's 10 µm per add
  const EM='https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual';
  setText('practice',
   `<b>Per hop, a random byte costs ${f2(perN)}–${f2(perB)} pJ</b> on the loaded mesh (mesh rail to board, data-dependent and fixed together). `+
   `A 64-byte line carried between the two farthest shires — ${diag} hops, about ${f0(diag*L)} mm of mesh travel, extrapolated from the 1–6 hops measured — costs ${f1(ln*perN*diag/1000)}–${f1(ln*perB*diag/1000)} nJ in hops alone, against ${f1(ln*DR/1000)} nJ to read the same line from DRAM and ${f2(ln*X.own_scratchpad_pj_per_byte/1000)} nJ from the shire's own scratchpad (the <a href="${EM}#bytes-through-the-memory-hierarchy">energy manual</a>, board power, random-data tensor loads). `+
   `On the same meter the ten hops are ${f1(DR/(diag*perB))}× cheaper than the DRAM read, and the whole hand-off — the far scratchpad read and leaving the shire included, about ${f1(ln*hand/1000)} nJ per line — is about ${f1(DR/hand)}× cheaper. `+
   `Each hop adds about ${pc(perB/X.own_scratchpad_pj_per_byte)} of what reading the byte from the shire's own scratchpad costs (${f2(perB)} against ${f2(X.own_scratchpad_pj_per_byte)} pJ, board power).`);
  setText('practice2',
   `In Dally's currency — "an add is worth 10 µm of movement" — a 32-bit operand crossing one hop costs ${f1(opB)} pJ of board power (${f1(opN)} on the mesh rail alone), about ${f1(lanes)} lanes of an eight-lane <code>fadd.ps</code> on random data (${f1(lane)} pJ, with its share of instruction issue). `+
   `So on this chip one lane of a vector float add is worth ${f1(1/lanes)} of a hop — about ${f1(addMm)} mm — of movement, ${dallyX} times Dally's 10 µm, because an instruction here costs far more than the adder's own 1 fJ per bit`+
   (FADDS?`; a scalar <code>fadd.s</code> (${f1(FADDS)} pJ, <a href="${EM}#every-instruction-the-core-executes">energy manual, §3.1</a>) is worth about ${f0(FADDS/opB)} hops`:'')+'.');
 } else {
  // a secondary guard: build_wire_report.py stops when the energy manual's context is missing, so this should never show
  setText('practice','energy-manual context missing from report.json');
 }

 /* 10. limits */
 setText('axistext',`(The first run's x-only and y-only pairs differ in link sharing as well as in direction, so they cannot separate the two either.)`);
 const SN=W_.sensitivity&&W_.sensitivity.no_leak_correction;
 if(SN){
  const ch=[];['v1','v2'].forEach(st=>['toggle_fj_per_bit_transition_hop','ones_fj_per_one_bit_hop'].forEach(k=>ch.push(SN[st].board[k].mean/W_.model[st].board[k].mean-1)));
  const nm=Math.max(...['v1','v2'].map(st=>Math.abs(SN[st].noc_rail.toggle_fj_per_bit_transition_hop.mean/W_.model[st].noc_rail.toggle_fj_per_bit_transition_hop.mean-1)));
  setText('senstext',
   `Board-power numbers also depend on the leakage correction: without it the board coefficients come out ${pcs(ch)} higher (the second run's <i>a</i> ${f0(SN.v2.board.toggle_fj_per_bit_transition_hop.mean)} fJ against ${f0(W_.model.v2.board.toggle_fj_per_bit_transition_hop.mean)}), while the mesh-rail ones ${nm<0.005?'do not move':'move by '+pc(nm)}. `+
   `Three independent reductions of the same bursts, made for this page's review, agree within 3% on the mesh rail's coefficients (6% on the free-link fixed part) and within about 7% on board power, comparing like with like for the leakage correction.`);
 }
 // per-second bound: if the one-hop zeros energy were all paid per second, how much of the fixed part's slope over 1-4 hops it would explain
 const psb=(fam,k)=>{const ds=[1,2,3,4],z=ds.map(d=>v(`${fam}/p0/hop${d}`,k)),bw=ds.map(d=>CHK.per_reader_gb_s[`${fam}/p0.5/hop${d}`]);return line(ds,ds.map((d,i)=>z[0]*bw[0]/bw[i])).slope/line(ds,z).slope;};
 setText('persectext',`Even if all of the one-hop zeros energy were cost per second, on the mesh rail it would explain at most ${pc(psb('wsep',NK))} of the link-disjoint fixed part and ${pc(psb('wu',NK))} of the loaded one. On board power, whose one-hop energy also includes the scratchpad read and the cores, the same bound is about ${Math.round(10*psb('wsep',BK))*10}% for the link-disjoint part, poorly determined on both cards, and ${pc(psb('wu',BK))} for the loaded one, so it cannot rule out that most of the board's fixed part is per second.`);
 // what these runs leave open, with the numbers that make it open
 const dStep=q=>hosts.map(h=>off4(`wu/p${q}/hop`,[1,2,3,6],NK,h)-off4(`wsep/p${q}/hop`,[1,2,3,5],NK,h));   // loaded minus link-disjoint, four-hop point off its line
 const bZ=db.wsep_d1_4.zeros_fj_per_bit_hop;
 setText('opentext',
  `Whether link sharing causes the loaded mesh's larger step between three and four hops (<a href="#distance">§4</a>): the step comes where sharing jumps, and on the mesh rail the loaded set's four-hop point sits ${pcs(dStep('0.5'))} (random data) and ${pcs(dStep('0'))} (zeros) further above its line than the link-disjoint set's, a difference resolved only on aifoundry3 and only for random data. `+
  `How board power splits the cost on free links (<a href="#ones">§5</a>, <a href="#contention">§6</a>): the total, ${f0(UB.random_bit_total.mean)} fJ per bit·mm, is resolved on both cards, but its data-dependent part (${f0(bD.mean)} fJ per bit per hop, ${f0(bD.lo)}–${f0(bD.hi)} over passes) and fixed part (${f0(bZ.mean)}, ${f0(bZ.lo)}–${f0(bZ.hi)}) are not, and neither is how much each grows on the loaded mesh (to ${f0(db.wu.random_minus_zeros_fj_per_bit_hop.mean)} and ${f0(db.wu.zeros_fj_per_bit_hop.mean)}); most of that scatter comes from the leakage correction. `+
  `Whether the 256 B blocks cost less than a full flip on board power (<a href="#lanes">§9</a>): their extra cost per hop, as a share of a full flip's, is ${byCard(flip256(BK).map(x=>pc(x)))} and not resolved from 100%; on the mesh rail (${pcs(flip256(NK))}) it is.`);
 const dr=(W_.dropped.aifoundry2||[]).filter(x=>x.why==='service processor starved');
 if(dr.length){
  const a3max=Math.max(...['waxis/y/hop3/p0','waxis/y/hop3/p0.5'].map(c=>C[c]&&C[c].took_ms_max&&C[c].took_ms_max.aifoundry3||0));
  const nS=dr.map(x=>x.samples);
  setText('starvetext',
   `On aifoundry2 the set of y-only pairs 3 hops apart slowed the service processor's management path so much (${f1(Math.min(...dr.map(x=>x.median_took_ms))/1000)}–${f1(Math.max(...dr.map(x=>x.max_took_ms))/1000)} s per reading instead of 22 ms) that each burst had ${Math.min(...nS)===Math.max(...nS)?Math.min(...nS):Math.min(...nS)+' or '+Math.max(...nS)} readings; those ${dr.length} bursts are dropped. `+
   (a3max?`On aifoundry3 the same traffic delayed occasional readings to ${f1(a3max/1000)} s; those bursts were kept.`:''));
 }
})();
