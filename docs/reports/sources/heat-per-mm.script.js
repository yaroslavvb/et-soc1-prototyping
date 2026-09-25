const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
function hover(g,tip,h,html){const s=ev=>{tip.innerHTML=html();tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.max(0,Math.min(ev.clientX-b.left+12,b.width-290))+'px';tip.style.top=(ev.clientY-b.top+12)+'px';};g.addEventListener('mousemove',s);g.addEventListener('mouseleave',()=>tip.style.display='none');}
function path(pts,x,y){return pts.map((p,i)=>`${i?'L':'M'}${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join(' ');}
function axes(svg,o){const {W,H,L,R,T,B,x,y}=o;
 for(const t of o.yt){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,o.yf?o.yf(t):t,'tick','end');}
 for(const t of o.xt){txt(svg,x(t),H-B+16,o.xf?o.xf(t):t,'tick','middle');}
 if(o.xl)txt(svg,(L+W-R)/2,H-4,o.xl,'lab','middle');if(o.yl)txt(svg,4,T-10,o.yl,'lab');}
function whisker(g,x,y1,y2,col){el('line',{x1:x,x2:x,y1,y2,stroke:col,'stroke-width':1.4},g);el('line',{x1:x-3,x2:x+3,y1,y2:y1,stroke:col,'stroke-width':1.4},g);el('line',{x1:x-3,x2:x+3,y1:y2,y2,stroke:col,'stroke-width':1.4},g);}
const f0=v=>v.toFixed(0),f1=v=>v.toFixed(1),f2=v=>v.toFixed(2),f3=v=>v.toFixed(3);
const W_=D.wire, IN=D.inputs, HD=D.headline;
const SET=(W_.model.v2&&W_.model.v2.board&&W_.model.v2.board.toggle_fj_per_bit_transition_hop)?'v2':'v1';
const HB=HD[`${SET}/board`], HN=HD[`${SET}/noc_rail`], UB=HD['uncontended/board'], UN=HD['uncontended/noc_rail'];
const bar=(p,fn)=>p?`<b>${fn(p.mean)}</b> <span class="small">[${fn(p.lo)}–${fn(p.hi)}]</span>`:'—';
const cards=(p,fn)=>p&&p.per_card?Object.keys(p.per_card).sort().map(h=>`a${h.slice(-1)} ${fn(typeof p.per_card[h]==='number'?p.per_card[h]:p.per_card[h].mean)}`).join(' · '):'';
function setText(id,html){const e=document.getElementById(id);if(e)e.innerHTML=html;}

/* ---------- KPIs ---------- */
(function(){
 setText('k-hop',`${f2(IN.hop_mm.value)} mm`);
 setText('k-noc',`${f1(UN.random_bit_data.mean)} + ${f1(UN.fixed_per_bit.mean)} fJ`);
 setText('k-noc-sub',`data-dependent + fixed, 0.485 V, fitted over 1–4 hops; loaded mesh ${f1(HN.random_bit_data.mean)} + ${f1(HN.fixed_per_bit.mean)} (the model, 1–6 hops)`);
 setText('k-one',`${f0(HN.per_one.mean)} vs ${f0(HN.per_transition.mean)} fJ`);
 const s09=D.scaled['0.9'];
 setText('k-09',`${f0(UN.random_bit_data.mean*s09)}–${f0(HN.random_bit_data.mean*s09)} fJ`);
})();

/* ---------- 1. the die and the mesh ---------- */
(function(){
 const W=700,H=420,{svg,tip,h}=host('mesh',W,H);
 const dw=IN.die_w_mm.value, dh=IN.die_h_mm.value, px=IN.pitch_x_mm.value, py=IN.pitch_y_mm.value;
 const sc=Math.min((W-60)/dw,(H-60)/dh), ox=30, oy=24, X=v=>ox+v*sc, Y=v=>oy+v*sc;
 el('rect',{x:X(0),y:Y(0),width:dw*sc,height:dh*sc,fill:'none',stroke:'var(--ink-2)','stroke-width':1.5,rx:3},svg);
 const gx0=(dw-6*px)/2, gy0=(dh-6*py)/2, mw=gx0;
 for(let c=0;c<8;c++)for(let r=0;r<6;r++){
   const isMem=(c===0||c===7), corner=isMem&&(r===0||r===5);
   if(corner)continue;
   const x0=isMem?(c===0?0:dw-mw):gx0+(c-1)*px, w=isMem?mw:px, y0=gy0+r*py;
   const top=(r===0&&(c===5||c===6));
   const fill=isMem?'var(--c4)':top?'var(--c5)':'var(--c1)';
   const g=el('g',{},svg);
   el('rect',{x:X(x0)+1,y:Y(y0)+1,width:w*sc-2,height:py*sc-2,fill,'fill-opacity':isMem?0.35:top?0.35:0.18,stroke:fill,'stroke-width':1},g);
   el('circle',{cx:X(x0+w/2),cy:Y(y0+py/2),r:3.2,fill:'var(--ink)'},g);
   hover(g,tip,h,()=>isMem?'memory shire + LPDDR4x PHY strip, ≈'+f2(mw)+' mm wide':top?(c===5?'I/O or PCIe shire (the two sources disagree on the order)':'PCIe or I/O shire'):`minion shire tile, ${f2(px)} × ${f2(py)} mm`);
 }
 for(let c=1;c<7;c++)for(let r=0;r<6;r++){ if(c<6){el('line',{x1:X(gx0+(c-1)*px+px/2)+3,x2:X(gx0+c*px+px/2)-3,y1:Y(gy0+r*py+py/2),y2:Y(gy0+r*py+py/2),stroke:'var(--ink-2)','stroke-width':1},svg);} if(r<5){el('line',{x1:X(gx0+(c-1)*px+px/2),x2:X(gx0+(c-1)*px+px/2),y1:Y(gy0+r*py+py/2)+3,y2:Y(gy0+(r+1)*py+py/2)-3,stroke:'var(--ink-2)','stroke-width':1},svg);} }
 for(let r=1;r<5;r++){const yy=Y(gy0+r*py+py/2); el('line',{x1:X(mw/2)+3,x2:X(gx0+px/2)-3,y1:yy,y2:yy,stroke:'var(--ink-2)','stroke-width':1},svg); el('line',{x1:X(dw-mw/2)-3,x2:X(gx0+5*px+px/2)+3,y1:yy,y2:yy,stroke:'var(--ink-2)','stroke-width':1},svg);}
 const yb=Y(dh)+16; el('line',{x1:X(gx0),x2:X(gx0+px),y1:yb,y2:yb,stroke:'var(--c2)','stroke-width':2},svg); txt(svg,X(gx0+px/2),yb+14,`one hop ≈ ${f2(IN.hop_mm.value)} mm`,'lab-strong','middle');
 txt(svg,X(dw/2),Y(0)-8,`≈ ${f1(dw)} × ${f1(dh)} mm, ${IN.die_mm2.value} mm²`,'lab','middle');
 document.getElementById('meshcap').textContent=`Drawn to scale from the pitch measured on Esperanto's published die plot. 8 × 6 mesh stops: 34 minion shires (blue) — the 32 compute shires (1,024 minions) that the other reports count, plus the master shire, which runs the firmware, and a spare — the PCIe and I/O shires (pink, top row), and four memory shires with their LPDDR4x PHYs down each side (amber); the corners are empty. The 6 × 6 grid of the other reports is the inner six columns. Dots are mesh stops, lines the links between neighbours. Hover a tile.`;
})();

