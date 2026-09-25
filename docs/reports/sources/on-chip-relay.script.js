/* Hand it to the next shire. Every number comes from D (onchip.json, built by workloads/onchip/analyze_onchip.py)
   except the pooled rerun energies in POOLED below. Charts use the shared toolkit CK (docs/reports/sources/chartkit.js). */
const $=id=>document.getElementById(id);
const f0=v=>v.toFixed(0),f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const num=CK.fmt.num, n0=v=>num(v,0);
const g1=v=>num(v,1);                                  // GB/s to one decimal, with separators
const gb=v=>v<100?num(v,1):num(v,0);                   // GB/s at chart precision: 47.9, 379, 1,263
const pj=v=>v<5?f2(v):f1(v);                           // pJ per byte: 3.99, 8.6, 105.7
const MED=[['dram','write it to DRAM, read it back next stage','var(--c2)','DRAM'],
           ['hop','write it where the next shire will read it','var(--c1)','next shire'],
           ['scp',"keep it in this shire's own scratchpad",'var(--c3)','own shire']];
const A2=D.cards[0], A3=D.cards[1], H=D.headline[A2], H3=D.headline[A3];
const WORD=['no','one','two','three','four','five','six','seven','eight','nine'];
const word=n=>WORD[n]||n0(n);
const rng=(vals,fmt)=>{const a=fmt(Math.min(...vals)),b=fmt(Math.max(...vals));return a===b?a:a+'–'+b;};
const pear=(xs,ys)=>{const n=xs.length,mx=xs.reduce((a,b)=>a+b)/n,my=ys.reduce((a,b)=>a+b)/n;
 let sxy=0,sxx=0,syy=0;xs.forEach((x,i)=>{sxy+=(x-mx)*(ys[i]-my);sxx+=(x-mx)**2;syy+=(ys[i]-my)**2;});
 return {r:sxy/Math.sqrt(sxx*syy),slope:sxy/sxx,icpt:my-sxy/sxx*mx};};

/* Pooled energies, per byte moved (relay_pj_per_byte) and per byte read (levels_pj_per_byte), from
   docs/reports/data/2026-09-23-energy-manual/reruns.json, written by
     python3 tools/ettelem/analyze_reruns.py docs/reports/data/2026-09-23-reruns-aifoundry2-warm \
       docs/reports/data/2026-09-23-reruns-aifoundry3 --out reruns.json
   Copied here (4 decimals) rather than read as data: reruns.json takes this page's onchip.json as its first pass,
   so feeding it back into onchip.json would make a file loop (PLAN2 DP-6). Update both together if the reruns change. */
const POOLED={
 relay:{dram:{mean:105.7441,lo:99.4722,hi:111.0366,n:8,per_card:{aifoundry2:{mean:102.1385,n:4},aifoundry3:{mean:109.3497,n:4}}},
  scp:{mean:3.9935,lo:3.9038,hi:4.2497,n:8,per_card:{aifoundry2:{mean:4.0178,n:4},aifoundry3:{mean:3.9691,n:4}}},
  hop:{mean:8.5934,lo:7.775,hi:9.2058,n:8,per_card:{aifoundry2:{mean:9.078,n:4},aifoundry3:{mean:8.1087,n:4}}}},
 read:{dram:{mean:121.9633,lo:116.7837,hi:129.0313,n:6},'scp-local':{mean:2.5152,lo:2.3927,hi:2.6439,n:6},
  'scp-remote':{mean:6.6546,lo:5.3096,hi:7.478,n:6}}
};

/* ---------- KPIs, the lede's computed spans and the two-card line of section 7 ---------- */
(function(){
 $('k1').textContent=(H.hop.gb_s/H.dram.gb_s).toFixed(1)+'× faster';
 $('k2').textContent=(H.scp.gb_s/H.dram.gb_s).toFixed(1)+'× faster';
 const p=D.power&&D.power.media, dr=p&&p.find(m=>m.medium==='dram'), hp=p&&p.find(m=>m.medium==='hop');
 $('k3').textContent=(dr&&hp)?(dr.pj_per_byte/hp.pj_per_byte).toFixed(0)+'× less':'—';
 $('k4').textContent='>32 MB';
 const gbs=D.distance.map(r=>r.gb_s);
 $('l-gbr').textContent=`${n0(Math.min(...gbs))}–${n0(Math.max(...gbs))} GB/s`;
 $('l-a3').textContent=`${(H3.hop.gb_s/H3.dram.gb_s).toFixed(1)}× and ${(H3.scp.gb_s/H3.dram.gb_s).toFixed(1)}×`;
 const rep=[].concat(...D.cards.map(c=>D.repeats[c]));
 const hopR=rng(rep.map(r=>r.hop_over_dram),v=>v.toFixed(1)), scpR=rng(rep.map(r=>r.scp_over_dram),v=>v.toFixed(1));
 $('l-rep').textContent=`${hopR}× and ${scpR}×`;
 const groups=D.repeats[A2].map(r=>r.group);
 $('cards').textContent=D.cards.map(c=>{const h=D.headline[c];return `${c} ${(h.hop.gb_s/h.dram.gb_s).toFixed(1)}×`;}).join(', ')+
   ' for the hand-off, '+D.cards.map(c=>{const h=D.headline[c];return (h.scp.gb_s/h.dram.gb_s).toFixed(1)+'×';}).join(' and ')+
   ` for the shire-local case. The same configuration ran ${word(groups.length)} times on each card (in the ${groups.slice(0,-1).join(', ')} and ${groups[groups.length-1]} sweeps), `+
   `and the two ratios run ${hopR}× and ${scpR}×; the scatter is almost all DRAM (${rng(rep.map(r=>r.dram),f1)} GB/s), and the hand-off ran at `+
   `${rng(rep.map(r=>r.hop),f0)} GB/s every time`;
})();

