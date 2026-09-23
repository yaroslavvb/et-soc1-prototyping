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
const f0=v=>v.toFixed(0),f3=v=>v.toFixed(3);
const E=D.enercat.cards, A2=E.aifoundry2, A3=E.aifoundry3||[];
const key=r=>[r.pattern,r.operands,r.harts,r.scp].join('|');
const a2={},a3={}; A2.forEach(r=>a2[key(r)]=r); A3.forEach(r=>a3[key(r)]=r);
const g=(p,o,h,s)=>a2[[p,o,h,!!s].join('|')];
const R=D.rest, P80=R.P_fix_w+R.A_leak_80_w;

/* ---------- KPIs ---------- */
(function(){
 document.getElementById('k1').textContent=f1(P80)+' W, '+Math.round(100*R.A_leak_80_w/P80)+'% leakage';
 document.getElementById('k2').textContent=f0(g('fmadd_ps','random',2).pj_per_op)+' pJ';
 document.getElementById('k3').textContent=f0(g('tload','random',1,false).pj_per_byte/g('tload','random',1,true).pj_per_byte)+'×';
 const rat=[]; for(const k in a2){ if(!a3[k])continue; const r2=a2[k],r3=a3[k]; const v2=r2.bytes?r2.pj_per_byte:r2.pj_per_op, v3=r2.bytes?r3.pj_per_byte:r3.pj_per_op; if(v2)rat.push(v3/v2);}
 rat.sort((a,b)=>a-b); document.getElementById('k4').textContent=f3(rat[rat.length>>1]);
 const corr=A2.map(r=>Math.abs(r.leak_correction_w)).sort((a,b)=>a-b);
 document.getElementById('corr').textContent=f2(corr[corr.length>>1])+' W in the median, '+f2(corr[corr.length-1])+' W at most';
})();