/* ---------- 2. energy against distance ---------- */
(function(){
 const pre=SET==='v2'?'wu/p':'wbern/p', Ps=SET==='v2'?['0','0.25','0.5','0.75','1']:['0','0.1','0.25','0.5','0.75','0.9','1'];
 const C=W_.configs; let key='pj_per_byte';
 const cols=['var(--c3)','var(--c1)','var(--c7)','var(--c2)','var(--c5)','var(--c4)','var(--bad)'];
 function draw(){
  const W=700,H=340,L=58,R2=150,T=30,B=46,{svg,tip,h}=host('dist',W,H);
  const ds=[0,1,2,3,4,6]; let mx=0;
  Ps.forEach(p=>ds.forEach(d=>{const c=C[`${pre}${p}/hop${d}`]; if(c&&c[key])mx=Math.max(mx,c[key].hi);}));
  mx*=1.08; const x=v=>L+(W-L-R2)*v/6.4, y=v=>H-B-(H-B-T)*v/mx;
  axes(svg,{W,H,L,R:R2,T,B,x,y,yt:[0,5,10,15,20,25].filter(v=>v<=mx),xt:ds,xl:'hops to the scratchpad read (0 = the shire’s own)',yl:(key==='pj_per_byte'?'board power':'mesh rail')+', pJ per payload byte above idle'});
  Ps.forEach((p,i)=>{const pts=[]; ds.forEach(d=>{const c=C[`${pre}${p}/hop${d}`]; if(!c||!c[key])return; pts.push([d,c[key].mean]);
     const g=el('g',{},svg); whisker(g,x(d),y(c[key].hi),y(c[key].lo),cols[i]); el('circle',{cx:x(d),cy:y(c[key].mean),r:3.5,fill:cols[i]},g);
     hover(g,tip,h,()=>`P(one) = ${p}, ${d} hop${d===1?'':'s'}<br>${f2(c[key].mean)} pJ/B [${f2(c[key].lo)}–${f2(c[key].hi)}], n = ${c[key].n}<br>${c.participants} readers, ${f0(c.gb_s)} GB/s`);});
   if(pts.length>1)el('path',{d:path(pts,x,y),class:'ln',stroke:cols[i],'stroke-width':1.3,'stroke-opacity':0.7},svg);
   el('rect',{x:W-R2+10,y:T+4+i*18,width:11,height:11,fill:cols[i]},svg); txt(svg,W-R2+26,T+14+i*18,`P(one) = ${p}`,'lab');});
  txt(svg,W-R2+10,T+Ps.length*18+22,'bars: range over','lab'); txt(svg,W-R2+10,T+Ps.length*18+38,'3 passes × 2 cards','lab');
 }
 const bx=document.getElementById('distbtn');
 bx.innerHTML=[['pj_per_byte','board power'],['noc_pj_per_byte','mesh rail only']].map(b=>`<button type="button" data-k="${b[0]}" aria-pressed="${b[0]===key}">${b[1]}</button>`).join('');
 bx.querySelectorAll('button').forEach(b=>b.onclick=()=>{key=b.dataset.k;bx.querySelectorAll('button').forEach(q=>q.setAttribute('aria-pressed',q.dataset.k===key));draw();});
 draw();
})();

/* ---------- 3. what a bit costs per hop: ones and transitions ---------- */
(function(){
 let src='board';
 function draw(){
  const W=720,H=340,L=58,R2=190,T=30,B=46,{svg,tip,h}=host('model',W,H);
  const key=src==='board'?'pj_per_byte':'noc_pj_per_byte';
  const sets=[['v1','wbern/p',['0','0.1','0.25','0.5','0.75','0.9','1'],'var(--c1)','first run: repeated 512 B image'],['v2','wu/p',['0','0.25','0.5','0.75','1'],'var(--c2)','second run: every line unique']];
  let mx=0; const pts=[];
  sets.forEach(s=>{const pat=W_.patterns||{}; s[2].forEach(p=>{const e=(s[0]==='v1'?pat[`bern:${p}`]:null); });});
  // slopes per pattern come from the model's per-pass points
  sets.forEach(s=>{const m=W_.model[s[0]]&&W_.model[s[0]][src]; if(!m||!m.per_pass)return;
    const acc={}; for(const hst in m.per_pass)m.per_pass[hst].forEach(f=>f.points.forEach(q=>{(acc[q.pattern]=acc[q.pattern]||{t:q.toggle,o:q.ones,v:[]}).v.push(q.slope);}));
    for(const k in acc){const a=acc[k],v=a.v; const mean=v.reduce((x,y)=>x+y,0)/v.length; pts.push({set:s,k,t:a.t,o:a.o,mean,lo:Math.min(...v),hi:Math.max(...v),n:v.length}); mx=Math.max(mx,Math.max(...v));}});
  mx*=1.12; const x=v=>L+(W-L-R2)*v, y=v=>H-B-(H-B-T)*v/mx;
  axes(svg,{W,H,L,R:R2,T,B,x,y,yt:[0,0.5,1,1.5,2,2.5,3].filter(v=>v<=mx),xt:[0,0.25,0.5,0.75,1],xl:'density of ones in the data, P',yl:`${src==='board'?'board power':'mesh rail'}: pJ per payload byte per hop (slope)`});
  const M=W_.model[SET][src], a=M.toggle_fj_per_bit_transition_hop.mean*8/1000, b=M.ones_fj_per_one_bit_hop.mean*8/1000, s0=M.s0_pj_per_byte_hop.mean;
  const curve=[],tog=[]; for(let p=0;p<=1.0001;p+=0.02){curve.push([p,s0+a*2*p*(1-p)+b*p]);}
  // the best pure-transition model (no ones term), fitted to the same points, for contrast
  const pp=pts.filter(q=>q.set[0]===SET&&!q.k.startsWith('wfrz')); let sxx=0,sx=0,sy=0,sxy=0,n=0; pp.forEach(q=>{sxx+=q.t*q.t;sx+=q.t;sy+=q.mean;sxy+=q.t*q.mean;n++;});
  const aT=(n*sxy-sx*sy)/(n*sxx-sx*sx), bT=(sy-aT*sx)/n; for(let p=0;p<=1.0001;p+=0.02)tog.push([p,bT+aT*2*p*(1-p)]);
  el('path',{d:path(tog,x,y),class:'ln',stroke:'var(--ref)','stroke-dasharray':'5 4','stroke-width':1.5},svg);
  el('path',{d:path(curve,x,y),class:'ln',stroke:'var(--ink)','stroke-width':1.6},svg);
  pts.forEach(q=>{const g=el('g',{},svg); const xx=x(q.o)+(q.set[0]==='v1'?-3:3); const col=q.k.startsWith('wfrz')?'var(--c3)':q.set[3];
    whisker(g,xx,y(q.hi),y(q.lo),col); el(q.k.startsWith('wfrz')?'rect':'circle',q.k.startsWith('wfrz')?{x:xx-4,y:y(q.mean)-4,width:8,height:8,fill:col}:{cx:xx,cy:y(q.mean),r:4,fill:col},g);
    hover(g,tip,h,()=>`<b>${q.k.replace(/\/$/,'')}</b> (${q.set[4]})<br>ones ${f3(q.o)}, bits differing from the previous flit ${f3(q.t)}<br>${f3(q.mean)} pJ/B per hop [${f3(q.lo)}–${f3(q.hi)}], n = ${q.n}<br>model: ${f3(s0+a*q.t+b*q.o)}`);});
  const lg=[['var(--c1)','first run: one 512 B image'],['var(--c2)','second run: lines unique'],['var(--c3)','second run: frozen line (■)'],['var(--ink)','ones + differences'],['var(--ref)','differences only']];
  lg.forEach((l,i)=>{el(i<3?'rect':'line',i<3?{x:W-R2+10,y:T+4+i*18,width:11,height:11,fill:l[0]}:{x1:W-R2+10,x2:W-R2+22,y1:T+10+i*18,y2:T+10+i*18,stroke:l[0],'stroke-width':2,'stroke-dasharray':i===4?'4 3':''},svg); txt(svg,W-R2+28,T+14+i*18,l[1],'lab');});
 }
 const bx=document.getElementById('modelbtn');
 bx.innerHTML=[['board','board power'],['noc_rail','mesh rail only']].map(b=>`<button type="button" data-k="${b[0]}" aria-pressed="${b[0]===src}">${b[1]}</button>`).join('');
 bx.querySelectorAll('button').forEach(b=>b.onclick=()=>{src=b.dataset.k;bx.querySelectorAll('button').forEach(q=>q.setAttribute('aria-pressed',q.dataset.k===src));draw();});
 draw();
})();

