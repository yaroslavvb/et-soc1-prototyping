const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
const chip=(s,t)=>`<span class="chip ${s}">${t}</span>`;
const M=[
 ['Board power, now','whole card · new value per 133 ms · 10 mW','DM_CMD_GET_MODULE_POWER (ettelem: up to 45 samples/s; the SP refreshes it once per pass)','works_now','works now'],
 ['Board power, PMIC average / min / max','whole card · the PMIC\'s running average (τ ≈ 1 s; 88% of a step after 2 s); min and max since the last stats reset','DM_CMD_GET_SP_STATS via ettelem (the stock CLI calls it unsupported), or the SPST trace','works_now','works now'],
 ['Rail power: minion cores, SRAM, mesh','3 rails · 1 mW · the PMIC\'s running average (τ ≈ 1 s; 88% of a step after 2 s), one record per 133 ms, plus min/max','same snapshot; the SPST trace keeps ~15 min of records with µs stamps','works_now','works now'],
 ['Rail voltage and clock','3 rails · 1 mV · avg/min/max; minion and mesh MHz','same snapshot','works_now','works now'],
 ['On-die voltage per domain','7 domains (DDR, SRAM, Maxion, minion, PCIe shire, mesh, IO shire) · 1 mV','DM_CMD_GET_ASIC_VOLTAGE; compare with the regulator set-points from DM_CMD_GET_MODULE_VOLTAGE for the drop to the die','works_now','works now'],
 ['On-die voltage per shire','34 minion shires × 3 rails + 8 memory shires × 2 · 1 mV · current, and hardware low/high between polls','SP log at DEBUG level: ettelem loglevel debug + sptrace (4 KB buffer, wraps about once per pass)','works_now','works now'],
 ['Temperature','IO shire, and mean, low and high of the 34 minion-shire sensors · 1 °C · per 133 ms; "low/high" are extremes since reset, not the current spread','DM_CMD_GET_MODULE_CURRENT_TEMPERATURE (its field labelled PMIC holds the minion mean again)','works_now','works now'],
 ['Power state, throttle residency, thresholds','card-wide · µs residency counters','DM_CMD_GET_MODULE_POWER_STATE, _RESIDENCY_*, _TEMPERATURE_THRESHOLDS, _STATIC_TDP_LEVEL','works_now','works now'],
 ['Device-wide bandwidth and utilisation','DDR, L2/L3, PCIe · 1 ms samples','MMST trace; a proxy for where memory energy goes','works_now','works now'],
 ['Energy per event','pJ per load, per multiply-add, per mesh hop · needs ≥10⁹ identical events/s for seconds','rail power above a same-temperature baseline ÷ event rate (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#where-the-energy-goes">memory anatomy</a>, <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment">the Horace experiment</a>; <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual">the energy manual</a> does it for every instruction and byte)','works_now','works now'],
 ['Static against dynamic power','per rail','frequency sweep at fixed voltage: DM_CMD_SET_FREQUENCY with power management off. Changes the card for everyone; not run here','works_now','works now, with care'],
 ['Instantaneous rail power','3 rails · 1 mW · per pass','the SP already reads it each pass and discards it; a few assignments in thermal_pwr_mgmt.c','needs_fw_change','firmware'],
 ['Faster sampling','tens to hundreds of Hz','the 133 ms pass is ~96 I2C transactions each followed by a hard-coded 1 ms wait; skip the 84-read snapshot and fix the wait','needs_fw_change','firmware'],
 ['Per-shire temperature; process detectors','34 shires · 0.06 °C in hardware; ring-oscillator counts in µs windows','sampled continuously by the PVT controllers, never exported','needs_fw_change','firmware'],
 ['DDR, PCIe, Maxion, IO rails','—','regulators with set-points but no current sense: only "board minus three rails"','impossible_on_silicon','no sensor'],
 ['Board power at kHz','whole card · ~1 ms','scope on the hot-swap controller\'s current-monitor pin, or a PCIe riser with a shunt','needs_tooling','hardware'],
];
document.getElementById('methods').innerHTML='<thead><tr><th>What</th><th>Granularity</th><th>How</th><th>Status</th></tr></thead><tbody>'+M.map(r=>`<tr><td class="lvl" style="white-space:normal">${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${chip(r[3],r[4])}</td></tr>`).join('')+'</tbody>';
const U=[
 ['Per-shire voltage map under load','Which shires sag under a full-chip load, and by how much (the low/high capture sees droops the polling misses).','Run the map during a load; the 4 KB log buffer wraps each pass, so poll it quickly.','Nothing: <code>tools/ettelem</code> does it.'],
 ['Temperature-controlled baselines','Energy per event to a few percent instead of 0.8 W of drift per °C.','Log temperature with every sample (ettelem does) and fit it, or interleave runs as the Horace experiment did.','Nothing.'],
 ['Static/dynamic split per rail','C·V²·f and leakage per rail; separates clock domains.','Sweep minion and mesh frequency at fixed voltage with power management off, restore after.','A quiet card and the lab\'s OK: it changes shared state.'],
 ['Chosen counter events','Event counts to regress rail power against: energy per L1 miss, per tensor op, per DRAM activate.','<a href="https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/patches/0003-pmc-configure-syscall-353f20e.patch">patches/0003</a> (verified in the simulator), or the debug interface\'s CSR write.','A signed firmware image, or an agreed debug-interface session.'],
 ['Instantaneous rails and a faster loop','Kernel boundaries visible in rail power; ~10× the sample rate.','A few lines in the service-processor firmware.','A signed image.'],
 ['Per-shire temperature map','Hot spots and thermal gradients across the mesh.','A new management command exporting what the PVT controllers already sample.','A signed image.'],
 ['kHz board power','Sub-launch power transients.','A scope on the 12 V current-monitor pin.','Physical access.'],
];
document.getElementById('unlock').innerHTML='<thead><tr><th>Step</th><th>What it gives</th><th>How</th><th>Needs</th></tr></thead><tbody>'+U.map((r,i)=>`<tr><td class="lvl" style="white-space:normal">${i+1}. ${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join('')+'</tbody>';

const S=D.thermal.series, PH=D.thermal.phases;
/* Leakage slope under load: least-squares line of power against die temperature over the matmul, from 5 s after
   launch (the rails have caught up) to the last whole second before it ends. */
(function(){const t0=PH.find(p=>p.phase==='matmul').t, t1=PH.find(p=>p.phase==='cool1').t;
 const P=S.filter(p=>p.t>=t0+5&&p.t+1<=t1);
 const slope=k=>{const n=P.length,mx=P.reduce((a,p)=>a+p.temp,0)/n,my=P.reduce((a,p)=>a+p[k],0)/n;
  return P.reduce((a,p)=>a+(p.temp-mx)*(p[k]-my),0)/P.reduce((a,p)=>a+(p.temp-mx)**2,0);};
 document.getElementById('slope-board').textContent=slope('board').toFixed(2);
 document.getElementById('slope-minion').textContent=slope('minion').toFixed(2);})();
function lines(id,keys,ymin,ymax,ticks,unit,H){const W=900,L=50,R=20,T=14,B=34;const {svg,tip,h}=host(id,W,H);
 const x=t=>L+t/176*(W-L-R),y=v=>H-B-(v-ymin)/(ymax-ymin)*(H-B-T);
 const names={matmul:'matmul',dram:'DRAM loads'};
 for(let i=0;i<PH.length-1;i++){if(names[PH[i].phase]){el('rect',{x:x(PH[i].t),y:T,width:x(PH[i+1].t)-x(PH[i].t),height:H-B-T,fill:'var(--grid)',opacity:0.45},svg);txt(svg,x(PH[i].t)+6,T+14,names[PH[i].phase],'lab');}}
 for(const t of ticks){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,t+unit,'tick','end');}
 for(let t=0;t<=170;t+=20)txt(svg,x(t),H-B+18,t+' s','tick','middle');
 for(const [k,cls] of keys){const d=S.map((p,i)=>`${i?'L':'M'}${x(p.t).toFixed(1)},${y(p[k]).toFixed(1)}`).join(' ');el('path',{d,class:'ln '+cls},svg);}
 const cross=el('line',{y1:T,y2:H-B,stroke:'var(--axis)','stroke-width':1,opacity:0},svg);const hit=el('rect',{x:L,y:T,width:W-L-R,height:H-B-T,fill:'transparent'},svg);
 hit.addEventListener('mousemove',ev=>{const r=svg.getBoundingClientRect();const vx=(ev.clientX-r.left)/r.width*W;const i=Math.max(0,Math.min(S.length-1,Math.round((vx-L)/(W-L-R)*176)));const p=S[i];cross.setAttribute('x1',x(p.t));cross.setAttribute('x2',x(p.t));cross.setAttribute('opacity',1);
  tip.innerHTML=`<b>${p.t} s</b> · ${p.temp.toFixed(0)} °C<br>board ${p.board.toFixed(1)} W<br>minion ${p.minion.toFixed(1)} · SRAM ${p.sram.toFixed(1)} · mesh ${p.noc.toFixed(1)}<br>rest ${(p.board-p.minion-p.sram-p.noc).toFixed(1)} W`;tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.min(ev.clientX-b.left+12,b.width-230)+'px';tip.style.top='10px';});
 hit.addEventListener('mouseleave',()=>{tip.style.display='none';cross.setAttribute('opacity',0);});}
document.getElementById('leg1').innerHTML=[['board','c1'],['minion cores','c2'],['SRAM','c3'],['mesh','c4']].map(([n,c])=>`<span><i style="background:var(--${c})"></i>${n}</span>`).join('');
lines('power',[['board','s1'],['minion','s2'],['sram','s3'],['noc','s4']],0,70,[0,10,20,30,40,50,60,70],'',300);
lines('temp',[['temp','s2']],70,90,[70,75,80,85,90],'',170);

/* The per-shire voltage map. The 32 compute shires sit where marty1885's logical layout puts them (the MARTY table in
   workloads/nocbench/analyze.py). The four dashed cells hold the master, spare, I/O and PCIe shires in an order not
   measured, so shires 32 (master) and 33 (spare) are drawn below the grid. Opacity encodes the minion-rail voltage. */
(function(){const MESH={0:[0,0],24:[1,0],9:[2,0],25:[3,0],2:[4,0],11:[5,0],8:[0,1],16:[1,1],1:[2,1],17:[3,1],10:[4,1],19:[5,1],3:[0,2],4:[1,2],13:[2,2],14:[3,2],18:[4,2],27:[5,2],12:[1,3],21:[2,3],22:[3,3],26:[4,3],20:[1,4],29:[2,4],30:[3,4],15:[4,4],23:[5,4],28:[1,5],5:[2,5],6:[3,5],7:[4,5],31:[5,5]};
 const EMPTY=[[0,3],[0,4],[0,5],[5,3]], OFF={32:[0,'master'],33:[1,'spare']};
 const W=520,cw=80,gy=500,H=gy+26+cw+4,{svg,tip,h}=host('vmap',W,H);
 for(const [cx,cy] of EMPTY)el('rect',{x:10+cx*cw+2,y:10+cy*cw+2,width:cw-4,height:cw-4,rx:8,fill:'none',stroke:'var(--axis)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 txt(svg,12,gy+16,'Not placed on the grid: the master shire (32) and the spare (33)','lab');
 function tile(s,X,Y,note){const v=D.shires[s];if(!v)return;const g=el('g',{},svg);const o=Math.max(0.15,Math.min(0.75,0.15+0.6*(v.mnn[0]-516)/5));
  el('rect',{x:X+2,y:Y+2,width:cw-4,height:cw-4,rx:8,fill:'var(--c1)',opacity:o.toFixed(2)},g);
  txt(g,X+cw/2,Y+30,'shire '+s,'lab','middle');txt(g,X+cw/2,Y+48,v.mnn[0]+' mV','lab-strong','middle');txt(g,X+cw/2,Y+64,'low '+v.mnn[1],'lab','middle');
  g.addEventListener('mousemove',ev=>{tip.innerHTML=`<b>Shire ${s}${note?' ('+note+')':''}</b><br>minion ${v.mnn[0]} mV [${v.mnn[1]}–${v.mnn[2]}]<br>SRAM ${v.sram[0]} [${v.sram[1]}–${v.sram[2]}]<br>mesh ${v.noc[0]} [${v.noc[1]}–${v.noc[2]}]`;tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.min(ev.clientX-b.left+12,b.width-200)+'px';tip.style.top=(ev.clientY-b.top+12)+'px';});g.addEventListener('mouseleave',()=>tip.style.display='none');}
 for(const [s,[cx,cy]] of Object.entries(MESH))tile(s,10+cx*cw,10+cy*cw);
 for(const [s,[i,note]] of Object.entries(OFF))tile(s,10+i*cw,gy+26,note);
})();