/* ---------- 1. idle law ---------- */
(function(){
 const W=700,H=320,L=58,R2=16,T=26,B=52,{svg,tip,h}=host('idle',W,H);
 const x=v=>L+(W-L-R2)*(v-40)/55, y=v=>H-B-(H-B-T)*(v-15)/35;
 axes(svg,{W,H,L,R:R2,T,B,x,y,yt:[20,30,40,50],xt:[40,50,60,70,80,90],xl:'die temperature, °C',yl:'idle board power, W'});
 const law=[]; for(let t=40;t<=95;t+=1) law.push([t,R.P_fix_w+R.A_leak_80_w*Math.exp((t-80)/R.T_L_c)]);
 el('path',{d:path(law,x,y),class:'ln s1'},svg);
 el('line',{x1:L,x2:W-R2,y1:y(R.P_fix_w),y2:y(R.P_fix_w),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 txt(svg,W-R2-4,y(R.P_fix_w)-6,'fixed '+f1(R.P_fix_w)+' W','lab','end');
 R.measured_idle.forEach(p=>{const gg=el('g',{},svg);el('circle',{cx:x(p.T),cy:y(p.P),r:3.5,fill:'var(--c2)'},gg);
   hover(gg,tip,h,()=>`${p.T} °C: ${f2(p.P)} W measured (${p.n} samples)<br>law: ${f2(R.P_fix_w+R.A_leak_80_w*Math.exp((p.T-80)/R.T_L_c))} W`);});
 if(R.cards){const c=R.cards.aifoundry3; /* aifoundry3 idle from E20: 23.6 W at 51 C */
   const gg=el('g',{},svg); el('circle',{cx:x(51),cy:y(23.6),r:4.5,fill:'none',stroke:'var(--c3)','stroke-width':2},gg);
   txt(svg,x(51)+8,y(23.6)+4,'aifoundry3, 51 °C','lab'); hover(gg,tip,h,()=>'aifoundry3 idle: 23.6 W at 51 °C<br>the aifoundry2 law says 24.5 W');}
 document.getElementById('idlecap').textContent=`Line: the law fitted on 21 September. Dots: every whole-degree idle bin of that session. Ring: the other card, 25 °C below the fitted range. Leakage share: ${Math.round(100*R.curve.find(c=>c.T===60).leak_frac)}% at 60 °C, ${Math.round(100*R.curve.find(c=>c.T===80).leak_frac)}% at 80 °C, ${Math.round(100*R.curve.find(c=>c.T===90).leak_frac)}% at 90 °C.`;
 const rl=R.rails_73c;
 document.getElementById('rails').innerHTML='<thead><tr><th>Idle at 73 °C, by rail</th><th class="num">W</th><th class="num">Share</th></tr></thead><tbody>'+
  [['Minions',rl.minion],['SRAM: L2, L3, scratchpad',rl.sram],['Mesh',rl.noc],['No rail sensor: PCIe, DDR PHY, IO shire, regulators',rl.unsensed]].map(r=>`<tr><td>${r[0]}</td><td class="num">${f2(r[1])}</td><td class="num">${Math.round(100*r[1]/rl.board)}%</td></tr>`).join('')+
  `<tr><td><b>Board</b></td><td class="num"><b>${f2(rl.board)}</b></td><td></td></tr></tbody>`;
})();

/* ---------- 2. awake ---------- */
(function(){
 const s1=g('spin','zeros',1),s2=g('spin','zeros',2);
 document.getElementById('awake').innerHTML='<thead><tr><th>Minions awake, doing the least they can</th><th class="num">W over idle, 1,024 minions</th><th class="num">per minion</th><th class="num">per instruction</th></tr></thead><tbody>'+
  `<tr><td>One hart per minion, an addi loop</td><td class="num">${f2(s1.over_idle_w)}</td><td class="num">${f2(s1.over_idle_w/1024*1e3)} mW</td><td class="num">${f1(s1.pj_per_op)} pJ</td></tr>`+
  `<tr><td>Both harts</td><td class="num">${f2(s2.over_idle_w)}</td><td class="num">${f2(s2.over_idle_w/1024*1e3)} mW</td><td class="num">${f1(s2.pj_per_op)} pJ</td></tr>`+
  `<tr><td>1,024 minions stalled in a load that never returns (the hot line)</td><td class="num">1.41</td><td class="num">1.4 mW</td><td class="num">—</td></tr>`+
  `<tr><td>Activity term under a dense matmul</td><td class="num">26.2</td><td class="num">25.6 mW</td><td class="num">—</td></tr></tbody>`;
})();

/* ---------- 3. instructions ---------- */
(function(){
 const list=[['iadd','add',1],['ixor','xor',1],['imul','mul',1],['fadd_s','fadd.s',1],['fmul_s','fmul.s',1],['fmadd_s','fmadd.s',1],
   ['fadd_ps','fadd.ps ×8',8],['fmul_ps','fmul.ps ×8',8],['fmadd_ps','fmadd.ps ×8',8],['iadd_pi','fadd.pi ×8',8],['imul_pi','fmul.pi ×8',8],
   ['fexp_ps','fexp.ps ×8',8],['frcp_ps','frcp.ps ×8',8]];
 const W=700,H=360,L=58,R2=150,T=26,B=70,{svg,tip,h}=host('instr',W,H);
 const mx=Math.max(...list.map(l=>g(l[0],'random',2).pj_per_op))*1.05;
 const bw=(W-L-R2)/list.length, x=i=>L+bw*i, y=v=>H-B-(H-B-T)*v/mx;
 axes(svg,{W,H,L,R:R2,T,B,x:i=>x(i),y,yt:[0,40,80,120,160],xt:[],yl:'pJ per instruction, above idle'});
 const cols={zeros:'var(--c3)',const:'var(--c4)',random:'var(--c2)'};
 list.forEach((l,i)=>{['zeros','const','random'].forEach((o,j)=>{const r=g(l[0],o,2); const gg=el('g',{},svg);
   el('rect',{x:x(i)+bw*(0.08+0.28*j),y:y(r.pj_per_op),width:bw*0.26,height:H-B-y(r.pj_per_op),fill:cols[o]},gg);
   hover(gg,tip,h,()=>`<b>${l[1]}</b>, ${o}<br>${f1(r.pj_per_op)} pJ per instruction${l[2]>1?' ('+f1(r.pj_per_op/l[2])+' per lane)':''}<br>${f2(r.over_idle_w)} W over idle at ${r.ops_per_s.toExponential(2)}/s`);});
   const t=txt(svg,x(i)+bw*0.5,H-B+14,l[1],'tick','end'); t.setAttribute('transform',`rotate(-40 ${x(i)+bw*0.5} ${H-B+14})`);});
 [['zeros','var(--c3)'],['one constant','var(--c4)'],['random data','var(--c2)']].forEach((s,i)=>{el('rect',{x:W-R2+8,y:T+6+i*20,width:11,height:11,fill:s[1]},svg);txt(svg,W-R2+25,T+16+i*20,s[0],'lab');});
 document.getElementById('instrcap').textContent='Both harts of every minion issuing the instruction back to back; the multiply and the transcendentals are multi-cycle and issue at a quarter to an eighth of the rate.';
 document.getElementById('instrtab').innerHTML='<thead><tr><th>Instruction</th><th class="num">zeros</th><th class="num">constant</th><th class="num">random</th><th class="num">random / zeros</th><th class="num">per lane, random</th><th class="num">issue per hart per cycle</th><th class="num">aifoundry3, random</th></tr></thead><tbody>'+
  list.map(l=>{const z=g(l[0],'zeros',2),c=g(l[0],'const',2),r=g(l[0],'random',2),r3=a3[[l[0],'random',2,false].join('|')];
   return `<tr><td><code>${l[1]}</code></td><td class="num">${f1(z.pj_per_op)}</td><td class="num">${f1(c.pj_per_op)}</td><td class="num"><b>${f1(r.pj_per_op)}</b></td><td class="num">${f2(r.pj_per_op/z.pj_per_op)}×</td><td class="num">${l[2]>1?f1(r.pj_per_op/l[2]):'—'}</td><td class="num">${f2(r.ops_per_cycle_per_hart)}</td><td class="num">${r3?f1(r3.pj_per_op):'—'}</td></tr>`;}).join('')+'</tbody>';
 const ia=g('iadd','zeros',2),fa=g('fadd_s','zeros',2),vz=g('fadd_ps','zeros',2),vr=g('fadd_ps','random',2),fm=g('fmadd_ps','random',2),ex=g('fexp_ps','random',2);
 const tz=D.tensor.rows.find(r=>r.config==='fp32_randn');
 document.getElementById('instrtext').innerHTML=
  `<b>An integer add is the cheapest thing a core does, ${f1(ia.pj_per_op)} pJ on zeros</b>, almost all of it the awake core. `+
  `<b>A scalar float add costs ${f1(fa.pj_per_op/ia.pj_per_op)}× that</b> even on zeros; the FPU does not gate on zero. `+
  `<b>An eight-lane vector op on zeros costs the same as the scalar one</b> (${f1(vz.pj_per_op)} against ${f1(fa.pj_per_op)} pJ): idle lanes are free, and on random data the lanes cost ${f1(vr.pj_per_op/vz.pj_per_op)}× — the data dependence of the tensor unit, in the vector unit. `+
  `<b>Per lane, a random-data <code>fmadd.ps</code> is ${f1(fm.pj_per_op/8)} pJ, ${f1((fm.pj_per_op_vs_spin||0)/8)} over the addi loop; the tensor unit does the same multiply-add for ${f2(tz.pj_marginal)}.</b> `+
  `The datapath energy is the same in both; the tensor unit saves instruction issue. Transcendentals are the dearest instructions on the chip: <code>fexp.ps</code> is ${f0(ex.pj_per_op)} pJ for eight lanes at a quarter of the rate.`;
 document.getElementById('tensor').innerHTML='<thead><tr><th>TensorFMA, 16×16×16, 1,024 minions, 80 °C</th><th class="num">pJ per MAC, marginal</th><th class="num">pJ per MAC, loaded</th><th class="num">W over idle</th><th class="num">MACs per second</th></tr></thead><tbody>'+
  D.tensor.rows.map(t=>`<tr><td>${t.label}</td><td class="num"><b>${f3(t.pj_marginal)}</b></td><td class="num">${f2(t.pj_loaded)}</td><td class="num">${f2(t.over_idle_w)}</td><td class="num">${t.per_s.toExponential(2)}</td></tr>`).join('')+'</tbody>';
 const fl=D.tensor.flips;
 document.getElementById('flips').textContent=Object.keys(fl.e_fJ).map(c=>`${f3(fl.e_fJ[c])} fJ per ${fl.classes[c]}`).join(', ');
})();

/* ---------- 4. memory ---------- */
(function(){
 const paths=[['ld_l1',false,2,'L1 hit, flw.ps','read'],['st_l1',false,2,'L1 hit, fsw.ps','write'],
   ['tload',true,1,'own scratchpad, tensor load','read'],['tstore',true,1,'own scratchpad, tensor store','write'],
   ['tload',false,1,'DRAM, tensor load','read'],['tstore',false,1,'DRAM, tensor store','write'],['st_stream',false,2,'DRAM through the L1 write-back path','write']];
 const W=700,H=340,L=58,R2=150,T=26,B=90,{svg,tip,h}=host('mem',W,H);
 const bw=(W-L-R2)/paths.length, x=i=>L+bw*i, y=v=>H-B-(H-B-T)*Math.log10(Math.max(v,0.1)/0.1)/Math.log10(1000/0.1);
 axes(svg,{W,H,L,R:R2,T,B,x:i=>x(i),y,yt:[0.1,1,10,100,1000],yf:v=>v+'',xt:[],yl:'pJ per byte, above idle'});
 paths.forEach((p,i)=>{['zeros','random'].forEach((o,j)=>{const r=g(p[0],o,p[2],p[1]); const gg=el('g',{},svg);
   el('rect',{x:x(i)+bw*(0.12+0.4*j),y:y(r.pj_per_byte),width:bw*0.36,height:H-B-y(r.pj_per_byte),fill:o==='zeros'?'var(--c3)':'var(--c2)'},gg);
   hover(gg,tip,h,()=>`<b>${p[3]}</b>, ${o}<br>${f2(r.pj_per_byte)} pJ/B at ${(r.bytes_per_s/1e9).toFixed(0)} GB/s<br>${f2(r.over_idle_w)} W over idle`);});
   const t=txt(svg,x(i)+bw*0.5,H-B+14,p[3],'tick','end'); t.setAttribute('transform',`rotate(-32 ${x(i)+bw*0.5} ${H-B+14})`);});
 [['zeros','var(--c3)'],['random data','var(--c2)']].forEach((s,i)=>{el('rect',{x:W-R2+8,y:T+6+i*20,width:11,height:11,fill:s[1]},svg);txt(svg,W-R2+25,T+16+i*20,s[0],'lab');});
 document.getElementById('memcap').textContent='Log scale. Tensor loads and stores bypass the caches; the L1 rows are hits in a 256 B buffer; the last bar is a plain vector store streaming to DRAM through the L1.';
 document.getElementById('memtab').innerHTML='<thead><tr><th>Path</th><th class="num">zeros pJ/B</th><th class="num">random pJ/B</th><th class="num">random / zeros</th><th class="num">GB/s</th><th class="num">aifoundry3, random</th></tr></thead><tbody>'+
  paths.map(p=>{const z=g(p[0],'zeros',p[2],p[1]),r=g(p[0],'random',p[2],p[1]),r3=a3[[p[0],'random',p[2],!!p[1]].join('|')];
   return `<tr><td>${p[3]} <span class="small">(${p[4]})</span></td><td class="num">${f2(z.pj_per_byte)}</td><td class="num"><b>${f2(r.pj_per_byte)}</b></td><td class="num">${f2(r.pj_per_byte/z.pj_per_byte)}×</td><td class="num">${(r.bytes_per_s/1e9).toFixed(0)}</td><td class="num">${r3?f2(r3.pj_per_byte):'—'}</td></tr>`;}).join('')+'</tbody>';
 const dl=g('tload','random',1,false),sl=g('tload','random',1,true),ds=g('tstore','random',1,false),ss=g('st_stream','random',2,false),dz=g('tload','zeros',1,false);
 document.getElementById('memtext').innerHTML=
  `<b>DRAM is ${f0(dl.pj_per_byte/sl.pj_per_byte)}× the shire's own scratchpad per byte read.</b> A DRAM write by tensor store costs about what a read costs (${f0(ds.pj_per_byte)} against ${f0(dl.pj_per_byte)} pJ/B); `+
  `<b>the same bytes written through the L1 cost ${f1(ss.pj_per_byte/ds.pj_per_byte)}× more</b> and arrive at a third of the bandwidth, because every store allocates a line and the line goes down through L2 and L3. `+
  `<b>Even DRAM is data-dependent</b>: zeros ${f0(dz.pj_per_byte)}, random ${f0(dl.pj_per_byte)} pJ/B; the scratchpad doubles. A scratchpad write is twice a scratchpad read.`;
 document.getElementById('memold').innerHTML='<thead><tr><th>Level</th><th>Working set</th><th class="num">pJ/B</th><th class="num">GB/s</th><th class="num">implied GHz</th></tr></thead><tbody>'+
  D.memory_reads.rows.map(r=>`<tr><td>${r.level}</td><td class="small">${r.what}</td><td class="num">${f2(r.pj_per_byte)}</td><td class="num">${r.gb_s.toFixed(0)}</td><td class="num">${r.implied_ghz?f2(r.implied_ghz):'—'}</td></tr>`).join('')+'</tbody>';
})();

/* ---------- 5. comm ---------- */
(function(){
 const rp={}; D.relay.power.media.forEach(m=>rp[m.medium]=m);
 document.getElementById('comm').innerHTML='<thead><tr><th>Ring, 1 KB messages unless said</th><th>What moves</th><th class="num">pJ/B</th><th class="num">GB/s aggregate</th></tr></thead><tbody>'+
  D.comm.rows.map(r=>`<tr><td>${r.ring}</td><td class="small">${r.what}</td><td class="num"><b>${f2(r.pj_per_byte)}</b> ± ${f2(r.pj_spread)}</td><td class="num">${r.gb_s.toFixed(0)}</td></tr>`).join('')+
  `<tr><td>slab handed to the next shire through its scratchpad</td><td class="small">write where the next shire reads, read there (E25)</td><td class="num"><b>${f1(rp.hop.pj_per_byte)}</b></td><td class="num">${(rp.hop.bytes_per_s/1e9).toFixed(0)}</td></tr>`+
  `<tr><td>the same through DRAM</td><td class="small">write to DRAM, read back</td><td class="num">${f1(rp.dram.pj_per_byte)}</td><td class="num">${(rp.dram.bytes_per_s/1e9).toFixed(0)}</td></tr></tbody>`;
 const xs=D.comm.rows.filter(r=>r.ring.startsWith('xshire')&&!r.ring.includes('c4')).map(r=>r.pj_per_byte);
 document.getElementById('commtext').innerHTML=`Inside a neighbourhood a byte costs under a picojoule; inside a shire about ${f1(D.comm.rows.find(r=>r.ring==='shire').pj_per_byte)} pJ; across the mesh ${f0(Math.min(...xs))}–${f0(Math.max(...xs))} pJ, roughly flat in distance. <b>The step is leaving the shire, not the hops after that.</b> Small messages cost more per byte: the per-message overhead is a few hundred cycles of both harts.`;
})();

/* ---------- 6. sync ---------- */
(function(){
 const at={}; D.sync.atomics.runs.forEach(r=>at[r.label]=r);
 const bar=1024*1.4e-3*D.sync.barrier_cycles_chip/0.6e9*1e9;
 document.getElementById('sync').innerHTML='<thead><tr><th>Event</th><th class="num">Energy</th><th class="num">Time</th><th>Note</th></tr></thead><tbody>'+
  `<tr><td>Global atomic, one line, 1,024 requesters</td><td class="num"><b>${f1(at.contended.nj_per_op)} nJ</b></td><td class="num">${f0(at.contended.cycles_per_op)} cycles each at the bank</td><td class="small">the bank serialises; every requester stalls; the host shire loses its memory path</td></tr>`+
  `<tr><td>Global atomic, 32 lines, one per shire</td><td class="num">${f1(at.spread.nj_per_op)} nJ</td><td class="num">${f2(at.spread.cycles_per_op)} cycles each, aggregate</td><td class="small">the same instruction, ${f0(at.contended.nj_per_op/at.spread.nj_per_op)}× cheaper</td></tr>`+
  `<tr><td>Uncontended remote atomic round trip</td><td class="num">—</td><td class="num">${f0(D.sync.remote_atomic_latency_cycles)} cycles</td><td class="small"></td></tr>`+
  `<tr><td>Chip-wide barrier, 1,024 minions</td><td class="num">≈ ${f0(bar)} nJ of waiting</td><td class="num">${D.sync.barrier_cycles_chip.toLocaleString()} cycles</td><td class="small">derived: 1,024 minions stalled at 1.4 mW for its length</td></tr>`+
  `<tr><td>FLB + credit barrier, one shire</td><td class="num">—</td><td class="num">237 cycles</td><td class="small">nocbench</td></tr>`+
  `<tr><td>TensorReduce + broadcast, 32 minions</td><td class="num">—</td><td class="num">432 cycles</td><td class="small">nocbench</td></tr></tbody>`;
})();

/* ---------- 7. composition ---------- */
(function(){
 const t=D.tensor.rows.find(r=>r.config==='fp32_randn'), tz=D.tensor.rows.find(r=>r.config==='fp32_zeros');
 const sm=D.tensor.flips.p_sm_full_chip_w;
 const parts=[['fixed',R.P_fix_w,'var(--ref)'],['leakage at 80 °C',R.A_leak_80_w,'var(--c4)'],['tensor state machines',sm,'var(--c3)'],['multiply-adds',t.over_idle_w-sm,'var(--c2)']];
 const W=700,H=150,L=16,R2=16,T=30,B=40,{svg,tip,h}=host('comp',W,H);
 const tot=parts.reduce((s,p)=>s+p[1],0), x0=L; let acc=0;
 parts.forEach(p=>{const gg=el('g',{},svg); const w=(W-L-R2)*p[1]/tot;
   el('rect',{x:x0+(W-L-R2)*acc/tot,y:T,width:w,height:44,fill:p[2]},gg);
   txt(svg,x0+(W-L-R2)*(acc+p[1]/2)/tot,T+58+(w<90?14:0),`${p[0]} ${f1(p[1])} W`,'lab','middle');
   hover(gg,tip,h,()=>`${p[0]}: ${f1(p[1])} W, ${Math.round(100*p[1]/tot)}%`); acc+=p[1];});
 txt(svg,L,T-10,`predicted ${f1(tot)} W; measured ${f1(t.idle_w+t.over_idle_w)} W`,'lab-strong');
 document.getElementById('compcap').textContent=`Random data. Per flop that is ${f1(1e12*tot/(2*t.per_s))} pJ loaded and ${f2(t.pj_marginal/2)} pJ marginal; ${Math.round(100*P80/tot)}% of the energy of the most arithmetic-dense thing this chip does is static.`;
 document.getElementById('comptext').innerHTML=`The same matmul on zeros draws ${f1(tz.over_idle_w)} W over idle instead of ${f1(t.over_idle_w)}, and the loaded cost per flop becomes ${f1(1e12*(P80+tz.over_idle_w)/(2*tz.per_s))} pJ, almost all of it static. <b>On this card the data decides the dynamic energy and the temperature decides the rest.</b>`;
 const rp={}; D.relay.power.media.forEach(m=>rp[m.medium]=m);
 const mr={}; D.memory_reads.rows.forEach(r=>mr[r.level]=r);
 const pr=(rd,wr)=>[(rd[0]+wr[0])/2,(rd[1]+wr[1])/2];
 const rz=(p,s)=>[g(p,'zeros',1,s).pj_per_byte,g(p,'random',1,s).pj_per_byte];
 const pd=pr(rz('tload',false),rz('tstore',false)), ps=pr(rz('tload',true),rz('tstore',true)), ph=pr([mr['scp-remote'].pj_per_byte,mr['scp-remote'].pj_per_byte],rz('tstore',true));
 document.getElementById('relaycheck').innerHTML='<thead><tr><th>The relay of 22 September, predicted from section 4</th><th class="num">predicted pJ/B, zeros … random</th><th class="num">measured</th></tr></thead><tbody>'+
  `<tr><td>intermediate in DRAM</td><td class="num">${f0(pd[0])} … ${f0(pd[1])}</td><td class="num"><b>${f1(rp.dram.pj_per_byte)}</b></td></tr>`+
  `<tr><td>in the shire's own scratchpad</td><td class="num">${f1(ps[0])} … ${f1(ps[1])}</td><td class="num"><b>${f2(rp.scp.pj_per_byte)}</b></td></tr>`+
  `<tr><td>in the next shire's scratchpad</td><td class="num">${f1(ph[0])} … ${f1(ph[1])}</td><td class="num"><b>${f2(rp.hop.pj_per_byte)}</b> <span class="small">(a little above: the add and the barrier)</span></td></tr></tbody>`;
})();

/* ---------- 8. cards ---------- */
(function(){
 const pts=[]; for(const k in a2){ if(!a3[k])continue; const r2=a2[k],r3=a3[k]; const v2=r2.bytes?r2.pj_per_byte:r2.pj_per_op, v3=r2.bytes?r3.pj_per_byte:r3.pj_per_op; if(v2&&v3)pts.push([v2,v3,k.replace(/\|/g,' ')]);}
 const W=700,H=340,L=58,R2=16,T=26,B=52,{svg,tip,h}=host('cards',W,H);
 const lo=0.2,hi=400, x=v=>L+(W-L-R2)*Math.log10(v/lo)/Math.log10(hi/lo), y=v=>H-B-(H-B-T)*Math.log10(v/lo)/Math.log10(hi/lo);
 axes(svg,{W,H,L,R:R2,T,B,x,y,yt:[1,10,100],xt:[1,10,100],xl:'aifoundry2, pJ per instruction or per byte',yl:'aifoundry3'});
 el('line',{x1:x(lo),y1:y(lo),x2:x(hi),y2:y(hi),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 pts.forEach(p=>{const gg=el('g',{},svg);el('circle',{cx:x(p[0]),cy:y(p[1]),r:3.5,fill:'var(--c1)','fill-opacity':0.8},gg);hover(gg,tip,h,()=>`${p[2]}<br>aifoundry2 ${f2(p[0])}, aifoundry3 ${f2(p[1])}<br>ratio ${f3(p[1]/p[0])}`);});
 const rat=pts.map(p=>p[1]/p[0]).sort((a,b)=>a-b);
 document.getElementById('cardscap').textContent=`Log axes, dashed line is equality. ${pts.length} entries; ratio ${f3(rat[0])} to ${f3(rat[rat.length-1])}, median ${f3(rat[rat.length>>1])}. The tensor-unit transfer of 22 September found ${f3(D.cards&&D.cards.scale||0.924)} for the same pair of cards, with aifoundry3 running 5 mV higher — the scale is the card, not the operating point.`;
})();

/* ---------- 3.1 every instruction, and 4.3 fine grain (from the three-pass catalogue) ---------- */
(function(){
 const C=D.catalogue; if(!C){return;}
 const cards=Object.keys(C.cards), S=C.cards[cards[0]].summary, S2=cards[1]?C.cards[cards[1]].summary:{};
 const LANES=new Set(['fadd.ps','fsub.ps','fmul.ps','fmin.ps','fmax.ps','fsgnj.ps','fsgnjn.ps','fsgnjx.ps','fmadd.ps','fmsub.ps','fnmadd.ps','fnmsub.ps','feq.ps','flt.ps','fle.ps','fcmov.ps','fcmovm.ps','fround.ps','ffrc.ps','fclass.ps','fcvt.ps.pw','fcvt.pw.ps','fswizz.ps','fadd.pi','fsub.pi','fmul.pi','fmulh.pi','fmulhu.pi','fand.pi','for.pi','fxor.pi','fnot.pi','fsll.pi','fsrl.pi','fsra.pi','fmin.pi','fmax.pi','fminu.pi','fmaxu.pi','feq.pi','flt.pi','fltu.pi','fle.pi','faddi.pi','fandi.pi','fslli.pi','fsrli.pi','fsrai.pi','fpackrepb.pi','fpackreph.pi','fexp.ps','flog.ps','frcp.ps','feqm.ps','fltm.ps','flem.ps','fbcx.ps','fbci.ps','fbci.pi']);
 const CLASSES=[['Scalar integer, one cycle',['add','sub','and','or','xor','sll','srl','sra','slt','sltu','addw','subw','sllw','srlw','sraw','addi','andi','ori','xori','slli','srli','srai','slti','sltiu','addiw','lui','auipc','nop']],
  ['Scalar integer multiply and divide',['mul','mulh','mulhu','mulhsu','mulw','div','divu','rem','remu','divw','divuw','remw','remuw']],
  ['Scalar float',['fadd.s','fsub.s','fmul.s','fmin.s','fmax.s','fsgnj.s','fsgnjn.s','fsgnjx.s','fmadd.s','fmsub.s','fnmadd.s','fnmsub.s']],
  ['Between the float and integer register files',['feq.s','flt.s','fle.s','fclass.s','fcvt.w.s','fcvt.wu.s','fmv.x.w','fcvt.s.w','fcvt.s.wu','fmv.w.x']],
  ['Vector float, 8 lanes',['fadd.ps','fsub.ps','fmul.ps','fmin.ps','fmax.ps','fsgnj.ps','fsgnjn.ps','fsgnjx.ps','fmadd.ps','fmsub.ps','fnmadd.ps','fnmsub.ps','feq.ps','flt.ps','fle.ps','fcmov.ps','fcmovm.ps','fround.ps','ffrc.ps','fclass.ps','fcvt.ps.pw','fcvt.pw.ps','fswizz.ps']],
  ['Vector integer, 8 lanes',['fadd.pi','fsub.pi','fmul.pi','fmulh.pi','fmulhu.pi','fand.pi','for.pi','fxor.pi','fnot.pi','fsll.pi','fsrl.pi','fsra.pi','fmin.pi','fmax.pi','fminu.pi','fmaxu.pi','feq.pi','flt.pi','fltu.pi','fle.pi','faddi.pi','fandi.pi','fslli.pi','fsrli.pi','fsrai.pi','fpackrepb.pi','fpackreph.pi']],
  ['Transcendental unit, 8 lanes',['fexp.ps','flog.ps','frcp.ps']],['Masks and broadcasts',['feqm.ps','fltm.ps','flem.ps','fbcx.ps','fbci.ps','fbci.pi']],
  ['Loads and stores that hit the L1',['lb','lh','lw','ld','lbu','lhu','lwu','sb','sh','sw','sd','flw','fsw','flw.ps','fsw.ps']],['Loads and stores that bypass the L1',['flwl.ps','fswl.ps']],
  ['Branches and jumps',['beq_taken','bne_nottaken','blt_data','bge_data','bltu_data','bgeu_data','jal']],['Atomics on a private line',['amoaddl.w','amoswapl.w','amoorl.w','amomaxl.w','amoaddl.d','amoaddg.w','amoaddg.d']],
  ['System',['csrr_fccnb','fence']],['Compressed against full-width, in-place forms',['c.add','add_norvc','c.addi','addi_norvc','c.mv','c.li']]];
 const g=(n,o)=>S[`${n}/${o}/h2`], g2=(n,o)=>S2[`${n}/${o}/h2`];
 document.getElementById('trapped').textContent='fdiv.s, fsqrt.s, fdiv.ps, fsqrt.ps, frsq.ps, fsin.ps, fdiv.pi, fdivu.pi, frem.pi, fremu.pi, fcvt.l.s, fcvt.s.l, csrr cycle';
 // chart: all instructions sorted by random-data energy
 const all=[]; CLASSES.forEach((c,ci)=>c[1].forEach(n=>{const r=g(n,'random'),z=g(n,'zeros'); if(r&&z) all.push({n,ci,r,z,r2:g2(n,'random')});}));
 all.sort((a,b)=>a.r.pj_per_op.mean-b.r.pj_per_op.mean);
 if(!all.length){return;}
 const W=Math.max(700,all.length*9+80),H=360,L=58,R2=16,T=26,B=96,{svg,tip,h}=host('allinstr',W,H);
 const mx=Math.max(...all.map(a=>a.r.pj_per_op.mean)); const bw=(W-L-R2)/all.length;
 const y=v=>H-B-(H-B-T)*Math.log10(Math.max(v,1)/1)/Math.log10(mx*1.1/1);
 axes(svg,{W,H,L,R:R2,T,B,x:v=>v,y,yt:[1,10,100,1000].filter(v=>v<=mx*1.1),yf:v=>v+'',xt:[],yl:'pJ per instruction, random data (log)'});
 const COL=['var(--c1)','var(--c7)','var(--c2)','var(--c5)','var(--c3)','var(--c4)','var(--bad)','var(--muted)','var(--ok)','var(--warn)','var(--ink-2)','var(--ref)','var(--axis)','var(--ink)'];
 all.forEach((a,i)=>{const gg=el('g',{},svg); const x=L+bw*i;
   el('rect',{x:x+1,y:y(a.r.pj_per_op.mean),width:Math.max(1,bw-2),height:H-B-y(a.r.pj_per_op.mean),fill:COL[a.ci%COL.length]},gg);
   el('line',{x1:x+bw/2,x2:x+bw/2,y1:y(a.z.pj_per_op.mean),y2:y(a.z.pj_per_op.mean),stroke:'var(--ink)'},gg);
   if(i%2===0){const t=txt(svg,x+bw/2,H-B+10,a.n,'tick','end'); t.setAttribute('font-size','9'); t.setAttribute('transform',`rotate(-60 ${x+bw/2} ${H-B+10})`);}
   hover(gg,tip,h,()=>`<b>${a.n}</b> — ${CLASSES[a.ci][0]}<br>random ${a.r.pj_per_op.mean.toFixed(1)} ± ${a.r.pj_per_op.se.toFixed(2)} pJ${LANES.has(a.n)?' ('+(a.r.pj_per_op.mean/8).toFixed(1)+' per lane)':''}<br>zeros ${a.z.pj_per_op.mean.toFixed(1)} pJ<br>${a.r.ops_per_cycle_per_hart.mean.toFixed(3)} per hart per cycle<br>${a.r2?cards[1]+': '+a.r2.pj_per_op.mean.toFixed(1)+' pJ, ratio '+(a.r2.pj_per_op.mean/a.r.pj_per_op.mean).toFixed(3):''}`);});
 const leg=document.createElement('div'); leg.className='legend'; leg.innerHTML=CLASSES.map((c,ci)=>`<span><i style="background:${COL[ci%COL.length]}"></i>${c[0]}</span>`).join(''); h.parentNode.insertBefore(leg,h);
 const rel=all.map(a=>a.r.pj_per_op.se/a.r.pj_per_op.mean).sort((a,b)=>a-b);
 document.getElementById('allcap').textContent=`${all.length} instructions. Bar: random data; tick: zeros. Standard error over the three passes is ${(100*rel[rel.length>>1]).toFixed(1)}% in the median and ${(100*rel[Math.floor(rel.length*0.9)]).toFixed(1)}% at the 90th percentile.`;
 document.getElementById('alltab').innerHTML='<thead><tr><th>Instruction</th><th class="num">zeros pJ</th><th class="num">random pJ</th><th class="num">± se</th><th class="num">per lane</th><th class="num">random / zeros</th><th class="num">issue per hart per cycle</th><th class="num">'+(cards[1]||'card 2')+'</th><th class="num">ratio</th></tr></thead><tbody>'+
  CLASSES.map(c=>`<tr><td colspan="9"><b>${c[0]}</b></td></tr>`+c[1].map(n=>{const r=g(n,'random'),z=g(n,'zeros'),r2=g2(n,'random'); if(!(r&&z))return '';
   return `<tr><td><code>${n}</code></td><td class="num">${z.pj_per_op.mean.toFixed(1)}</td><td class="num"><b>${r.pj_per_op.mean.toFixed(1)}</b></td><td class="num">${r.pj_per_op.se.toFixed(2)}</td><td class="num">${LANES.has(n)?(r.pj_per_op.mean/8).toFixed(1):'—'}</td><td class="num">${(r.pj_per_op.mean/z.pj_per_op.mean).toFixed(2)}×</td><td class="num">${r.ops_per_cycle_per_hart.mean.toFixed(3)}</td><td class="num">${r2?r2.pj_per_op.mean.toFixed(1):'—'}</td><td class="num">${r2?(r2.pj_per_op.mean/r.pj_per_op.mean).toFixed(3):'—'}</td></tr>`;}).join('')).join('')+'</tbody>';
 const cheapest=all[0], dearest=all[all.length-1];
 const cc=C.cross_card;
 document.getElementById('alltext').innerHTML=`The cheapest instruction is <code>${cheapest.n}</code> at ${cheapest.r.pj_per_op.mean.toFixed(1)} pJ and the dearest <code>${dearest.n}</code> at ${dearest.r.pj_per_op.mean.toFixed(0)} pJ, a span of ${(dearest.r.pj_per_op.mean/cheapest.r.pj_per_op.mean).toFixed(0)}×. `+
  (cc?`Across ${cc.n} configurations the second card is ${cc.median.toFixed(3)}× the first (10th to 90th percentile ${cc.p10.toFixed(3)} to ${cc.p90.toFixed(3)}). `:'')+
  `Within a class the instructions cost the same to within a few percent — the energy is the unit's, not the opcode's — and the classes differ by an order of magnitude.`;

 /* ---- wires ---- */
 const Wf=C.cards[cards[0]].wire; if(Wf&&Wf.random&&Wf.zeros){
  const W2=700,H2=320,L2=58,R3=140,T2=26,B2=52,{svg:sv,tip:tp,h:hh}=host('wire',W2,H2);
  const mxh=Math.max(...Wf.random.points.map(p=>p.hops)), mxy=Math.max(...Wf.random.points.map(p=>p.pj_per_byte))*1.15;
  const x=v=>L2+(W2-L2-R3)*v/(mxh+0.5), yy=v=>H2-B2-(H2-B2-T2)*v/mxy;
  axes(sv,{W:W2,H:H2,L:L2,R:R3,T:T2,B:B2,x,y:yy,yt:[0,2,4,6,8,10].filter(v=>v<=mxy),xt:[0,1,2,3,4,5,6,7,8].filter(v=>v<=mxh),xl:'hops across the mesh to the scratchpad read',yl:'pJ per byte'});
  [['zeros',Wf.zeros,'var(--c3)'],['random',Wf.random,'var(--c2)']].forEach((s2,i)=>{const wf=s2[1];
   el('path',{d:path([[0,wf.intercept_pj_per_byte],[mxh,wf.intercept_pj_per_byte+wf.slope_pj_per_byte_per_hop*mxh]],x,yy),class:'ln',stroke:s2[2],'stroke-dasharray':'5 4'},sv);
   wf.points.forEach(p=>{const gg=el('g',{},sv);el('circle',{cx:x(p.hops),cy:yy(p.pj_per_byte),r:4,fill:s2[2]},gg);hover(gg,tp,hh,()=>`${p.hops} hops, ${s2[0]}: ${p.pj_per_byte.toFixed(2)} ± ${p.se.toFixed(2)} pJ/B<br>${p.shires} shires reading`);});
   if(wf.local_pj_per_byte!=null){const gg=el('g',{},sv);el('circle',{cx:x(0),cy:yy(wf.local_pj_per_byte),r:4,fill:'none',stroke:s2[2],'stroke-width':2},gg);hover(gg,tp,hh,()=>`own scratchpad, ${s2[0]}: ${wf.local_pj_per_byte.toFixed(2)} pJ/B`);}
   el('rect',{x:W2-R3+8,y:T2+6+i*20,width:11,height:11,fill:s2[2]},sv);txt(sv,W2-R3+25,T2+16+i*20,s2[0]+' data','lab');});
  const dz=Wf.zeros.slope_pj_per_byte_per_hop, dr=Wf.random.slope_pj_per_byte_per_hop;
  document.getElementById('wirecap').textContent=`1 KB tensor loads from a scratchpad exactly d hops away, every shire reading, at most two readers per target. Rings at d = 0 are the shire's own scratchpad. Dashed: straight-line fits.`;
  document.getElementById('wiretext').innerHTML=`<b>One hop of mesh costs ${dr.toFixed(3)} pJ per byte on random data and ${dz.toFixed(3)} on zeros.</b> The difference, ${(dr-dz).toFixed(3)} pJ/B per hop — <b>${((dr-dz)*1000/8).toFixed(1)} fJ per bit per hop</b> — is the switching energy of the wires and router flops themselves; the ${dz.toFixed(3)} pJ/B that a hop costs even when no bit changes is clocking, arbitration and buffering. The intercept, ${Wf.random.intercept_pj_per_byte.toFixed(2)} pJ/B on random data against ${(Wf.random.local_pj_per_byte||0).toFixed(2)} for the shire's own scratchpad, is the array access plus the step of leaving the shire at all.`;
 }
 /* ---- lines and rows ---- */
 const fz=S['l1fill/stride32/zeros'],fr=S['l1fill/stride32/random'],gz=S['l1fill/stride64/zeros'],gr=S['l1fill/stride64/random'];
 if(fz&&fr&&gz&&gr){
  document.getElementById('linetab').innerHTML='<thead><tr><th>32 B loads through the L1 from the shire’s scratchpad</th><th class="num">fills per load</th><th class="num">zeros pJ per load</th><th class="num">random pJ per load</th></tr></thead><tbody>'+
   [['32','0.5',fz,fr],['64','1',gz,gr],['128','1',S['l1fill/stride128/zeros'],S['l1fill/stride128/random']]].map(r=>r[2]&&r[3]?`<tr><td>stride ${r[0]} B</td><td class="num">${r[1]}</td><td class="num">${r[2].pj_per_op.mean.toFixed(1)}</td><td class="num">${r[3].pj_per_op.mean.toFixed(1)}</td></tr>`:'').join('')+
   '<tr><td colspan="4"><b>64 B tensor loads from the scratchpad, by stride</b></td></tr>'+
   ['64','128','256'].map(st=>{const z=S[`scpline/stride${st}/zeros`],r=S[`scpline/stride${st}/random`]; return z&&r?`<tr><td>stride ${st} B (${st==='64'?'cycles the banks':st==='128'?'alternates two banks':'the same bank every time'})</td><td class="num">—</td><td class="num">${(z.pj_per_byte.mean*64).toFixed(1)} per 64 B</td><td class="num">${(r.pj_per_byte.mean*64).toFixed(1)} per 64 B, ${(r.bytes_per_s.mean/1e9).toFixed(0)} GB/s</td></tr>`:'';}).join('')+'</tbody>';
  const fillz=2*(gz.pj_per_op.mean-fz.pj_per_op.mean), fillr=2*(gr.pj_per_op.mean-fr.pj_per_op.mean);
  document.getElementById('linetext').innerHTML=`Twice the difference between the stride-64 and stride-32 rows is what filling one 64 B line from the scratchpad into the L1 costs: <b>${fillz.toFixed(0)} pJ on zeros, ${fillr.toFixed(0)} pJ on random data</b> — ${(fillz/64).toFixed(1)} and ${(fillr/64).toFixed(1)} pJ per byte of line, the same as a tensor load pays for the same bytes from the same scratchpad. About ${(fillr-fillz).toFixed(0)} pJ of a fill is the toggling of its 512 bits, ${((fillr-fillz)*1000/512).toFixed(0)} fJ per bit on the path from the shire cache into the L1.`;
 }
 const rz2=n=>S[`dramrow2/${n}/zeros`], rr2=n=>S[`dramrow2/${n}/random`];
 if(rz2('seq')&&rz2('rowmiss')){
  document.getElementById('rowtab').innerHTML='<thead><tr><th>1 KB tensor loads from DRAM, 32 harts with 64 MB each</th><th class="num">zeros pJ/B</th><th class="num">random pJ/B</th><th class="num">GB/s</th></tr></thead><tbody>'+
   [['seq','sequential: next bank, 32 columns per row visit'],['rowhit','same bank and row, next column, every access'],['rowmiss','a new row on every visit to a bank']].map(r=>{const z=rz2(r[0]),x=rr2(r[0]);return z&&x?`<tr><td>${r[1]}</td><td class="num">${z.pj_per_byte.mean.toFixed(1)} ± ${z.pj_per_byte.se.toFixed(1)}</td><td class="num">${x.pj_per_byte.mean.toFixed(1)} ± ${x.pj_per_byte.se.toFixed(1)}</td><td class="num">${(x.bytes_per_s.mean/1e9).toFixed(1)}</td></tr>`:'';}).join('')+'</tbody>';
  const l3=S['dramrow/stride8K/random'], l3z=S['dramrow/stride8K/zeros'];
  document.getElementById('rowtext').innerHTML=`<b>The row pattern does not change the energy per byte</b>: row hits, row misses and the streaming case agree within their pass-to-pass error on both operand sets. Either the controller closes pages after each access, so the baseline already includes an activation, or the activation is small next to the transfer; the instruments cannot tell which, and for a programmer it makes no difference.`+(l3&&l3z?` An earlier version of this experiment with all 1,024 minions and only 32 KB touched per hart fitted in the L3 and measured that instead: <b>${l3z.pj_per_byte.mean.toFixed(1)} pJ/B on zeros, ${l3.pj_per_byte.mean.toFixed(1)} on random data at ${(l3.bytes_per_s.mean/1e9).toFixed(0)} GB/s</b>, the L3 read by tensor loads through the mesh.`:'');
 }
 /* ---- rails: where the current flows ---- */
 (function(){
  const groups=[['scalar integer',['add','sub','and','or','xor','sll','srl','sra','slt','sltu','addi','andi','ori','xori','slli','srli'].map(n=>`${n}/random/h2`)],
   ['scalar multiply',['mul','mulh','mulhu','mulhsu'].map(n=>`${n}/random/h2`)],['scalar float',['fadd.s','fsub.s','fmul.s','fmadd.s','fmsub.s'].map(n=>`${n}/random/h2`)],
   ['vector float',['fadd.ps','fsub.ps','fmul.ps','fmadd.ps','fmsub.ps'].map(n=>`${n}/random/h2`)],['vector integer',['fadd.pi','fsub.pi','fmul.pi','fand.pi','fxor.pi'].map(n=>`${n}/random/h2`)],
   ['transcendental',['fexp.ps','flog.ps','frcp.ps'].map(n=>`${n}/random/h2`)],['L1 hits',['lw','ld','sw','sd','flw.ps','fsw.ps'].map(n=>`${n}/random/h2`)],
   ['L1-bypass to the L2',['flwl.ps','fswl.ps'].map(n=>`${n}/random/h2`)],['atomics, local L2',['amoaddl.w/random/h2','amoaddl.d/random/h2']],['atomics, home L3',['amoaddg.w/random/h2','amoaddg.d/random/h2']],
   ['own scratchpad, tensor load',['tload/scp/random']],['own scratchpad, tensor store',['tstore/scp/random']],['scratchpad 1 hop away',['wire/hop1/random']],['scratchpad 3 hops away',['wire/hop3/random']],['scratchpad 6 hops away',['wire/hop6/random']],
   ['L3, tensor load',['dramrow/stride8K/random']],['DRAM, tensor load',['tload/dram/random']],['DRAM, tensor store',['tstore/dram/random']],['DRAM via the L1 write-back path',['st_stream/dram/random']]];
  const rows=[]; groups.forEach(gp=>{const rs=gp[1].map(k=>S[k]).filter(Boolean); if(!rs.length)return;
   const o=rs.reduce((a,r)=>a+r.over_idle_w.mean,0)/rs.length, m=rs.reduce((a,r)=>a+r.rails_over_w.minion_w.mean,0)/rs.length,
         sr=rs.reduce((a,r)=>a+r.rails_over_w.sram_w.mean,0)/rs.length, n=rs.reduce((a,r)=>a+r.rails_over_w.noc_w.mean,0)/rs.length;
   rows.push({label:gp[0],o,parts:[['minions',m,'var(--c1)'],['SRAM',sr,'var(--c3)'],['mesh',n,'var(--c2)'],['unmetered',o-m-sr-n,'var(--ref)']]});});
  if(!rows.length)return;
  const W=700,H=rows.length*26+60,L=220,R=16,T=30,B=20,{svg,tip,h}=host('railsplit',W,H);
  const x=v=>L+(W-L-R)*Math.max(0,Math.min(1,v));
  rows.forEach((r,i)=>{const y=T+i*26; let acc=0; txt(svg,L-8,y+15,r.label,'lab','end');
   r.parts.forEach(p=>{const fr=Math.max(0,p[1]/r.o); const gg=el('g',{},svg); el('rect',{x:x(acc),y:y+2,width:Math.max(0,x(acc+fr)-x(acc)),height:20,fill:p[2]},gg);
    hover(gg,tip,h,()=>`<b>${r.label}</b>: ${r.o.toFixed(2)} W over idle<br>${p[0]} ${p[1].toFixed(2)} W (${Math.round(100*fr)}%)`); acc+=fr;});});
  [['minions','var(--c1)'],['SRAM','var(--c3)'],['mesh','var(--c2)'],['unmetered (regulators, PHYs)','var(--ref)']].forEach((s2,i)=>{el('rect',{x:L+8+i*110,y:T-22,width:11,height:11,fill:s2[1]},svg);const t=txt(svg,L+23+i*110,T-13,s2[0],'lab');t.setAttribute('font-size','10');});
  document.getElementById('railscap').textContent='Random data. The split of each burst’s power over idle across the three rails the service processor meters, read from the end of the burst and corrected for the rails’ one-second filter; the remainder has no sensor.';
  const wire6=rows.find(r=>r.label==='scratchpad 6 hops away'), si=rows.find(r=>r.label==='scalar integer'), dr=rows.find(r=>r.label==='DRAM, tensor load');
  if(wire6&&si) document.getElementById('railstext').innerHTML=`<b>An instruction’s energy is the core’s</b>: ${Math.round(100*si.parts[0][1]/si.o)}% of a scalar integer burst is on the minion rail, almost nothing on the SRAM or the mesh, and the rest is what the regulators lose delivering it. <b>A byte fetched across the mesh is mostly wire</b>: six hops away, ${Math.round(100*wire6.parts[2][1]/wire6.o)}% of the energy is on the mesh rail and ${Math.round(100*wire6.parts[1][1]/wire6.o)}% on the SRAM that holds it, with the minions that asked for it at ${Math.round(100*wire6.parts[0][1]/wire6.o)}%.`+(dr?` <b>A DRAM byte is mostly off-chip</b>: ${Math.round(100*(dr.parts[3][1])/dr.o)}% of its energy is on no metered rail at all — the DDR PHY and the memory itself.`:'');
 })();

 /* ---- SRAM leakage ---- */
 const sl=C.cards[cards[0]].sram_leakage; if(sl&&sl.fit&&sl.curve.length>2){
  const W3=700,H3=280,L3=58,R4=16,T3=26,B3=52,{svg:sv,tip:tp,h:hh}=host('sram',W3,H3);
  const xs=sl.curve.map(c=>c.T), ys=sl.curve.map(c=>c.sram_w);
  const x=v=>L3+(W3-L3-R4)*(v-Math.min(...xs)+1)/(Math.max(...xs)-Math.min(...xs)+2), yy=v=>H3-B3-(H3-B3-T3)*(v-Math.min(...ys)*0.9)/(Math.max(...ys)*1.05-Math.min(...ys)*0.9);
  axes(sv,{W:W3,H:H3,L:L3,R:R4,T:T3,B:B3,x,y:yy,yt:[1.5,2,2.5,3,3.5].filter(v=>v>=Math.min(...ys)*0.9&&v<=Math.max(...ys)*1.05),xt:xs.filter((v,i)=>i%2===0),xl:'die temperature, °C',yl:'SRAM rail, W (idle)'});
  const fit=sl.fit, law=[]; for(let t=Math.min(...xs);t<=Math.max(...xs);t+=0.5) law.push([t,fit.P_fix_w+fit.A_leak_80_w*Math.exp((t-80)/36)]);
  el('path',{d:path(law,x,yy),class:'ln s1'},sv);
  sl.curve.forEach(c=>{const gg=el('g',{},sv);el('circle',{cx:x(c.T),cy:yy(c.sram_w),r:3.5,fill:'var(--c2)'},gg);hover(gg,tp,hh,()=>`${c.T} °C: ${c.sram_w.toFixed(3)} W on the SRAM rail (${c.n} idle samples)`);});
  document.getElementById('sramcap').textContent=`The rail feeding 128 MB of on-chip SRAM, at idle. Fit: ${fit.P_fix_w.toFixed(2)} W + ${fit.A_leak_80_w.toFixed(2)} W·e^((T−80)/36): ${fit.mw_per_mb_at_80.toFixed(1)} mW per MB at 80 °C, ${(fit.mw_per_mb_at_80/8/1024/1024*1e6).toFixed(1)} nW per bit including the cache logic on the same rail. A byte that sits in scratchpad for a second at 80 °C costs ${(fit.mw_per_mb_at_80/1024/1024*1e9).toFixed(1)} pJ of leakage, against ${(S['tload/scp/random']||{pj_per_byte:{mean:0}}).pj_per_byte.mean.toFixed(1)} pJ to read it once.`;
 }
 const nb=[0,1,2,3].map(k=>S[`neigh/${k}/random`]); if(nb.every(v=>v)){
  document.getElementById('neightab').innerHTML='<thead><tr><th>Which neighbourhood reads the shire’s own scratchpad (random data)</th><th class="num">pJ/B</th><th class="num">± se</th><th class="num">GB/s</th></tr></thead><tbody>'+
   nb.map((v,k)=>`<tr><td>neighbourhood ${k}, minions ${8*k}–${8*k+7}</td><td class="num">${v.pj_per_byte.mean.toFixed(2)}</td><td class="num">${v.pj_per_byte.se.toFixed(2)}</td><td class="num">${(v.bytes_per_s.mean/1e9).toFixed(0)}</td></tr>`).join('')+'</tbody>';
 }
})();