/* ---------- section 1: the three media ---------- */
$('media').innerHTML='<thead><tr><th>Where a stage’s output goes</th><th class="num">GB/s</th><th class="num">Cycles for the whole relay</th><th class="num">Against DRAM</th><th class="num">Shire 0 ends holding</th></tr></thead><tbody>'+
 MED.map(([m,label])=>`<tr><td>${label}</td><td class="num">${g1(H[m].gb_s)}</td><td class="num">${n0(H[m].cycles_max)}</td><td class="num">${m==='dram'?'—':(H[m].gb_s/H.dram.gb_s).toFixed(1)+'×'}</td><td class="num">${H[m].shire0_final.toFixed(0)}</td></tr>`).join('')+'</tbody>';
CK.stackTable('media');

/* ---------- section 1: same watts, different work (three panels side by side) ---------- */
(function(){
 const p=D.power; if(!p){$('samew').textContent='';return;}
 const med=m=>p.media.find(x=>x.medium===m);
 const PANELS=[
  {key:'w',title:'Watts over idle',val:m=>med(m).over_idle_w,lab:v=>f2(v)+' W'},
  {key:'gb',title:'GB/s during the power bursts',val:m=>med(m).bytes_per_s/1e9,lab:v=>g1(v)},
  {key:'pj',title:`pJ per byte moved, ${POOLED.relay.dram.n} passes`,val:m=>POOLED.relay[m].mean,
   lab:(v,m)=>{const q=POOLED.relay[m];return `${pj(q.mean)} [${pj(q.lo)}–${pj(q.hi)}]`;}}];
 const tip=(key,m,label)=>{const x=med(m),q=POOLED.relay[m],pc=q.per_card;
  if(key==='w')return `<b>${label}</b> · ${f2(x.over_idle_w)} W over idle (board power, ${A2}; idle ${f2(p.idle.board_w)} W)<br>${x.n} readings over ${f1(x.wall_s)} s; the kernel ran ${f0(100*x.duty)}% of the burst`;
  if(key==='gb')return `<b>${label}</b> · ${g1(x.bytes_per_s/1e9)} GB/s while the kernel runs (cycle counter), over ${x.runs} launches in the power burst<br>the headline run of the table above: ${g1(H[m].gb_s)} GB/s`;
  return `<b>${label}</b> · ${pj(q.mean)} pJ per byte moved, mean of ${q.n} passes [${pj(q.lo)}–${pj(q.hi)}]<br>`+
   `${A2} ${pj(pc[A2].mean)} (n = ${pc[A2].n}), ${A3} ${pj(pc[A3].mean)} (n = ${pc[A3].n}); this session ${pj(x.pj_per_byte)}`;};
 CK.frame('samew',{label:'Watts over idle, GB/s and pJ per byte for DRAM, the next shire and the own scratchpad',
  height:W=>W<600?3*128+8:132,
  draw(f){
   const svg=f.svg,W=f.W,narrow=f.narrow,LW=narrow?78:92,GAP=28,RES=narrow?118:112;
   const pw=narrow?W-LW-4:(W-LW-2*GAP-4)/3, bh=20;
   const nodes=[];
   PANELS.forEach((P,pi)=>{
    const x0=narrow?LW:LW+pi*(pw+GAP), y0=narrow?pi*128:0;
    const mx=Math.max(...MED.map(m=>P.key==='pj'?POOLED.relay[m[0]].hi:P.val(m[0])));
    const x=CK.lin(0,mx,x0,x0+pw-RES);
    CK.txt(svg,narrow?0:x0,y0+14,P.title,'lab-strong');
    CK.el('line',{x1:x0,x2:x0,y1:y0+24,y2:y0+24+3*34,class:'ck-axis'},svg);
    MED.forEach(([m,,col,label],i)=>{
     const yc=y0+24+i*34+17, v=P.val(m), g=CK.el('g',{},svg);
     if(narrow||pi===0) CK.txt(svg,narrow?0:LW-8,yc+4,label,'lab',narrow?'start':'end');
     const b=CK.el('rect',{x:x0,y:yc-bh/2,width:Math.max(2,x(v)-x0),height:bh,rx:3},g); b.style.fill=col;
     let end=x(v);
     if(P.key==='pj'){
      const q=POOLED.relay[m],pc=q.per_card,s=med(m).pj_per_byte;
      const wk=CK.el('g',{'aria-hidden':'true'},g); wk.style.stroke='var(--ink)'; wk.style.strokeWidth='1.5';
      CK.el('line',{x1:x(q.lo),x2:x(q.hi),y1:yc,y2:yc},wk);
      CK.el('line',{x1:x(q.lo),x2:x(q.lo),y1:yc-5,y2:yc+5},wk); CK.el('line',{x1:x(q.hi),x2:x(q.hi),y1:yc-5,y2:yc+5},wk);
      const d2=CK.el('circle',{cx:x(pc[A2].mean),cy:yc-9,r:3},g); d2.style.fill='var(--ink)';
      const d3=CK.el('circle',{cx:x(pc[A3].mean),cy:yc+9,r:3,fill:'none'},g); d3.style.stroke='var(--ink)'; d3.style.strokeWidth='1.2';
      const t=CK.el('line',{x1:x(s),x2:x(s),y1:yc-bh/2-3,y2:yc+bh/2+3},g); t.style.stroke='var(--ink)'; t.style.strokeWidth='2';
      end=Math.max(end,x(q.hi));
     }
     CK.txt(svg,end+6,yc+4,P.key==='gb'&&m!=='dram'?`${P.lab(v,m)} (${(v/P.val('dram')).toFixed(0)}×)`:P.lab(v,m),'lab');
     CK.tip(f,g,tip(P.key,m,label));
     nodes.push(g);
    });
   });
   CK.keynav(f,nodes);
  }});
 const w=p.media.map(m=>m.over_idle_w), dr=med('dram'), q=POOLED.relay;
 $('samewcap').textContent=
  `Watts and GB/s are the power session on ${A2}: board power over an idle of ${f2(p.idle.board_w)} W, and the rate while the kernel runs, `+
  `from the cycle counter, during those bursts (the headline runs in the table above ran at ${MED.map(m=>g1(H[m[0]].gb_s)).join(', ')} GB/s). `+
  `Energy per byte pools ${q.dram.n} passes, ${word(q.dram.per_card[A2].n)} per card with this session among them: the bar is the mean, the whisker the range, `+
  `the filled dot ${A2}'s mean, the ring ${A3}'s, the tick this session. The power moves by ${f1(Math.max(...w)-Math.min(...w))} W while the work grows `+
  `${f0(med('hop').bytes_per_s/dr.bytes_per_s)}× and ${f0(med('scp').bytes_per_s/dr.bytes_per_s)}×.`;
})();

