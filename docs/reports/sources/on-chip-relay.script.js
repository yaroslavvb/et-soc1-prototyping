const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
function hover(g,tip,h,html){const s=ev=>{tip.innerHTML=html();tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.max(0,Math.min(ev.clientX-b.left+12,b.width-290))+'px';tip.style.top=(ev.clientY-b.top+12)+'px';};g.addEventListener('mousemove',s);g.addEventListener('mouseleave',()=>tip.style.display='none');}
function path(pts,x,y){return pts.map((p,i)=>`${i?'L':'M'}${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join(' ');}
function axes(svg,o){const {W,H,L,R,T,B,x,y}=o;
 for(const t of o.yt){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,o.yf?o.yf(t):t,'tick','end');}
 for(const t of o.xt){txt(svg,x(t),H-B+16,o.xf?o.xf(t):t,'tick','middle');}
 if(o.xl)txt(svg,(L+W-R)/2,H-4,o.xl,'lab','middle');if(o.yl)txt(svg,4,T-8,o.yl,'lab');}
const f0=v=>v.toFixed(0),f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
/* GB/s and other figures in the thousands get separators; cycle counts are integers */
const g1=v=>v.toLocaleString('en-GB',{minimumFractionDigits:1,maximumFractionDigits:1});
const gi=v=>Math.round(v).toLocaleString('en-GB');
const MED=[['dram','write it to DRAM, read it back next stage','var(--c2)'],
           ['hop','write it where the next shire will read it','var(--c1)'],
           ['scp',"keep it in this shire's own scratchpad",'var(--c3)']];
const A2=D.cards[0], H=D.headline[A2];

/* ---------- KPIs ---------- */
(function(){
 document.getElementById('k1').textContent=(H.hop.gb_s/H.dram.gb_s).toFixed(1)+'× faster';
 document.getElementById('k2').textContent=(H.scp.gb_s/H.dram.gb_s).toFixed(1)+'× faster';
 const p=D.power&&D.power.media, dr=p&&p.find(m=>m.medium==='dram'), hp=p&&p.find(m=>m.medium==='hop');
 document.getElementById('k3').textContent=(dr&&hp)?(dr.pj_per_byte/hp.pj_per_byte).toFixed(0)+'× less':'—';
 document.getElementById('k4').textContent='>32 MB';
 document.getElementById('cards').textContent=D.cards.map(c=>{
   const h=D.headline[c];return `${c} ${(h.hop.gb_s/h.dram.gb_s).toFixed(1)}×`;}).join(', ')+
   ' for the hand-off, '+D.cards.map(c=>{const h=D.headline[c];return (h.scp.gb_s/h.dram.gb_s).toFixed(1)+'×';}).join(' and ')+
   ' for the shire-local case';
})();

/* ---------- section 1: the three media ---------- */
document.getElementById('media').innerHTML='<thead><tr><th>Where a stage’s output goes</th><th class="num">GB/s</th><th class="num">Cycles for the whole relay</th><th class="num">Against DRAM</th><th class="num">Shire 0 ends holding</th></tr></thead><tbody>'+
 MED.map(([m,label])=>`<tr><td>${label}</td><td class="num">${g1(H[m].gb_s)}</td><td class="num">${gi(H[m].cycles_max)}</td><td class="num">${m==='dram'?'—':(H[m].gb_s/H.dram.gb_s).toFixed(1)+'×'}</td><td class="num">${H[m].shire0_final.toFixed(0)}</td></tr>`).join('')+'</tbody>';

(function(){
 const W=700,H2=210,L=150,R=80,T=20,B=40,{svg,tip,h}=host('head',W,H2);
 const mx=Math.max(...MED.map(m=>H[m[0]].gb_s))*1.12;
 const x=v=>L+(W-L-R)*v/mx, y=i=>T+22+i*52;
 axes(svg,{W,H:H2,L,R,T,B,x,y:v=>v,yt:[],xt:[0,500,1000,1500],xf:gi,xl:'GB/s of intermediate data, at 600 MHz'});
 MED.forEach((m,i)=>{const r=H[m[0]],g=el('g',{},svg);
  el('rect',{x:L,y:y(i)-15,width:Math.max(2,x(r.gb_s)-L),height:26,fill:m[2],rx:3},g);
  txt(svg,L-8,y(i)+4,m[0]==='dram'?'DRAM':m[0]==='hop'?'next shire':'own shire','lab','end');
  txt(svg,x(r.gb_s)+7,y(i)+4,g1(r.gb_s)+(m[0]==='dram'?' GB/s':' GB/s  '+(r.gb_s/H.dram.gb_s).toFixed(1)+'×'),'lab-strong');
  hover(g,tip,h,()=>`${m[1]}<br>${g1(r.gb_s)} GB/s<br>${gi(r.cycles_max)} cycles<br>every element verified`);});
 document.getElementById('headcap').textContent=
  'Eight stages, 1 MB per shire per stage, 1,024 minions, 512 MB of reads and writes. Identical kernel, '+
  'identical barriers; only the destination of each stage differs.';
})();

/* ---------- section 2: power ---------- */
(function(){
 const p=D.power; if(!p){return;}
 const name={dram:'DRAM',scp:"own shire's scratchpad",hop:"next shire's scratchpad"};
 document.getElementById('power').innerHTML='<thead><tr><th>Where the intermediate goes</th><th class="num">GB/s on the card</th><th class="num">Watts over idle</th><th class="num">pJ per byte moved</th></tr></thead><tbody>'+
  ['dram','hop','scp'].map(m=>{const r=p.media.find(x=>x.medium===m);
   return `<tr><td>${name[m]}</td><td class="num">${g1(r.bytes_per_s/1e9)}</td><td class="num">${f2(r.over_idle_w)}</td><td class="num">${f1(r.pj_per_byte)}</td></tr>`;}).join('')+
  `</tbody>`;
 const dr=p.media.find(m=>m.medium==='dram'),hp=p.media.find(m=>m.medium==='hop'),sc=p.media.find(m=>m.medium==='scp');
 document.getElementById('powernote').textContent=
  `One session on aifoundry2, board power. Idle was ${f2(p.idle.board_w)} W at a die temperature of ${f0(p.idle.die_c)} °C, and the `+
  `minion clock stayed at 600 MHz throughout. All three sit within a watt of each other while moving between `+
  `${g1(dr.bytes_per_s/1e9)} and ${g1(sc.bytes_per_s/1e9)} GB/s, so the energy per byte differs by about `+
  `${(dr.pj_per_byte/sc.pj_per_byte).toFixed(0)}× for the shire-local case and ${(dr.pj_per_byte/hp.pj_per_byte).toFixed(0)}× for the hand-off. `+
  `The GB/s column is the rate while the kernel runs, from the cycle counter, and the kernel ran only `+
  `${f0(100*Math.min(...p.media.map(m=>m.duty)))}–${f0(100*Math.max(...p.media.map(m=>m.duty)))}% of each burst; `+
  `the watts are averaged over the whole burst, launch gaps included, so pJ per byte is watts over idle ÷ `+
  `(GB/s × ${Math.min(...p.media.map(m=>m.duty)).toFixed(2)}–${Math.max(...p.media.map(m=>m.duty)).toFixed(2)}).`;
})();

/* ---------- section 3: working-set size ---------- */
(function(){
 const rows=D.size, W=700,H2=330,L=62,R=130,T=26,B=52,{svg,tip,h}=host('size',W,H2);
 const xs=rows.map(r=>r.stage_bytes*32/1048576);
 const x=v=>L+(W-L-R)*Math.log2(v/2)/Math.log2(32/2), y=v=>H2-B-(H2-B-T)*Math.log10(Math.max(v,20)/20)/Math.log10(2000/20);
 axes(svg,{W,H:H2,L,R,T,B,x,y,yt:[20,100,500,2000],yf:gi,xt:[2,4,8,16,32],xf:v=>v+' MB',
   xl:'working set, one buffer across the whole chip',yl:'GB/s'});
 el('line',{x1:x(16),x2:x(16),y1:T,y2:H2-B,stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 txt(svg,x(16)-6,T+12,'footprint = 32 MB of L3','lab','end');
 MED.forEach(m=>{
  el('path',{d:path(rows.map(r=>[r.stage_bytes*32/1048576,r[m[0]].gb_s]),x,y),class:'ln',stroke:m[2]},svg);
  rows.forEach(r=>{const g=el('g',{},svg);
   el('circle',{cx:x(r.stage_bytes*32/1048576),cy:y(r[m[0]].gb_s),r:4,fill:m[2]},g);
   hover(g,tip,h,()=>`${(r.stage_bytes*32/1048576)} MB per buffer<br>${m[1]}<br>${g1(r[m[0]].gb_s)} GB/s`);});});
 MED.forEach((m,i)=>{el('rect',{x:W-R+6,y:T+6+i*20,width:11,height:11,fill:m[2]},svg);
  txt(svg,W-R+23,T+16+i*20,m[0]==='dram'?'DRAM':m[0]==='hop'?'next shire':'own shire','lab');});
 const mb=r=>r.stage_bytes*32/1048576, small=rows[0], big=rows[rows.length-1];
 const and=a=>a.slice(0,-1).join(', ')+' and '+a[a.length-1];
 const fit=rows.filter(r=>2*mb(r)<=32), lastfit=fit[fit.length-1];
 const hopMax=Math.max(...fit.map(r=>r.hop_over_dram));
 document.getElementById('sizecap').textContent=
  `Log axes. Two buffers are live at once, so the chip footprint is twice the figure on the x axis; the dashed line `+
  `marks where that footprint equals the 32 MB L3.`;
 document.getElementById('sizetext').innerHTML=
  `At ${mb(small)} MB per buffer the DRAM route runs at <b>${g1(small.dram.gb_s)} GB/s</b>, because it is not `+
  `going to DRAM at all: the 32 MB L3 holds the whole thing. Handing the data to the next shire then buys `+
  `${small.hop_over_dram.toFixed(2)}×, which is nothing, and keeping it in the shire's own scratchpad `+
  `${small.scp_over_dram.toFixed(1)}×. Up to ${mb(lastfit)} MB per buffer, while both buffers fit in the L3, the hand-off `+
  `wins at most ${hopMax.toFixed(1)}×. At ${mb(big)} MB per buffer, a ${2*mb(big)} MB footprint, the DRAM route falls to `+
  `<b>${g1(big.dram.gb_s)} GB/s</b> and stays there: ${and(D.bigsize.slice(-3).map(r=>g1(r.gb_s)))} GB/s at `+
  `${and(D.bigsize.slice(-3).map(r=>String(mb(r))))} MB per buffer. `+
  `<b>The advantage is not a property of the computation. It is the L3 capacity.</b> Below it the cache is already doing most of the job; `+
  `above it, nothing is, unless you place the data yourself.`;
})();

