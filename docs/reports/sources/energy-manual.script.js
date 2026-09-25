const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
function hover(g,tip,h,html){const s=ev=>{tip.innerHTML=html();tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=(h.scrollLeft+Math.max(0,Math.min(ev.clientX-b.left+12,b.width-290)))+'px';tip.style.top=(ev.clientY-b.top+12)+'px';};g.addEventListener('mousemove',s);g.addEventListener('mouseleave',()=>tip.style.display='none');}
function path(pts,x,y){return pts.map((p,i)=>`${i?'L':'M'}${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join(' ');}
function axes(svg,o){const {W,H,L,R,T,B,x,y}=o;
 for(const t of o.yt){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,o.yf?o.yf(t):t,'tick','end');}
 for(const t of o.xt){txt(svg,x(t),H-B+16,o.xf?o.xf(t):t,'tick','middle');}
 if(o.xl)txt(svg,(L+W-R)/2,H-4,o.xl,'lab','middle');if(o.yl)txt(svg,4,T-8,o.yl,'lab');}
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const f0=v=>v.toFixed(0),f3=v=>v.toFixed(3);
const fs=v=>Math.abs(v)>=10?v.toFixed(1):v.toFixed(2);   /* two decimals below 10, one above: no more digits than the bars carry */
const E=D.enercat.cards, A2=E.aifoundry2, A3=E.aifoundry3||[];
const key=r=>[r.pattern,r.operands,r.harts,r.scp].join('|');
const a2={},a3={}; A2.forEach(r=>a2[key(r)]=r); A3.forEach(r=>a3[key(r)]=r);
const g=(p,o,h,s)=>a2[[p,o,h,!!s].join('|')];
const R=D.rest, P80=R.P_fix_w+R.A_leak_80_w;
/* Confidence bars. CB[key] is the catalogue's pooled entry: mean over every pass on every card, lo-hi the range
   those passes spanned, per_card each card's mean and pass-to-pass standard error. cb() scales a per-instruction
   figure to per byte where needed; bt() renders "mean [lo-hi]"; pcs() the per-card column; ebar() draws a bar. */
const CB=(D.catalogue&&D.catalogue.combined)||{}, RR=D.reruns||{};
const cb=(k,sc)=>{const c=CB[k]; if(!c)return null; sc=sc||1; const pc={}; for(const h in c.per_card)pc[h]={mean:c.per_card[h].mean*sc,se:(c.per_card[h].se||0)*sc,n:c.per_card[h].n};
  return {mean:c.mean*sc,lo:c.lo*sc,hi:c.hi*sc,n:c.n,per_card:pc};};
const pick=(fn,v)=>fn===fs?(Math.abs(v)>=10?f1:f2):fn;   /* fs: one precision for a whole bar, set by its mean */
const bt=(c,fn)=>{if(!c)return '—'; const g=pick(fn,c.mean); return `<b>${g(c.mean)}</b> <span class="small">[${g(c.lo)}–${g(c.hi)}]</span>`;};
const more=(v,fn)=>{let s=fn(v); if(v>0&&+s===0){const d=(s.split('.')[1]||'').length; for(let k=d+1;k<=d+2&&+s===0;k++)s=v.toFixed(k);} return s;};
const pcs=(c,fn)=>c?Object.keys(c.per_card).sort().map(h=>{const g=pick(fn,c.per_card[h].mean); return `a${h.slice(-1)} ${g(c.per_card[h].mean)} ± ${more(c.per_card[h].se||0,g)}`;}).join('<br>'):'—';
const sup=n=>String(n).split('').map(ch=>'⁰¹²³⁴⁵⁶⁷⁸⁹'['0123456789'.indexOf(ch)]||ch).join('');
const sci=v=>{const e=Math.floor(Math.log10(v)); return (v/10**e).toFixed(2)+' × 10'+sup(e);};
const nf=v=>Math.round(v).toLocaleString('en-US');
const WORD=['no','one','two','three','four','five','six','seven','eight'];
/* least-squares line through points [[x,y],...]: {a (intercept), b (slope), r2} */
function lfit(pts){const n=pts.length,mx=pts.reduce((s,p)=>s+p[0],0)/n,my=pts.reduce((s,p)=>s+p[1],0)/n;
 let sxx=0,sxy=0,syy=0; pts.forEach(p=>{sxx+=(p[0]-mx)**2;sxy+=(p[0]-mx)*(p[1]-my);syy+=(p[1]-my)**2;});
 const b=sxy/sxx,a=my-b*mx; return {a,b,r2:sxy*sxy/(sxx*syy)};}
function ebar(svg,x,y1,y2,col){const g2=el('g',{},svg); el('line',{x1:x,x2:x,y1,y2,stroke:col||'var(--ink)','stroke-width':1.5},g2);
  el('line',{x1:x-3,x2:x+3,y1,y2:y1,stroke:col||'var(--ink)','stroke-width':1.5},g2); el('line',{x1:x-3,x2:x+3,y1:y2,y2,stroke:col||'var(--ink)','stroke-width':1.5},g2); return g2;}

/* ---------- KPIs ---------- */
(function(){
 document.getElementById('k1').textContent=f1(P80)+' W, '+Math.round(100*R.A_leak_80_w/P80)+'% leakage';
 const fm=cb('fmadd.ps/random/h2'); document.getElementById('k2').textContent=fm?`${f0(fm.mean)} pJ [${f0(fm.lo)}–${f0(fm.hi)}]`:f0(g('fmadd_ps','random',2).pj_per_op)+' pJ';
 const dl=cb('tload/dram/random'),sl=cb('tload/scp/random'); document.getElementById('k3').textContent=dl&&sl?`${f0(dl.mean/sl.mean)}× [${f0(dl.lo/sl.hi)}–${f0(dl.hi/sl.lo)}]`:f0(g('tload','random',1,false).pj_per_byte/g('tload','random',1,true).pj_per_byte)+'×';
 const cc=D.catalogue&&D.catalogue.cross_card; if(cc){document.getElementById('k4').textContent=f3(cc.median); document.getElementById('k4sub').textContent=`median ratio aifoundry3 / aifoundry2 (10–90%: ${f3(cc.p10)}–${f3(cc.p90)})`;}
 else{const rat=[]; for(const k in a2){ if(!a3[k])continue; const r2=a2[k],r3=a3[k]; const v2=r2.bytes?r2.pj_per_byte:r2.pj_per_op, v3=r2.bytes?r3.pj_per_byte:r3.pj_per_op; if(v2)rat.push(v3/v2);}
 rat.sort((a,b)=>a-b); document.getElementById('k4').textContent=f3(rat[rat.length>>1]);}
 /* the correction each burst of the three-pass catalogue received, per card (build_energy_manual.py) */
 const LC=D.catalogue&&D.catalogue.leak_correction;
 if(LC&&LC.aifoundry2){const a=LC.aifoundry2,b=LC.aifoundry3;
  document.getElementById('corr').textContent=`${f2(a.median_w)} W in the median and ${f2(a.max_w)} W at most over aifoundry2's ${nf(a.bursts)} bursts`+(b?` (${f2(b.median_w)} and ${f2(b.max_w)} W over aifoundry3's ${nf(b.bursts)})`:'');}
 else{const corr=A2.map(r=>Math.abs(r.leak_correction_w)).sort((a,b)=>a-b);
  document.getElementById('corr').textContent=f2(corr[corr.length>>1])+' W in the median, '+f2(corr[corr.length-1])+' W at most';}
})();

/* ---------- 1. idle law ---------- */
(function(){
 const W=700,H=320,L=58,R2=16,T=26,B=52,{svg,tip,h}=host('idle',W,H);
 const x=v=>L+(W-L-R2)*(v-40)/55, y=v=>H-B-(H-B-T)*(v-10)/40;
 axes(svg,{W,H,L,R:R2,T,B,x,y,yt:[10,20,30,40,50],xt:[40,50,60,70,80,90],xl:'die temperature, °C',yl:'idle board power, W'});
 const law=[]; for(let t=40;t<=95;t+=1) law.push([t,R.P_fix_w+R.A_leak_80_w*Math.exp((t-80)/R.T_L_c)]);
 el('path',{d:path(law,x,y),class:'ln s1'},svg);
 el('line',{x1:L,x2:W-R2,y1:y(R.P_fix_w),y2:y(R.P_fix_w),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 txt(svg,W-R2-4,y(R.P_fix_w)-6,'fixed '+f1(R.P_fix_w)+' W','lab','end');
 R.measured_idle.forEach(p=>{const gg=el('g',{},svg);el('circle',{cx:x(p.T),cy:y(p.P),r:3.5,fill:'var(--c2)'},gg);
   hover(gg,tip,h,()=>`${p.T} °C: ${f2(p.P)} W measured (${p.n} samples)<br>law: ${f2(R.P_fix_w+R.A_leak_80_w*Math.exp((p.T-80)/R.T_L_c))} W`);});
 const lawAt=T=>R.P_fix_w+R.A_leak_80_w*Math.exp((T-80)/R.T_L_c);
 /* the other card: its idle bins from the 22 September card transfer (cards-report.json), against the aifoundry2 law */
 const LK=D.cards&&D.cards.leakage, ic3=(LK&&LK.idle_curve)||[];
 ic3.forEach(p=>{const gg=el('g',{},svg); el('circle',{cx:x(p.T),cy:y(p.W),r:4.5,fill:'none',stroke:'var(--c3)','stroke-width':2},gg);
   hover(gg,tip,h,()=>`aifoundry3 idle: ${f2(p.W)} W at ${p.T} °C (${nf(p.n)} samples)<br>the aifoundry2 law says ${f2(lawAt(p.T))} W`);});
 if(ic3.length){const p0=ic3.reduce((a,b)=>a.T<b.T?a:b); txt(svg,x(p0.T)-9,y(p0.W)+4,'aifoundry3','lab','end');}
 const tmin=Math.min(...R.measured_idle.map(p=>p.T)), tmax=Math.max(...R.measured_idle.map(p=>p.T));
 const r3=ic3.length?` Rings: the other card's idle at ${Math.min(...ic3.map(p=>p.T))}–${Math.max(...ic3.map(p=>p.T))} °C (22 September), ${tmin-Math.max(...ic3.map(p=>p.T))}–${tmin-Math.min(...ic3.map(p=>p.T))} °C below the coolest fitted bin and ${LK.mean_offset_W>=0?'+':''}${f1(LK.mean_offset_W)} W from the law on average.`:'';
 document.getElementById('idlecap').textContent=`Line: the law fitted on 21 September, P = ${f1(R.P_fix_w)} W + ${f1(R.A_leak_80_w)} W·e^((T−80)/${f0(R.T_L_c)}), whose slope at 80 °C is ${f2(R.lambda_80_w_per_c)} W per °C. Dots: every whole-degree idle bin of that session on aifoundry2, ${tmin}–${tmax} °C.${r3} Leakage share: ${Math.round(100*R.curve.find(c=>c.T===60).leak_frac)}% at 60 °C, ${Math.round(100*R.curve.find(c=>c.T===80).leak_frac)}% at 80 °C, ${Math.round(100*R.curve.find(c=>c.T===90).leak_frac)}% at 90 °C.`;
 const rl=R.rails_73c;
 document.getElementById('rails').innerHTML='<thead><tr><th>Idle at 73 °C, by rail</th><th class="num">W</th><th class="num">Share</th></tr></thead><tbody>'+
  [['Minions',rl.minion],['SRAM: L2, L3, scratchpad',rl.sram],['Mesh',rl.noc],['No rail sensor: PCIe, DDR PHY, IO shire, regulators',rl.unsensed]].map(r=>`<tr><td>${r[0]}</td><td class="num">${f2(r[1])}</td><td class="num">${Math.round(100*r[1]/rl.board)}%</td></tr>`).join('')+
  `<tr><td><b>Board</b> <span class="small">(aifoundry2 on 22 September at ${f0(rl.die_c)} °C, ${rl.hours_idle!=null?f1(rl.hours_idle):'about 20'} hours after the last workload, apart from a 4.9 s single-hart probe a few minutes before: ${rl.samples||300} samples over a minute, sd ${f2(rl.board_sd!=null?rl.board_sd:0.04)} W; the rails' sd 0.01 W or less)</span></td><td class="num"><b>${f2(rl.board)}</b></td><td></td></tr></tbody>`;
})();

