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
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const f3=v=>v.toFixed(3);
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
 const knee=D.size.find(r=>r.hop_over_dram>3)||D.size[D.size.length-1];
 document.getElementById('k4').textContent='>32 MB';
 document.getElementById('cards').textContent=D.cards.map(c=>{
   const h=D.headline[c];return `${c} ${(h.hop.gb_s/h.dram.gb_s).toFixed(1)}×`;}).join(', ')+
   ' for the hand-off, '+D.cards.map(c=>{const h=D.headline[c];return (h.scp.gb_s/h.dram.gb_s).toFixed(1)+'×';}).join(' and ')+
   ' for the shire-local case';
})();

/* ---------- section 1: the three media ---------- */
document.getElementById('media').innerHTML='<thead><tr><th>Where a stage’s output goes</th><th class="num">GB/s</th><th class="num">Cycles for the whole relay</th><th class="num">Against DRAM</th><th class="num">Shire 0 ends holding</th></tr></thead><tbody>'+
 MED.map(([m,label])=>`<tr><td>${label}</td><td class="num">${f1(H[m].gb_s)}</td><td class="num">${H[m].cycles_max.toLocaleString()}</td><td class="num">${m==='dram'?'—':(H[m].gb_s/H.dram.gb_s).toFixed(1)+'×'}</td><td class="num">${H[m].shire0_final.toFixed(0)}</td></tr>`).join('')+'</tbody>';

(function(){
 const W=700,H2=210,L=150,R=80,T=20,B=40,{svg,tip,h}=host('head',W,H2);
 const mx=Math.max(...MED.map(m=>H[m[0]].gb_s))*1.12;
 const x=v=>L+(W-L-R)*v/mx, y=i=>T+22+i*52;
 axes(svg,{W,H:H2,L,R,T,B,x,y:v=>v,yt:[],xt:[0,500,1000,1500],xl:'GB/s of intermediate data, at 600 MHz'});
 MED.forEach((m,i)=>{const r=H[m[0]],g=el('g',{},svg);
  el('rect',{x:L,y:y(i)-15,width:Math.max(2,x(r.gb_s)-L),height:26,fill:m[2],rx:3},g);
  txt(svg,L-8,y(i)+4,m[0]==='dram'?'DRAM':m[0]==='hop'?'next shire':'own shire','lab','end');
  txt(svg,x(r.gb_s)+7,y(i)+4,f1(r.gb_s)+(m[0]==='dram'?' GB/s':' GB/s  '+(r.gb_s/H.dram.gb_s).toFixed(1)+'×'),'lab-strong');
  hover(g,tip,h,()=>`${m[1]}<br>${f1(r.gb_s)} GB/s<br>${r.cycles_max.toLocaleString()} cycles<br>every element verified`);});
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
   return `<tr><td>${name[m]}</td><td class="num">${f1(r.bytes_per_s/1e9)}</td><td class="num">${f2(r.over_idle_w)}</td><td class="num">${f2(r.pj_per_byte)}</td></tr>`;}).join('')+
  `<tr><td>idle card</td><td class="num">0</td><td class="num">—</td><td class="num">—</td></tr></tbody>`;
 const dr=p.media.find(m=>m.medium==='dram'),hp=p.media.find(m=>m.medium==='hop'),sc=p.media.find(m=>m.medium==='scp');
 document.getElementById('powernote').textContent=
  `Idle was ${f2(p.idle.board_w)} W. All three sit within a watt of each other while moving between `+
  `${f1(dr.bytes_per_s/1e9)} and ${f1(sc.bytes_per_s/1e9)} GB/s, so the energy per byte differs by `+
  `${(dr.pj_per_byte/sc.pj_per_byte).toFixed(0)}× for the shire-local case and ${(dr.pj_per_byte/hp.pj_per_byte).toFixed(0)}× for the hand-off. `+
  `Measured independently in the memory-hierarchy work: 133 pJ/B for DRAM, 2.6 local scratchpad, 6.3 remote.`;
})();