/* ---------- section 4: arithmetic intensity ---------- */
(function(){
 const rows=D.intensity, W=700,H2=330,L=58,R=130,T=26,B=52,{svg,tip,h}=host('intensity',W,H2);
 const x=v=>L+(W-L-R)*Math.log2(v)/Math.log2(256), y=v=>H2-B-(H2-B-T)*Math.log10(Math.max(v,1))/Math.log10(40);
 axes(svg,{W,H:H2,L,R,T,B,x,y,yt:[1,2,5,10,20,40],yf:v=>v+'×',xt:[1,4,16,64,256],
   xl:'vector adds applied to every element, per stage',yl:'faster than the DRAM route'});
 el('line',{x1:L,x2:W-R,y1:y(1),y2:y(1),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 [['scp_over_dram',"own shire's scratchpad",'var(--c3)'],['hop_over_dram',"next shire's scratchpad",'var(--c1)']]
  .forEach((s2,i)=>{
   el('path',{d:path(rows.map(r=>[r.work,r[s2[0]]]),x,y),class:'ln',stroke:s2[2]},svg);
   rows.forEach(r=>{const g=el('g',{},svg);
    el('circle',{cx:x(r.work),cy:y(r[s2[0]]),r:4,fill:s2[2]},g);
    hover(g,tip,h,()=>`${r.work} add${r.work>1?'s':''} per element (${r.work/8} flop per byte moved)<br>${s2[1]}: ${r[s2[0]].toFixed(1)}× DRAM<br>${g1(r[s2[0]==='scp_over_dram'?'scp':'hop'].gb_s)} GB/s`);});
   el('rect',{x:W-R+6,y:T+6+i*20,width:11,height:11,fill:s2[2]},svg);
   txt(svg,W-R+23,T+16+i*20,s2[1].replace("'s scratchpad",''),'lab');});   /* legend: 'own shire', 'next shire' */
 const last=rows[rows.length-1], at=w=>rows.find(r=>r.work===w).hop_over_dram.toFixed(1);
 document.getElementById('intcap').textContent='Log axes. The dashed line is parity with DRAM. Each element is 4 bytes read '+
  'and 4 bytes written, so w adds per element are w/8 flops per byte moved.';
 document.getElementById('inttext').innerHTML=
  `One add per element is pure data movement, and the hand-off is ${at(1)}× ahead (this sweep's own run; the `+
  `headline run in §1 gives ${(H.hop.gb_s/H.dram.gb_s).toFixed(1)}×). The lead holds to about four adds per element `+
  `(${at(4)}×) and then falls faster with each quadrupling: ${at(16)}× at 16, ${at(64)}× at 64, ${at(128)}× at 128 and `+
  `${at(last.work)}× at ${last.work} adds — ${last.work/8} flops per byte moved, counting the byte read and the byte `+
  `written (${last.work/4} per byte read). <b>For this vector-add kernel, on-chip placement pays several-fold up to `+
  `about ${64/8} flops per byte moved (${at(64)}×) and is still ${at(last.work)}× at ${last.work/8}.</b> The tensor unit `+
  `does twice the <code>fadd.ps</code> rate; for it the `+
  `<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points">ridge points</a> report puts the DRAM crossover `+
  `near 130 FLOP per byte read.`;
})();

/* ---------- section 5: distance ---------- */
(function(){
 const d=D.distance, k=n=>d.find(r=>r.hop_distance===n).mesh_hops, gb=d.map(r=>r.gb_s), mh=d.map(r=>r.mesh_hops.mean);
 const rng=m=>`${m.min} to ${m.max}`;
 document.getElementById('distintro').innerHTML=
  `The obvious worry about handing data to another shire is the network in between. Shire numbers do not follow `+
  `the mesh: on the shire map of the <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">on-chip `+
  `communication report</a>, the next shire in the ring is on average ${f1(k(1).mean)} mesh hops away `+
  `(${rng(k(1))}), two places on ${f1(k(2).mean)}, and sixteen places on only ${f1(k(16).mean)} (${rng(k(16))}). `+
  `Across offsets whose mean distance runs from ${f1(Math.min(...mh))} to ${f1(Math.max(...mh))} hops the bandwidth `+
  `stays between ${f0(Math.min(...gb))} and ${f0(Math.max(...gb))} GB/s and does not follow the distance:`;
 const W='style="white-space:normal"';
 document.getElementById('dist').innerHTML=`<thead><tr><th class="num" ${W}>Shire IDs back round the ring</th>`+
  `<th class="num" ${W}>Mesh hops, mean (range)</th><th class="num">GB/s</th>`+
  `<th class="num" ${W}>Against the next shire in ID order</th></tr></thead><tbody>`+
  d.map(r=>`<tr><td class="num">${r.hop_distance}</td><td class="num">${f1(r.mesh_hops.mean)} (${r.mesh_hops.min}–${r.mesh_hops.max})</td>`+
   `<td class="num">${g1(r.gb_s)}</td><td class="num">${(r.gb_s/d[0].gb_s).toFixed(2)}×</td></tr>`).join('')+'</tbody>';
})();