/* ---------- 2. awake ---------- */
(function(){
 const s1=g('spin','zeros',1),s2=g('spin','zeros',2), c1=cb('spin/zeros/h1'), c2=cb('spin/zeros/h2');
 const S2=(D.catalogue&&D.catalogue.cards.aifoundry2&&D.catalogue.cards.aifoundry2.summary)||{};
 const w1=S2['spin/zeros/h1']?S2['spin/zeros/h1'].over_idle_w.mean:s1.over_idle_w, w2=S2['spin/zeros/h2']?S2['spin/zeros/h2'].over_idle_w.mean:s2.over_idle_w;
 const hot=RR.hotline_over_idle_w&&RR.hotline_over_idle_w.contended;
 const at={}; D.sync.atomics.runs.forEach(r=>at[r.label]=r); const hw=at.contended.over_idle_w;
 const ab=D.awake.spin_hart0_1024, t=D.tensor.rows.find(r=>r.config==='fp32_randn'), AT=D.tensor.activity_term_mw_per_minion||{};
 document.getElementById('awake').innerHTML='<thead><tr><th>Minions awake, doing the least they can</th><th class="num">pJ per instruction</th><th class="num">per card</th><th class="num">W over idle, 1,024 minions (a2)</th><th class="num">per minion (a2)</th></tr></thead><tbody>'+
  `<tr><td>One hart per minion, an addi loop</td><td class="num">${c1?bt(c1,f1):f1(s1.pj_per_op)}</td><td class="num small">${pcs(c1,f1)}</td><td class="num">${f2(w1)}</td><td class="num">${f2(w1/1024*1e3)} mW</td></tr>`+
  `<tr><td>Both harts</td><td class="num">${c2?bt(c2,f1):f1(s2.pj_per_op)}</td><td class="num small">${pcs(c2,f1)}</td><td class="num">${f2(w2)}</td><td class="num">${f2(w2/1024*1e3)} mW</td></tr>`+
  `<tr><td>The 21 September ablation's integer loop (four adds and a branch), hart 0, 80 °C</td><td class="num">${f1(ab.pj_marginal)}</td><td class="num small">a2 only</td><td class="num">${f2(ab.over_idle_w)}</td><td class="num">${f2(ab.over_idle_w/1024*1e3)} mW</td></tr>`+
  `<tr><td>1,024 minions stalled on one contended atomic (the hot line: each waits about ${nf(Math.round(1024*at.contended.cycles_per_op/1000)*1000)} cycles for its turn)</td><td class="num">—</td><td class="num small">${hot?pcs(hot,f2):'a2 only, 22 September'}</td><td class="num">${hot?bt(hot,f2):f2(hw)}</td><td class="num">${f1((hot?hot.mean:hw)/1024*1e3)} mW</td></tr>`+
  `<tr><td>For scale: every minion running a random-data fp32 matmul (the activity term, section 3.2${AT.fp32_randn_8?`; ${f1(AT.fp32_randn_8)} mW per minion with 256 or 512 active, ${f1(AT.fp32_randn_24)} with 768`:''})</td><td class="num">—</td><td class="num small">a2 only</td><td class="num">${f1(t.over_idle_w)}</td><td class="num">${f1(AT.fp32_randn||t.over_idle_w/1024*1e3)} mW</td></tr></tbody>`;
 const nop=cb('nop/zeros/h2'), fen=cb('fence/zeros/h2');
 if(nop&&fen) document.getElementById('awaketext').innerHTML=
  `The addi loop is not the floor: it increments seven registers, so its operands change on every instruction. With both harts a <code>nop</code> costs ${f1(nop.mean)} pJ [${f1(nop.lo)}–${f1(nop.hi)}] and a <code>fence</code> ${f1(fen.mean)} [${f1(fen.lo)}–${f1(fen.hi)}] per instruction (section 3.1), so the awake core is about ${f1(fen.mean)}–${f1(nop.mean)} pJ per issue slot. `+
  `The ablation in <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power">Why is the ET-SoC-1 low power?</a>, whose loop issued at half the one-hart addi loop's rate on hart 0, measured ${f2(ab.over_idle_w)} W (${f1(ab.over_idle_w/1024*1e3)} mW per minion, ${f1(ab.pj_marginal)} pJ per instruction). `+
  `A minion stalled on a contended atomic draws less than one spinning: ${f1(hw/1024*1e3)} mW against ${f1(w1/1024*1e3)}.`;
})();

/* ---------- 3. instructions ---------- */
(function(){
 const list=[['add','add',1],['xor','xor',1],['mul','mul',1],['fadd.s','fadd.s',1],['fmul.s','fmul.s',1],['fmadd.s','fmadd.s',1],
   ['fadd.ps','fadd.ps ×8',8],['fmul.ps','fmul.ps ×8',8],['fmadd.ps','fmadd.ps ×8',8],['fadd.pi','fadd.pi ×8',8],['fmul.pi','fmul.pi ×8',8],
   ['fexp.ps','fexp.ps ×8',8],['frcp.ps','frcp.ps ×8',8]];
 const S2=(D.catalogue&&D.catalogue.cards.aifoundry2&&D.catalogue.cards.aifoundry2.summary)||{};
 const q=(n,o)=>cb(`${n}/${o}/h2`), rate=n=>S2[`${n}/random/h2`]?S2[`${n}/random/h2`].ops_per_cycle_per_hart.mean:null;
 if(!q('add','random')){return;}
 const W=700,H=360,L=58,R2=150,T=26,B=70,{svg,tip,h}=host('instr',W,H);
 const mx=Math.max(...list.map(l=>q(l[0],'random').hi))*1.12;
 const bw=(W-L-R2)/list.length, x=i=>L+bw*i, y=v=>H-B-(H-B-T)*v/mx;
 axes(svg,{W,H,L,R:R2,T,B,x:i=>x(i),y,yt:[0,40,80,120,160],xt:[],yl:'pJ per instruction, above idle'});
 const cols={zeros:'var(--c3)',const:'var(--c4)',random:'var(--c2)'};
 list.forEach((l,i)=>{['zeros','const','random'].forEach((o,j)=>{const c=q(l[0],o); if(!c)return; const gg=el('g',{},svg); const xx=x(i)+bw*(0.08+0.28*j);
   el('rect',{x:xx,y:y(c.mean),width:bw*0.26,height:H-B-y(c.mean),fill:cols[o]},gg); ebar(gg,xx+bw*0.13,y(c.hi),y(c.lo));
   hover(gg,tip,h,()=>`<b>${l[1]}</b>, ${o}<br>${f1(c.mean)} pJ per instruction [${f1(c.lo)}–${f1(c.hi)}], n = ${c.n}${l[2]>1?' ('+f1(c.mean/l[2])+' per lane)':''}<br>${pcs(c,f1).replace('<br>',' · ')}`);});
   const t=txt(svg,x(i)+bw*0.5,H-B+14,l[1],'tick','end'); t.setAttribute('transform',`rotate(-40 ${x(i)+bw*0.5} ${H-B+14})`);});
 [['zeros','var(--c3)'],['one constant','var(--c4)'],['random data','var(--c2)']].forEach((s2,i)=>{el('rect',{x:W-R2+8,y:T+6+i*20,width:11,height:11,fill:s2[1]},svg);txt(svg,W-R2+25,T+16+i*20,s2[0],'lab');});
 txt(svg,W-R2+8,T+76,'bar: range over 3 passes','lab'); txt(svg,W-R2+8,T+92,'on each of 2 cards','lab');
 document.getElementById('instrcap').innerHTML='Both harts of every minion issuing the instruction back to back; the multiply and the transcendentals are multi-cycle and issue at 0.4× (<code>frcp.ps</code>) down to an eighth (<code>mul</code>) of the one-cycle rate. Each bar is the mean over three shuffled passes on each of two cards; the whisker is the range those six passes spanned.';
 document.getElementById('instrtab').innerHTML='<thead><tr><th>Instruction</th><th class="num">zeros</th><th class="num">constant</th><th class="num">random</th><th class="num">random / zeros</th><th class="num">per lane, random</th><th class="num">issue per hart per cycle</th><th class="num">per card, random</th></tr></thead><tbody>'+
  list.map(l=>{const z=q(l[0],'zeros'),c=q(l[0],'const'),r=q(l[0],'random'); if(!(z&&r))return '';
   return `<tr><td><code>${l[1]}</code></td><td class="num">${bt(z,f1)}</td><td class="num">${bt(c,f1)}</td><td class="num">${bt(r,f1)}</td><td class="num">${f2(r.mean/z.mean)}×</td><td class="num">${l[2]>1?f1(r.mean/l[2]):'—'}</td><td class="num">${rate(l[0])!=null?f2(rate(l[0])):'—'}</td><td class="num small">${pcs(r,f1)}</td></tr>`;}).join('')+'</tbody>';
 const ia=q('add','zeros'),fa=q('fadd.s','zeros'),vz=q('fadd.ps','zeros'),vr=q('fadd.ps','random'),fm=q('fmadd.ps','random'),ex=q('fexp.ps','random'),lg=q('flog.ps','random');
 const nop=cb('nop/zeros/h2'),fen=cb('fence/zeros/h2');
 const byp=['flwl.ps','fswl.ps'].map(n=>q(n,'random')).filter(Boolean).map(c=>c.mean), amo=['amoaddl.w','amoswapl.w','amoorl.w','amomaxl.w','amoaddl.d','amoaddg.w','amoaddg.d'].map(n=>q(n,'random')).filter(Boolean).map(c=>c.mean);
 const tz=D.tensor.rows.find(r=>r.config==='fp32_randn'), tb=D.tensor.bars&&D.tensor.bars.fp32_randn;
 const lane=[(fm.mean-nop.mean)/8,(fm.mean-fen.mean)/8], tref=tb?tb.mean:tz.pj_marginal;
 document.getElementById('instrtext').innerHTML=
  `<b>An integer add costs ${f1(ia.mean)} pJ on zeros</b> [${f1(ia.lo)}–${f1(ia.hi)}], barely more than a <code>nop</code> (${f1(nop.mean)}) or a <code>fence</code> (${f1(fen.mean)}): on zeros it is almost all the awake core. `+
  `<b>A scalar float add costs ${f1(fa.mean/ia.mean)}× that</b> even on zeros; the FPU does not gate on zero. `+
  `<b>An eight-lane vector op on zeros costs the same as the scalar one</b> (${f1(vz.mean)} against ${f1(fa.mean)} pJ, bars overlapping): idle lanes are free, and on random data the lanes cost ${f1(vr.mean/vz.mean)}× — the data dependence of the tensor unit, in the vector unit. `+
  `<b>Per lane, a random-data <code>fmadd.ps</code> is ${f1(fm.mean/8)} pJ [${f1(fm.lo/8)}–${f1(fm.hi/8)}]; the tensor unit does the same multiply-add for ${tb?f1(tb.mean)+' ['+f1(tb.lo)+'–'+f1(tb.hi)+']':f2(tz.pj_marginal)}.</b> `+
  `Take out the vector instruction's issue — ${f1(fen.mean)}–${f1(nop.mean)} pJ, what a fence or a nop costs (section 2) — and the lane is ${f1(Math.min(...lane))}–${f1(Math.max(...lane))} pJ, about ${f0(100*(Math.min(...lane)+Math.max(...lane))/2/tref-100)}% above the tensor unit: the datapath energy is close, and what the tensor unit mostly saves is instruction issue. `+
  `<b>Transcendentals are the dearest arithmetic</b>: <code>fexp.ps</code> is ${f0(ex.mean)} pJ and <code>flog.ps</code> ${f0(lg.mean)} pJ for eight lanes, at a quarter of the rate; only loads and stores that bypass the L1 (${f0(Math.min(...byp))}–${f0(Math.max(...byp))} pJ) and atomics (${nf(Math.min(...amo))}–${nf(Math.max(...amo))} pJ) cost more.`;
 const TB=D.tensor.bars||{};
 document.getElementById('tensor').innerHTML='<thead><tr><th>Tensor unit, one instruction per tile (fp32 16×16×16 = 4,096 MACs; fp16 8,192; int8 16,384), all 1,024 minions, 80 °C</th><th class="num">pJ per MAC, marginal</th><th class="num">per card</th><th class="num">pJ per MAC, loaded (a2)</th><th class="num">W over idle (a2)</th><th class="num">MACs per second</th></tr></thead><tbody>'+
  D.tensor.rows.map(t=>{const b=TB[t.config]; return `<tr><td>${t.label}</td><td class="num">${b?bt(b,f3):'<b>'+f3(t.pj_marginal)+'</b>'}</td><td class="num small">${b?Object.keys(b.per_card).sort().map(h=>`a${h.slice(-1)} ${f3(b.per_card[h].mean)}`).join('<br>')+(b.cards>1?'':'<br>(a2 only)'):''}</td><td class="num">${f2(t.pj_loaded)}</td><td class="num">${f2(t.over_idle_w)}</td><td class="num">${sci(t.per_s)}</td></tr>`;}).join('')+
  '</tbody>';
 document.getElementById('tensornote').innerHTML='<b>Marginal</b>: board power above idle per MAC. <b>Loaded</b>: total board power, idle included, per MAC — what a MAC costs when it is the only thing running. Bars on the fp32 rows: the envelope of ±1 sd around the ablation’s two runs on aifoundry2 and the 22 September transfer’s runs on both cards; fp16 and int8 were run twice on aifoundry2, and their bar is ±1 sd of those two runs: '+
  (()=>{const hw=k=>TB[k]?100*(TB[k].hi-TB[k].lo)/2/TB[k].mean:null; const rn=['fp16_randn','int8_randn'].map(hw), z=hw('int8_zeros'), on=['fp16_ones','int8_ones'].map(hw);
     return `under ${f0(Math.ceil(Math.max(...rn)))}% on random data, ${f1(z)}% on int8 zeros, ${f0(Math.min(...on))}–${f0(Math.max(...on))}% on the ones patterns.`;})();
 const fl=D.tensor.flips;
 document.getElementById('flips').textContent=Object.keys(fl.e_fJ).map(c=>`${f3(fl.e_fJ[c])} fJ per ${fl.classes[c]}`).join(', ');
})();