/* ---------- the model table ---------- */
(function(){
 const rows=[['<i>a</i>: per flit-to-flit difference (a bit that differs from the same bit of the previous flit)','per_transition'],['<i>b</i>: per one-bit carried (a 1, whether it changed or not)','per_one'],['per random payload bit, data-dependent part (½<i>a</i> + ½<i>b</i>)','random_bit_data'],['per payload bit, independent of the data (clocking, headers, requests)','fixed_per_bit']];
 const t=document.getElementById('modeltab'); if(!t)return;
 t.innerHTML='<thead><tr><th>At 0.485 V, 400 MHz; the model on the loaded mesh</th><th class="num">mesh rail, fJ per hop</th><th class="num">fJ per mm</th><th class="num">board power, fJ per hop</th><th class="num">fJ per mm</th></tr></thead><tbody>'+
  rows.map(r=>`<tr><td>${r[0]}</td><td class="num">${bar(HN.per_hop[r[1]],f0)}</td><td class="num">${bar(HN[r[1]],f1)}</td><td class="num">${bar(HB.per_hop[r[1]],f0)}</td><td class="num">${bar(HB[r[1]],f1)}</td></tr>`).join('')+
  `<tr><td colspan="5"><b>With every flow on its own links</b>, fitted over 1–4 hops (only random and zeros were run this way)</td></tr>`+
  `<tr><td>per random payload bit, data-dependent part</td><td class="num">${bar(UN.per_hop.random_bit_data,f0)}</td><td class="num">${bar(UN.random_bit_data,f1)}</td><td class="num">${bar(UB.per_hop.random_bit_data,f0)}</td><td class="num">${bar(UB.random_bit_data,f1)}</td></tr>`+
  `<tr><td>per payload bit, independent of the data</td><td class="num">${bar(UN.per_hop.fixed_per_bit,f0)}</td><td class="num">${bar(UN.fixed_per_bit,f1)}</td><td class="num">${bar(UB.per_hop.fixed_per_bit,f0)}</td><td class="num">${bar(UB.fixed_per_bit,f1)}</td></tr>`+
  `<tr><td><b>A random payload bit, everything, free links</b></td><td class="num">—</td><td class="num"><b>${f1(UN.random_bit_total.mean)}</b> <span class="small">[${f1(UN.random_bit_total.lo)}–${f1(UN.random_bit_total.hi)}]</span></td><td class="num">—</td><td class="num"><b>${f1(UB.random_bit_total.mean)}</b> <span class="small">[${f1(UB.random_bit_total.lo)}–${f1(UB.random_bit_total.hi)}]</span></td></tr>`+
  `<tr><td colspan="5"><b>On the loaded mesh</b> (all pairs, sections 4–5; the model fitted over 1–6 hops)</td></tr>`+
  `<tr><td><b>A random payload bit, everything, loaded mesh</b></td><td class="num">—</td><td class="num"><b>${f1(HN.random_bit_total.mean)}</b> <span class="small">[${f1(HN.random_bit_total.lo)}–${f1(HN.random_bit_total.hi)}]</span></td><td class="num">—</td><td class="num"><b>${f1(HB.random_bit_total.mean)}</b> <span class="small">[${f1(HB.random_bit_total.lo)}–${f1(HB.random_bit_total.hi)}]</span></td></tr>`+
  `<tr><td colspan="5" class="small">Fit per card and pass over ${SET==='v2'?'five bit densities and the frozen line':'seven bit densities'}, then pooled: bold is the mean, brackets the range over passes and cards, with the hop length’s range (${IN.hop_mm.range[0]}–${IN.hop_mm.range[1]} mm) folded into the per-mm bars. Residual of the fit: ${f3(HN.rms_pj_per_byte_hop)} pJ/B/hop on the mesh rail, ${f3(HB.rms_pj_per_byte_hop)} on board power. Over the same 1–4 hops as the free-link rows, the loaded mesh rail gives ${f0(W_.disjoint_flows.noc_pj_per_byte.wu.random_minus_zeros_fj_per_bit_hop.mean/IN.hop_mm.value)} + ${f0(W_.disjoint_flows.noc_pj_per_byte.wu.zeros_fj_per_bit_hop.mean/IN.hop_mm.value)} fJ/mm (section 6).</td></tr></tbody>`;
})();

