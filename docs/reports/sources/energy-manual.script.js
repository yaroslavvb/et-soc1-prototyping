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