/* ---------- 4. memory ---------- */
(function(){
 const paths=[['flw.ps/zeros/h2','flw.ps/random/h2',1/32,'L1 hit, flw.ps','read'],['fsw.ps/zeros/h2','fsw.ps/random/h2',1/32,'L1 hit, fsw.ps','write'],
   ['tload/scp/zeros','tload/scp/random',1,'own scratchpad, tensor load','read'],['tstore/scp/zeros','tstore/scp/random',1,'own scratchpad, tensor store','write'],
   ['tload/dram/zeros','tload/dram/random',1,'DRAM, tensor load','read'],['tstore/dram/zeros','tstore/dram/random',1,'DRAM, tensor store','write'],['st_stream/dram/zeros','st_stream/dram/random',1,'DRAM through the L1 write-back path','write']];
 const S2=(D.catalogue&&D.catalogue.cards.aifoundry2&&D.catalogue.cards.aifoundry2.summary)||{};
 if(!cb(paths[0][1])){return;}
 const W=700,H=390,L=58,R2=150,T=26,B=140,{svg,tip,h}=host('mem',W,H);
 const bw=(W-L-R2)/paths.length, x=i=>L+bw*i, y=v=>H-B-(H-B-T)*Math.log10(Math.max(v,0.1)/0.1)/Math.log10(1000/0.1);
 axes(svg,{W,H,L,R:R2,T,B,x:i=>x(i),y,yt:[0.1,1,10,100,1000],yf:v=>v+'',xt:[],yl:'pJ per byte, above idle (log)'});
 paths.forEach((p,i)=>{[['zeros',p[0]],['random',p[1]]].forEach((o,j)=>{const c=cb(o[1],p[2]); if(!c)return; const gg=el('g',{},svg); const xx=x(i)+bw*(0.12+0.4*j);
   el('rect',{x:xx,y:y(c.mean),width:bw*0.36,height:H-B-y(c.mean),fill:o[0]==='zeros'?'var(--c3)':'var(--c2)'},gg); ebar(gg,xx+bw*0.18,y(c.hi),y(c.lo));
   const bps=S2[o[1]]?S2[o[1]].bytes_per_s.mean:0;
   hover(gg,tip,h,()=>`<b>${p[3]}</b>, ${o[0]}<br>${f2(c.mean)} pJ/B [${f2(c.lo)}–${f2(c.hi)}], n = ${c.n}${bps?' at '+(bps/1e9).toFixed(0)+' GB/s':''}<br>${pcs(c,f2).replace('<br>',' · ')}`);});
   const t=txt(svg,x(i)+bw*0.5,H-B+14,p[3],'tick','end'); t.setAttribute('transform',`rotate(-32 ${x(i)+bw*0.5} ${H-B+14})`);});
 [['zeros','var(--c3)'],['random data','var(--c2)']].forEach((s2,i)=>{el('rect',{x:W-R2+8,y:T+6+i*20,width:11,height:11,fill:s2[1]},svg);txt(svg,W-R2+25,T+16+i*20,s2[0],'lab');});
 txt(svg,W-R2+8,T+56,'whisker: range over','lab'); txt(svg,W-R2+8,T+72,'3 passes × 2 cards','lab');
 document.getElementById('memcap').textContent='Log scale. Tensor loads skip the L1 (the L2 and L3 cache them when the working set fits); tensor stores skip the L1 and the L2; the L1 rows are hits in a 256 B buffer; the last bar is a plain vector store streaming to DRAM through the L1. Whiskers: the range over three shuffled passes on each of two cards.';
 document.getElementById('memtab').innerHTML='<thead><tr><th>Path</th><th class="num">zeros pJ/B</th><th class="num">random pJ/B</th><th class="num">random / zeros</th><th class="num">GB/s</th><th class="num">per card, random</th></tr></thead><tbody>'+
  paths.map(p=>{const z=cb(p[0],p[2]),r=cb(p[1],p[2]); if(!(z&&r))return ''; const bps=S2[p[1]]?S2[p[1]].bytes_per_s.mean:0;
   return `<tr><td>${p[3]} <span class="small">(${p[4]})</span></td><td class="num">${bt(z,fs)}</td><td class="num">${bt(r,fs)}</td><td class="num">${f2(r.mean/z.mean)}×</td><td class="num">${bps?nf(bps/1e9):'—'}</td><td class="num small">${pcs(r,fs)}</td></tr>`;}).join('')+'</tbody>';
 const dl=cb('tload/dram/random'),sl=cb('tload/scp/random'),ds=cb('tstore/dram/random'),ss=cb('st_stream/dram/random'),dz=cb('tload/dram/zeros');
 document.getElementById('memtext').innerHTML=
  `<b>DRAM is ${f0(dl.mean/sl.mean)}× the shire's own scratchpad per byte read.</b> A DRAM write by tensor store costs about what a read costs (${f0(ds.mean)} against ${f0(dl.mean)} pJ/B); `+
  `<b>the same bytes written through the L1 cost ${f1(ss.mean/ds.mean)}× more</b> and arrive at a third of the bandwidth, because every store allocates a line and the line goes down through L2 and L3. `+
  `<b>Even DRAM is data-dependent</b>: zeros ${f0(dz.mean)} [${f0(dz.lo)}–${f0(dz.hi)}], random ${f0(dl.mean)} [${f0(dl.lo)}–${f0(dl.hi)}] pJ/B; the scratchpad doubles. A scratchpad write is twice a scratchpad read.`;
 const lv=RR.levels_pj_per_byte;
 if(lv&&lv.dram){
  const LV=[['l1','L1 hits','256 B per hart, 2,048 harts'],['l2','L2','256 KB per shire (L2 is 512 KB)'],['l3','L3','768 KB per shire, 24 MB in all (L3 is 32 MB)'],['dram','DRAM','256 MB in all'],['scp-local','own scratchpad','2 MB of the shire’s own L2 scratchpad'],['scp-remote','remote scratchpad',`2 MB of the scratchpad 16 shire IDs away (${D.comm.mesh_hops?f1(D.comm.mesh_hops.xshire16.mean):'about 2'} mesh hops on average)`]];
  const l1c=cb('flw.ps/random/h2',1/32), gh=D.memory_reads.rows.map(r=>r.implied_ghz).filter(v=>v!=null);
  document.getElementById('memold').innerHTML='<thead><tr><th>Level</th><th>Working set</th><th class="num">pJ/B</th><th class="num">per card</th></tr></thead><tbody>'+
   LV.map(r=>lv[r[0]]?`<tr><td>${r[1]}</td><td class="small">${r[2]}</td><td class="num">${bt(lv[r[0]],fs)}</td><td class="num small">${pcs(lv[r[0]],fs)}</td></tr>`:'').join('')+
   '</tbody>';
  document.getElementById('memoldnote').innerHTML=`L1: both harts of every minion re-reading a private 256 B buffer with 32 B vector loads, in the memory-hierarchy probe's own loop over a buffer whose contents it does not set; it reads ${l1c&&lv.l1?f0(100*(lv.l1.mean/l1c.mean-1))+'%':'well'} above the catalogue's L1 row in section 4.1 (${l1c?f2(l1c.mean):'—'} pJ/B on random data), which is the figure to use. `+
   `L2, L3, DRAM and the scratchpads: hart 0 of every minion streaming 1 KB tensor loads — which skip the L1 but are cached in the L2 and L3 — over a working set sized to each level. The probe does not set the memory's contents, so these rows sit between the zeros and random columns of section 4.1 and are not directly comparable to them. `+
   `${(w=>w[0].toUpperCase()+w.slice(1))(String(WORD[RR.passes.levels/2]||RR.passes.levels/2))} passes on each card at a pinned 600 MHz (n = ${RR.passes.levels}). The 18 September run of the same experiment, in <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy">Memory hierarchy</a>, had the governor free and its clock averaged ${gh.length?f2(Math.min(...gh))+'–'+f2(Math.max(...gh)):'0.6–0.7'} GHz across the levels; it is superseded.`;
 } else {
  document.getElementById('memold').innerHTML='<thead><tr><th>Level</th><th>Working set</th><th class="num">pJ/B</th><th class="num">GB/s</th><th class="num">implied GHz</th></tr></thead><tbody>'+
   D.memory_reads.rows.map(r=>`<tr><td>${r.level}</td><td class="small">${r.what}</td><td class="num">${f2(r.pj_per_byte)}</td><td class="num">${r.gb_s.toFixed(0)}</td><td class="num">${r.implied_ghz?f2(r.implied_ghz):'—'}</td></tr>`).join('')+'</tbody>';
 }
})();