/* ---------- section 2: power ---------- */
(function(){
 const p=D.power; if(!p){return;}
 const name={dram:'DRAM',scp:"own shire's scratchpad",hop:"next shire's scratchpad"}, q=POOLED.relay;
 $('power').innerHTML=`<thead><tr><th>Where the intermediate goes</th><th class="num">GB/s on the card</th><th class="num">Watts over idle</th><th class="num">pJ, this session</th><th class="num">pJ per byte moved, all passes: mean [range], n = ${q.dram.n}</th></tr></thead><tbody>`+
  ['dram','hop','scp'].map(m=>{const r=p.media.find(x=>x.medium===m);
   return `<tr><td>${name[m]}</td><td class="num">${g1(r.bytes_per_s/1e9)}</td><td class="num">${f2(r.over_idle_w)}</td><td class="num">${pj(r.pj_per_byte)}</td><td class="num">${pj(q[m].mean)} [${pj(q[m].lo)}–${pj(q[m].hi)}]</td></tr>`;}).join('')+
  `</tbody>`;
 CK.stackTable('power');
 const duty=p.media.map(m=>m.duty);
 $('powernote').textContent=
  `One session on ${A2}, board power. Idle was ${f2(p.idle.board_w)} W at a die temperature of ${f0(p.idle.die_c)} °C, and the `+
  `minion clock stayed at 600 MHz throughout. The GB/s column is the rate while the kernel runs, from the cycle counter, and the kernel ran only `+
  `${f0(100*Math.min(...duty))}–${f0(100*Math.max(...duty))}% of each burst; `+
  `the watts are averaged over the whole burst, launch gaps included, so pJ per byte is watts over idle ÷ `+
  `(GB/s × ${Math.min(...duty).toFixed(2)}–${Math.max(...duty).toFixed(2)}).`;
 const pc=q.dram.per_card, r=POOLED.read;
 $('remeasured').innerHTML=
  `<b>Re-measured.</b> The last column pools this session with the energy manual's 23 September passes (n = ${q.dram.n}, `+
  `${pc[A2].n===pc[A3].n?word(pc[A2].n)+' per card':word(pc[A2].n)+' on '+A2+', '+word(pc[A3].n)+' on '+A3}; `+
  `<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-between-cores-and-shires">§5</a>): `+
  `${f0(q.dram.mean/q.hop.mean)}× and ${f0(q.dram.mean/q.scp.mean)}× less than DRAM. Reading a byte costs ${f0(r.dram.mean)} `+
  `[${f0(r.dram.lo)}–${f0(r.dram.hi)}] pJ from DRAM, ${f2(r['scp-local'].mean)} from the shire's own scratchpad and `+
  `${f2(r['scp-remote'].mean)} from another shire's (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy">the energy manual, §4</a>).`;
})();