/* ---------- 4. lanes and flit width ---------- */
(function(){
 const W=700,H=280,L=58,R2=16,T=30,B=46,{svg,tip,h}=host('alt',W,H);
 const Ns=[16,32,64,128,256]; const P=W_.patterns; const v=Ns.map(n=>P[`alt:${n}`]&&P[`alt:${n}`].pj_per_byte.slope).filter(Boolean);
 if(!v.length)return; const M0=W_.model.v1.board; const mx=Math.max(...v.map(q=>q.hi),M0.s0_pj_per_byte_hop.mean+(M0.ones_fj_per_one_bit_hop.mean*0.5+M0.toggle_fj_per_bit_transition_hop.mean)*8/1000)*1.1;
 const bw=(W-L-R2)/Ns.length, x=i=>L+bw*i+bw/2, y=q=>H-B-(H-B-T)*q/mx;
 axes(svg,{W,H,L,R:R2,T,B,x,y,yt:[0,0.5,1,1.5,2,2.5].filter(q=>q<=mx),xt:[],yl:'board power: pJ per payload byte per hop'});
 const M=W_.model.v1.board, a=M.toggle_fj_per_bit_transition_hop.mean*8/1000, b=M.ones_fj_per_one_bit_hop.mean*8/1000, s0=M.s0_pj_per_byte_hop.mean;
 Ns.forEach((n,i)=>{const e=P[`alt:${n}`]; if(!e)return; const s=e.pj_per_byte.slope; const g=el('g',{},svg);
   el('rect',{x:x(i)-bw*0.28,y:y(s.mean),width:bw*0.56,height:H-B-y(s.mean),fill:n===256?'var(--c2)':'var(--c1)','fill-opacity':0.8},g); whisker(g,x(i),y(s.hi),y(s.lo),'var(--ink)');
   const tl=n===256?1:0; const pred=s0+b*0.5+a*tl; el('line',{x1:x(i)-bw*0.34,x2:x(i)+bw*0.34,y1:y(pred),y2:y(pred),stroke:'var(--ink)','stroke-dasharray':'4 3','stroke-width':1.5},svg);
   txt(svg,x(i),H-B+16,`${n} B`,'tick','middle');
   hover(g,tip,h,()=>`blocks of ${n} B, alternately all-0 and all-1<br>${f3(s.mean)} pJ/B per hop [${f3(s.lo)}–${f3(s.hi)}]<br>on one lane consecutive lines are i and i+4: ${n<=128?'the same block value, no transitions':'opposite values, every bit flips'}<br>dashed: the model with ${tl} transitions per bit`);});
 txt(svg,(L+W-R2)/2,H-4,'block size N (half the pattern period)','lab','middle');
})();