/* ---------- 5. comm ---------- */
(function(){
 const rp={}; D.relay.power.media.forEach(m=>rp[m.medium]=m);
 const rg=RR.rings_pj_per_byte||{}, rr=RR.relay_pj_per_byte||{}, MH=D.comm.mesh_hops||{};
 const val=(r)=>rg[r.ring]?bt(rg[r.ring],f2):`<b>${f2(r.pj_per_byte)}</b> ± ${f2(r.pj_spread)}`;
 const hopk=k=>{const m=MH[k]; return !m?'—':m.mean?`${f1(m.mean)} <span class="small">(${m.min}–${m.max})</span>`:'0';};
 const name=k=>{const x=k.match(/^xshire(\d+)(-c4)?$/); if(x)return `Shires ${x[1]} ID${x[1]==='1'?'':'s'} apart${x[2]?', 128 B':''}`;
   return {pair:'Pair',neigh:'Neighbourhood',shire:'Shire','shire-c4':'Shire, 128 B'}[k]||k;};
 /* in-shire rings first, then the 1 KB rings between shires by mean mesh distance, then the 128 B rows */
 const small=k=>k.endsWith('c4'), dist=k=>(MH[k]||{mean:0}).mean;
 const rows=[...D.comm.rows].sort((a,b)=>(small(a.ring)-small(b.ring))||(dist(a.ring)-dist(b.ring)));
 document.getElementById('comm').innerHTML='<thead><tr><th>Ring, 1 KB messages unless said</th><th>What moves</th><th class="num">Mesh hops, mean (range)</th><th class="num">pJ/B</th><th class="num">per card</th><th class="num">GB/s aggregate</th></tr></thead><tbody>'+
  rows.map(r=>`<tr><td>${name(r.ring)} <span class="small">(${r.ring})</span></td><td class="small">${r.what}</td><td class="num">${hopk(r.ring)}</td><td class="num">${val(r)}</td><td class="num small">${rg[r.ring]?pcs(rg[r.ring],f2):'a2, 2 runs'}</td><td class="num">${nf(r.gb_s)}</td></tr>`).join('')+
  '<tr><td colspan="6"><b>Handing a slab to the next shire</b> <span class="small">(the relay: a stage reads a slab, adds 1 and writes it where the next stage reads it)</span></td></tr>'+
  [['hop','in the next shire’s scratchpad','write where the next shire reads, read there; the next shire by ID',MH.xshire1?hopk('xshire1'):'—'],['dram','through DRAM','write to DRAM, read back','—'],['scp','kept in this shire’s scratchpad','write and read in place','0']].map(m=>
   `<tr><td>${m[1]}</td><td class="small">${m[2]}</td><td class="num">${m[3]}</td><td class="num">${rr[m[0]]?bt(rr[m[0]],f1):'<b>'+f1(rp[m[0]].pj_per_byte)+'</b>'}</td><td class="num small">${rr[m[0]]?pcs(rr[m[0]],f1):'a2 only'}</td><td class="num">${nf(rp[m[0]].bytes_per_s/1e9)}</td></tr>`).join('')+
  '</tbody>';
 document.getElementById('commnote').innerHTML=(rg.shire?(()=>{
    const d=D.comm.rows.filter(r=>rg[r.ring]&&r.pj_per_byte_local).map(r=>100*(r.pj_per_byte_local/rg[r.ring].mean-1)).sort((a,b)=>a-b);
    const dr=(RR.dropped||[]).map(x=>x.sampler_median_ms).filter(v=>v!=null);
    const pc=(rr.dram||{}).per_card||{}, n2=(pc.aifoundry2||{}).n, n3=(pc.aifoundry3||{}).n;
    return `<p class="small">Rings: re-measured on 23 September with the manual's own sampler, ${WORD[RR.passes.rings/2]||RR.passes.rings/2} passes on each card (n = ${rg.shire.n}). The 18 September pair of runs, sampled without the die temperature and so without a leakage correction, is not pooled; the values <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a> publishes from it read ${f0(d[0])}–${f0(d[d.length-1])}% higher in every configuration (median ${f0(d[d.length>>1])}%). `+
      `The s ↔ s+16 ring starves the service processor's own management path — the sampler's latency rises from 22 ms to ${dr.length?f0(Math.min(...dr))+'–'+f0(Math.max(...dr)):'about 150'} ms and the board reading is held for seconds — so its aifoundry2 passes were dropped and that row is aifoundry3 only. `+
      `Relay: 22 September (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay">Hand it to the next shire</a>) and ${WORD[n2-1]||n2-1} warm passes on aifoundry2, ${WORD[n3]||n3} passes on aifoundry3 (n = ${rr.dram?rr.dram.n:'—'}). `+
      `Mesh hops: the Manhattan distance between shire s and shire s + k (or s − 1 for the relay), averaged over all 32 compute shires.</p>`;})():'');
 const mesh=D.comm.rows.filter(r=>r.ring.startsWith('xshire')&&!r.ring.includes('c4'));
 const xs=mesh.map(r=>rg[r.ring]?rg[r.ring].mean:r.pj_per_byte);
 const fit=MH.xshire1?lfit(mesh.map(r=>[MH[r.ring].mean,rg[r.ring]?rg[r.ring].mean:r.pj_per_byte])):null, hx=mesh.map(r=>(MH[r.ring]||{}).mean||0);
 const nb=rg.neigh?rg.neigh.mean:D.comm.rows.find(r=>r.ring==='neigh').pj_per_byte, sh=rg.shire?rg.shire.mean:D.comm.rows.find(r=>r.ring==='shire').pj_per_byte;
 const pr=rg.pair?rg.pair.mean:D.comm.rows.find(r=>r.ring==='pair').pj_per_byte;
 const hop=rr.hop?rr.hop.mean:rp.hop.pj_per_byte, dram=rr.dram?rr.dram.mean:rp.dram.pj_per_byte;
 const hw=['dram','hop','scp'].filter(k=>rr[k]).map(k=>100*(rr[k].hi-rr[k].lo)/2/rr[k].mean), ow=['dram','hop','scp'].map(k=>rp[k].over_idle_w);
 document.getElementById('commtext').innerHTML=`Between the two minions of a pair a byte costs under a picojoule (${f2(pr)} pJ); around a neighbourhood or a shire about ${f1((nb+sh)/2)} pJ; across the mesh ${f0(Math.min(...xs))}–${f0(Math.max(...xs))} pJ`+
  (fit?`: about ${f0(fit.a)} pJ to leave the shire plus ${f1(fit.b)} pJ per mesh hop (a straight line through the six 1 KB rings between shires against their mean distances of ${f1(Math.min(...hx))}–${f1(Math.max(...hx))} hops, r² ${f2(fit.r2)}; <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm">Heat per millimetre</a> measures 1.5 pJ/B per hop on the mesh rail and 2.2 on board power directly). <b>Leaving the shire is the biggest single step, but the hops after it are not free.</b> `:'. ')+
  `Small messages cost more per byte (the 128 B rows): the per-message overhead is 40–224 cycles of the sending and receiving harts (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>). `+
  `Handing a slab to the next shire through its scratchpad is ${f0(dram/hop)}× cheaper than the DRAM round trip. The three relay bars are ±${f0(Math.min(...hw))}–${f0(Math.max(...hw))}% because each is a ${f0(Math.min(...ow))}–${f0(Math.max(...ow))} W signal over a board idle that drifts; the DRAM relay's power also rides on a path with no rail sensor.`;
})();

/* ---------- 6. sync ---------- */
(function(){
 const at={}; D.sync.atomics.runs.forEach(r=>at[r.label]=r);
 const hn=RR.hotline_nj_per_op||{};
 const bar=1024*1.4e-3*D.sync.barrier_cycles_chip/0.6e9*1e9;
 const conm=hn.contended?hn.contended.mean:at.contended.nj_per_op, sprm=hn.spread?hn.spread.mean:at.spread.nj_per_op;
 document.getElementById('sync').innerHTML='<thead><tr><th>Event</th><th class="num">Energy</th><th class="num">per card</th><th class="num">Time</th><th>Note</th></tr></thead><tbody>'+
  `<tr><td>Global atomic, one line, 1,024 requesters</td><td class="num">${hn.contended?bt(hn.contended,f1)+' nJ':'<b>'+f1(at.contended.nj_per_op)+' nJ</b>'}</td><td class="num small">${hn.contended?pcs(hn.contended,f1):'a2 only'}</td><td class="num">${f0(at.contended.cycles_per_op)} cycles each at the bank</td><td class="small">the bank serialises and every requester waits its turn; the host shire's own loads stop</td></tr>`+
  `<tr><td>Global atomic, 32 lines, one per shire</td><td class="num">${hn.spread?bt(hn.spread,f2)+' nJ':f1(at.spread.nj_per_op)+' nJ'}</td><td class="num small">${hn.spread?pcs(hn.spread,f2):'a2 only'}</td><td class="num">${f2(at.spread.cycles_per_op)} cycles each, aggregate</td><td class="small">the same instruction, ${f0(conm/sprm)}× cheaper</td></tr>`+
  `<tr><td>Uncontended remote atomic round trip</td><td class="num">—</td><td></td><td class="num">${f0(D.sync.remote_atomic_latency_cycles)} cycles</td><td class="small"></td></tr>`+
  `<tr><td>Chip-wide barrier, 1,024 minions</td><td class="num">≈ ${f0(bar/1000)} µJ of waiting</td><td></td><td class="num">${D.sync.barrier_cycles_chip.toLocaleString()} cycles</td><td class="small">derived: 1,024 minions stalled at 1.4 mW for its length</td></tr>`+
  `<tr><td>FLB (fast local barrier) + credit barrier, one shire</td><td class="num">—</td><td></td><td class="num">237 cycles</td><td class="small"><a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>, 18 September</td></tr>`+
  `<tr><td>TensorReduce (the hardware reduction tree) + broadcast, 32 minions</td><td class="num">—</td><td></td><td class="num">432 cycles</td><td class="small"><a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>, 18 September</td></tr>`+
  '</tbody>';
 document.getElementById('syncnote').innerHTML=(hn.contended?`Hot line: 22 September and ${WORD[(hn.contended.per_card.aifoundry2||{n:1}).n-1]} warm passes on aifoundry2, ${WORD[(hn.contended.per_card.aifoundry3||{n:0}).n]} passes on aifoundry3 (n = ${hn.contended.n}). The first session alone gave ${f1(at.contended.nj_per_op)} and ${f2(at.spread.nj_per_op)} nJ. The contended row’s bar is wide because the whole chip stalled draws only about ${f1(conm*at.contended.ops_per_s*1e-9)} W over idle (${f1(at.contended.over_idle_w)} W in the first session), and the per-operation figure divides that small number by a rate the bank fixes at one per 10 cycles.`:'');
})();