/* ---------- section 3: working-set size, to 256 MB ---------- */
(function(){
 const rows=D.size, mb=r=>r.stage_bytes*32/1048576, top=Math.max(...rows.map(mb));
 const big=D.bigsize.filter(r=>mb(r)>top);                    // DRAM-only continuation past the on-chip limit
 CK.legend('sizelegend',MED.map(m=>({key:m[0],label:m[3],mark:'dot',color:m[2]})));
 CK.frame('size',{label:'Relay bandwidth against working-set size for the three media, to 256 MB per buffer',height:W=>W<600?320:340,
  draw(f){
   const svg=f.svg,W=f.W,Hh=f.H,L=52,R=26,T=26,B=46,narrow=f.narrow;
   const x=CK.log(2,256,L,W-R), y=CK.log(20,2000,Hh-B,T);
   const sh=CK.el('rect',{x:x(top),y:T,width:W-R-x(top),height:Hh-B-T,'aria-hidden':'true'},svg); sh.style.fill='var(--grid)'; sh.style.opacity='0.6';
   CK.axes(f,{x,y,L,R,T,B,xt:narrow?[2,8,32,256]:[2,4,8,16,32,64,128,256],yt:[20,100,500,2000],yfmt:n0,xfmt:v=>v+' MB',
     xl:'working set, one buffer across the whole chip'});
   CK.txt(svg,4,T-10,'GB/s','lab');
   const lines=narrow?['no room on chip:','two buffers must','fit in 2.25 MB','per shire']:['no room: two buffers must fit','in the 2.25 MB left of each','shire’s scratchpad'];
   lines.forEach((t,i)=>CK.txt(svg,x(top)+6,y(400)+i*14,t,'lab'));
   CK.el('line',{x1:x(top/2),x2:x(top/2),y1:T,y2:Hh-B,style:'stroke:var(--ref);stroke-width:1.5;stroke-dasharray:5 4'},svg);
   CK.txt(svg,x(top/2)-6,T+12,narrow?'footprint = L3':'footprint = 32 MB of L3','lab','end');
   MED.forEach(m=>{
    const pts=rows.map(r=>[mb(r),r[m[0]].gb_s]).concat(m[0]==='dram'?big.map(r=>[mb(r),r.gb_s]):[]);
    CK.el('path',{d:CK.path(pts,x,y),fill:'none',style:`stroke:${m[2]};stroke-width:2`},svg);
    for(const [a,b] of pts){const c=CK.el('circle',{cx:x(a),cy:y(b),r:4,'aria-hidden':'true'},svg);c.style.fill=m[2];}
   });
   /* one focusable column per size: the crosshair lists every medium at that size */
   const cols=rows.map(r=>({mb:mb(r),r})).concat(big.map(r=>({mb:mb(r),big:r}))), nodes=[];
   for(const c of cols){
    const g=CK.el('g',{},svg), xc=x(c.mb);
    CK.el('rect',{x:xc-14,y:T,width:28,height:Hh-B-T,class:'ck-hit'},g);
    const ln=CK.el('line',{x1:xc,x2:xc,y1:T,y2:Hh-B,class:'xh'},g); ln.style.stroke='var(--ink-2)'; ln.style.strokeWidth='1'; ln.style.opacity='0';
    g.addEventListener('pointerenter',()=>{ln.style.opacity='0.6';}); g.addEventListener('pointerleave',()=>{ln.style.opacity='0';});
    g.addEventListener('focus',()=>{ln.style.opacity='0.6';}); g.addEventListener('blur',()=>{ln.style.opacity='0';});
    const html=c.big?`<b>${c.mb} MB per buffer</b> (footprint ${2*c.mb} MB)<br>DRAM ${gb(c.big.gb_s)} GB/s; the on-chip routes have no room`
     :`<b>${c.mb} MB per buffer</b> (footprint ${2*c.mb} MB)<br>DRAM ${gb(c.r.dram.gb_s)}, next shire ${gb(c.r.hop.gb_s)} (${f2(c.r.hop_over_dram)}×), `+
      `own ${gb(c.r.scp.gb_s)} (${f2(c.r.scp_over_dram)}×) GB/s`;
    CK.tip(f,g,html); nodes.push(g);
   }
   CK.keynav(f,nodes);
  }});
 const small=rows[0], last=rows[rows.length-1];
 const and=a=>a.slice(0,-1).join(', ')+' and '+a[a.length-1];
 const fit=rows.filter(r=>2*mb(r)<=32), lastfit=fit[fit.length-1];
 const hopMax=Math.max(...fit.map(r=>r.hop_over_dram));
 $('sizecap').textContent=
  `${A2}, log axes. Two buffers are live at once, so the chip footprint is twice the figure on the x axis; the dashed line `+
  `marks where that footprint equals the 32 MB L3. Past ${top} MB per buffer only the DRAM route can run: the buffers start 256 KB into `+
  `each shire's 2.5 MB scratchpad, and two of them no longer fit in what is left.`;
 $('sizetext').innerHTML=
  `At ${mb(small)} MB per buffer the DRAM route runs at <b>${g1(small.dram.gb_s)} GB/s</b>, because it is not `+
  `going to DRAM at all: the 32 MB L3 holds the whole thing. Handing the data to the next shire then buys `+
  `${small.hop_over_dram.toFixed(2)}×, which is nothing, and keeping it in the shire's own scratchpad `+
  `${small.scp_over_dram.toFixed(1)}×. Up to ${mb(lastfit)} MB per buffer, while both buffers fit in the L3, the hand-off `+
  `wins at most ${hopMax.toFixed(1)}×. At ${mb(last)} MB per buffer, a ${2*mb(last)} MB footprint, the DRAM route falls to `+
  `<b>${g1(last.dram.gb_s)} GB/s</b> and stays there: ${and(big.map(r=>g1(r.gb_s)))} GB/s at `+
  `${and(big.map(r=>String(mb(r))))} MB per buffer. `+
  `<b>The advantage is not a property of the computation. It is the L3 capacity.</b> Below it the cache is already doing most of the job; `+
  `above it, nothing is, unless you place the data yourself.`;
})();