/* ---------- section 3: working-set size ---------- */
(function(){
 const rows=D.size, W=700,H2=330,L=62,R=130,T=26,B=52,{svg,tip,h}=host('size',W,H2);
 const xs=rows.map(r=>r.stage_bytes*32/1048576);
 const x=v=>L+(W-L-R)*Math.log2(v/2)/Math.log2(32/2), y=v=>H2-B-(H2-B-T)*Math.log10(Math.max(v,20)/20)/Math.log10(2000/20);
 axes(svg,{W,H:H2,L,R,T,B,x,y,yt:[20,100,500,2000],yf:v=>v+'',xt:[2,4,8,16,32],xf:v=>v+' MB',
   xl:'working set, one buffer across the whole chip',yl:'GB/s'});
 el('line',{x1:x(32),x2:x(32),y1:T,y2:H2-B,stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 txt(svg,x(32)-6,T+12,'32 MB of L3','lab','end');
 MED.forEach(m=>{
  el('path',{d:path(rows.map(r=>[r.stage_bytes*32/1048576,r[m[0]].gb_s]),x,y),class:'ln',stroke:m[2]},svg);
  rows.forEach(r=>{const g=el('g',{},svg);
   el('circle',{cx:x(r.stage_bytes*32/1048576),cy:y(r[m[0]].gb_s),r:4,fill:m[2]},g);
   hover(g,tip,h,()=>`${(r.stage_bytes*32/1048576)} MB per buffer<br>${m[1]}<br>${f1(r[m[0]].gb_s)} GB/s`);});});
 MED.forEach((m,i)=>{el('rect',{x:W-R+6,y:T+6+i*20,width:11,height:11,fill:m[2]},svg);
  txt(svg,W-R+23,T+16+i*20,m[0]==='dram'?'DRAM':m[0]==='hop'?'next shire':'own shire','lab');});
 const small=rows[0], big=rows[rows.length-1];
 document.getElementById('sizecap').textContent=
  `Log axes. Two buffers are live at once, so the chip footprint is twice the figure on the x axis.`;
 document.getElementById('sizetext').innerHTML=
  `At ${(small.stage_bytes*32/1048576)} MB per buffer the DRAM route runs at <b>${f1(small.dram.gb_s)} GB/s</b>, because it is not `+
  `going to DRAM at all — the 32 MB L3 is holding the whole thing, and putting the data in a scratchpad by hand buys `+
  `${small.hop_over_dram.toFixed(1)}×. At ${(big.stage_bytes*32/1048576)} MB it falls to <b>${f1(big.dram.gb_s)} GB/s</b> and stays there: `+
  `${D.bigsize.slice(-3).map(r=>f1(r.gb_s)).join(', ')} GB/s at ${D.bigsize.slice(-3).map(r=>(r.stage_bytes*32/1048576)+' MB').join(', ')}. `+
  `<b>The advantage is not a property of the computation. It is the L3 capacity.</b> Below it the cache is already doing the job; `+
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
    hover(g,tip,h,()=>`${r.work} add${r.work>1?'s':''} per element<br>${s2[1]}: ${r[s2[0]].toFixed(1)}× DRAM<br>${f1(r[s2[0]==='scp_over_dram'?'scp':'hop'].gb_s)} GB/s`);});
   el('rect',{x:W-R+6,y:T+6+i*20,width:11,height:11,fill:s2[2]},svg);
   txt(svg,W-R+23,T+16+i*20,s2[1],'lab');});
 const last=rows[rows.length-1];
 document.getElementById('intcap').textContent='Log axes. The dashed line is parity with DRAM.';
 document.getElementById('inttext').innerHTML=
  `One add per element is pure data movement and the hand-off is ${rows[0].hop_over_dram.toFixed(1)}× ahead. `+
  `Every quadrupling of the arithmetic roughly halves the lead, and by ${last.work} adds per element — `+
  `${(last.work/8).toFixed(0)} flops per byte read — it is down to ${last.hop_over_dram.toFixed(1)}×. `+
  `The rule this gives: <b>on-chip placement is worth it below roughly ten flops per byte</b>, and above that the `+
  `arithmetic is the wall and it does not matter where the operands came from.`;
})();

/* ---------- section 5: distance ---------- */
document.getElementById('dist').innerHTML='<thead><tr><th class="num">Shires the slab moves per stage</th><th class="num">GB/s</th><th class="num">Against handing it next door</th></tr></thead><tbody>'+
 D.distance.map(r=>`<tr><td class="num">${r.hop_distance}</td><td class="num">${f1(r.gb_s)}</td><td class="num">${(r.gb_s/D.distance[0].gb_s).toFixed(2)}×</td></tr>`).join('')+'</tbody>';