/* ---------- 7. composition ---------- */
(function(){
 const t=D.tensor.rows.find(r=>r.config==='fp32_randn'), tz=D.tensor.rows.find(r=>r.config==='fp32_zeros');
 const sm=D.tensor.flips.p_sm_full_chip_w;
 /* the multiply-adds as the flip model prices a random tile (section 3.2), not the measured over-idle power */
 const pat=(D.cards&&D.cards.patterns||[]).find(p=>p.values==='randn'), fm=pat?pat.model:t.over_idle_w;
 const parts=[['fixed',R.P_fix_w,'var(--ref)'],['leakage at 80 °C',R.A_leak_80_w,'var(--c4)'],['tensor state machines',sm,'var(--c3)'],['multiply-adds',fm-sm,'var(--c2)']];
 const W=700,H=150,L=16,R2=16,T=30,B=40,{svg,tip,h}=host('comp',W,H);
 const tot=parts.reduce((s,p)=>s+p[1],0), x0=L, meas=t.idle_w+t.over_idle_w; let acc=0;
 parts.forEach(p=>{const gg=el('g',{},svg); const w=(W-L-R2)*p[1]/tot;
   el('rect',{x:x0+(W-L-R2)*acc/tot,y:T,width:w,height:44,fill:p[2]},gg);
   txt(svg,x0+(W-L-R2)*(acc+p[1]/2)/tot,T+58+(w<90?14:0),`${p[0]} ${f1(p[1])} W`,'lab','middle');
   hover(gg,tip,h,()=>`${p[0]}: ${f1(p[1])} W, ${Math.round(100*p[1]/tot)}%`); acc+=p[1];});
 txt(svg,L,T-10,`predicted ${f1(tot)} W (fixed + leakage + the flip model's ${f1(fm)} W); measured ${f1(meas)} W`,'lab-strong');
 const tb=D.tensor.bars&&D.tensor.bars.fp32_randn;
 document.getElementById('compcap').textContent=`Random data, all 1,024 minions, launched at 80 °C. The bar is built from the tables: the idle law of section 1 and the flip model of section 3.2; the measurement is the 21 September ablation on aifoundry2. Per flop that is ${f1(1e12*meas/(2*t.per_s))} pJ loaded and ${f2((tb?tb.mean:t.pj_marginal)/2)} pJ marginal${tb?' ['+f2(tb.lo/2)+'–'+f2(tb.hi/2)+' over runs and cards]':''}; ${Math.round(100*P80/tot)}% of the energy of the most arithmetic-dense thing this chip does is static. The static part carries the idle law’s bar: ±0.2 W on this card, +0.7 W on the other.`;
 document.getElementById('comptext').innerHTML=`The same matmul on zeros draws ${f1(tz.over_idle_w)} W over idle instead of ${f1(t.over_idle_w)}, and the loaded cost per flop becomes ${f1(1e12*(P80+tz.over_idle_w)/(2*tz.per_s))} pJ, almost all of it static. <b>On this card the data decides the dynamic energy and the temperature decides the rest.</b>`;
 /* The relay as a consistency check. It reads with 32 B vector loads through the L1 and writes with tensor stores;
    its "next shire" is shire s - 1 by ID, 3.5 mesh hops away on average. Each byte is read once and written once,
    so each bracket is the mean of a read row and a write row, zeros ... random (its data is one constant per slab). */
 const rp={}; D.relay.power.media.forEach(m=>rp[m.medium]=m);
 const rr2=RR.relay_pj_per_byte||{}, MH=D.comm.mesh_hops||{}, hh=MH.xshire1?MH.xshire1.mean:3.5;
 const zr=k=>{const z=cb(k+'/zeros'),r=cb(k+'/random'); return z&&r?[z.mean,r.mean]:null;};
 const mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2];
 const lo=Math.floor(hh), hi=Math.ceil(hh), wl=zr(`wire/hop${lo}`), wh=zr(`wire/hop${hi}`);
 const wire=wl&&wh?[wl[0]+(wh[0]-wl[0])*(hh-lo)/Math.max(1,hi-lo),wl[1]+(wh[1]-wl[1])*(hh-lo)/Math.max(1,hi-lo)]:null;
 const ts=zr('tstore/scp'), pd=mid(zr('tload/dram'),zr('tstore/dram')), l1f=zr('l1fill/stride32'), ps=l1f&&ts?mid(l1f,ts):null, ph=wire&&ts?mid(wire,ts):null;
 const inb=(v,b)=>v<b[0]?'a little below':v>b[1]?'above':'inside';
 document.getElementById('relaycheck').innerHTML='<thead><tr><th>The relay, priced from section 4</th><th class="num">priced pJ/B, zeros … random</th><th class="num">measured</th></tr></thead><tbody>'+
  `<tr><td>intermediate in DRAM <span class="small">(tensor load and tensor store)</span></td><td class="num">${f0(pd[0])} … ${f0(pd[1])}</td><td class="num">${rr2.dram?bt(rr2.dram,f1):'<b>'+f1(rp.dram.pj_per_byte)+'</b>'} <span class="small">(${inb(rr2.dram?rr2.dram.mean:rp.dram.pj_per_byte,pd)})</span></td></tr>`+
  (ps?`<tr><td>in the shire's own scratchpad <span class="small">(32 B loads through the L1, tensor store)</span></td><td class="num">${f1(ps[0])} … ${f1(ps[1])}</td><td class="num">${rr2.scp?bt(rr2.scp,f2):'<b>'+f2(rp.scp.pj_per_byte)+'</b>'} <span class="small">(${inb(rr2.scp?rr2.scp.mean:rp.scp.pj_per_byte,ps)})</span></td></tr>`:'')+
  (ph?`<tr><td>in the next shire's scratchpad <span class="small">(the wire read at ${f1(hh)} hops, tensor store)</span></td><td class="num">${f1(ph[0])} … ${f1(ph[1])}</td><td class="num">${rr2.hop?bt(rr2.hop,f2):'<b>'+f2(rp.hop.pj_per_byte)+'</b>'} <span class="small">(${inb(rr2.hop?rr2.hop.mean:rp.hop.pj_per_byte,ph)})</span></td></tr>`:'')+'</tbody>';
 document.getElementById('relaytext').innerHTML=`No row of section 4 was derived from the relay, so this is an out-of-sample check. The relay reads with 32 B vector loads through the L1 and writes with tensor stores, and its “next shire” is on average ${f1(hh)} mesh hops away (shire s − 1 by ID). Each byte is read once and written once, so each bracket is the mean of the matching read and write rows, from zeros to random data, because the relay's data is one constant per slab. The own-scratchpad read uses the 32 B loads through the L1 of section 4.3, and the next-shire read the wire read of section 4.3 interpolated to ${f1(hh)} hops; the DRAM row uses the tensor-load read of section 4.1, the nearest row the catalogue has. It is a consistency check, not a prediction: `+
  [['DRAM',rr2.dram?rr2.dram.mean:rp.dram.pj_per_byte,pd],['the own scratchpad',rr2.scp?rr2.scp.mean:rp.scp.pj_per_byte,ps],['the next shire',rr2.hop?rr2.hop.mean:rp.hop.pj_per_byte,ph]].filter(x=>x[2]).map(x=>
   x[1]<x[2][0]?`${x[0]} measures ${f0(100*(1-x[1]/x[2][0]))}% below its bracket`:x[1]>x[2][1]?`${x[0]} ${f0(100*(x[1]/x[2][1]-1))}% above it`:`${x[0]} falls inside`).join(', ')+
  `; the adds and barriers the relay also runs are in no table.`;
})();