/* ---------- section 4: arithmetic intensity ---------- */
(function(){
 const rows=D.intensity;
 const S=[['scp_over_dram',"own shire",'var(--c3)','scp'],['hop_over_dram',"next shire",'var(--c1)','hop']];
 CK.legend('intlegend',S.map(s=>({key:s[0],label:s[1],mark:'dot',color:s[2]})));
 CK.frame('intensity',{label:'Advantage over the DRAM route against vector adds per element',height:W=>W<600?320:340,
  draw(f){
   const svg=f.svg,W=f.W,Hh=f.H,L=48,R=14,T=48,B=46,narrow=f.narrow;
   const x=CK.log(1,256,L,W-R), y=CK.log(1,40,Hh-B,T);
   CK.axes(f,{x,y,L,R,T,B,xt:narrow?[1,16,256]:[1,4,16,64,256],yt:[1,2,5,10,20,40],yfmt:v=>v+'×',xfmt:v=>String(v),
     xl:'vector adds applied to every element, per stage'});
   CK.txt(svg,4,14,'faster than the DRAM route','lab');
   /* top axis: flops per byte read, w/4, the unit of the ridge points */
   CK.txt(svg,W-R,14,'flops per byte read','lab','end');
   CK.el('line',{x1:L,x2:W-R,y1:T,y2:T,class:'ck-axis'},svg);
   for(const w of (narrow?[1,16,256]:[1,4,16,64,256])) CK.txt(svg,x(w),T-8,num(w/4),'tick','middle');
   CK.el('line',{x1:L,x2:W-R,y1:y(1),y2:y(1),style:'stroke:var(--ref);stroke-width:1.5;stroke-dasharray:5 4'},svg);
   S.forEach(s=>{
    CK.el('path',{d:CK.path(rows.map(r=>[r.work,r[s[0]]]),x,y),fill:'none',style:`stroke:${s[2]};stroke-width:2`},svg);
    for(const r of rows){const c=CK.el('circle',{cx:x(r.work),cy:y(r[s[0]]),r:4,'aria-hidden':'true'},svg);c.style.fill=s[2];}
   });
   const nodes=[];
   for(const r of rows){
    const g=CK.el('g',{},svg), xc=x(r.work);
    CK.el('rect',{x:xc-14,y:T,width:28,height:Hh-B-T,class:'ck-hit'},g);
    CK.tip(f,g,`<b>${r.work} add${r.work>1?'s':''} per element</b> (${num(r.work/8)} flop per byte moved, ${num(r.work/4)} per byte read)<br>`+
     S.map(s=>`${s[1]}: ${r[s[0]].toFixed(1)}× DRAM (${g1(r[s[3]].gb_s)} GB/s)`).join('<br>'));
    nodes.push(g);
   }
   CK.keynav(f,nodes);
  }});
 const last=rows[rows.length-1], at=w=>rows.find(r=>r.work===w).hop_over_dram.toFixed(1);
 $('intcap').textContent=`${A2}, log axes. The dashed line is parity with DRAM. Each element is 4 bytes read `+
  'and 4 bytes written, so w adds per element are w/8 flops per byte moved; the top axis counts flops per byte read (w/4), the unit of the ridge points report.';
 $('inttext').innerHTML=
  `One add per element is pure data movement, and the hand-off is ${at(1)}× ahead. The lead holds to about four adds per element `+
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
 const d=D.distance, k=n=>d.find(r=>r.hop_distance===n).mesh_hops, mh=d.map(r=>r.mesh_hops.mean);
 const gb2=d.map(r=>r.by_card[A2].gb_s), gb3=d.map(r=>r.by_card[A3].gb_s), Ls=d.map(r=>r.longest.hops);
 const rk=a=>a.map((v,i)=>i).sort((i,j)=>a[j]-a[i]).join(','), same=rk(gb2)===rk(gb3);
 const byL=[...new Set(Ls)].sort((a,b)=>b-a);
 const rngOf=Lh=>rng(d.filter(r=>r.longest.hops===Lh).map(r=>r.gb_s),n0);
 const and=a=>a.slice(0,-1).join(', ')+' and '+a[a.length-1];
 const rngH=m=>`${m.min} to ${m.max}`;
 $('distintro').innerHTML=
  `The obvious worry about handing data to another shire is the network in between. Shire numbers do not follow `+
  `the mesh: on the shire map of the <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">on-chip `+
  `communication report</a>, the next shire in the ring is on average ${f1(k(1).mean)} mesh hops away `+
  `(${rngH(k(1))}), two places on ${f1(k(2).mean)}, and sixteen places on only ${f1(k(16).mean)} (${rngH(k(16))}). `+
  `Across the ${word(d.length)} offsets the bandwidth runs from ${n0(Math.min(...gb2))} to ${n0(Math.max(...gb2))} GB/s. It does not follow `+
  `the mean distance (${f1(Math.min(...mh))} to ${f1(Math.max(...mh))} hops). It falls with the longest hand-off in the ring: `+
  `${and(byL.map(String))} hops give ${and(byL.map(rngOf))} GB/s${same?', in the same order on both cards':''}. That is what one would expect `+
  `when every stage waits at a barrier for its slowest shire, but ${word(d.length)} offsets are a correlation, not a controlled test.`;
 const W_='style="white-space:normal"';
 $('dist').innerHTML=`<thead><tr><th class="num" ${W_}>Shire IDs back round the ring</th>`+
  `<th class="num" ${W_}>Mesh hops, mean</th><th class="num" ${W_}>Longest hand-off, hops</th><th class="num">GB/s, a2 / a3</th>`+
  `<th class="num" ${W_}>Against the next shire in ID order, a2 / a3</th></tr></thead><tbody>`+
  d.map(r=>`<tr><td class="num">${r.hop_distance}</td><td class="num">${f1(r.mesh_hops.mean)}</td><td class="num">${r.longest.hops}</td>`+
   `<td class="num">${g1(r.by_card[A2].gb_s)} / ${g1(r.by_card[A3].gb_s)}</td>`+
   `<td class="num">${(r.by_card[A2].gb_s/d[0].by_card[A2].gb_s).toFixed(2)}× / ${(r.by_card[A3].gb_s/d[0].by_card[A3].gb_s).toFixed(2)}×</td></tr>`).join('')+'</tbody>';
 CK.stackTable('dist');
 const slope=D.cards.map(c=>pear(Ls,d.map(r=>r.by_card[c].stage_cycles)).slope);
 const best=Math.max(...gb2), worst=d[0].by_card[A2].gb_s;
 $('distafter').innerHTML=
  `The headline in section 1 uses offset ${d[0].hop_distance}, the slowest of these. Transfers here are 32 KB per minion and pipelined, yet `+
  `the mesh distance still shows: the stage time grows about ${rng(slope,v=>n0(Math.round(v/100)*100))} cycles for each hop of the longest `+
  `hand-off (a least-squares line over the ${word(d.length)} offsets, one per card). The practical consequence is to keep the longest hand-off `+
  `short; in this sweep the ID ring's ${d[0].longest.hops}-hop pair cost ${f0(100*(1-worst/best))}% of the bandwidth of the best offset. `+
  `Placement is not free in energy either. On a loaded mesh each hop costs 1.5–2.2 pJ per byte of random data `+
  `(<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm#meaning">Heat per millimetre, §8</a>), about half of what a tensor `+
  `load of that byte from the shire's own scratchpad costs. The hand-off's bytes cross ${f1(k(1).mean)} hops on average, so a physical `+
  `neighbour should cost less (untested; section 7). This relay's slabs each hold a single value repeated, and such data costs less to `+
  `carry than random data.`;

 /* ---- the map and the scatter ---- */
 const LAY=D.layout, ring=D.ring, n=ring.length;
 const hops=(a,b)=>Math.abs(LAY[a][0]-LAY[b][0])+Math.abs(LAY[a][1]-LAY[b][1]);
 const src=(s,o)=>ring[(ring.indexOf(s)-o+n)%n];
 const R={longest:{},mean:{}};
 for(const c of D.cards){const g=d.map(r=>r.by_card[c].gb_s);R.longest[c]=pear(Ls,g);R.mean[c]=pear(mh,g);}
 let off=d[0].hop_distance, xm='longest', f=null;
 CK.seg('ringoff',{label:'Ring offset (shire IDs back)',options:d.map(r=>[r.hop_distance,String(r.hop_distance)]),value:off,onChange:v=>{off=v;upd();}});
 CK.seg('ringx',{label:'Scatter against',options:[['longest','longest hand-off'],['mean','mean hops']],value:xm,onChange:v=>{xm=v;upd();}});
 const out=CK.readout('ringout');
 function upd(){
  const r=d.find(q=>q.hop_distance===off);
  out.set(`<b>Offset ${off}:</b> mean ${f1(r.mesh_hops.mean)} hops, longest ${r.longest.hops} → ${f1(r.by_card[A2].gb_s)} GB/s (${A2}), ${f1(r.by_card[A3].gb_s)} (${A3}). `+
   `Bandwidth against the ${xm==='longest'?'longest hand-off':'mean hops'}, ${word(d.length)} offsets: r = ${num(R[xm][A2].r,2)} (${A2}), ${num(R[xm][A3].r,2)} (${A3}).`);
  if(f) f.redraw();
 }
 const ramp=h=>CK.ramp((h-1)/9);
 f=CK.frame('ring',{label:'Mesh map of who reads from whom at the chosen ring offset, and relay bandwidth against hand-off distance',
  height:W=>W<600?Math.min(44,Math.floor((W-20)/6))*6+62+300:360,
  draw(f){
   const svg=f.svg,W=f.W,narrow=f.narrow, r=d.find(q=>q.hop_distance===off);
   const c=narrow?Math.min(44,Math.floor((W-20)/6)):44, mapW=6*c, mx=narrow?Math.round((W-mapW)/2):8, my=24;
   const cx=s=>mx+LAY[s][0]*c+c/2, cy=s=>my+LAY[s][1]*c+c/2;
   const defs=CK.el('defs',{},svg);
   for(const [id,col] of [['rl-ah','var(--c2)'],['rl-ah2','var(--ink)']]){
    const m=CK.el('marker',{id,viewBox:'0 0 10 10',refX:8,refY:5,markerWidth:5,markerHeight:5,orient:'auto-start-reverse'},defs);
    CK.el('path',{d:'M0,0 L10,5 L0,10 z',style:`fill:${col}`},m);
   }
   CK.txt(svg,mx,14,`Who reads from whom at offset ${off}`,'lab');
   for(const [ex,ey] of D.empty) CK.el('rect',{x:mx+ex*c+3,y:my+ey*c+3,width:c-6,height:c-6,rx:5,fill:'none',style:'stroke:var(--grid);stroke-dasharray:3 3'},svg);
   const order=ring.slice().sort((a,b)=>LAY[a][1]-LAY[b][1]||LAY[a][0]-LAY[b][0]), cells=[];
   const arrow=(a,b,g,col,mk,w,shift)=>{  // straight source -> destination, stopping short of the destination's centre
    const x1=cx(a),y1=cy(a),x2=cx(b),y2=cy(b),L=Math.hypot(x2-x1,y2-y1),ux=(x2-x1)/L,uy=(y2-y1)/L,px=-uy*shift,py=ux*shift;
    CK.el('line',{x1:x1+ux*8+px,y1:y1+uy*8+py,x2:x2-ux*12+px,y2:y2-uy*12+py,'marker-end':`url(#${mk})`,style:`stroke:${col};stroke-width:${w}`},g);};
   const cellG=CK.el('g',{},svg), longG=CK.el('g',{'aria-hidden':'true'},svg), own=CK.el('g',{'aria-hidden':'true'},svg);
   const labG=CK.el('g',{'aria-hidden':'true',style:'pointer-events:none'},svg);
   for(const s of order){
    const h=hops(s,src(s,off)), g=CK.el('g',{},cellG);
    const rc=CK.el('rect',{x:mx+LAY[s][0]*c+2,y:my+LAY[s][1]*c+2,width:c-4,height:c-4,rx:6},g); rc.style.fill=ramp(h); rc.style.stroke='var(--grid)';
    const lt=CK.txt(labG,cx(s),cy(s)+4,String(s),'lab-strong','middle'); lt.style.fill=CK.rampInk((h-1)/9);
    lt.style.paintOrder='stroke'; lt.style.stroke=ramp(h); lt.style.strokeWidth='3px';
    g.dataset.s=s; cells.push(g);
    CK.tip(f,g,`<b>shire ${s}</b> reads from shire ${src(s,off)} · ${h} hop${h>1?'s':''}`);
    const on=()=>{own.textContent='';arrow(src(s,off),s,own,'var(--ink)','rl-ah2',2,0);}, offf=()=>{own.textContent='';};
    g.addEventListener('pointerenter',on); g.addEventListener('pointerleave',offf); g.addEventListener('focus',on); g.addEventListener('blur',offf);
   }
   for(const [a,b] of r.longest.pairs){
    const rev=r.longest.pairs.some(([p,q])=>p===b&&q===a);
    arrow(a,b,longG,'var(--c2)','rl-ah',2.5,rev?3:0);
   }
   CK.keynav(f,cells,{step:(k,K,nodes)=>{
     if(K!=='ArrowUp'&&K!=='ArrowDown')return null;
     const s=+nodes[k].dataset.s,[x,y]=LAY[s],dy=K==='ArrowDown'?1:-1;
     for(let yy=y+dy;yy>=0&&yy<6;yy+=dy){const j=nodes.findIndex(q=>LAY[+q.dataset.s][0]===x&&LAY[+q.dataset.s][1]===yy);if(j>=0)return j;}
     return k;}});
   /* colour key */
   const ky=my+mapW+10, kw=Math.min(mapW,200), kx=mx+(mapW-kw)/2;
   for(let h=1;h<=10;h++){const q=CK.el('rect',{x:kx+(h-1)*kw/10,y:ky,width:kw/10-1,height:10},svg);q.style.fill=ramp(h);q.style.stroke='var(--grid)';}
   CK.txt(svg,kx,ky+24,'1 hop','tick','start'); CK.txt(svg,kx+kw,ky+24,'10 hops','tick','end');
   const ak=CK.el('g',{'aria-hidden':'true'},svg);
   CK.el('line',{x1:kx,x2:kx+22,y1:ky+38,y2:ky+38,'marker-end':'url(#rl-ah)',style:'stroke:var(--c2);stroke-width:2.5'},ak);
   CK.txt(svg,kx+28,ky+42,'longest hand-off','tick');
   /* scatter */
   const sx0=narrow?48:mx+mapW+70, sx1=W-14, sy0=narrow?ky+78:28, sy1=f.H-44;
   const x=xm==='longest'?CK.lin(5.5,10.5,sx0,sx1):CK.lin(1,5,sx0,sx1), y=CK.lin(575,750,sy1,sy0);
   CK.axes({svg,W:sx1+14,H:sy1+44},{x,y,L:sx0,R:14,T:sy0,B:44,xt:xm==='longest'?[6,7,8,9,10]:[1,2,3,4,5],yt:[600,650,700,750],
     yfmt:n0,xl:xm==='longest'?'longest hand-off in the ring, mesh hops':'mean hand-off, mesh hops'});
   CK.txt(svg,sx0-44,sy0-10,'GB/s, whole relay','lab');
   const xv=q=>xm==='longest'?q.longest.hops:q.mesh_hops.mean;
   const F=R[xm][A2];
   /* the least-squares line, clipped to the plot (it would run past the axes at the ends) */
   const fy=v=>F.icpt+F.slope*v, cl=[y.domain[0],y.domain[1]].map(g=>(g-F.icpt)/F.slope).sort((p,q)=>p-q);
   const lx0=Math.max(x.domain[0],cl[0]), lx1=Math.min(x.domain[1],cl[1]);
   CK.el('line',{x1:x(lx0),x2:x(lx1),y1:y(fy(lx0)),y2:y(fy(lx1)),'aria-hidden':'true',
     style:'stroke:var(--ref);stroke-width:1.5;stroke-dasharray:5 4'},svg);
   /* r is in the readout above the chart, which follows the toggle */
   const pts=[];
   for(const q of d.slice().sort((a,b)=>xv(a)-xv(b))){
    const g=CK.el('g',{},svg), sel=q.hop_distance===off, X=x(xv(q));
    const p2=CK.el('circle',{cx:X,cy:y(q.by_card[A2].gb_s),r:sel?6.5:5},g); p2.style.fill='var(--c1)';
    const p3=CK.el('circle',{cx:X,cy:y(q.by_card[A3].gb_s),r:sel?10:8.5,fill:'none'},g); p3.style.stroke='var(--c1)'; p3.style.strokeWidth='1.5';
    if(sel){const rr=CK.el('circle',{cx:X,cy:y(q.by_card[A2].gb_s),r:14,fill:'none','aria-hidden':'true'},g);rr.style.stroke='var(--ink)';rr.style.strokeWidth='2';}
    const edge=X>sx1-70;
    CK.txt(g,edge?X-8:X+12,y(q.by_card[A2].gb_s)+(edge?-14:4),`offset ${q.hop_distance}`,'tick',edge?'end':'start');
    CK.tip(f,g,`<b>offset ${q.hop_distance}</b> · longest hand-off ${q.longest.hops} hops, mean ${f1(q.mesh_hops.mean)}<br>`+
     `${f1(q.by_card[A2].gb_s)} GB/s (${A2}), ${f1(q.by_card[A3].gb_s)} (${A3})<br>Enter shows this offset on the map`);
    g.dataset.o=q.hop_distance; g.addEventListener('click',()=>{off=q.hop_distance;segSet();});
    pts.push(g);
   }
   CK.keynav(f,pts,{onEnter:n=>{off=+n.dataset.o;segSet();}});
  }});
 function segSet(){const b=[...document.querySelectorAll('#ringoff [role=radio]')].find(e=>e.textContent===String(off));if(b)b.click();}
 upd();
 $('ringcap').textContent=
  `The map colours each shire by how many mesh hops the slab it reads at this offset has to travel (the stronger the blue, the farther); the arrows mark `+
  `the longest hand-offs, drawn straight from source to destination because the route the data takes on the mesh was not measured. `+
  `The scatter puts the relay's bandwidth against the longest hand-off (or, toggled, the mean): r = ${rng(D.cards.map(c=>R.longest[c].r),v=>num(v,2))} `+
  `against the longest on the two cards, ${D.cards.map(c=>num(R.mean[c].r,2)).join(' and ')} against the mean. Filled ${A2}, rings ${A3}. `+
  `Consistent with the slowest pair setting the pace at each barrier; ${word(d.length)} offsets, not a controlled test.`;
})();