/* ---------- 5. against the literature ---------- */
(function(){
 const s09=D.scaled['0.9'];
 const rows=[
  ['ET-SoC-1 mesh rail, data, free links, 0.485 V',UN.random_bit_data,'var(--c1)','measured: link-disjoint flows'],
  ['ET-SoC-1 mesh rail, everything, free links',UN.random_bit_total,'var(--c1)','measured: link-disjoint flows'],
  ['ET-SoC-1 board power, everything, free links',UB.random_bit_total,'var(--c1)','measured: link-disjoint flows'],
  ['ET-SoC-1 mesh rail, everything, loaded mesh',HN.random_bit_total,'var(--c1)','measured: all pairs'],
  ['ET-SoC-1 board power, everything, loaded mesh',HB.random_bit_total,'var(--c1)','measured: all pairs'],
  ['ET-SoC-1 mesh rail data, free links, at 0.9 V (× '+f2(s09)+')',{mean:UN.random_bit_data.mean*s09,lo:UN.random_bit_data.lo*s09,hi:UN.random_bit_data.hi*s09},'var(--c7)','scaled'],
  ['ET-SoC-1 mesh rail data, loaded, at 0.9 V',{mean:HN.random_bit_data.mean*s09,lo:HN.random_bit_data.lo*s09,hi:HN.random_bit_data.hi*s09},'var(--c7)','scaled'],
  ['ET-SoC-1 mesh rail, everything, loaded mesh, at 0.9 V',{mean:HN.random_bit_total.mean*s09,lo:HN.random_bit_total.lo*s09,hi:HN.random_bit_total.hi*s09},'var(--c7)','scaled; assumes the fixed part is also C·V²'],
  ...D.literature.filter(l=>l.fj_bit_mm<300).map(l=>[`${l.who}${l.v?' ('+l.v+' V)':''}`,{mean:l.fj_bit_mm,lo:(l.range||[l.fj_bit_mm])[0],hi:(l.range||[0,l.fj_bit_mm])[1]||l.fj_bit_mm},'var(--c2)',l.conditions]),
  ['plain 7 nm repeated wire, first principles, 0.485 V',{mean:D.first_principles.at_0485.per_random_bit_fj_mm[1],lo:D.first_principles.at_0485.per_random_bit_fj_mm[0],hi:D.first_principles.at_0485.per_random_bit_fj_mm[2]},'var(--c3)','200–400 fF/mm, ½CV² per transition, half the bits flip'],
  ['plain 7 nm repeated wire, first principles, 0.9 V',{mean:D.first_principles.at_09.per_random_bit_fj_mm[1],lo:D.first_principles.at_09.per_random_bit_fj_mm[0],hi:D.first_principles.at_09.per_random_bit_fj_mm[2]},'var(--c3)','same, at 0.9 V']];
 const W=700,rh=24,L=330,R2=20,T=34,B=36,H=T+rows.length*rh+B,{svg,tip,h}=host('comparechart',W,H);
 const lo=5,hi=400,x=v=>L+(W-L-R2)*Math.log10(v/lo)/Math.log10(hi/lo);
 [5,10,20,50,100,200,400].forEach(v=>{el('line',{x1:x(v),x2:x(v),y1:T-6,y2:H-B,class:'grid-line'},svg);txt(svg,x(v),H-B+16,v,'tick','middle');});
 txt(svg,(L+W-R2)/2,H-6,'fJ per random bit per mm (log)','lab','middle');
 rows.forEach((r,i)=>{const y0=T+i*rh; const g=el('g',{},svg); txt(g,L-8,y0+15,r[0],'lab','end');
   el('rect',{x:x(lo),y:y0+5,width:Math.max(1,x(r[1].mean)-x(lo)),height:rh-10,fill:r[2],'fill-opacity':0.75},g);
   if(r[1].hi>r[1].lo){const yc=y0+rh/2; el('line',{x1:x(r[1].lo),x2:x(r[1].hi),y1:yc,y2:yc,stroke:'var(--ink)','stroke-width':1.4},g);
     [r[1].lo,r[1].hi].forEach(v=>el('line',{x1:x(v),x2:x(v),y1:yc-5,y2:yc+5,stroke:'var(--ink)','stroke-width':1.4},g));}
   txt(g,x(r[1].hi)+6,y0+15,f0(r[1].mean),'tick');
   hover(g,tip,h,()=>`<b>${r[0]}</b><br>${f1(r[1].mean)} fJ per random bit·mm${r[1].hi>r[1].lo?` [${f1(r[1].lo)}–${f1(r[1].hi)}]`:''}<br>${r[3]}`);});
 el('line',{x1:x(100),x2:x(100),y1:T-10,y2:H-B,stroke:'var(--c2)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg); txt(svg,x(100)+4,T-12,'Dally ~100','lab');
})();

/* ---------- table of contents and anchors are in the template ---------- */
(function(){const ol=document.getElementById('toclist'); if(!ol)return;
 ol.innerHTML=[...document.querySelectorAll('main h2')].map(h=>{if(!h.id)h.id=h.textContent.toLowerCase().replace(/^\d+\.\s*/,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,50);return `<li><a href="#${h.id}">${h.textContent.replace(/^\d+\.\s*/,'')}</a></li>`;}).join('');})();

/* ---------- the numeric sentences: every number below is computed from D ---------- */
(function(){
 const s09=D.scaled['0.9'], s05=D.scaled['0.5'], L=IN.hop_mm.value, X=D.context||{}, C=W_.configs, CK=W_.checks||{};
 const v=(cfg,key)=>C[cfg]&&C[cfg][key]?C[cfg][key].mean:null;
 const vc=(cfg,key,h)=>C[cfg]&&C[cfg][key]&&C[cfg][key].per_card[h]?C[cfg][key].per_card[h].mean:null;
 const pc=x=>`${f0(100*x)}%`;
 const span=(xs,fn)=>{const lo=Math.min(...xs),hi=Math.max(...xs);return fn(lo)===fn(hi)?fn(lo):`${fn(lo)}–${fn(hi)}`;};
 const pcs=xs=>`${span(xs.map(x=>100*x),f0)}%`;
 const sg=x=>`${x<0?'\u2212':'+'}${Math.abs(x).toFixed(1)}`;
 const r5=x=>Math.round(20*x)*5, pc5=xs=>{const a=r5(Math.min(...xs)),b=r5(Math.max(...xs));return a===b?`about ${a}%`:`${a}–${b}%`;};
 function line(xs,ys){const n=xs.length,mx=xs.reduce((a,b)=>a+b,0)/n,my=ys.reduce((a,b)=>a+b,0)/n;let sxy=0,sxx=0;xs.forEach((x,i)=>{sxy+=(x-mx)*(ys[i]-my);sxx+=(x-mx)*(x-mx);});const s=sxy/sxx;return {slope:s,intercept:my-s*mx};}
 const slope=(pre,key,ds)=>line(ds,ds.map(d=>v(`${pre}${d}`,key))).slope;
 const kek=D.literature.find(l=>l.who.startsWith('Keckler')), KEK=kek?kek.fj_bit_mm:121;
 const dn=W_.disjoint_flows.noc_pj_per_byte, db=W_.disjoint_flows.pj_per_byte;
 const sh=c=>CK.link_sharing&&CK.link_sharing[c]?CK.link_sharing[c].shared_link_hop_fraction:0;
 const hosts=W_.hosts;
 const NK='noc_pj_per_byte', BK='pj_per_byte', D6=[1,2,3,4,6];

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
 const onesMore=[NK,BK].map(k=>slope('wu/p1/hop',k,D6)/slope('wu/p0.5/hop',k,D6)-1);
 const onesLess1=[NK,BK].map(k=>1-v('wu/p1/hop1',k)/v('wu/p0.5/hop1',k));
 setText('l-ones',pcs(onesMore));
 setText('l-ones1',pcs(onesLess1));
 setText('l-09',`${f0(UN.random_bit_data.mean*s09)}–${f0(HN.random_bit_data.mean*s09)} fJ per bit·mm`);
 setText('l-05',`${span([100/(UN.random_bit_data.mean*s05),100/(HN.random_bit_data.mean*s05)],f1)} times`);
 const drops=[].concat(...Object.values(W_.dropped||{}));
 const why=[...new Set(drops.map(x=>x.why))];
 setText('l-drop',`${drops.length} bursts${why.length===1&&why[0]==='service processor starved'?' (a starved meter)':''}`);

 /* 4. distance */
 const null0=(v('wu/p0.5/hop0',NK)-v('wu/p0/hop0',NK))/(v('wu/p0.5/hop1',NK)-v('wu/p0/hop1',NK));
 const d4=q=>[NK,BK].map(k=>CK.d4_off_line[`wu/p${q}/${k}`]);
 const ex=k=>CK.exit_step_hops[k];
 const sepLin=Math.max(CK.wsep_max_off_line['wsep/p0/noc_pj_per_byte'],CK.wsep_max_off_line['wsep/p0.5/noc_pj_per_byte']);
 setText('disttext',
  `On the mesh rail the data-dependent energy is zero at <i>d</i> = 0 (${f1(100*Math.abs(null0))}% of its one-hop value: the shire's own scratchpad does not use the mesh) and grows by nearly the same amount with every hop out to 6. `+
  `On this loaded mesh the step from three to four hops is larger — the four-hop point sits ${pcs([...d4('0.5'),...d4('0')])} above the straight line through the others for random data and zeros, ${pcs(d4('1'))} for all ones — where the share of link-hops on shared links jumps from ${pc(sh('wu/p0.5/hop3'))} to ${pc(sh('wu/p0.5/hop4'))}; with link-disjoint flows (section 6) the mesh rail grows linearly to within ${Math.max(1,Math.ceil(100*sepLin))}%. `+
  `Leaving the shire adds a step of its own (the mesh-stop crossings) whose size depends on the data and the meter: about ${f1(ex('wu/p0.5/pj_per_byte'))} hops' worth for random data on board power, ${span([ex('wu/p0.5/noc_pj_per_byte'),ex('wu/random_minus_zeros/noc_pj_per_byte')],f2)} of a hop on the mesh rail in this sweep (${f1(ex('wsep/p0.5/noc_pj_per_byte'))} with link-disjoint flows), and almost nothing for all-ones data (${sg(Math.min(ex('wu/p1/pj_per_byte'),ex('wu/p1/noc_pj_per_byte')))} to ${sg(Math.max(ex('wu/p1/pj_per_byte'),ex('wu/p1/noc_pj_per_byte')))} hops). `+
  `The lines fan out with the density of ones; the all-ones line (<i>P</i> = 1) starts ${pcs(onesLess1)} below the random one at one hop and climbs ${pcs(onesMore)} faster.`);

 /* 5. ones */
 setText('onestext',
  `If the mesh's wires held their value between flits and only transitions cost energy, the per-hop cost would follow 2<i>P</i>(1−<i>P</i>): zero for all-zeros and for all-ones, highest at <i>P</i> = ½, symmetric about it (dashed). `+
  `It does not: all-ones costs about as much per hop as random data (${pcs(onesMore)} more), <i>P</i> = ¾ more than <i>P</i> = ¼, and the frozen line — half ones, no differences between flits at all — sits halfway up. `+
  `Two terms fit every pattern — <i>a</i>, an energy per bit that differs from the previous flit, and <i>b</i>, an energy per one carried — on both cards and both meters, to ${f2(HN.rms_pj_per_byte_hop)} pJ/B per hop on the mesh rail and ${f2(HB.rms_pj_per_byte_hop)} on board power:`);
 const M=W_.model[SET].noc_rail, aN=M.toggle_fj_per_bit_transition_hop.mean, bN=M.ones_fj_per_one_bit_hop.mean, s0N=M.s0_pj_per_byte_hop.mean*1000/8;
 const fb=2*aN/(2*aN+bN), Et=aN/fb, Cmm=2*(Et/L)/(IN.noc_v.value*IN.noc_v.value);
 const onesToZeros=s0N/(s0N+bN);
 const dP=Math.sqrt(2*512*0.25/Math.PI)/512, save=bN*dP/(s0N+0.5*aN+0.5*bN);   // per-flit inversion of 512 random bits
 setText('modeltext',
  `On the mesh rail, on the loaded mesh, the fit gives <b>${f0(HN.per_transition.mean)} fJ per mm</b> per flit-to-flit difference and <b>${f0(HN.per_one.mean)}</b> per one carried, the same within a few percent on both cards (per one: ${cards(HN.per_one,f0)}). `+
  `A cost per one-bit that does not need the bit to differ from the previous flit needs wires or nodes that rest at 0. The simplest case is ordinary logic whose output goes to 0 when no flit is present — a crossbar output with no grant, or data gated by valid. `+
  `Then each one rises and falls at the ends of a train of flits, and <i>a</i> and <i>b</i> are the same energy per transition, <i>E</i><sub>t</sub>, split by how often flits come back to back: if a fraction <i>f</i> of flits is followed directly by another, <i>a</i> = <i>f</i>·<i>E</i><sub>t</sub> and <i>b</i> = 2(1−<i>f</i>)·<i>E</i><sub>t</sub>, and the fitted <i>b</i>/<i>a</i> = ${f2(bN/aN)} gives <i>f</i> ≈ ${f1(fb)}. A transition then costs about ${f0(Et)} fJ per hop: ½<i>CV</i>² at ${IN.noc_v.value} V with <i>C</i> = ${f0(Cmm)} fF/mm, ordinary wire capacitance. `+
  `Precharged structures, such as buffer arrays with precharged read lines, would also do it. The fit cannot say which circuit it is — slowing the flows at a fixed distance would; it can say that the effect is the mesh's own: it is on the mesh rail, it grows with every hop, and it is absent at <i>d</i> = 0.`);
 setText('modeltext2',
  `Either way it matters for anyone encoding data for this mesh: <b>zeros are cheap to move, ones are not</b>. `+
  `Storing or sending ones-dense data complemented would make it cost what its complement costs: all-ones data would then cost what zeros cost, ${pc(onesToZeros)} of its present per-hop cost, since the data-independent part remains. For random data a per-flit inversion code would save about ${Math.max(1,Math.round(100*save))}%. On this chip the mesh is fixed, so only software can choose the representation.`);

 /* 6. contention */
 const agD=(v('wu/p0.5/hop1',NK)-v('wu/p0/hop1',NK))/(v('wsep/p0.5/hop1',NK)-v('wsep/p0/hop1',NK))-1;
 const agR=v('wu/p0.5/hop1',NK)/v('wsep/p0.5/hop1',NK)-1, agZ=v('wu/p0/hop1',NK)/v('wsep/p0/hop1',NK)-1;
 const uD=dn.wu.random_minus_zeros_fj_per_bit_hop.mean, sD=dn.wsep_d1_4.random_minus_zeros_fj_per_bit_hop.mean;
 const uZ=dn.wu.zeros_fj_per_bit_hop.mean, sZ=dn.wsep_d1_4.zeros_fj_per_bit_hop.mean;
 const bwd=Math.max(...[1,2,3,4].map(d=>Math.abs(CK.per_reader_gb_s[`wu/p0.5/hop${d}`]/CK.per_reader_gb_s[`wsep/p0.5/hop${d}`]-1)));
 const rd=d=>CK.link_sharing[`wsep/p0.5/hop${d}`].reader_shires;
 const xa=W_.axes['x/noc_pj_per_byte/random_bit_fj_per_bit_hop_d1_3'];
 const xz=line([1,2,3],[1,2,3].map(d=>v(`waxis/x/hop${d}/p0`,NK))).slope*1000/8;
 const bD=db.wsep_d1_4.random_minus_zeros_fj_per_bit_hop;
 setText('conttext',
  `In the all-pairs traffic of sections 4 and 5, flows share links more as the distance grows (none at one hop, ${pcs([sh('wu/p0.5/hop2'),sh('wu/p0.5/hop3')])} of link-hops at two and three, ${pc(sh('wu/p0.5/hop4'))} at four, ${pc(sh('wu/p0.5/hop6'))} at six, with dimension-ordered routing). `+
  `The second run added pairs chosen so that no two flows share a link and every scratchpad has one reader. At one hop, where neither set shares a link, the data-dependent parts agree within ${Math.ceil(100*Math.abs(agD))}%, and the totals within ${Math.ceil(100*Math.abs(agR))}% for random data and ${Math.ceil(100*Math.abs(agZ))}% for zeros on the mesh rail (the all-pairs one-hop map puts two readers on some targets). `+
  `Beyond one hop the loaded mesh climbs faster: over the same one to four hops, <b>${f0(uD)} against ${f0(sD)} fJ per bit per hop</b> for the data-dependent part and ${f0(uZ)} against ${f0(sZ)} for the rest, on the mesh rail.`);
 setText('conttext2',
  `That is energy the loaded mesh spends beyond carrying the bits, most likely buffer writes and arbitration where flows meet; flits are not held long, since each reader's bandwidth is within ${Math.ceil(100*bwd)}% of what it gets on free links. It raises the data-independent part proportionally more (+${f0(100*(uZ/sZ-1))}% against +${f0(100*(uD/sD-1))}%). `+
  `The link-disjoint set also has only straight paths, one reader per target and fewer readers at long distances (${rd(1)} shires at one hop, ${rd(5)} at five), but straight x-only flows that do share links (the first run, one to three hops: ${span(Object.values(xa.per_card).map(c=>c.mean),f0)} and ${f0(xz)} fJ) cost about as much as the loaded mesh, which points to sharing rather than turns. `+
  `On board power the contrast is larger (${f0(db.wsep_d1_4.random_minus_zeros_fj_per_bit_hop.mean)} against ${f0(db.wu.random_minus_zeros_fj_per_bit_hop.mean)}, ${f0(db.wsep_d1_4.zeros_fj_per_bit_hop.mean)} against ${f0(db.wu.zeros_fj_per_bit_hop.mean)}) but noisier (${f0(bD.lo)}–${f0(bD.hi)} over passes for the free-link data part), and part of it is the regulator's loss, which grows with load.`);

 /* 7. the 256 B blocks */
 const A2=CK.alt256||{}, ab=A2.board, an=A2.noc_rail;
 if(ab&&an){
  const v1a=W_.model.v1.noc_rail.toggle_fj_per_bit_transition_hop.mean, v2a=W_.model.v2.noc_rail.toggle_fj_per_bit_transition_hop.mean;
  setText('alttext',
   `The 256-byte pattern costs less than the model predicts if every bit flipped on every flit (dashed): its extra cost per hop is ${pc(ab.fraction_of_full_flip_per_hop)} of that on board power and ${pc(an.fraction_of_full_flip_per_hop)} on the mesh rail, and it does not fall as more of the links are shared: `+
   `on the mesh rail it adds ${f2(an.increment_1_to_3)} pJ/B per hop from one to three hops, where ${pcs([sh('walt/n256/hop1'),sh('walt/n256/hop3')])} of link-hops are shared, and ${f2(an.increment_3_to_6)} from three to six, where ${pcs([sh('walt/n256/hop3'),sh('walt/n256/hop6')])} are. `+
   `So it is not other flows slipping in between, and the other in-flight load is unlikely too: in the first run its lines are identical to the first load's, yet the first run's cost per difference equals the second's (${f0(v1a)} against ${f0(v2a)} fJ per hop on the mesh rail). `+
   `Why is open; one possibility is that when all wires flip the same way together, the capacitance between neighbours is not charged. Most of the excess is paid on leaving the shire (${f2(an.excess_pj_per_byte_at_d['1'])} pJ/B at one hop on the mesh rail, ${f2(an.excess_per_hop)} per further hop).`);
 }

 /* 8. against the rule of thumb */
 const fp=D.first_principles, w485=fp.at_0485.per_random_bit_fj_mm, w09=fp.at_09.per_random_bit_fj_mm;
 const n09=[UN.random_bit_data.mean*s09,HN.random_bit_data.mean*s09], kek485=KEK/s09;
 const tot=[UN.random_bit_total.mean,UB.random_bit_total.mean,HN.random_bit_total.mean,HB.random_bit_total.mean];
 const brk=Math.min(...n09)<100&&Math.max(...n09)>100?"brackets Dally's 100":(Math.max(...n09)<=100?"is below Dally's 100":"is above Dally's 100");
 setText('comparetext',
  `At the voltage it runs at, the ET-SoC-1's mesh moves a random bit a millimetre for <b>${f0(UN.random_bit_data.mean)}–${f0(UB.random_bit_data.mean)} fJ</b> of data-dependent heat and <b>${f0(UN.random_bit_total.mean)}–${f0(UB.random_bit_total.mean)} fJ</b> in all on free links, and ${f0(HN.random_bit_data.mean)}–${f0(HB.random_bit_data.mean)} and ${f0(HN.random_bit_total.mean)}–${f0(HB.random_bit_total.mean)} fJ on the loaded mesh (mesh rail to board): in all, ${f2(Math.min(...tot)/100)}–${f2(Math.max(...tot)/100)} of Dally's 100 taken literally. `+
  `But 0.485 V is low: the same capacitance at 0.9 V would cost ${f2(s09)}× more, <b>${f0(n09[0])}–${f0(n09[1])} fJ</b> per random bit·mm for the mesh rail's data-dependent part (free links to loaded), which ${brk} and is ${f1(n09[0]/KEK)}–${f1(n09[1]/KEK)} of Keckler's ${KEK} (40 nm, 0.9 V). Board power would say up to ${f0(HB.random_bit_data.mean*s09)}, but it carries the regulator's loss, which is not switched capacitance on the die.`);
 setText('comparetext2',
  `At equal voltage the mesh rail's data-dependent cost per random bit·mm, routers included, is ${f1(UN.random_bit_data.mean/kek485)}–${f1(HN.random_bit_data.mean/kek485)} of Keckler's 40 nm repeated-wire figure (${f0(kek485)} fJ at 0.485 V). Wire capacitance per mm barely changes between process nodes (Dally 2018: "about 200fF/mm and independent of scaling"), so that is roughly what one would expect, and <b>the mesh's advantage over the 0.9 V literature is mostly V²</b>. `+
  `A plain repeated wire estimated from a predictive 7 nm kit (ASAP7) with Ho's repeater factors would cost ${f0(w485[0])}–${f0(w485[2])} fJ per random bit·mm at 0.485 V (${f0(w09[0])}–${f0(w09[2])} at 0.9 V, ${f1(w09[0]/KEK)}–${f1(w09[2]/KEK)} of Keckler's figure, which therefore holds more than an ideal wire or counts differently). The free-link mesh-rail data cost, ${f0(UN.random_bit_data.mean)}, is ${UN.random_bit_data.mean>w485[2]?'just above':'at'} the top of that range; these data cannot say how much the routers add.`);

 /* 9. in practice: every comparison on board power, the energy manual's meter */
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
   `Each hop adds about ${pc(perB/X.own_scratchpad_pj_per_byte)} of what reading the byte from the shire's own scratchpad costs (${f2(perB)} against ${f2(X.own_scratchpad_pj_per_byte)} pJ, board power). `+
   `In Dally's currency — "an add is worth 10 µm of movement" — a 32-bit operand crossing one hop costs ${f1(opB)} pJ of board power (${f1(opN)} on the mesh rail alone), about ${f1(lanes)} lanes of an eight-lane <code>fadd.ps</code> on random data (${f1(lane)} pJ, with its share of instruction issue). `+
   `So on this chip one lane of a vector float add is worth ${f1(1/lanes)} of a hop — about ${f1(addMm)} mm — of movement, ${dallyX} times Dally's 10 µm, because an instruction here costs far more than the adder's own 1 fJ per bit`+
   (FADDS?`; a scalar <code>fadd.s</code> (${f1(FADDS)} pJ, <a href="${EM}#every-instruction-the-core-executes">energy manual, §3.1</a>) is worth about ${f0(FADDS/opB)} hops`:'')+'.');
 }

 /* 10. limits */
 const xy12=h=>{const g=ax_=>((vc(`waxis/${ax_}/hop2/p0.5`,NK,h)-vc(`waxis/${ax_}/hop2/p0`,NK,h))-(vc(`waxis/${ax_}/hop1/p0.5`,NK,h)-vc(`waxis/${ax_}/hop1/p0`,NK,h)));return 1-g('y')/g('x');};
 const ya=W_.axes['y/noc_pj_per_byte/random_bit_fj_per_bit_hop_d1_3'], yh=Object.keys(ya.per_card), xh=xa.per_card;
 const up3=yh.length===1&&xh[yh[0]]?ya.per_card[yh[0]].mean/xh[yh[0]].mean-1:null;
 setText('axistext',
  `(The x-only and y-only sets agree only to about 10% — y is ${pcs(hosts.map(xy12))} below x over one and two hops on both cards`+
  (up3!==null?`, and ${pc(Math.abs(up3))} ${up3>0?'above':'below'} over one to three hops on ${yh[0]}, the only card with a usable three-hop y point`:'')+
  ` — and they differ in link sharing, so they do not test this.)`);
 const SN=W_.sensitivity&&W_.sensitivity.no_leak_correction;
 if(SN){
  const ch=[];['v1','v2'].forEach(st=>['toggle_fj_per_bit_transition_hop','ones_fj_per_one_bit_hop'].forEach(k=>ch.push(SN[st].board[k].mean/W_.model[st].board[k].mean-1)));
  const nm=Math.max(...['v1','v2'].map(st=>Math.abs(SN[st].noc_rail.toggle_fj_per_bit_transition_hop.mean/W_.model[st].noc_rail.toggle_fj_per_bit_transition_hop.mean-1)));
  setText('senstext',
   `Board-power numbers also depend on the leakage correction: without it the board coefficients come out ${pcs(ch)} higher (the second run's <i>a</i> ${f0(SN.v2.board.toggle_fj_per_bit_transition_hop.mean)} fJ against ${f0(W_.model.v2.board.toggle_fj_per_bit_transition_hop.mean)}), while the mesh-rail ones ${nm<0.005?'do not move':'move by '+pc(nm)}. `+
   `Three independent reductions of the same bursts, made for this page's review, agree within 3% on the mesh rail and within about 7% on board power.`);
 }
 const dr=(W_.dropped.aifoundry2||[]).filter(x=>x.why==='service processor starved');
 if(dr.length){
  const a3max=Math.max(...['waxis/y/hop3/p0','waxis/y/hop3/p0.5'].map(c=>C[c]&&C[c].took_ms_max&&C[c].took_ms_max.aifoundry3||0));
  const nS=dr.map(x=>x.samples);
  setText('starvetext',
   `On aifoundry2 the set of y-only pairs 3 hops apart slowed the service processor's management path so much (${f1(Math.min(...dr.map(x=>x.median_took_ms))/1000)}–${f1(Math.max(...dr.map(x=>x.max_took_ms))/1000)} s per reading instead of 22 ms) that each burst had ${Math.min(...nS)===Math.max(...nS)?Math.min(...nS):Math.min(...nS)+' or '+Math.max(...nS)} readings; those ${dr.length} bursts are dropped. `+
   (a3max?`On aifoundry3 the same traffic delayed occasional readings to ${f1(a3max/1000)} s; those bursts were kept, and they give the only y-only three-hop point.`:''));
 }
})();