/* ---------- 8. cards ---------- */
(function(){
 const pts=[];
 if(D.catalogue&&D.catalogue.cards.aifoundry3){const S2=D.catalogue.cards.aifoundry2.summary,S3=D.catalogue.cards.aifoundry3.summary;
  for(const k in S2){const r2=S2[k],r3=S3[k]; if(!r3)continue; const f=r2.bytes_per_s.mean>0?'pj_per_byte':'pj_per_op'; if(r2[f].mean>0&&r3[f].mean>0)pts.push([r2[f].mean,r3[f].mean,k,r2[f].se,r3[f].se]);}}
 else{for(const k in a2){ if(!a3[k])continue; const r2=a2[k],r3=a3[k]; const v2=r2.bytes?r2.pj_per_byte:r2.pj_per_op, v3=r2.bytes?r3.pj_per_byte:r3.pj_per_op; if(v2&&v3)pts.push([v2,v3,k.replace(/\|/g,' '),0,0]);}}
 const W=700,H=340,L=58,R2=16,T=26,B=52,{svg,tip,h}=host('cards',W,H);
 const lo=0.2,hi=2000, x=v=>L+(W-L-R2)*Math.log10(v/lo)/Math.log10(hi/lo), y=v=>H-B-(H-B-T)*Math.log10(v/lo)/Math.log10(hi/lo);
 axes(svg,{W,H,L,R:R2,T,B,x,y,yt:[1,10,100,1000],xt:[1,10,100,1000],xl:'aifoundry2, pJ per instruction or per byte (mean of 3 passes)',yl:'aifoundry3'});
 el('line',{x1:x(lo),y1:y(lo),x2:x(hi),y2:y(hi),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 pts.forEach(p=>{const gg=el('g',{},svg); if(p[3]||p[4]){el('line',{x1:x(Math.max(lo,p[0]-p[3])),x2:x(p[0]+p[3]),y1:y(p[1]),y2:y(p[1]),stroke:'var(--c1)','stroke-opacity':0.5},gg);el('line',{x1:x(p[0]),x2:x(p[0]),y1:y(Math.max(lo,p[1]-p[4])),y2:y(p[1]+p[4]),stroke:'var(--c1)','stroke-opacity':0.5},gg);}
  el('circle',{cx:x(p[0]),cy:y(p[1]),r:3,fill:'var(--c1)','fill-opacity':0.75},gg);hover(gg,tip,h,()=>`${p[2]}<br>aifoundry2 ${f2(p[0])} ± ${f2(p[3])}, aifoundry3 ${f2(p[1])} ± ${f2(p[4])}<br>ratio ${f3(p[1]/p[0])}`);});
 const rat=pts.map(p=>p[1]/p[0]).sort((a,b)=>a-b);
 const rer=[]; ['relay_pj_per_byte','hotline_nj_per_op','rings_pj_per_byte','levels_pj_per_byte'].forEach(sec=>{const o=RR[sec]||{}; for(const k in o){const v=o[k]; if(v&&v.per_card.aifoundry2&&v.per_card.aifoundry3)rer.push(v.per_card.aifoundry3.mean/v.per_card.aifoundry2.mean);}}); rer.sort((a,b)=>a-b);
 document.getElementById('cardscap').textContent=`Log axes, dashed line is equality; the cross on each point is ± its pass-to-pass standard error on each card. ${pts.length} entries; ratio ${f3(rat[0])} to ${f3(rat[rat.length-1])}, 10th–90th percentile ${f3(rat[Math.floor(rat.length/10)])}–${f3(rat[Math.floor(rat.length*0.9)])}, median ${f3(rat[rat.length>>1])}.`+(rer.length?` The ${rer.length} rerun entries of sections 4.2, 5 and 6 give ${f3(rer[rer.length>>1])} in the median (${f2(rer[0])}–${f2(rer[rer.length-1])}).`:'')+` The tensor-unit transfer of 22 September found ${f3(D.cards&&D.cards.scale||0.924)} for the same pair of cards, with aifoundry3 running 5 mV higher — the scale is the card, not the operating point.`;
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
 const W=Math.max(700,all.length*11+80),H=380,L=58,R2=16,T=26,B=100,{svg,tip,h}=host('allinstr',W,H); svg.style.minWidth=W+'px';
 const mx=Math.max(...all.map(a=>{const c=CB[`${a.n}/random/h2`]; return c?c.hi:a.r.pj_per_op.mean;}))*1.3; const bw=(W-L-R2)/all.length;
 const y=v=>H-B-(H-B-T)*Math.log10(Math.max(v,1)/1)/Math.log10(mx/1);
 axes(svg,{W,H,L,R:R2,T,B,x:v=>v,y,yt:[1,10,100,1000].filter(v=>v<=mx),yf:v=>v+'',xt:[],yl:'pJ per instruction, random data (log)'});
 const COL=['var(--c1)','var(--c7)','var(--c2)','var(--c5)','var(--c3)','var(--c4)','var(--bad)','var(--muted)','var(--ok)','var(--warn)','var(--ink-2)','var(--ref)','var(--axis)','var(--ink)'];
 all.forEach((a,i)=>{const gg=el('g',{},svg); const x=L+bw*i; const c=CB[`${a.n}/random/h2`];
   el('rect',{x:x+1,y:y(a.r.pj_per_op.mean),width:Math.max(1,bw-2),height:H-B-y(a.r.pj_per_op.mean),fill:COL[a.ci%COL.length]},gg);
   if(c){const cx=x+bw/2; el('line',{x1:cx,x2:cx,y1:y(c.hi),y2:y(c.lo),stroke:'var(--ink)','stroke-width':1.2},gg);
     el('line',{x1:cx-2.5,x2:cx+2.5,y1:y(c.hi),y2:y(c.hi),stroke:'var(--ink)','stroke-width':1.2},gg); el('line',{x1:cx-2.5,x2:cx+2.5,y1:y(c.lo),y2:y(c.lo),stroke:'var(--ink)','stroke-width':1.2},gg);}
   el('line',{x1:x+1,x2:x+bw-1,y1:y(a.z.pj_per_op.mean),y2:y(a.z.pj_per_op.mean),stroke:'var(--ink)'},gg);
   {const t=txt(svg,x+bw/2+3,H-B+10,a.n,'tick','end'); t.setAttribute('font-size','9'); t.setAttribute('transform',`rotate(-65 ${x+bw/2+3} ${H-B+10})`);}
   hover(gg,tip,h,()=>`<b>${a.n}</b> — ${CLASSES[a.ci][0]}<br>random ${a.r.pj_per_op.mean.toFixed(1)} ± ${a.r.pj_per_op.se.toFixed(2)} pJ on ${cards[0]}${LANES.has(a.n)?' ('+(a.r.pj_per_op.mean/8).toFixed(1)+' per lane)':''}<br>${c?'both cards: '+c.mean.toFixed(1)+' ['+c.lo.toFixed(1)+'–'+c.hi.toFixed(1)+'], n = '+c.n+'<br>':''}zeros ${a.z.pj_per_op.mean.toFixed(1)} pJ<br>${a.r.ops_per_cycle_per_hart.mean.toFixed(3)} per hart per cycle<br>${a.r2?cards[1]+': '+a.r2.pj_per_op.mean.toFixed(1)+' ± '+a.r2.pj_per_op.se.toFixed(2)+' pJ, ratio '+(a.r2.pj_per_op.mean/a.r.pj_per_op.mean).toFixed(3):''}`);});
 const leg=document.createElement('div'); leg.className='legend'; leg.innerHTML=CLASSES.map((c,ci)=>`<span><i style="background:${COL[ci%COL.length]}"></i>${c[0]}</span>`).join(''); h.parentNode.insertBefore(leg,h);
 const rel=all.map(a=>a.r.pj_per_op.se/a.r.pj_per_op.mean).sort((a,b)=>a-b);
 const half=all.map(a=>CB[`${a.n}/random/h2`]).filter(Boolean).map(c=>(c.hi-c.lo)/2/c.mean).sort((a,b)=>a-b);
 document.getElementById('allcap').textContent=`${all.length} instructions. Bar: random data on ${cards[0]}; whisker: the range over three passes on each of two cards; tick: zeros. Pass-to-pass standard error on one card is ${(100*rel[rel.length>>1]).toFixed(1)}% in the median and ${(100*rel[Math.floor(rel.length*0.9)]).toFixed(1)}% at the 90th percentile; half the whisker is ±${(100*half[half.length>>1]).toFixed(1)}% in the median and ±${(100*half[Math.floor(half.length*0.9)]).toFixed(1)}% at the 90th, most of it the difference between the cards.`;
 document.getElementById('alltab').innerHTML='<thead><tr><th>Instruction</th><th class="num">zeros pJ, both cards</th><th class="num">random pJ, both cards</th><th class="num">per lane</th><th class="num">random / zeros</th><th class="num">issue per hart per cycle</th><th class="num">'+cards[0]+' ± se</th><th class="num">'+(cards[1]||'card 2')+' ± se</th><th class="num">ratio</th></tr></thead><tbody>'+
  CLASSES.map(c=>`<tr><td colspan="9"><b>${c[0]}</b></td></tr>`+c[1].map(n=>{const r=g(n,'random'),z=g(n,'zeros'),r2=g2(n,'random'),cr=cb(`${n}/random/h2`),cz=cb(`${n}/zeros/h2`); if(!(r&&z))return '';
   return `<tr><td><code>${n}</code></td><td class="num">${cz?bt(cz,f1):z.pj_per_op.mean.toFixed(1)}</td><td class="num">${cr?bt(cr,f1):'<b>'+r.pj_per_op.mean.toFixed(1)+'</b>'}</td><td class="num">${LANES.has(n)?((cr?cr.mean:r.pj_per_op.mean)/8).toFixed(1):'—'}</td><td class="num">${((cr?cr.mean:r.pj_per_op.mean)/(cz?cz.mean:z.pj_per_op.mean)).toFixed(2)}×</td><td class="num">${r.ops_per_cycle_per_hart.mean.toFixed(3)}</td><td class="num">${r.pj_per_op.mean.toFixed(1)} ± ${r.pj_per_op.se.toFixed(2)}</td><td class="num">${r2?r2.pj_per_op.mean.toFixed(1)+' ± '+r2.pj_per_op.se.toFixed(2):'—'}</td><td class="num">${r2?(r2.pj_per_op.mean/r.pj_per_op.mean).toFixed(3):'—'}</td></tr>`;}).join('')).join('')+'</tbody>';
 /* cheapest and dearest by the pooled mean over both cards, the page's convention */
 const pool=all.filter(a=>CB[`${a.n}/random/h2`]).map(a=>({n:a.n,ci:a.ci,m:CB[`${a.n}/random/h2`].mean,z:(CB[`${a.n}/zeros/h2`]||{}).mean})).sort((a,b)=>a.m-b.m);
 const cheapest=pool[0], dearest=pool[pool.length-1];
 const cc=C.cross_card;
 const span=(ns,o)=>{const v=ns.map(n=>CB[`${n}/${o}/h2`]).filter(Boolean).map(c=>c.mean); return [Math.min(...v),Math.max(...v),v.length];};
 const one=CLASSES[0][1], z1=span(one,'zeros'), r1=span(one,'random');
 const rat=(a,b)=>CB[`${a}/random/h2`]&&CB[`${b}/random/h2`]?CB[`${a}/random/h2`].mean/CB[`${b}/random/h2`].mean:null;
 const dv=rat('divu','mulw'), ag=['amoaddg.w','amoaddg.d'].flatMap(a=>['amoaddl.w','amoaddl.d'].map(l=>rat(a,l))).filter(v=>v);
 document.getElementById('alltext').innerHTML=`The cheapest instruction is <code>${cheapest.n}</code> at ${f1(cheapest.m)} pJ and the dearest <code>${dearest.n}</code> at ${nf(dearest.m)} pJ, a span of ${f0(dearest.m/cheapest.m)}× (pooled over both cards). `+
  (cc?`Across ${cc.n} configurations the second card is ${f3(cc.median)}× the first (10th to 90th percentile ${f3(cc.p10)} to ${f3(cc.p90)}). `:'')+
  `Instructions that share a unit and a latency cost about the same on zeros — the ${z1[2]} one-cycle integer ops span ${f1(z1[0])}–${f1(z1[1])} pJ — but data and latency spread every class: on random data the same ${r1[2]} span ${f1(r1[0])}–${f1(r1[1])} pJ, a 64-bit divide costs ${f0(dv)}× a <code>mulw</code>, and a global <code>amoaddg</code> ${f0(Math.min(...ag))}× a local <code>amoaddl</code>.`;

 /* ---- wires ---- */
 const Wf=C.cards[cards[0]].wire; if(Wf&&Wf.random&&Wf.zeros){
  const W2=700,H2=320,L2=58,R3=140,T2=26,B2=52,{svg:sv,tip:tp,h:hh}=host('wire',W2,H2);
  const mxh=Math.max(...Wf.random.points.map(p=>p.hops)), mxy=Math.max(...Wf.random.points.map(p=>p.pj_per_byte))*1.15;
  const x=v=>L2+(W2-L2-R3)*v/(mxh+0.5), yy=v=>H2-B2-(H2-B2-T2)*v/mxy;
  axes(sv,{W:W2,H:H2,L:L2,R:R3,T:T2,B:B2,x,y:yy,yt:[0,5,10,15,20,25,30].filter(v=>v<=mxy),xt:[0,1,2,3,4,5,6,7,8].filter(v=>v<=mxh),xl:'hops across the mesh to the scratchpad read',yl:'pJ per byte'});
  const Wf2=cards[1]&&C.cards[cards[1]].wire;
  [['zeros',Wf.zeros,'var(--c3)'],['random',Wf.random,'var(--c2)']].forEach((s2,i)=>{const wf=s2[1];
   el('path',{d:path([[0,wf.intercept_pj_per_byte],[mxh,wf.intercept_pj_per_byte+wf.slope_pj_per_byte_per_hop*mxh]],x,yy),class:'ln',stroke:s2[2],'stroke-dasharray':'5 4'},sv);
   wf.points.forEach(p=>{const c=CB[`wire/hop${p.hops}/${s2[0]}`]; const gg=el('g',{},sv); if(c){el('line',{x1:x(p.hops),x2:x(p.hops),y1:yy(c.hi),y2:yy(c.lo),stroke:s2[2],'stroke-width':1.5},gg);}
    el('circle',{cx:x(p.hops),cy:yy(p.pj_per_byte),r:4,fill:s2[2]},gg);hover(gg,tp,hh,()=>`${p.hops} hops, ${s2[0]}: ${p.pj_per_byte.toFixed(2)} ± ${p.se.toFixed(2)} pJ/B on ${cards[0]}${c?'<br>both cards: '+c.mean.toFixed(2)+' ['+c.lo.toFixed(2)+'–'+c.hi.toFixed(2)+'], n = '+c.n:''}<br>${p.shires} shires reading`);});
   if(Wf2&&Wf2[s2[0]]){Wf2[s2[0]].points.forEach(p=>{const gg=el('g',{},sv);el('circle',{cx:x(p.hops)+3,cy:yy(p.pj_per_byte),r:3.5,fill:'none',stroke:s2[2],'stroke-width':1.5},gg);hover(gg,tp,hh,()=>`${p.hops} hops, ${s2[0]}: ${p.pj_per_byte.toFixed(2)} ± ${p.se.toFixed(2)} pJ/B on ${cards[1]}`);});}
   if(wf.local_pj_per_byte!=null){const gg=el('g',{},sv);el('circle',{cx:x(0),cy:yy(wf.local_pj_per_byte),r:4,fill:'none',stroke:s2[2],'stroke-width':2},gg);hover(gg,tp,hh,()=>`own scratchpad, ${s2[0]}: ${wf.local_pj_per_byte.toFixed(2)} pJ/B`);}
   el('rect',{x:W2-R3+8,y:T2+6+i*20,width:11,height:11,fill:s2[2]},sv);txt(sv,W2-R3+25,T2+16+i*20,s2[0]+' data','lab');});
  txt(sv,W2-R3+8,T2+58,'filled: '+cards[0],'lab'); if(Wf2)txt(sv,W2-R3+8,T2+74,'hollow: '+cards[1],'lab'); txt(sv,W2-R3+8,T2+90,'bar: range, both cards','lab');
  const dz=Wf.zeros.slope_pj_per_byte_per_hop, dr=Wf.random.slope_pj_per_byte_per_hop;
  const dz2=Wf2&&Wf2.zeros?Wf2.zeros.slope_pj_per_byte_per_hop:null, dr2=Wf2&&Wf2.random?Wf2.random.slope_pj_per_byte_per_hop:null;
  const shr=d=>(Wf.random.points.find(p=>p.hops===d)||{}).shires, full=Wf.random.points.filter(p=>p.shires===32).map(p=>p.hops);
  document.getElementById('wirecap').textContent=`1 KB tensor loads from a scratchpad exactly d hops away, all 32 shires reading up to ${Math.max(...full)} hops (${shr(6)} at 6 hops, ${shr(8)} at 8, so the 8-hop point has half the traffic), at most two readers per target. Rings at d = 0 are the shire's own scratchpad. Dashed: straight-line fits over 1–8 hops.`;
  const tog=(dr-dz)*1000/8, tog2=dr2!=null?(dr2-dz2)*1000/8:null;
  /* the same points fitted over 1-6 hops, leaving out d = 8, which only 16 shires reach */
  const s6=wf=>wf?lfit(wf.points.filter(p=>p.hops>=1&&p.hops<=6).map(p=>[p.hops,p.pj_per_byte])).b:null;
  const r6=s6(Wf.random), z6=s6(Wf.zeros), r6b=Wf2?s6(Wf2.random):null, z6b=Wf2?s6(Wf2.zeros):null;
  document.getElementById('wiretext').innerHTML=`<b>One hop of mesh costs ${dr.toFixed(2)} pJ per byte on random data and ${dz.toFixed(2)} on zeros</b> on ${cards[0]}${dr2!=null?' ('+dr2.toFixed(2)+' and '+dz2.toFixed(2)+' on '+cards[1]+')':''}, fitted over 1–8 hops. `+
   `What random data adds over zeros — <b>${tog.toFixed(0)}${tog2!=null?' and '+tog2.toFixed(0):''} fJ per random bit per hop</b> on the two cards — is the data-dependent energy of the links and routers: part of it is bits that differ from one flit (the unit the mesh moves as a whole) to the next, and part is the ones carried, which cost even when they do not change; <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm">Heat per millimetre</a> separates the two with chosen bit patterns and converts them to fJ per bit·mm. `+
   `The ${dz.toFixed(2)} pJ/B that a hop costs on all-zero data is clocking, arbitration and buffering. The intercept, ${Wf.random.intercept_pj_per_byte.toFixed(2)} pJ/B on random data against ${(Wf.random.local_pj_per_byte||0).toFixed(2)} for the shire's own scratchpad, is the array access plus the step of leaving the shire at all.`+
   (r6!=null?` Fitted over 1–6 hops instead, leaving out d = 8, where only ${shr(8)} shires have a partner and the point sits nearly level with d = 6, the same data give ${f2(r6)}${r6b!=null?' and '+f2(r6b):''} pJ/B per hop on random data and ${f0((r6-z6)*1000/8)}${r6b!=null?' and '+f0((r6b-z6b)*1000/8):''} fJ per random bit per hop, which is what Heat per millimetre measures (2.17 pJ/B per hop on board power, loaded mesh): use its figures for wires.`:'');
 }
 /* ---- lines and rows ---- */
 const fz=S['l1fill/stride32/zeros'],fr=S['l1fill/stride32/random'],gz=S['l1fill/stride64/zeros'],gr=S['l1fill/stride64/random'];
 if(fz&&fr&&gz&&gr){
  document.getElementById('linetab').innerHTML='<thead><tr><th>32 B loads through the L1 from the shire’s scratchpad</th><th class="num">fills per load</th><th class="num">zeros pJ per load</th><th class="num">random pJ per load</th></tr></thead><tbody>'+
   [['32','0.5','l1fill/stride32'],['64','1','l1fill/stride64'],['128','1','l1fill/stride128']].map(r=>{const z=cb(r[2]+'/zeros',32),x=cb(r[2]+'/random',32);return z&&x?`<tr><td>stride ${r[0]} B</td><td class="num">${r[1]}</td><td class="num">${bt(z,f1)}</td><td class="num">${bt(x,f1)}</td></tr>`:'';}).join('')+
   '<tr><td colspan="4"><b>64 B tensor loads from the scratchpad, by stride</b></td></tr>'+
   ['64','128','256'].map(st=>{const z=cb(`scpline/stride${st}/zeros`,64),r=cb(`scpline/stride${st}/random`,64),rs=S[`scpline/stride${st}/random`]; return z&&r?`<tr><td>stride ${st} B (${st==='64'?'cycles the banks':st==='128'?'alternates two banks':'the same bank every time'})</td><td class="num">—</td><td class="num">${bt(z,f1)} per 64 B</td><td class="num">${bt(r,f1)} per 64 B, ${nf(rs.bytes_per_s.mean/1e9)} GB/s</td></tr>`:'';}).join('')+
   '<tr><td colspan="4" class="small">Each entry: mean over three passes on each of two cards, and the range those six passes spanned.</td></tr></tbody>';
  const c32z=cb('l1fill/stride32/zeros',32),c64z=cb('l1fill/stride64/zeros',32),c32r=cb('l1fill/stride32/random',32),c64r=cb('l1fill/stride64/random',32);
  const fillz=2*(c64z.mean-c32z.mean), fillr=2*(c64r.mean-c32r.mean);
  const per=h=>2*((c64r.per_card[h]||{mean:0}).mean-(c32r.per_card[h]||{mean:0}).mean);
  const tlz=cb('tload/scp/zeros'), tlr=cb('tload/scp/random');
  document.getElementById('linetext').innerHTML=`Twice the difference between the stride-64 and stride-32 rows is what filling one 64 B line from the scratchpad into the L1 costs: <b>${fillz.toFixed(0)} pJ on zeros, ${fillr.toFixed(0)} pJ on random data</b> (${Object.keys(c64r.per_card).sort().map(h=>'a'+h.slice(-1)+' '+per(h).toFixed(0)).join(', ')} on random data) — ${f1(fillz/64)} and ${f1(fillr/64)} pJ per byte of line, about ${Math.round(100*(fillz/64+fillr/64)/(tlz.mean+tlr.mean)/5)*5}% of the ${f1(tlz.mean)} and ${f1(tlr.mean)} pJ/B a tensor load pays for the same bytes from the same scratchpad. What random data adds over zeros is about ${(fillr-fillz).toFixed(0)} pJ for the fill's 512 bits, ${((fillr-fillz)*1000/512).toFixed(0)} fJ per bit on the path from the shire cache into the L1.`;
 }
 const rz2=n=>S[`dramrow2/${n}/zeros`], rr2=n=>S[`dramrow2/${n}/random`];
 if(rz2('seq')&&rz2('rowmiss')){
  document.getElementById('rowtab').innerHTML='<thead><tr><th>1 KB tensor loads from DRAM, 32 harts with 64 MB each</th><th class="num">zeros pJ/B</th><th class="num">random pJ/B</th><th class="num">GB/s</th></tr></thead><tbody>'+
   [['seq','sequential: next bank, 32 columns per row visit'],['rowhit','same bank and row, next column, every access'],['rowmiss','a new row on every visit to a bank']].map(r=>{const z=rz2(r[0]),x=rr2(r[0]),cz=cb(`dramrow2/${r[0]}/zeros`),cx=cb(`dramrow2/${r[0]}/random`);return z&&x?`<tr><td>${r[1]}</td><td class="num">${cz?bt(cz,f1):z.pj_per_byte.mean.toFixed(1)+' ± '+z.pj_per_byte.se.toFixed(1)}</td><td class="num">${cx?bt(cx,f1):x.pj_per_byte.mean.toFixed(1)+' ± '+x.pj_per_byte.se.toFixed(1)}</td><td class="num">${(x.bytes_per_s.mean/1e9).toFixed(1)}</td></tr>`:'';}).join('')+
   `<tr><td colspan="4" class="small">${cb('dramrow2/seq/random')&&cb('dramrow2/seq/random').n>3?'Mean and range over three passes on each of two cards.':'Mean and range over three passes on aifoundry2.'}</td></tr></tbody>`;
  const l3=S['dramrow/stride8K/random'], l3z=S['dramrow/stride8K/zeros'];
  document.getElementById('rowtext').innerHTML=`<b>The row pattern does not change the energy per byte</b>: row hits, row misses and the streaming case agree within their pass-to-pass error on both operand sets. Either the controller closes pages after each access, so the baseline already includes an activation, or the activation is small next to the transfer; the instruments cannot tell which, and for a programmer it makes no difference.`+(l3&&l3z?` An earlier version of this experiment with all 1,024 minions and only 32 KB touched per hart fitted in the L3 and measured that instead: <b>${l3z.pj_per_byte.mean.toFixed(1)} pJ/B on zeros, ${l3.pj_per_byte.mean.toFixed(1)} on random data at ${nf(l3.bytes_per_s.mean/1e9)} GB/s</b>, the L3 read by tensor loads through the mesh.`:'');
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
  [['minions','var(--c1)'],['SRAM','var(--c3)'],['mesh','var(--c2)'],['no sensor (regulators, PHYs)','var(--ref)']].forEach((s2,i)=>{el('rect',{x:L+8+i*90,y:T-22,width:11,height:11,fill:s2[1]},svg);const t=txt(svg,L+23+i*90,T-13,s2[0],'lab');t.setAttribute('font-size','10');});
  document.getElementById('railscap').textContent='Random data, aifoundry2, mean of three passes. The split of each burst’s power over idle across the three rails the PMIC meters, read from the end of the burst and corrected for the lag of the PMIC’s own running average (about one second); the remainder has no sensor.';
  const wire6=rows.find(r=>r.label==='scratchpad 6 hops away'), si=rows.find(r=>r.label==='scalar integer'), dr=rows.find(r=>r.label==='DRAM, tensor load');
  const U=D.unmetered, uf=U&&U.aifoundry2, dd=U&&U.ddr_droop;
  /* the fit's residual on the configurations that move DRAM, from the per-configuration means and the fitted coefficients */
  const dramRms=h=>{const u=U&&U[h], SS=C.cards[h]&&C.cards[h].summary; if(!u||!SS)return null; const r=[];
   for(const k in SS){if(!k.includes('dram')||k.startsWith('dramrow/stride8K'))continue; const e=SS[k], R_=e.rails_over_w, m=R_.minion_w.mean, sr=R_.sram_w.mean, n=R_.noc_w.mean;
    r.push(e.over_idle_w.mean-m-sr-n-(u.coef.minion*m+u.coef.sram*sr+u.coef.noc*n+u.coef.dram_pj_per_byte*e.bytes_per_s.mean*1e-12));}
   return r.length?{rms:Math.sqrt(r.reduce((a,v)=>a+v*v,0)/r.length),n:r.length}:null;};
  const dr2=dramRms('aifoundry2'), dr3=dramRms('aifoundry3');
  const unmetText=uf?` <b>Attributed:</b> over the whole catalogue the unmetered part of each configuration's power over idle fits as ${(100*uf.coef.minion).toFixed(0)}% of the minion rail's watts (a delivery loss), ${(100*uf.coef.sram).toFixed(0)}% of the SRAM rail's, ${(100*uf.coef.noc).toFixed(0)}% of the mesh's (more than a regulator: the memory shires' logic on an unmetered rail works when the mesh moves bytes to them) and ${uf.coef.dram_pj_per_byte.toFixed(0)} pJ per DRAM byte off-rail, to rms ${uf.rms_w.toFixed(2)} W over ${uf.n} configuration means${dr2?` and ${f1(dr2.rms)} W over the ${dr2.n} that move DRAM`:''}${U.aifoundry3?'; on aifoundry3 '+(100*U.aifoundry3.coef.minion).toFixed(0)+'%, '+(100*U.aifoundry3.coef.sram).toFixed(0)+'%, '+(100*U.aifoundry3.coef.noc).toFixed(0)+'% and '+U.aifoundry3.coef.dram_pj_per_byte.toFixed(0)+' pJ/B'+(dr3?`, ${f1(dr3.rms)} W over its ${dr3.n} DRAM configurations`:''):''}. The idle 15 W is not split. <code>tools/ettelem/fit_unmetered.py</code> reproduces this fit exactly from the catalogue.`:'';
  const droopText=dd?` <b>A droop meter for DRAM:</b> the memory shires' Moortec voltage monitors report the 0.8 V DDR rail every 133 ms (<code>die_mv.ddr</code>, ${dd.idle_die_mv.ddr.toFixed(0)} mV at idle), and it droops ${dd.mv_per_dram_offrail_w.toFixed(2)} mV per watt of off-rail DRAM power (rms ${dd.rms_mv.toFixed(2)} mV over the catalogue; the committed script reproduces the coefficient to within 3%, 0.87 against 0.84 mV/W): 1 mV ≈ ${f1(1/dd.mv_per_dram_offrail_w)} W of DRAM, refreshed every 133 ms. It is a proxy calibrated against the fit, not a meter: heavy on-chip traffic moves it too (${(()=>{const e=(dd.examples||[]).find(x=>x.cfg==='tload/scp/random'); return e?`a scratchpad-read burst droops it ${f1(e.droop_ddr_mv)} mV with no DRAM traffic`:'mesh and scratchpad bursts droop it with no DRAM traffic';})()}). How this and every other instrument could be pushed further is <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability">the limits of observability</a>.`:'';
  if(wire6&&si) document.getElementById('railstext').innerHTML=`<p><b>An instruction’s energy is the core’s</b>: ${Math.round(100*si.parts[0][1]/si.o)}% of a scalar integer burst is on the minion rail, almost nothing on the SRAM or the mesh, and the rest is what the regulators lose delivering it. <b>A byte fetched across the mesh is mostly wire</b>: six hops away, ${Math.round(100*wire6.parts[2][1]/wire6.o)}% of the energy is on the mesh rail and ${Math.round(100*wire6.parts[1][1]/wire6.o)}% on the SRAM that holds it, with the minions that asked for it at ${Math.round(100*wire6.parts[0][1]/wire6.o)}%.`+(dr?` <b>A DRAM byte is mostly off-chip</b>: ${Math.round(100*(dr.parts[3][1])/dr.o)}% of its energy is on no metered rail at all — the DDR PHY and the memory itself.`:'')+'</p>'+(unmetText?'<p>'+unmetText.trim()+'</p>':'')+(droopText?'<p>'+droopText.trim()+'</p>':'');
 })();

 /* ---- SRAM leakage ---- */
 const sl=C.cards[cards[0]].sram_leakage; if(sl&&sl.fit&&sl.curve.length>2){
  const W3=700,H3=280,L3=58,R4=16,T3=26,B3=52,{svg:sv,tip:tp,h:hh}=host('sram',W3,H3);
  const xs=sl.curve.map(c=>c.T), ys=sl.curve.map(c=>c.sram_w);
  const x=v=>L3+(W3-L3-R4)*(v-Math.min(...xs)+1)/(Math.max(...xs)-Math.min(...xs)+2), yy=v=>H3-B3-(H3-B3-T3)*(v-Math.min(...ys)*0.9)/(Math.max(...ys)*1.05-Math.min(...ys)*0.9);
  axes(sv,{W:W3,H:H3,L:L3,R:R4,T:T3,B:B3,x,y:yy,yt:[1.5,2,2.5,3,3.5].filter(v=>v>=Math.min(...ys)*0.9&&v<=Math.max(...ys)*1.05),xt:xs.filter((v,i)=>i%2===0),xl:'die temperature, °C',yl:'SRAM rail, W (idle)'});
  const fit=sl.fit, law=[]; for(let t=Math.min(...xs);t<=Math.max(...xs);t+=0.5) law.push([t,fit.P_fix_w+fit.A_leak_80_w*Math.exp((t-80)/36)]);
  el('path',{d:path(law,x,yy),class:'ln s1'},sv);
  sl.curve.forEach(c=>{const gg=el('g',{},sv);el('circle',{cx:x(c.T),cy:yy(c.sram_w),r:3.5,fill:'var(--c2)'},gg);hover(gg,tp,hh,()=>`${c.T} °C: ${c.sram_w.toFixed(3)} W on the SRAM rail (${c.n} idle samples, ${cards[0]})`);});
  const sl2=cards[1]&&C.cards[cards[1]].sram_leakage; let sl2note='';
  if(sl2&&sl2.curve&&sl2.curve.length){const inr=sl2.curve.filter(c=>c.T>=Math.min(...xs)-1&&c.T<=Math.max(...xs)+1);
   inr.forEach(c=>{const gg=el('g',{},sv);el('circle',{cx:x(c.T),cy:yy(c.sram_w),r:3.5,fill:'none',stroke:'var(--c3)','stroke-width':2},gg);hover(gg,tp,hh,()=>`${c.T} °C: ${c.sram_w.toFixed(3)} W on the SRAM rail (${c.n} idle samples, ${cards[1]})`);});
   const lo2=sl2.curve[0]; sl2note=` ${cards[1]} idles cooler: its SRAM rail reads ${lo2.sram_w.toFixed(2)} W at ${lo2.T} °C, where the ${cards[0]} fit, extrapolated, says ${(fit.P_fix_w+fit.A_leak_80_w*Math.exp((lo2.T-80)/36)).toFixed(2)} W${inr.length?'; its points inside the fitted range are the hollow ones':''}.`;}
  const c80=sl.curve.find(c=>c.T===80), rd=cb('tload/scp/random'), fit2=sl2&&sl2.fit;
  const mb=c80?1000*c80.sram_w/128:fit.mw_per_mb_at_80, nj=mb/1048576*1e6;
  document.getElementById('sramcap').textContent=`The rail feeding 128 MB of on-chip SRAM, at idle, on ${cards[0]}. Fitted with the idle law's 36 °C e-folding imposed: ${f2(fit.P_fix_w).replace('-','−')} W + ${f2(fit.A_leak_80_w)} W·e^((T−80)/36); ${fit.P_fix_w<0?'the negative constant says the rail rises faster than that shape. ':''}`+
   (c80?`The whole rail at 80 °C is ${f2(c80.sram_w)} W, ${f1(mb)} mW per MB, an upper bound on the arrays' leakage including the cache logic${fit2?`; ${cards[1]}'s rail, fitted the same way, gives ${f0(fit2.mw_per_mb_at_80)} mW/MB, an extrapolation from its idle at ${Math.min(...sl2.curve.map(c=>c.T))}–${Math.max(...sl2.curve.map(c=>c.T))} °C`:''}. `:'')+
   `At about ${f0(mb)} mW per MB, a byte held in scratchpad for one second leaks about ${f0(nj)} nJ — as much as reading it ${rd?nf(Math.round(nj*1000/rd.mean/100)*100):'—'} times (${rd?f1(rd.mean):'—'} pJ per read).`+sl2note;
 }
 const nb=[0,1,2,3].map(k=>S[`neigh/${k}/random`]); if(nb.every(v=>v)){
  document.getElementById('neightab').innerHTML='<thead><tr><th>Which neighbourhood reads the shire’s own scratchpad (random data)</th><th class="num">pJ/B, both cards</th><th class="num">per card</th><th class="num">GB/s</th></tr></thead><tbody>'+
   nb.map((v,k)=>{const c=cb(`neigh/${k}/random`);return `<tr><td>neighbourhood ${k}, minions ${8*k}–${8*k+7}</td><td class="num">${c?bt(c,f2):v.pj_per_byte.mean.toFixed(2)}</td><td class="num small">${c?pcs(c,f2):v.pj_per_byte.se.toFixed(2)}</td><td class="num">${nf(v.bytes_per_s.mean/1e9)}</td></tr>`;}).join('')+'</tbody>';
 }
})();

/* ---------- contents: every h2 and h3, with its section number; runs before the template adds its # links ---------- */
(function(){const ol=document.getElementById('toclist'); if(!ol)return;
 ol.style.listStyle='none'; ol.style.paddingLeft='0'; ol.style.margin='6px 0 0';
 document.querySelectorAll('main h2, main h3').forEach(hd=>{if(!hd.id)return;
  const li=document.createElement('li'), a=document.createElement('a'); a.href='#'+hd.id; a.textContent=hd.textContent.replace(/\s+/g,' ').trim();
  if(hd.tagName==='H3'){li.style.marginLeft='1.4em'; li.className='small';} li.appendChild(a); ol.appendChild(li);});})();