/* ---------- 6. contention ---------- */
(function(){
 const C=W_.configs; let key='noc_pj_per_byte';
 function draw(){
  const W=700,H=330,L=58,R2=190,T=30,B=46,{svg,tip,h}=host('cont',W,H);
  const series=[['wu/p0.5/hop',[1,2,3,4,6],'var(--c2)','loaded mesh, random'],['wsep/p0.5/hop',[1,2,3,4,5],'var(--c1)','own links, random'],
                ['wu/p0/hop',[1,2,3,4,6],'var(--c4)','loaded mesh, zeros'],['wsep/p0/hop',[1,2,3,4,5],'var(--c3)','own links, zeros']];
  let mx=0; series.forEach(sr=>sr[1].forEach(d=>{const c=C[sr[0]+d]; if(c&&c[key])mx=Math.max(mx,c[key].hi);})); mx*=1.1;
  const x=v=>L+(W-L-R2)*v/6.4, y=v=>H-B-(H-B-T)*v/mx;
  axes(svg,{W,H,L,R:R2,T,B,x,y,yt:[0,2,4,6,8,10,12,14,16,18,20].filter(v=>v<=mx),xt:[1,2,3,4,5,6],xl:'hops',yl:(key==='pj_per_byte'?'board power':'mesh rail')+', pJ per payload byte above idle'});
  series.forEach((sr,i)=>{const pts=[]; sr[1].forEach(d=>{const c=C[sr[0]+d]; if(!c||!c[key])return; pts.push([d,c[key].mean]); const g=el('g',{},svg);
     whisker(g,x(d),y(c[key].hi),y(c[key].lo),sr[2]); el('circle',{cx:x(d),cy:y(c[key].mean),r:3.5,fill:sr[2]},g);
     hover(g,tip,h,()=>`<b>${sr[3]}</b>, ${d} hop${d>1?'s':''}<br>${f2(c[key].mean)} pJ/B [${f2(c[key].lo)}–${f2(c[key].hi)}]<br>${Math.round(c.participants/32)} reader shires, ${f0(c.gb_s)} GB/s`);});
    el('path',{d:path(pts,x,y),class:'ln',stroke:sr[2],'stroke-width':1.4,'stroke-dasharray':i>1?'5 3':''},svg);
    el('rect',{x:W-R2+10,y:T+4+i*18,width:11,height:11,fill:sr[2]},svg); txt(svg,W-R2+26,T+14+i*18,sr[3],'lab');});
  const dj=W_.disjoint_flows[key]; if(dj&&dj.wsep_d1_4&&dj.wu){
   const u=dj.wsep_d1_4.random_minus_zeros_fj_per_bit_hop, l=dj.wu.random_minus_zeros_fj_per_bit_hop, uz=dj.wsep_d1_4.zeros_fj_per_bit_hop, lz=dj.wu.zeros_fj_per_bit_hop;
   txt(svg,W-R2+10,T+100,'per bit per hop, 1–4 hops, fJ:','lab-strong');
   txt(svg,W-R2+10,T+118,`data: ${f0(u.mean)} own links, ${f0(l.mean)} loaded`,'lab');
   txt(svg,W-R2+10,T+136,`fixed: ${f0(uz.mean)} own links, ${f0(lz.mean)} loaded`,'lab');}
 }
 const bx=document.getElementById('contbtn');
 bx.innerHTML=[['noc_pj_per_byte','mesh rail only'],['pj_per_byte','board power']].map(b=>`<button type="button" data-k="${b[0]}" aria-pressed="${b[0]===key}">${b[1]}</button>`).join('');
 bx.querySelectorAll('button').forEach(b=>b.onclick=()=>{key=b.dataset.k;bx.querySelectorAll('button').forEach(q=>q.setAttribute('aria-pressed',q.dataset.k===key));draw();});
 draw();
})();
