/* The energy manual's page script. D is manual.json (tools/ettelem/build_energy_manual.py); CK is the shared chart
   toolkit (docs/reports/sources/chartkit.js). Every number the page prints is computed from D here, except the few
   typed constants that say where they come from. Every chart is drawn with CK: sized to its container, keyboard- and
   touch-reachable, tokens only. */
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
function ebar(svg,x,y1,y2,col){const g2=CK.el('g',{},svg), st={stroke:col||'var(--ink)','stroke-width':1.5};
  CK.el('line',Object.assign({x1:x,x2:x,y1,y2},st),g2); CK.el('line',Object.assign({x1:x-3,x2:x+3,y1,y2:y1},st),g2); CK.el('line',Object.assign({x1:x-3,x2:x+3,y1:y2,y2},st),g2); return g2;}

/* ---------- shared for the CK charts ---------- */
const $=id=>document.getElementById(id);
const HUB='https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability';
const lawAt=T=>R.P_fix_w+R.A_leak_80_w*Math.exp((T-80)/R.T_L_c);
const CARDS=Object.keys(D.catalogue.cards), SA=D.catalogue.cards[CARDS[0]].summary, SB=CARDS[1]?D.catalogue.cards[CARDS[1]].summary:{};
const S2=SA;
const at={}; D.sync.atomics.runs.forEach(r=>at[r.label]=r);
const HOT=RR.hotline_over_idle_w&&RR.hotline_over_idle_w.contended;       /* 1,024 minions stalled on one line, W over idle */
const TB=D.tensor.bars||{};
const rp={}; D.relay.power.media.forEach(m=>rp[m.medium]=m);
const MH=D.comm.mesh_hops||{};
/* a mark: a group with a visible shape and a larger invisible hit target, carrying a tooltip */
function mark(f,parent,shape,attrs,hitR,html){const gg=CK.el('g',{},parent); if(hitR&&attrs.cx!=null)CK.el('circle',{cx:attrs.cx,cy:attrs.cy,r:hitR,class:'ck-hit'},gg);
 CK.el(shape,attrs,gg); CK.tip(f,gg,html); return gg;}
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
const LANES=new Set([...CLASSES[4][1],...CLASSES[5][1],...CLASSES[6][1],...CLASSES[7][1]]);
/* the wire read interpolated to a fractional hop count (the relay's next shire is 3.5 hops away on average) */
const wireAt=(hh,o)=>{const lo=Math.floor(hh),hi=Math.ceil(hh),a=cb(`wire/hop${lo}/${o}`),b=cb(`wire/hop${hi}/${o}`); if(!a||!b)return null;
 const t=hi>lo?(hh-lo)/(hi-lo):0, mix=k=>a[k]+(b[k]-a[k])*t, pc={};
 for(const h in a.per_card)if(b.per_card[h])pc[h]={mean:a.per_card[h].mean+(b.per_card[h].mean-a.per_card[h].mean)*t,se:Math.max(a.per_card[h].se,b.per_card[h].se)};
 return {mean:mix('mean'),lo:mix('lo'),hi:mix('hi'),n:Math.min(a.n,b.n),per_card:pc};};
const HH=MH.xshire1?MH.xshire1.mean:3.5;
/* off-rail energy per byte on aifoundry2: power over idle less the three rails and the fitted delivery losses on them
   (the attribution of Limits of observability §4.2; coefficients in D.unmetered) */
const offRail=k=>{const u=D.unmetered&&D.unmetered.aifoundry2, e=SA[k]; if(!u||!e||!e.bytes_per_s.mean)return null;
 const r=e.rails_over_w, m=r.minion_w.mean, s=r.sram_w.mean, n=r.noc_w.mean, c=u.coef;
 return (e.over_idle_w.mean-m-s-n-(c.minion*m+c.sram*s+c.noc*n))/e.bytes_per_s.mean*1e12;};

/* place text labels next to points without overlapping each other or the given boxes; a label that fits nowhere
   is left out (the tooltip still names the point). items: {x, y, text}; boxes: [x0, y0, x1, y1]; bounds likewise */
function placeLabels(parent,items,boxes,bounds,cls){const bx=boxes.slice(), wOf=t=>t.length*6.3+2, H=12;
 const hit=b=>b[0]<bounds[0]||b[2]>bounds[2]||b[1]<bounds[1]||b[3]>bounds[3]||bx.some(o=>!(b[2]<=o[0]||b[0]>=o[2]||b[3]<=o[1]||b[1]>=o[3]));
 items.forEach(it=>{const w=wOf(it.text);
  for(const [dx,dy,an] of [[9,4,'start'],[-9,4,'end'],[0,-10,'middle'],[0,18,'middle'],[8,-8,'start'],[8,16,'start'],[-8,-8,'end'],[-8,16,'end'],[0,-22,'middle'],[0,30,'middle'],[-10,-20,'end'],[10,-20,'start'],[-10,28,'end'],[10,28,'start']]){
   const x0=an==='start'?it.x+dx:an==='end'?it.x+dx-w:it.x+dx-w/2, b=[x0,it.y+dy-10,x0+w,it.y+dy-10+H]; if(hit(b))continue;
   bx.push(b); const t=CK.txt(parent,it.x+dx,it.y+dy,it.text,cls||'lab',an); t.classList.add('halo'); if(it.series)t.setAttribute('data-series',it.series); return;}});}

/* ---------- KPIs ---------- */
(function(){
 /* D3 (version 3): the idle law is led by its measured slope; its split into fixed and leakage is the range over the
    e-foldings that fit the idle bins equally well (R.profile, build_energy_manual.py) */
 const PF=R.profile, lkr=PF?`${f0(PF.A_leak_80_w[0])}–${f0(PF.A_leak_80_w[1])} W`:'';
 $('k1').textContent=`+${f2(R.lambda_80_w_per_c)} W/°C`;
 if(PF){$('k1sub').textContent=`on ${f1(P80)} W, of which ${lkr} is leakage (the data do not pin the split closer)`;
  $('restlede').textContent=`At rest the card draws ${f1(P80)} W at 80 °C and ${f2(R.lambda_80_w_per_c)} W more per degree (aifoundry2), ${lkr} of it leakage.`;}
 const fm=cb('fmadd.ps/random/h2'); $('k2').textContent=fm?`${f0(fm.mean)} pJ [${f0(fm.lo)}–${f0(fm.hi)}]`:f0(g('fmadd_ps','random',2).pj_per_op)+' pJ';
 const dl=cb('tload/dram/random'),sl=cb('tload/scp/random'); $('k3').textContent=dl&&sl?`${f0(dl.mean/sl.mean)}× [${f0(dl.lo/sl.hi)}–${f0(dl.hi/sl.lo)}]`:f0(g('tload','random',1,false).pj_per_byte/g('tload','random',1,true).pj_per_byte)+'×';
 const cc=D.catalogue&&D.catalogue.cross_card, DB=D.catalogue&&D.catalogue.die_c_busy_median;
 if(cc){$('k4').textContent=f3(cc.median); $('k4sub').textContent=`median ratio aifoundry3 / aifoundry2, each at its own die temperature (10–90%: ${f3(cc.p10)}–${f3(cc.p90)})`;
  if(DB&&DB.aifoundry2&&DB.aifoundry3)$('cardlede').textContent=`aifoundry3 reads about ${f0(100*(1-cc.median))}% lower than aifoundry2 (median ${f2(cc.median)}; 80% of entries ${f0(100*(1-cc.p90))}–${f0(100*(1-cc.p10))}% lower), each card at its own die temperature, aifoundry3's about ${f0(Math.round((DB.aifoundry2-DB.aifoundry3)/5)*5)} °C cooler; whether the difference is the card or the temperature is not yet known.`;}
 /* section 9: the unsensed remainder at idle, per card (catalogue idle stretches, build_energy_manual.py) */
 const IU=D.catalogue&&D.catalogue.idle_unsensed;
 if(IU&&IU.aifoundry2&&IU.aifoundry3)$('unsensed').textContent=`The unsensed remainder, about ${f0(IU.aifoundry2.mean)} W on aifoundry2 and ${f0(IU.aifoundry3.mean)} W on aifoundry3, the largest single component of idle on both cards,`;
 /* the correction each burst of the three-pass catalogue received, per card (build_energy_manual.py) */
 const LC=D.catalogue&&D.catalogue.leak_correction;
 if(LC&&LC.aifoundry2){const a=LC.aifoundry2,b=LC.aifoundry3;
  $('corr').textContent=`${f2(a.median_w)} W in the median and ${f2(a.max_w)} W at most over aifoundry2's ${nf(a.bursts)} bursts`+(b?` (${f2(b.median_w)} and ${f2(b.max_w)} W over aifoundry3's ${nf(b.bursts)})`:'');}
})();

/* ---------- 1. the card at rest ---------- */
(function(){
 const rl=R.rails_73c;
 /* The two slopes are typed: the idle gaps of the aifoundry2 catalogue (every 600 MHz sample at least 1.5 s before
    and 2.5 s after any burst, n ≈ 9,800, 71–83 °C) fitted against the die temperature give 0.033 W/°C for board
    minus the three rails and 0.548 W/°C for the rails together; no committed script writes them. */
 const PF=R.profile, IU=D.catalogue&&D.catalogue.idle_unsensed, rg0=v=>`${f0(v[0])}–${f0(v[1])}`;
 const split=PF?`How much of the ${f1(P80)} W is leakage they do not: the idle bins fit equally well with the leakage e-folding anywhere from ${PF.T_L_window_c[0]} to ${PF.T_L_window_c[1]} °C (doubling every ${rg0(PF.doubling_c)} °C), which puts the leakage at 80 °C at ${rg0(PF.A_leak_80_w)} W and the fixed part at ${rg0(PF.P_fix_w)} W. `:'';
 const uns=IU&&IU.aifoundry2&&IU.aifoundry3?`draw about ${f0(IU.aifoundry2.mean)} W at idle on aifoundry2 (${rg0(IU.aifoundry2.die_c)} °C) and ${f0(IU.aifoundry3.mean)} W on aifoundry3 (${rg0(IU.aifoundry3.die_c)} °C), and`:`draw about ${f0(rl.unsensed)} W at idle and`;
 $('resttext').innerHTML=`Everything below is <em>above</em> this. On aifoundry2 the idle card draws ${f1(P80)} W at 80 °C and ${f2(R.lambda_80_w_per_c)} W more for each degree there, and that slope is what the idle measurements pin down${PF?` (${f2(PF.lambda_80_w_per_c[0])}–${f2(PF.lambda_80_w_per_c[1])} W per °C for every e-folding that fits)`:''}. ${split}The law drawn below is the best fit, ${f1(R.P_fix_w)} W fixed and ${f1(R.A_leak_80_w)} W of leakage at 80 °C e-folding every ${f0(R.T_L_c)} °C: a fit, not a block-by-block account. The blocks with no rail sensor (PCIe, the DDR PHY, the IO shire, the regulators) ${uns} barely move with temperature: 0.03 W per °C over 71–83 °C in the catalogue's idle gaps. The three metered rails carry the leakage, 0.55 W per °C between them at about 75 °C. What the unsensed blocks spend when a kernel uses them (DRAM traffic through the DDR PHY, the regulators' delivery loss) is counted in the per-event costs below, and <a href="${HUB}#the-unmetered-remainder-attributed">Limits of observability, §4.2</a> attributes it. The leakage answers to temperature, which the kernel sets.`;
 const LK=D.cards&&D.cards.leakage, ic3=(LK&&LK.idle_curve)||[];
 CK.legend('idle-legend',[{key:'law',label:'the law, fitted on aifoundry2',mark:'line',color:'var(--c1)'},{key:'fix',label:'its constant, at the best fit',mark:'dash',color:'var(--ref)'},
   {key:'a2',label:'aifoundry2 idle bins',mark:'dot',color:'var(--c2)'}].concat(ic3.length?[{key:'a3',label:'aifoundry3 idle bins',mark:'ring',color:'var(--c3)'}]:[]));
 CK.frame('idle',{height:W=>W<600?260:320,label:'Idle board power against die temperature: the law and the measured idle bins',draw:f=>{
  const L=40,Rr=12,T=24,B=40, x=CK.lin(40,95,L,f.W-Rr), y=CK.lin(10,50,f.H-B,T);
  CK.axes(f,{x,y,L,R:Rr,T,B,xt:[40,50,60,70,80,90],yt:[10,20,30,40,50],xl:'die temperature, °C',yl:'idle board power, W'});
  const law=[]; for(let t=40;t<=95;t++) law.push([t,lawAt(t)]);
  CK.el('path',{d:CK.path(law,x,y),class:'ln s1'},f.svg);
  CK.el('line',{x1:L,x2:f.W-Rr,y1:y(R.P_fix_w),y2:y(R.P_fix_w),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},f.svg);
  CK.txt(f.svg,f.W-Rr-4,y(R.P_fix_w)-6,'best-fit constant '+f1(R.P_fix_w)+' W','lab','end');
  const n2=R.measured_idle.map(p=>mark(f,f.svg,'circle',{cx:x(p.T),cy:y(p.P),r:3.5,fill:'var(--c2)'},8,`aifoundry2 idle at ${p.T} °C: <b>${f2(p.P)} W</b> (${nf(p.n)} samples)<br>the law: ${f2(lawAt(p.T))} W`));
  const n3=ic3.map(p=>mark(f,f.svg,'circle',{cx:x(p.T),cy:y(p.W),r:4.5,fill:'none',stroke:'var(--c3)','stroke-width':2},8,`aifoundry3 idle at ${p.T} °C: <b>${f2(p.W)} W</b> (${nf(p.n)} samples)<br>the aifoundry2 law: ${f2(lawAt(p.T))} W`));
  if(ic3.length){const p0=ic3.reduce((a,b)=>a.T<b.T?a:b); CK.txt(f.svg,x(p0.T)-9,y(p0.W)+4,'aifoundry3','lab','end');}
  CK.keynav(f,n2); CK.keynav(f,n3);
 }});
 const tmin=Math.min(...R.measured_idle.map(p=>p.T)), tmax=Math.max(...R.measured_idle.map(p=>p.T));
 const sg=v=>(v<0?'−':'+')+f2(Math.abs(v)), LR=D.catalogue&&D.catalogue.idle_law_residual;
 const r3=ic3.length?` Rings: aifoundry3's idle at ${Math.min(...ic3.map(p=>p.T))}–${Math.max(...ic3.map(p=>p.T))} °C (22 September), ${tmin-Math.max(...ic3.map(p=>p.T))}–${tmin-Math.min(...ic3.map(p=>p.T))} °C below the coolest fitted bin: ${LK.mean_offset_W>=0?'+':''}${f1(LK.mean_offset_W)} W from the law (the mean of its ${WORD[ic3.length]} temperature bins).`+
  (LR&&LR.aifoundry2&&LR.aifoundry3?` In the idle stretches of the 23 September catalogue aifoundry3 sat ${sg(LR.aifoundry3.mean)} W from the law at ${f0(LR.aifoundry3.die_c[0])}–${f0(LR.aifoundry3.die_c[1])} °C and aifoundry2 ${sg(LR.aifoundry2.mean)} W at ${f0(LR.aifoundry2.die_c[0])}–${f0(LR.aifoundry2.die_c[1])} °C (three passes each).`:''):'';
 const lf=t=>PF.leak_frac[String(t)].map(v=>Math.round(100*v)).join('–')+'%';
 const share=PF?` Leakage share on aifoundry2 over those e-foldings: ${lf(60)} at 60 °C, ${lf(80)} at 80 °C, ${lf(90)} at 90 °C (${Math.round(100*R.curve.find(c=>c.T===60).leak_frac)}%, ${Math.round(100*R.curve.find(c=>c.T===80).leak_frac)}% and ${Math.round(100*R.curve.find(c=>c.T===90).leak_frac)}% at the best fit).`:
  ` Leakage share: ${Math.round(100*R.curve.find(c=>c.T===60).leak_frac)}% at 60 °C, ${Math.round(100*R.curve.find(c=>c.T===80).leak_frac)}% at 80 °C, ${Math.round(100*R.curve.find(c=>c.T===90).leak_frac)}% at 90 °C.`;
 $('idlecap').textContent=`Line: the law fitted on 21 September, P = ${f1(R.P_fix_w)} W + ${f1(R.A_leak_80_w)} W·e^((T−80)/${f0(R.T_L_c)}), whose slope at 80 °C is ${f2(R.lambda_80_w_per_c)} W per °C${PF?`; with the e-folding anywhere from ${PF.T_L_window_c[0]} to ${PF.T_L_window_c[1]} °C the law passes the dots as well, at ${f2(PF.lambda_80_w_per_c[0])}–${f2(PF.lambda_80_w_per_c[1])} W per °C`:''}. Dots: every whole-degree idle bin of that session on aifoundry2, ${tmin}–${tmax} °C.${r3}${share}`;
 $('rails').innerHTML='<thead><tr><th>Idle at 73 °C, by rail</th><th class="num">W</th><th class="num">Share</th></tr></thead><tbody>'+
  [['Minions',rl.minion],['SRAM: L2, L3, scratchpad',rl.sram],['Mesh',rl.noc],['No rail sensor: PCIe, DDR PHY, IO shire, regulators',rl.unsensed]].map(r=>`<tr><td>${r[0]}</td><td class="num">${f2(r[1])}</td><td class="num">${Math.round(100*r[1]/rl.board)}%</td></tr>`).join('')+
  `<tr><td><b>Board</b> <span class="small">(aifoundry2 on 22 September at ${f0(rl.die_c)} °C, ${rl.hours_idle!=null?f1(rl.hours_idle):'about 20'} hours after the last workload, apart from a 4.9 s single-hart probe a few minutes before: ${rl.samples||300} samples over a minute, sd ${f2(rl.board_sd!=null?rl.board_sd:0.04)} W; the rails' sd 0.01 W or less)</span></td><td class="num"><b>${f2(rl.board)}</b></td><td></td></tr></tbody>`;
})();

/* ---------- 1.1 the SRAM arrays at rest ---------- */
(function(){
 const C=D.catalogue, sl=C.cards[CARDS[0]].sram_leakage; if(!(sl&&sl.fit&&sl.curve.length>2))return;
 const sl2=CARDS[1]&&C.cards[CARDS[1]].sram_leakage, fit=sl.fit, lawS=t=>fit.P_fix_w+fit.A_leak_80_w*Math.exp((t-80)/36);
 const xs=sl.curve.map(c=>c.T), ys=sl.curve.map(c=>c.sram_w), inr=sl2&&sl2.curve?sl2.curve.filter(c=>c.T>=Math.min(...xs)-1&&c.T<=Math.max(...xs)+1):[];
 CK.legend('sram-legend',[{key:'fit',label:'fit, 36 °C e-folding imposed',mark:'line',color:'var(--c1)'},{key:'a2',label:CARDS[0]+' idle bins',mark:'dot',color:'var(--c2)'}].concat(inr.length?[{key:'a3',label:CARDS[1]+' idle bins',mark:'ring',color:'var(--c3)'}]:[]));
 CK.frame('sram',{height:W=>W<600?240:280,label:'The SRAM rail at idle against die temperature',draw:f=>{
  const L=44,Rr=12,T=24,B=40, x=CK.lin(Math.min(...xs)-1,Math.max(...xs)+1,L,f.W-Rr), y=CK.lin(Math.min(...ys)*0.9,Math.max(...ys)*1.05,f.H-B,T);
  CK.axes(f,{x,y,L,R:Rr,T,B,xl:'die temperature, °C',yl:'SRAM rail at idle, W',yfmt:v=>f1(v)});
  const law=[]; for(let t=Math.min(...xs)-1;t<=Math.max(...xs)+1;t+=0.5) law.push([t,lawS(t)]);
  CK.el('path',{d:CK.path(law,x,y),class:'ln s1'},f.svg);
  const n2=sl.curve.map(c=>mark(f,f.svg,'circle',{cx:x(c.T),cy:y(c.sram_w),r:3.5,fill:'var(--c2)'},8,`${CARDS[0]}, ${c.T} °C: <b>${f3(c.sram_w)} W</b> on the SRAM rail (${nf(c.n)} idle samples)`));
  const n3=inr.map(c=>mark(f,f.svg,'circle',{cx:x(c.T),cy:y(c.sram_w),r:4.5,fill:'none',stroke:'var(--c3)','stroke-width':2},8,`${CARDS[1]}, ${c.T} °C: <b>${f3(c.sram_w)} W</b> on the SRAM rail (${nf(c.n)} idle samples)`));
  CK.keynav(f,n2); CK.keynav(f,n3);
 }});
 let sl2note='';
 /* the other card at its most-sampled idle bin: the aifoundry2 fit does not describe it, and card and shape are confounded */
 if(sl2&&sl2.curve&&sl2.curve.length){const lo2=sl2.curve.reduce((a,b)=>b.n>a.n?b:a); sl2note=` On ${CARDS[1]}, which idles cooler, the rail reads ${f2(lo2.sram_w)} W at ${lo2.T} °C (its most-sampled bin), where the ${CARDS[0]} fit, extrapolated, says ${f2(lawS(lo2.T))} W: the ${CARDS[0]} fit does not describe ${CARDS[1]}, and whether that is the card or the fit's shape outside its range is not known${inr.length?'; its points inside the fitted range are the hollow ones':''}.`;}
 const c80=sl.curve.find(c=>c.T===80), rd=cb('tload/scp/random');
 const mb=c80?1000*c80.sram_w/128:fit.mw_per_mb_at_80, nj=mb/1048576*1e6;
 $('sramcap').textContent=`The rail feeding 128 MB of on-chip SRAM, at idle, on ${CARDS[0]}. Fitted with the idle law's 36 °C e-folding imposed: ${f2(fit.P_fix_w).replace('-','−')} W + ${f2(fit.A_leak_80_w)} W·e^((T−80)/36); ${fit.P_fix_w<0?'the negative constant says the rail rises faster than that shape. ':''}`+
  (c80?`The whole rail at 80 °C is ${f2(c80.sram_w)} W, ${f1(mb)} mW per MB, an upper bound on the arrays' leakage including the cache logic. `:'')+
  `At about ${f0(mb)} mW per MB, a byte held in scratchpad for one second at 80 °C leaks at most about ${f0(nj)} nJ on ${CARDS[0]} — as much as reading it ${rd?nf(Math.round(nj*1000/rd.mean/100)*100):'—'} times (${rd?f1(rd.mean):'—'} pJ per read).`+sl2note;
})();

/* ---------- 2. awake ---------- */
(function(){
 const s1=g('spin','zeros',1),s2=g('spin','zeros',2), c1=cb('spin/zeros/h1'), c2=cb('spin/zeros/h2');
 const w1=S2['spin/zeros/h1']?S2['spin/zeros/h1'].over_idle_w.mean:s1.over_idle_w, w2=S2['spin/zeros/h2']?S2['spin/zeros/h2'].over_idle_w.mean:s2.over_idle_w;
 const hw=at.contended.over_idle_w, h2w=HOT&&HOT.per_card.aifoundry2?HOT.per_card.aifoundry2.mean:hw;
 const ab=D.awake.spin_hart0_1024, t=D.tensor.rows.find(r=>r.config==='fp32_randn'), AT=D.tensor.activity_term_mw_per_minion||{};
 const WL='https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power';
 const two=(a,b)=>`${a}<br><span class="small">${b}</span>`;
 $('awake').innerHTML='<thead><tr><th>Minions awake, doing the least they can</th><th class="num">pJ per instruction</th><th class="num">per card</th><th class="num">W over idle, 1,024 minions (a2)</th><th class="num">per minion (a2)</th></tr></thead><tbody>'+
  `<tr><td>One hart per minion, an addi loop</td><td class="num">${c1?bt(c1,f1):f1(s1.pj_per_op)}</td><td class="num small">${pcs(c1,f1)}</td><td class="num">${f2(w1)}</td><td class="num">${f2(w1/1024*1e3)} mW</td></tr>`+
  `<tr><td>Both harts</td><td class="num">${c2?bt(c2,f1):f1(s2.pj_per_op)}</td><td class="num small">${pcs(c2,f1)}</td><td class="num">${f2(w2)}</td><td class="num">${f2(w2/1024*1e3)} mW</td></tr>`+
  `<tr><td>${two("The 21 September ablation's integer loop, hart 0",`four adds and a branch, about half the one-hart addi loop's issue rate, 80 °C; <a href="${WL}">Why is the ET-SoC-1 low power?</a>`)}</td><td class="num">${f1(ab.pj_marginal)}</td><td class="num small">a2 only, two runs</td><td class="num">${f2(ab.over_idle_w)}</td><td class="num">${f2(ab.over_idle_w/1024*1e3)} mW</td></tr>`+
  `<tr><td>${two('1,024 minions stalled on one contended atomic (less than a spinning minion)',`the hot line: each waits about ${nf(Math.round(1024*at.contended.cycles_per_op/1000)*1000)} cycles for its turn`)}</td><td class="num">—</td><td class="num small">${HOT?pcs(HOT,f2)+'<br>both '+bt(HOT,f2):'a2 only, 22 September'}</td><td class="num">${f2(h2w)}</td><td class="num">${f2(h2w/1024*1e3)} mW</td></tr>`+
  `<tr><td>${two('For scale: every minion running a random-data fp32 matmul',`the activity term, section 3.2${AT.fp32_randn_8?`; ${f1(AT.fp32_randn_8)} mW per minion with 256 or 512 active, ${f1(AT.fp32_randn_24)} with 768`:''}`)}</td><td class="num">—</td><td class="num small">a2 only, two runs per point</td><td class="num">${f1(t.over_idle_w)}</td><td class="num">${f1(AT.fp32_randn||t.over_idle_w/1024*1e3)} mW</td></tr></tbody>`;
 const nop=cb('nop/zeros/h2'), fen=cb('fence/zeros/h2');
 if(nop&&fen) $('awaketext').innerHTML=
  `The addi loop is not the floor: it increments seven registers, so its operands change on every instruction. With both harts a <code>nop</code> costs ${f1(nop.mean)} pJ [${f1(nop.lo)}–${f1(nop.hi)}] and a <code>fence</code> ${f1(fen.mean)} [${f1(fen.lo)}–${f1(fen.hi)}] per instruction (section 3.1), so the awake core is about ${f1(fen.mean)}–${f1(nop.mean)} pJ per issue slot.`;
})();

/* ---------- 3. instructions ---------- */
(function(){
 const list=[['add','add',1],['xor','xor',1],['mul','mul',1],['fadd.s','fadd.s',1],['fmul.s','fmul.s',1],['fmadd.s','fmadd.s',1],
   ['fadd.ps','fadd.ps ×8',8],['fmul.ps','fmul.ps ×8',8],['fmadd.ps','fmadd.ps ×8',8],['fadd.pi','fadd.pi ×8',8],['fmul.pi','fmul.pi ×8',8],
   ['fexp.ps','fexp.ps ×8',8],['frcp.ps','frcp.ps ×8',8]];
 const q=(n,o)=>cb(`${n}/${o}/h2`), rate=n=>S2[`${n}/random/h2`]?S2[`${n}/random/h2`].ops_per_cycle_per_hart.mean:null;
 if(!q('add','random')){return;}
 const cols={zeros:'var(--c3)',const:'var(--c4)',random:'var(--c2)'}, OPS=[['zeros','zeros'],['const','one constant'],['random','random data']];
 CK.legend('instr-leg',OPS.map(([o,lab])=>({key:o,label:lab,mark:'box',color:cols[o]})));
 const mx=Math.max(...list.map(l=>q(l[0],'random').hi))*1.04;
 CK.frame('instr',{height:W=>W<600?320:360,minW:320,maxW:820,label:`Energy per instruction for ${list.length} scalar and vector instructions on zeros, one constant and random data`,draw:f=>{
  const narrow=f.W<600, L=40,R2=8,T=24,B=narrow?88:72, bw=(f.W-L-R2)/list.length, xg=i=>L+bw*i, y=CK.lin(0,mx,f.H-B,T);
  CK.axes(f,{x:CK.lin(0,list.length,L,f.W-R2),y,L,R:R2,T,B,xt:[],yl:'pJ per instruction, above idle'});
  const nav={}; OPS.forEach(([o])=>nav[o]=[]);
  list.forEach((l,i)=>{OPS.forEach(([o,lab],j)=>{const c=q(l[0],o); if(!c)return; const w=bw*0.26, xx=xg(i)+bw*(0.08+0.28*j);
    const gg=CK.el('g',{'data-series':o},f.svg);
    CK.el('rect',{x:xx,y:y(c.mean),width:w,height:f.H-B-y(c.mean),fill:cols[o]},gg); ebar(gg,xx+w/2,y(c.hi),y(c.lo));
    CK.tip(f,gg,`<b>${l[1]}</b>, ${lab}<br>${f1(c.mean)} pJ per instruction [${f1(c.lo)}–${f1(c.hi)}], n = ${c.n}${l[2]>1?' ('+f1(c.mean/l[2])+' per lane)':''}<br>${pcs(c,f1).replace('<br>',' · ')}`);
    nav[o].push(gg);});
   const lx=xg(i)+bw*0.5, ly=f.H-B+12, t=CK.txt(f.svg,lx,ly,l[1],'tick','end'); t.setAttribute('transform',`rotate(${narrow?-60:-40} ${lx} ${ly})`);});
  OPS.forEach(([o])=>CK.keynav(f,nav[o]));
 }});
 const c0=q('add','random'), nc=Object.keys(c0.per_card).length;
 $('instrcap').innerHTML=`Both harts of every minion issuing the instruction back to back; the multiply and the transcendentals are multi-cycle and issue at 0.4× (<code>frcp.ps</code>) down to an eighth (<code>mul</code>) of the one-cycle rate. Whiskers: the range over ${WORD[c0.n/nc]||c0.n/nc} passes on each of ${WORD[nc]||nc} cards.`;
 $('instrtab').innerHTML='<thead><tr><th>Instruction</th><th class="num">zeros</th><th class="num">constant</th><th class="num">random</th><th class="num">random / zeros</th><th class="num">per lane, random</th><th class="num">issue / hart / cycle</th></tr></thead><tbody>'+
  list.map(l=>{const z=q(l[0],'zeros'),c=q(l[0],'const'),r=q(l[0],'random'); if(!(z&&r))return '';
   return `<tr><td><code>${l[1]}</code></td><td class="num">${bt(z,f1)}</td><td class="num">${bt(c,f1)}</td><td class="num">${bt(r,f1)}</td><td class="num">${f2(r.mean/z.mean)}×</td><td class="num">${l[2]>1?f1(r.mean/l[2]):'—'}</td><td class="num">${rate(l[0])!=null?f2(rate(l[0])):'—'}</td></tr>`;}).join('')+'</tbody>';
 const ia=q('add','zeros'),fa=q('fadd.s','zeros'),vz=q('fadd.ps','zeros'),vr=q('fadd.ps','random'),fm=q('fmadd.ps','random'),ex=q('fexp.ps','random'),lg=q('flog.ps','random');
 const nop=cb('nop/zeros/h2'),fen=cb('fence/zeros/h2');
 const byp=['flwl.ps','fswl.ps'].map(n=>q(n,'random')).filter(Boolean).map(c=>c.mean), amo=['amoaddl.w','amoswapl.w','amoorl.w','amomaxl.w','amoaddl.d','amoaddg.w','amoaddg.d'].map(n=>q(n,'random')).filter(Boolean).map(c=>c.mean);
 const tz=D.tensor.rows.find(r=>r.config==='fp32_randn'), tb=TB.fp32_randn;
 const lane=[(fm.mean-nop.mean)/8,(fm.mean-fen.mean)/8], tref=tb?tb.mean:tz.pj_marginal;
 /* the issue share of the tensor unit's saving, per card: (issue / 8) / (fmadd.ps per lane - tensor unit), with the
    fence or the nop on zeros as the issue cost (the pooled bars mix two cards that differ) */
 const issueShare=tb&&tb.per_card?['aifoundry2','aifoundry3'].filter(h=>tb.per_card[h]&&fm.per_card[h]&&nop.per_card[h]&&fen.per_card[h]).map(h=>{
   const sv=fm.per_card[h].mean/8-tb.per_card[h].mean, sh=[fen,nop].map(c=>100*c.per_card[h].mean/8/sv); return `${f0(Math.min(...sh))}–${f0(Math.max(...sh))}%`;}):[];
 const dvs=['div','divu','rem','remu'].map(n=>q(n,'random')).filter(Boolean).map(c=>c.mean), rc=q('frcp.ps','random');
 $('instrtext').innerHTML=
  `<b>An integer add on zeros, ${f1(ia.mean)} pJ [${f1(ia.lo)}–${f1(ia.hi)}], is within noise of a <code>nop</code> (${f1(nop.mean)} pJ) on both cards</b>: on zeros it cannot be told apart from the awake core that issues it. `+
  `<b>A scalar float add costs ${f1(fa.mean/ia.mean)}× an integer add</b> even on zeros; the FPU does not gate on zero. `+
  `<b>An eight-lane vector op on zeros costs the same as the scalar one</b> (${f1(vz.mean)} against ${f1(fa.mean)} pJ, bars overlapping): lanes computing on zeros add nothing, and on random data the lanes cost ${f1(vr.mean/vz.mean)}× — the data dependence of the tensor unit, in the vector unit. `+
  `<b>Per lane, a random-data <code>fmadd.ps</code> is ${f1(fm.mean/8)} pJ [${f1(fm.lo/8)}–${f1(fm.hi/8)}]; the tensor unit does the same multiply-add for ${tb?f1(tb.mean)+' ['+f1(tb.lo)+'–'+f1(tb.hi)+']':f2(tz.pj_marginal)}.</b> `+
  `Take out the vector instruction's issue — ${f1(fen.mean)}–${f1(nop.mean)} pJ, what a fence or a nop costs (section 2) — and the lane is ${f1(Math.min(...lane))}–${f1(Math.max(...lane))} pJ, about ${f0(100*(Math.min(...lane)+Math.max(...lane))/2/tref-100)}% above the tensor unit. Read that way, of the ${f1(fm.mean/8-tref)} pJ per multiply-add the tensor unit saves, roughly half is instruction issue and the rest datapath`+
  (issueShare.length===2?` (${issueShare[0]} issue on aifoundry2, ${issueShare[1]} on aifoundry3, with the fence or the nop as the issue cost)`:'')+
  `; that is arithmetic on rows whose operands differ (uniform in [0.5, 2) here, normal for the tensor unit), not a measured decomposition. `+
  `<b>The transcendentals rank with the 64-bit divides as the dearest arithmetic</b>: <code>flog.ps</code> is ${f0(lg.mean)} pJ and <code>fexp.ps</code> ${f0(ex.mean)} for eight lanes, at a quarter of the rate, against ${f0(Math.min(...dvs))}–${f0(Math.max(...dvs))} pJ for the 64-bit divides and remainders; <code>frcp.ps</code> (${f0(rc.mean)}) is cheaper. Only loads and stores that bypass the L1 (${f0(Math.min(...byp))}–${f0(Math.max(...byp))} pJ) and atomics (${nf(Math.min(...amo))}–${nf(Math.max(...amo))} pJ) cost more.`;
 $('tensor').innerHTML='<thead><tr><th>Tensor unit, 1,024 minions</th><th class="num">pJ per MAC, marginal</th><th class="num">per card</th><th class="num">pJ per MAC, loaded (a2)</th><th class="num">W over idle (a2)</th><th class="num">MACs per second</th></tr></thead><tbody>'+
  D.tensor.rows.map(t=>{const b=TB[t.config]; return `<tr><td>${t.label}</td><td class="num">${b?bt(b,f3):'<b>'+f3(t.pj_marginal)+'</b>'}</td><td class="num small">${b?Object.keys(b.per_card).sort().map(h=>`a${h.slice(-1)} ${f3(b.per_card[h].mean)}`).join('<br>')+(b.cards>1?'':'<br>(a2 only)'):''}</td><td class="num">${f2(t.pj_loaded)}</td><td class="num">${f2(t.over_idle_w)}</td><td class="num">${sci(t.per_s)}</td></tr>`;}).join('')+
  '</tbody>';
 $('tensornote').innerHTML='One instruction per tile: fp32 16×16×16 = 4,096 multiply-adds (MACs), fp16 8,192, int8 16,384, on all 1,024 minions, launched at 80 °C on aifoundry2'+(D.cards&&D.cards.launch&&D.cards.launch.aifoundry3?' and '+f0(D.cards.launch.aifoundry3.T)+' °C on aifoundry3 (so the per-card fp32 values compare a warm card with a cool one)':'')+'. <b>Marginal</b>: board power above idle per MAC. <b>Loaded</b>: total board power, idle included, per MAC — what a MAC costs when it is the only thing running. Bars on the fp32 rows: the envelope of ±1 sd around the ablation’s two runs on aifoundry2 and the 22 September transfer’s runs on both cards; fp16 and int8 were run twice on aifoundry2, and their bar is ±1 sd of those two runs: '+
  (()=>{const hw=k=>TB[k]?100*(TB[k].hi-TB[k].lo)/2/TB[k].mean:null; const rn=['fp16_randn','int8_randn'].map(hw), z=hw('int8_zeros'), on=['fp16_ones','int8_ones'].map(hw);
     return `under ${f0(Math.ceil(Math.max(...rn)))}% on random data, ${f1(z)}% on int8 zeros, ${f0(Math.min(...on))}–${f0(Math.max(...on))}% on the ones patterns.`;})();
 const fl=D.tensor.flips;
 $('flips').textContent=Object.keys(fl.e_fJ).map(c=>`${f3(fl.e_fJ[c])} fJ per ${fl.classes[c]}`).join(', ');
})();

/* ---------- 3.1 every instruction: a beeswarm per class (em-v3) ---------- */
(function(){
 const all=[]; CLASSES.forEach((c,ci)=>c[1].forEach(n=>{if(CB[`${n}/random/h2`]&&CB[`${n}/zeros/h2`]&&SA[`${n}/random/h2`])all.push({n,ci});}));
 if(!all.length)return;
 $('trapped').textContent='fdiv.s, fsqrt.s, fdiv.ps, fsqrt.ps, frsq.ps, fsin.ps, fdiv.pi, fdivu.pi, frem.pi, fremu.pi, fcvt.l.s, fcvt.s.l, csrr cycle';
 const st={unit:'instr',card:'both',zeros:false,found:null};
 const nop=cb('nop/zeros/h2'), fen=cb('fence/zeros/h2');
 const div=a=>st.unit==='lane'&&LANES.has(a.n)?8:1;
 const val=(a,o)=>{const k=`${a.n}/${o}/h2`; if(st.card==='both')return CB[k].mean/div(a); const s=D.catalogue.cards[st.card].summary[k]; return s?s.pj_per_op.mean/div(a):null;};
 const barTxt=(a,o)=>{const k=`${a.n}/${o}/h2`, d=div(a); if(st.card==='both'){const c=CB[k]; return `${f1(c.mean/d)} pJ [${f1(c.lo/d)}–${f1(c.hi/d)}]`;}
   const s=D.catalogue.cards[st.card].summary[k]; return s?`${f1(s.pj_per_op.mean/d)} ± ${f2(s.pj_per_op.se/d)} pJ`:'—';};
 const tipHtml=a=>()=>{const k=`${a.n}/random/h2`, r2=SA[k], r3=SB[k], per=st.unit==='lane'&&LANES.has(a.n)?' per lane':'';
   return `<b>${a.n}</b> — ${CLASSES[a.ci][0]}<br>random: ${barTxt(a,'random')}${per}<br>zeros: ${barTxt(a,'zeros')}${per}; random / zeros ${f2(val(a,'random')/val(a,'zeros'))}×<br>`+
    `issue ${f3(r2.ops_per_cycle_per_hart.mean)} per hart per cycle<br>${CARDS[0]} ${f1(r2.pj_per_op.mean)} ± ${f2(r2.pj_per_op.se)}${r3?`, ${CARDS[1]} ${f1(r3.pj_per_op.mean)} ± ${f2(r3.pj_per_op.se)} pJ; ratio ${f3(r3.pj_per_op.mean/r2.pj_per_op.mean)}`:' pJ'}`;};
 const cardLabel=()=>st.card==='both'?'both cards (the mean over every pass)':st.card;
 let lay=null, nodes=[], overlay=null, fr=null;
 function layout(W){
  const key=[W,st.unit,st.card].join('|'); if(lay&&lay.key===key)return lay;
  const L=10,Rr=14,T=30,B=34, lo=st.unit==='lane'?1:3, x=CK.log(lo,2000,L,W-Rr), r=3.5, sep=2*r+1;
  let y0=T; const rows=[];
  CLASSES.forEach((c,ci)=>{const pts=all.filter(a=>a.ci===ci).map(a=>({a,x:x(Math.max(lo,val(a,'random')||lo))})).sort((p,q)=>p.x-q.x);
   if(!pts.length)return; const placed=[];
   pts.forEach(p=>{for(let k=0;k<200;k++){const o=(k%2?1:-1)*Math.ceil(k/2); if(placed.every(q=>(q.x-p.x)**2+(q.o-o)**2>=sep*sep)){p.o=o;break;}} if(p.o==null)p.o=0; placed.push(p);});
   const ext=Math.max(...placed.map(p=>Math.abs(p.o)));
   rows.push({ci,label:c[0],y:y0,cy:y0+17+ext+r+1,pts:placed}); y0+=17+2*(ext+r+1)+12;});
  lay={key,x,rows,H:y0+B,L,Rr,T,lo}; return lay;}
 const seg=(g,a,cy)=>{const xr=lay.x(Math.max(lay.lo,val(a,'random'))),xz=lay.x(Math.max(lay.lo,val(a,'zeros')));
  CK.el('line',{x1:xz,x2:xr,y1:cy,y2:cy,stroke:'var(--ink-2)','stroke-width':1.2},g); CK.el('circle',{cx:xz,cy,r:3.5,fill:'var(--surface)',stroke:'var(--c3)','stroke-width':1.8},g);};
 const showZero=(i)=>{if(!overlay)return; while(overlay.firstChild)overlay.removeChild(overlay.firstChild); if(i==null)return; const p=nodes[i]; seg(overlay,p.a,p.cy);};
 CK.seg('all-unit',{options:[['instr','per instruction'],['lane','per lane']],value:'instr',onChange:v=>{st.unit=v; fr.redraw(); cap();}});
 CK.seg('all-card',{options:[['both','both cards']].concat(CARDS.map(h=>[h,h])),value:'both',onChange:v=>{st.card=v; fr.redraw(); cap();}});
 const zb=document.createElement('button'); zb.type='button'; zb.textContent='show zeros for all'; zb.setAttribute('aria-pressed','false');
 zb.addEventListener('click',()=>{st.zeros=!st.zeros; zb.setAttribute('aria-pressed',String(st.zeros)); fr.redraw();});
 const zs=$('all-zeros'); zs.className='controls'; zs.style.margin='0'; zs.appendChild(zb);
 $('all-names').innerHTML=all.map(a=>`<option value="${a.n}">`).join('');
 const ro=CK.readout('all-readout');
 fr=CK.frame('allinstr',{height:W=>layout(W).H,label:'Energy per instruction, every instruction, by class',draw:f=>{
  const Ly=layout(f.W), x=Ly.x, svg=f.svg, top=Ly.T, bot=f.H-34;
  const ticks=(f.W<600?[1,3,10,30,100,300,1000]:[1,2,5,10,20,50,100,200,500,1000,2000]).filter(t=>t>=Ly.lo), xf=v=>CK.fmt.num(v);
  const ax=CK.el('g',{'aria-hidden':'true'},svg), fl=st.unit==='instr'&&nop&&fen, flab=fl?`awake core ${f1(fen.mean)}–${f1(nop.mean)} pJ`:'', fx=fl?x(nop.mean)+4:0, fw=flab.length*6.2;
  ticks.forEach(t=>{CK.el('line',{x1:x(t),x2:x(t),y1:top-6,y2:bot,class:'grid-line'},ax); CK.txt(ax,x(t),bot+16,xf(t),'tick','middle');
   if(!fl||x(t)+12<fx||x(t)-12>fx+fw)CK.txt(ax,x(t),top-10,xf(t),'tick','middle');});
  Ly.rows.slice(1).forEach(rw=>CK.el('line',{x1:Ly.L,x2:f.W-Ly.Rr,y1:rw.y-4,y2:rw.y-4,stroke:'var(--grid)','stroke-dasharray':'2 3'},ax));
  CK.txt(ax,(Ly.L+f.W-Ly.Rr)/2,f.H-4,st.unit==='lane'?'pJ per instruction, or per lane for the vector and transcendental units (log)':'pJ per instruction, above idle (log)','lab','middle');
  if(fl){const x0=x(fen.mean),x1=x(nop.mean); CK.el('rect',{x:x0,y:top-4,width:Math.max(2,x1-x0),height:bot-top+4,fill:'var(--grid)',opacity:0.8},ax);
   CK.txt(ax,fx,top-10,flab,'tick','start');}
  const layer=CK.el('g',{},svg); overlay=CK.el('g',{'aria-hidden':'true'},svg); nodes=[];
  Ly.rows.forEach(rw=>{CK.txt(layer,Ly.L,rw.y+13,rw.label,'lab','start');
   rw.pts.forEach(p=>{const cy=rw.cy+p.o; if(st.zeros)seg(layer,p.a,cy);
    const gg=mark(f,layer,'circle',{cx:p.x,cy,r:3.5,fill:'var(--c2)'},7,tipHtml(p.a));
    gg.addEventListener('focus',()=>{showZero(nodes.findIndex(q=>q.g===gg)); ro.set(tipHtml(p.a)());});
    gg.addEventListener('pointerenter',()=>showZero(nodes.findIndex(q=>q.g===gg)));
    gg.addEventListener('pointerleave',()=>showZero(st.found));
    gg.addEventListener('blur',()=>showZero(st.found));
    nodes.push({g:gg,a:p.a,cy,x:p.x,row:rw.ci});});});
  /* the dearest are the two global atomics, whose order is not resolved: label the pair, not one of them */
  const mx=nodes.reduce((a,b)=>val(a.a,'random')>val(b.a,'random')?a:b), mrow=Ly.rows.find(rw=>rw.ci===mx.row);
  const gl=nodes.filter(n=>/^amoaddg\./.test(n.a.n)).map(n=>val(n.a,'random')), gv=gl.length?gl.reduce((a,b)=>a+b,0)/gl.length:val(mx.a,'random');
  CK.txt(layer,f.W-Ly.Rr,mrow.y+13,gl.length===2?`dearest: the global atomics, ~${nf(Math.round(gv/10)*10)} pJ`:`dearest: ${mx.a.n}, ${nf(val(mx.a,'random'))} pJ`,'lab','end');
  CK.keynav(f,nodes.map(n=>n.g),{step:(k,K)=>{if(K!=='ArrowDown'&&K!=='ArrowUp')return null;
   const rs=[...new Set(nodes.map(n=>n.row))], ri=rs.indexOf(nodes[k].row)+(K==='ArrowDown'?1:-1); if(ri<0||ri>=rs.length)return k;
   let best=null; nodes.forEach((n,j)=>{if(n.row===rs[ri]&&(best==null||Math.abs(n.x-nodes[k].x)<Math.abs(nodes[best].x-nodes[k].x)))best=j;}); return best;}});
  if(st.found!=null){const j=nodes.findIndex(n=>n.a.n===st.foundName); st.found=j<0?null:j; showZero(st.found);}
 }});
 const inp=$('all-find');
 const find=()=>{const v=inp.value.trim().toLowerCase(), j=nodes.findIndex(n=>n.a.n.toLowerCase()===v);
  st.found=j<0?null:j; st.foundName=j<0?null:nodes[j].a.n; showZero(st.found); ro.set(j<0?(v?'No instruction by that name in the catalogue.':''):tipHtml(nodes[j].a)()+'<br><span class="small">Enter moves the focus to its dot.</span>'); return j;};
 inp.addEventListener('input',find);
 inp.addEventListener('keydown',ev=>{if(ev.key==='Enter'){const j=find(); if(j>=0){ev.preventDefault(); nodes[j].g.focus();}}});
 const relOf=S=>all.filter(a=>S[`${a.n}/random/h2`]).map(a=>S[`${a.n}/random/h2`].pj_per_op.se/S[`${a.n}/random/h2`].pj_per_op.mean).sort((a,b)=>a-b);
 const rel=relOf(SA), rel3=relOf(SB), pct=(r,q)=>(100*r[Math.floor(r.length*q)]).toFixed(1);
 const half=all.map(a=>CB[`${a.n}/random/h2`]).map(c=>(c.hi-c.lo)/2/c.mean).sort((a,b)=>a-b);
 function cap(){$('allcap').textContent=`${all.length} instructions, one dot each at its random-data energy on ${cardLabel()}${st.unit==='lane'?', per lane for the eight-lane units':''}, one row per class. The hollow ring and the line to it are the same instruction on zeros: for the dot in focus, or for all of them with the toggle. `+
  (st.unit==='instr'?`The shaded band is the awake core, what a fence or a nop costs with both harts (${f1(fen.mean)}–${f1(nop.mean)} pJ). `:'')+
  `Pass-to-pass standard error is ${(100*rel[rel.length>>1]).toFixed(1)}% in the median and ${(100*rel[Math.floor(rel.length*0.9)]).toFixed(1)}% at the 90th percentile on ${CARDS[0]}${rel3.length?` (${(100*rel3[rel3.length>>1]).toFixed(1)}% and ${pct(rel3,0.9)}% on ${CARDS[1]})`:''}; half the range over both cards' passes is ±${(100*half[half.length>>1]).toFixed(1)}% in the median and ±${(100*half[Math.floor(half.length*0.9)]).toFixed(1)}% at the 90th, about half of it the difference between the cards.`;}
 cap();
 const S=SA, gz=(n,o)=>S[`${n}/${o}/h2`], gz2=(n,o)=>SB[`${n}/${o}/h2`];
 $('alltab').innerHTML='<thead><tr><th>Instruction</th><th class="num">zeros pJ, both cards</th><th class="num">random pJ, both cards</th><th class="num">per lane</th><th class="num">random / zeros</th><th class="num">issue per hart per cycle</th><th class="num">'+CARDS[0]+' ± se</th><th class="num">'+(CARDS[1]||'card 2')+' ± se</th><th class="num">ratio</th></tr></thead><tbody>'+
  CLASSES.map(c=>`<tr><td colspan="9"><b>${c[0]}</b></td></tr>`+c[1].map(n=>{const r=gz(n,'random'),z=gz(n,'zeros'),r2=gz2(n,'random'),cr=cb(`${n}/random/h2`),cz=cb(`${n}/zeros/h2`); if(!(r&&z))return '';
   return `<tr><td><code>${n}</code></td><td class="num">${cz?bt(cz,f1):z.pj_per_op.mean.toFixed(1)}</td><td class="num">${cr?bt(cr,f1):'<b>'+r.pj_per_op.mean.toFixed(1)+'</b>'}</td><td class="num">${LANES.has(n)?((cr?cr.mean:r.pj_per_op.mean)/8).toFixed(1):'—'}</td><td class="num">${((cr?cr.mean:r.pj_per_op.mean)/(cz?cz.mean:z.pj_per_op.mean)).toFixed(2)}×</td><td class="num">${r.ops_per_cycle_per_hart.mean.toFixed(3)}</td><td class="num">${r.pj_per_op.mean.toFixed(1)} ± ${r.pj_per_op.se.toFixed(2)}</td><td class="num">${r2?r2.pj_per_op.mean.toFixed(1)+' ± '+r2.pj_per_op.se.toFixed(2):'—'}</td><td class="num">${r2?(r2.pj_per_op.mean/r.pj_per_op.mean).toFixed(3):'—'}</td></tr>`;}).join('')).join('')+'</tbody>';
 /* cheapest and dearest by the pooled mean over both cards, the page's convention */
 const pool=all.map(a=>({n:a.n,m:CB[`${a.n}/random/h2`].mean})).sort((a,b)=>a.m-b.m), cheapest=pool[0], dearest=pool[pool.length-1];
 const cc=D.catalogue.cross_card;
 const span=(ns,o)=>{const v=ns.map(n=>CB[`${n}/${o}/h2`]).filter(Boolean).map(c=>c.mean); return [Math.min(...v),Math.max(...v),v.length];};
 const one=CLASSES[0][1], z1=span(one,'zeros'), r1=span(one,'random');
 const rat=(a,b)=>CB[`${a}/random/h2`]&&CB[`${b}/random/h2`]?CB[`${a}/random/h2`].mean/CB[`${b}/random/h2`].mean:null;
 const dv=rat('divu','mulw'), ag=['amoaddg.w','amoaddg.d'].flatMap(a=>['amoaddl.w','amoaddl.d'].map(l=>rat(a,l))).filter(v=>v);
 /* the two cheapest (fence, nop) and the two dearest (the global atomics) are each a pair whose order is not resolved */
 const two=pool.slice(0,2), top=pool.slice(-2), topm=(top[0].m+top[1].m)/2;
 $('alltext').innerHTML=`The cheapest are <code>${two[0].n}</code> and <code>${two[1].n}</code> (${f1(two[0].m)}–${f1(two[1].m)} pJ on random data) and the dearest the global atomics <code>${top[0].n}</code> and <code>${top[1].n}</code> (about ${nf(Math.round(topm/10)*10)} pJ), a span of about ${f0(Math.round(topm/two[0].m/10)*10)}× (pooled over both cards); within each pair the order is not resolved. `+
  (cc?`Across ${cc.n} configurations ${CARDS[1]} is ${f3(cc.median)}× ${CARDS[0]} (10th to 90th percentile ${f3(cc.p10)} to ${f3(cc.p90)}), each at its own die temperature (section 8). `:'')+
  `Instructions that share a unit and a latency cost about the same on zeros — the ${z1[2]} one-cycle integer ops span ${f1(z1[0])}–${f1(z1[1])} pJ — but data and latency spread every class: on random data the same ${r1[2]} span ${f1(r1[0])}–${f1(r1[1])} pJ, a 64-bit divide costs ${f0(dv)}× a <code>mulw</code>, and a global <code>amoaddg</code> ${f0(Math.min(...ag))}× a local <code>amoaddl</code>.`;
})();

/* ---------- 4. where bytes should live: energy per byte against bandwidth (em-v2) ---------- */
(function(){
 const rg=RR.rings_pj_per_byte||{}, rr=RR.relay_pj_per_byte||{};
 const FAM={read:['reads','var(--c1)'],write:['writes','var(--c2)'],msg:['core to core (rings of section 5)','var(--c7)'],relay:['the relay (a read and a write)','var(--c3)']};
 const P=[], cat=(fam,k,sfx,sc,label,short)=>{if(!CB[`${k}/random${sfx}`])return; P.push({fam,label,short,key:k,
   e:o=>cb(`${k}/${CB[`${k}/${o}${sfx}`]?o:'random'}${sfx}`,sc), op:o=>CB[`${k}/${o}${sfx}`]?o:'random',
   gbs:o=>{const s=SA[`${k}/${CB[`${k}/${o}${sfx}`]?o:'random'}${sfx}`]; return s.bytes_per_s.mean>0?s.bytes_per_s.mean/1e9:s.ops_per_s.mean*32/1e9;}});};
 cat('read','flw.ps','/h2',1/32,'L1 hit, 32 B vector loads','L1 hits');
 cat('read','l1fill/stride32','',1,'own scratchpad, 32 B loads through the L1',null);
 cat('read','tload/scp','',1,'own scratchpad, tensor load','own scratchpad');
 [1,2,3,4,5,6,8].forEach(d=>cat('read',`wire/hop${d}`,'',1,`a scratchpad ${d} hop${d>1?'s':''} away, tensor load`,null));
 cat('read','dramrow/stride8K','',1,'L3, tensor load through the mesh','L3');
 cat('read','tload/dram','',1,'DRAM, tensor load','DRAM');
 cat('write','fsw.ps','/h2',1/32,'L1 hit, 32 B vector stores',null);
 cat('write','tstore/scp','',1,'own scratchpad, tensor store',null);
 cat('write','tstore/dram','',1,'DRAM, tensor store',null);
 cat('write','st_stream/dram','',1,'DRAM, stores through the L1','stores through the L1');
 D.comm.rows.filter(r=>!r.ring.endsWith('c4')&&rg[r.ring]).forEach(r=>{const m=MH[r.ring];
   P.push({fam:'msg',key:r.ring,label:`ring: ${r.ring}${m&&m.mean?` (${f1(m.mean)} mesh hops on average)`:''}, 1 KB messages`,short:null,e:()=>rg[r.ring],op:()=>'its own data',gbs:()=>r.gb_s});});
 [['dram','through DRAM'],['hop','to the next shire'],['scp','in its own scratchpad']].forEach(([m,t])=>{if(rr[m])P.push({fam:'relay',key:'relay-'+m,label:`the relay, intermediate ${t}`,short:m==='scp'?null:'relay '+t.replace('the ',''),e:()=>rr[m],op:()=>'one constant per slab',gbs:()=>rp[m].bytes_per_s/1e9});});
 const st={o:'random',X:10,on:Object.keys(FAM)};
 const LABEL_ORDER=['DRAM','own scratchpad','L1 hits','relay through DRAM','relay to next shire','stores through the L1','L3'], NARROW=LABEL_ORDER.slice(0,5);
 CK.seg('map-data',{label:'data',options:[['random','random'],['zeros','zeros']],value:'random',onChange:v=>{st.o=v; fr.redraw(); read();}});
 CK.range('map-watts',{label:'power over idle you can spend',stops:[1,2,3,5,7,10,15,20,30],value:10,fmt:v=>v+' W',onInput:v=>{st.X=v; fr.redraw(); read();}});
 CK.legend('map-legend',Object.keys(FAM).map(k=>({key:k,label:FAM[k][0],mark:'dot',color:FAM[k][1]})),{toggle:true,onChange:on=>{st.on=on; CK.showSeries(fr,on);}});
 const W_=(p,o)=>p.e(o).mean*p.gbs(o)/1000;
 const tipH=p=>()=>{const o=st.o, c=p.e(o), gb=p.gbs(o); return `<b>${p.label}</b>, ${p.op(o)}<br>${fs(c.mean)} pJ/B [${fs(c.lo)}–${fs(c.hi)}] at ${nf(gb)} GB/s<br>${f1(c.mean*gb/1000)} W over idle<br>${pcs(c,fs).replace('<br>',' · ')}`;};
 const fr=CK.frame('bytemap',{height:W=>W<600?440:Math.round(Math.min(480,Math.max(360,W*0.6))),label:'Energy per byte against aggregate bandwidth, every path',draw:f=>{
  const L=44,Rr=14,T=24,B=40, x=CK.log(10,40000,L,f.W-Rr), y=CK.log(0.3,500,f.H-B,T), o=st.o;
  CK.axes(f,{x,y,L,R:Rr,T,B,xl:'aggregate bandwidth, GB/s (log)',yl:'pJ per byte, above idle (log)'});
  const clipId='mapclip'; const cp=CK.el('clipPath',{id:clipId},CK.el('defs',{},f.svg)); CK.el('rect',{x:L,y:T,width:f.W-Rr-L,height:f.H-B-T},cp);
  const dg=CK.el('g',{'clip-path':`url(#${clipId})`,'aria-hidden':'true'},f.svg);
  const boxes=[], dlab=[];
  const diag=(w,cls,sw,strong)=>{const a=[10,w*1000/10],b=[40000,w*1000/40000]; CK.el('line',{x1:x(a[0]),y1:y(a[1]),x2:x(b[0]),y2:y(b[1]),stroke:cls,'stroke-width':sw},dg);
   /* label just inside where the line leaves the plot at the bottom or the right */
   const gb=Math.min(40000,w*1000/0.3), pj=w*1000/gb, lx=Math.min(x(gb),f.W-Rr)-3, ly=Math.min(f.H-B-4,Math.max(T+10,y(pj)-4)), tw=(w+' W').length*6.4+4;
   dlab.push([lx,ly,w+' W',strong]); boxes.push([lx-tw,ly-11,lx,ly+3]);};
  [1,3,10,30].forEach(w=>{if(w!==st.X)diag(w,'var(--axis)',1,false);});
  diag(st.X,'var(--ink)',1.6,true);
  dlab.forEach(d=>CK.txt(f.svg,d[0],d[1],d[2],d[3]?'lab-strong':'tick','end').classList.add('halo'));
  const layer=CK.el('g',{},f.svg), groups={}, labs=[];
  const hops=P.filter(p=>/^wire\//.test(p.key)); if(hops.length){const pts=hops.map(p=>[p.gbs(o),p.e(o).mean]);
   CK.el('path',{d:CK.path(pts,x,y),fill:'none',stroke:'var(--c1)','stroke-width':1,opacity:0.6,'data-series':'read'},layer);}
  P.forEach(p=>{const c=p.e(o), gb=p.gbs(o), cx=x(gb), cy=y(c.mean), col=FAM[p.fam][1];
   const gg=CK.el('g',{'data-series':p.fam},layer);
   CK.el('line',{x1:cx,x2:cx,y1:y(c.hi),y2:y(c.lo),stroke:col,'stroke-width':1.5},gg);
   const m=mark(f,gg,'circle',{cx,cy,r:4.5,fill:col,stroke:'var(--surface)','stroke-width':1.5},9,tipH(p));
   (groups[p.fam]=groups[p.fam]||[]).push([gb,m]); boxes.push([cx-4,cy-4,cx+4,cy+4]);
   if(p.short&&(!f.narrow||NARROW.includes(p.short)))labs.push({x:cx,y:cy,text:p.short,series:p.fam,rank:LABEL_ORDER.indexOf(p.short)});});
  const h1=hops[0]; if(h1&&!f.narrow)labs.push({x:x(h1.gbs(o)),y:y(h1.e(o).mean),text:'1–8 hops away',series:'read',rank:50});
  const rg1=P.find(p=>p.key==='xshire4'); if(rg1)labs.push({x:x(rg1.gbs()),y:y(rg1.e().mean),text:'rings between shires',series:'msg',rank:60});
  const rg0=P.find(p=>p.key==='pair'); if(rg0&&!f.narrow)labs.push({x:x(rg0.gbs()),y:y(rg0.e().mean),text:'pair',series:'msg',rank:70});
  placeLabels(layer,labs.sort((a,b)=>a.rank-b.rank),boxes,[L,T,f.W-Rr,f.H-B]);
  Object.keys(groups).forEach(k=>CK.keynav(f,groups[k].sort((a,b)=>a[0]-b[0]).map(z=>z[1])));
 }});
 CK.showSeries(fr,st.on);
 const KEYS=[['tload/dram','DRAM tensor loads'],['tload/scp','the own scratchpad'],['wire/hop6','a scratchpad 6 hops away'],['relay-hop','the relay to the next shire'],['flw.ps','L1 hits']];
 const bw=v=>v>=1000?f1(v/1000)+' TB/s':nf(v)+' GB/s';
 const ro=CK.readout('map-readout');
 function read(){const o=st.o;
  ro.set(`Within <b>${st.X} W</b> over idle, ${o==='zeros'?'on zeros':'on random data'}: `+KEYS.map(([k,l])=>{const p=P.find(q=>q.key===k); if(!p)return ''; const gb=p.gbs(o), cap=st.X*1000/p.e(o).mean;
   return cap>=gb?`${l} all of its ${bw(gb)}`:`${l} ${bw(cap)} of its ${bw(gb)}`;}).filter(Boolean).join('; ')+'.');}
 read();
 const pd=P.find(p=>p.key==='tload/dram'), ps=P.find(p=>p.key==='tload/scp'), prd=P.find(p=>p.key==='relay-dram'), prh=P.find(p=>p.key==='relay-hop');
 const rings=P.filter(p=>p.fam==='msg').map(p=>W_(p,'random'));
 $('mapcap').innerHTML=(pd&&ps?`<b>DRAM (${f0(pd.e('random').mean)} pJ/B at ${f0(pd.gbs('random'))} GB/s, ${f1(W_(pd,'random'))} W) and the shire's own scratchpad (${f1(ps.e('random').mean)} pJ/B at ${nf(ps.gbs('random'))} GB/s, ${f1(W_(ps,'random'))} W) sit on the same 10 W diagonal, ${f0(ps.gbs('random')/pd.gbs('random'))}× apart in bandwidth</b> (random data). `:'')+
  (prd&&prh?`The relay through DRAM (${f1(prd.e().mean)} pJ/B at ${f0(prd.gbs())} GB/s) and to the next shire (${f1(prh.e().mean)} pJ/B at ${nf(prh.gbs())} GB/s) both draw about ${f0((W_(prd)+W_(prh))/2)} W, and the second moves ${f0(prh.gbs()/prd.gbs())}× the bytes. `:'')+
  (rings.length?`The rings between cores draw ${f1(Math.min(...rings))}–${f1(Math.max(...rings))} W. `:'')+
  `Diagonals: constant power over idle, pJ/B × GB/s; the slider picks one. Whiskers: the range over every pass on both cards. The L1 rows' bandwidth is their instruction rate times 32 B; the relay counts each byte it reads and each it writes. Reads and writes switch between zeros and random data; the rings and the relay carry their own data. The numbers are in the tables of sections 4.1, 4.3 and 5.`;
})();

/* ---------- 4.1 / 4.2 memory tables ---------- */
(function(){
 const paths=[['flw.ps/zeros/h2','flw.ps/random/h2',1/32,'L1 hit, flw.ps','read'],['fsw.ps/zeros/h2','fsw.ps/random/h2',1/32,'L1 hit, fsw.ps','write'],
   ['tload/scp/zeros','tload/scp/random',1,'own scratchpad, tensor load','read'],['tstore/scp/zeros','tstore/scp/random',1,'own scratchpad, tensor store','write'],
   ['tload/dram/zeros','tload/dram/random',1,'DRAM, tensor load','read'],['tstore/dram/zeros','tstore/dram/random',1,'DRAM, tensor store','write'],['st_stream/dram/zeros','st_stream/dram/random',1,'DRAM, stores through the L1','write']];
 if(!cb(paths[0][1])){return;}
 $('memcap').textContent='Tensor loads skip the L1 (the L2 and L3 cache them when the working set fits); tensor stores skip the L1 and the L2; the L1 rows are hits in a 256 B buffer, and their GB/s is the instruction rate times 32 B; the last row is a plain vector store to DRAM through the L1.';
 $('memtab').innerHTML='<thead><tr><th>Path</th><th class="num">zeros pJ/B</th><th class="num">random pJ/B</th><th class="num">random / zeros</th><th class="num">GB/s</th><th class="num">per card, random</th></tr></thead><tbody>'+
  paths.map(p=>{const z=cb(p[0],p[2]),r=cb(p[1],p[2]); if(!(z&&r))return ''; const s2=S2[p[1]], bps=!s2?0:s2.bytes_per_s.mean>0?s2.bytes_per_s.mean:p[2]<1?s2.ops_per_s.mean/p[2]:0;
   return `<tr><td>${p[3]} <span class="small">(${p[4]})</span></td><td class="num">${bt(z,fs)}</td><td class="num">${bt(r,fs)}</td><td class="num">${f2(r.mean/z.mean)}×</td><td class="num">${bps?nf(bps/1e9):'—'}</td><td class="num small">${pcs(r,fs)}</td></tr>`;}).join('')+'</tbody>';
 const dl=cb('tload/dram/random'),sl=cb('tload/scp/random'),ds=cb('tstore/dram/random'),ss=cb('st_stream/dram/random'),dz=cb('tload/dram/zeros');
 const oS=offRail('st_stream/dram/random'), oT=offRail('tstore/dram/random');
 /* the DRAM write against the read, per card (the pooled 136 against 129 mixes two cards that differ) */
 const wr=['aifoundry2','aifoundry3'].filter(h=>ds.per_card[h]&&dl.per_card[h]).map(h=>f1(100*(ds.per_card[h].mean/dl.per_card[h].mean-1)));
 $('memtext').innerHTML=
  `<b>DRAM is ${f0(dl.mean/sl.mean)}× the shire's own scratchpad per byte read.</b> A DRAM write by tensor store costs about what a read costs, within 15% (${f0(ds.mean)} against ${f0(dl.mean)} pJ/B${wr.length===2?`; ${wr[0]}% more on aifoundry2, ${wr[1]}% on aifoundry3`:''}); `+
  `<b>the same bytes written through the L1 cost ${f1(ss.mean/ds.mean)}× more</b> and arrive at a third of the bandwidth, consistent with each store allocating its line, so that the line is read from DRAM before it is written back and the byte pays for a read and a write. `+
  (oS&&oT?`Off-rail it costs ${f0(oS)} pJ against a tensor store's ${f0(oT)} (<a href="${HUB}#the-unmetered-remainder-attributed">Limits of observability, §4.2</a>), and a tensor load plus a tensor store come to ${f0(dl.mean+ds.mean)} of its ${f0(ss.mean)} pJ/B. `:'')+
  `<b>Even DRAM is data-dependent</b>: zeros ${f0(dz.mean)} [${f0(dz.lo)}–${f0(dz.hi)}], random ${f0(dl.mean)} [${f0(dl.lo)}–${f0(dl.hi)}] pJ/B; the scratchpad doubles. A scratchpad write is twice a scratchpad read.`;
 const lv=RR.levels_pj_per_byte;
 if(lv&&lv.dram){
  const LV=[['l1','L1 hits','256 B per hart, 2,048 harts'],['l2','L2','256 KB per shire (L2 is 512 KB)'],['l3','L3','768 KB per shire, 24 MB in all (L3 is 32 MB)'],['dram','DRAM','256 MB in all'],['scp-local','own scratchpad','2 MB of the shire’s own L2 scratchpad'],['scp-remote','remote scratchpad',`2 MB of the scratchpad 16 shire IDs away (${MH.xshire16?f1(MH.xshire16.mean):'about 2'} mesh hops on average)`]];
  const l1c=cb('flw.ps/random/h2',1/32), gh=D.memory_reads.rows.map(r=>r.implied_ghz).filter(v=>v!=null);
  /* the level's L1 loop against the catalogue's L1 row, per card: the two cards differ (+56% and +31%) */
  const l1pc=l1c&&lv.l1?['aifoundry2','aifoundry3'].filter(h=>lv.l1.per_card[h]&&l1c.per_card[h]).map(h=>[f0(100*(lv.l1.per_card[h].mean/l1c.per_card[h].mean-1)),f2(l1c.per_card[h].mean)]):[];
  /* The two L1 loops: memhier.c's (8 flw.ps per loop iteration; minion-cycles per load from its 18 September row, B per cycle being
     clock-independent in the minion's domain, and the 23 September reruns reproduce it) and the catalogue's (enercat.c's RUN
     macro, 64 per iteration; both cards' issue rate). */
  const mh1=D.memory_reads.rows.find(r=>r.level==='l1'), cycMH=mh1&&mh1.implied_ghz?32/(mh1.gb_s/(mh1.implied_ghz*1024)):null,
   fl2=[SA,SB].map(S=>S['flw.ps/random/h2']).filter(Boolean), cycCat=fl2.length?1/(2*fl2.reduce((a,e)=>a+e.ops_per_cycle_per_hart.mean,0)/fl2.length):null,
   tbsCat=SA['flw.ps/random/h2']?SA['flw.ps/random/h2'].ops_per_s.mean*32/1e12:null;
  $('memold').innerHTML='<thead><tr><th>Level</th><th>Working set</th><th class="num">pJ/B</th><th class="num">per card</th></tr></thead><tbody>'+
   LV.map(r=>lv[r[0]]?`<tr><td>${r[1]}</td><td class="small">${r[2]}</td><td class="num">${bt(lv[r[0]],fs)}</td><td class="num small">${pcs(lv[r[0]],fs)}</td></tr>`:'').join('')+'</tbody>';
  $('memoldnote').innerHTML=`L1: both harts of every minion re-reading a private 256 B buffer with 32 B vector loads, in the memory-hierarchy probe's own loop over a buffer whose contents it does not set. `+
   `That loop (8 loads per loop iteration) issued a load every ${cycMH?f1(cycMH):'3'} minion-cycles where the catalogue's (64) issued one every ${cycCat?f1(cycCat):'1.4'}${tbsCat?` (${f1(tbsCat)} TB/s)`:''}, and it reads ${l1pc.length===2?`${l1pc[0][0]}% above the catalogue's L1 row of section 4.1 on aifoundry2 and ${l1pc[1][0]}% on aifoundry3 (${l1pc[0][1]} and ${l1pc[1][1]} pJ/B on random data)`:`${l1c&&lv.l1?f0(100*(lv.l1.mean/l1c.mean-1))+'%':'well'} above the catalogue's L1 row in section 4.1 (${l1c?f2(l1c.mean):'—'} pJ/B on random data)`}, which is the figure to use. `+
   `L2, L3, DRAM and the scratchpads: hart 0 of every minion streaming 1 KB tensor loads — which skip the L1 but are cached in the L2 and L3 — over a working set sized to each level. The probe does not set the memory's contents, so these rows are not directly comparable to the zeros and random columns of section 4.1: the own scratchpad sits between them, and the DRAM level is within noise of the random-data row. `+
   `On L1, L2 and the own scratchpad the two cards differ beyond their pass-to-pass error (aifoundry3 is lower on L1 and L2, higher on its own scratchpad), and on L1 and the own scratchpad not by the 0.95 of section 8, so for those rows use the per-card column; contents left in the unset buffers, which can differ by card, are as likely a cause as the card. `+
   `${(w=>w[0].toUpperCase()+w.slice(1))(String(WORD[RR.passes.levels/2]||RR.passes.levels/2))} passes on each card at 600 MHz, pinned there on aifoundry3 and held there on aifoundry2 by a warm die (n = ${RR.passes.levels}). The 18 September run of the same experiment (one run on aifoundry2, in <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy">Memory hierarchy</a>) had the governor free and its clock averaged ${gh.length?f2(Math.min(...gh))+'–'+f2(Math.max(...gh)):'0.6–0.7'} GHz across the levels; it is superseded.`;
 }
})();

/* ---------- 4.3 finer grain: wires, lines, rows, neighbourhoods ---------- */
(function(){
 const C=D.catalogue, S=SA;
 const Wf=C.cards[CARDS[0]].wire, Wf2=CARDS[1]&&C.cards[CARDS[1]].wire;
 if(Wf&&Wf.random&&Wf.zeros){
  const st={upto:8}, fitOf=(wf,upto)=>lfit(wf.points.filter(p=>p.hops>=1&&p.hops<=upto).map(p=>[p.hops,p.pj_per_byte]));
  const mxh=Math.max(...Wf.random.points.map(p=>p.hops)), shr=d=>(Wf.random.points.find(p=>p.hops===d)||{}).shires, full=Wf.random.points.filter(p=>p.shires===32).map(p=>p.hops);
  CK.seg('wire-fit',{label:'straight-line fit',options:[['8','over 1–'+mxh+' hops'],['6','over 1–6 hops']],value:'8',onChange:v=>{st.upto=+v; fw.redraw(); wread();}});
  CK.legend('wire-legend',[{key:'z',label:'zeros',mark:'dot',color:'var(--c3)'},{key:'r',label:'random data',mark:'dot',color:'var(--c2)'},{key:'h',label:CARDS[1]+' (hollow)',mark:'ring',color:'var(--ink-2)'},{key:'f',label:'fit, '+CARDS[0],mark:'dash',color:'var(--ink-2)'}]);
  const mxy=Math.max(...Wf.random.points.map(p=>(CB[`wire/hop${p.hops}/random`]||{hi:p.pj_per_byte}).hi))*1.08;
  const fw=CK.frame('wire',{height:W=>W<600?270:320,label:'Energy per byte against mesh distance',draw:f=>{
   const L=40,Rr=12,T=24,B=40, x=CK.lin(-0.4,mxh+0.5,L,f.W-Rr), y=CK.lin(0,mxy,f.H-B,T);
   CK.axes(f,{x,y,L,R:Rr,T,B,xt:[0,1,2,3,4,5,6,7,8].filter(v=>v<=mxh),xl:f.narrow?'mesh hops to the scratchpad read (0: its own)':'hops across the mesh to the scratchpad read (0: the shire’s own)',yl:'pJ per byte'});
   const dx=f.narrow?3:4, groups=[];
   [['zeros','var(--c3)'],['random','var(--c2)']].forEach(([o,col])=>{const wf=Wf[o], ft=fitOf(wf,st.upto);
    CK.el('line',{x1:x(0),x2:x(mxh),y1:y(ft.a),y2:y(ft.a+ft.b*mxh),stroke:col,'stroke-width':1.5,'stroke-dasharray':'5 4'},f.svg);
    const nodes=[];
    if(wf.local_pj_per_byte!=null){const l2=Wf2&&Wf2[o]&&Wf2[o].local_pj_per_byte;
     nodes.push(mark(f,f.svg,'circle',{cx:x(0)-dx/2,cy:y(wf.local_pj_per_byte),r:4,fill:col},8,`the shire's own scratchpad, ${o}: <b>${f2(wf.local_pj_per_byte)} pJ/B</b> on ${CARDS[0]}${l2!=null?`, ${f2(l2)} on ${CARDS[1]}`:''}`));}
    wf.points.forEach(p=>{const c=CB[`wire/hop${p.hops}/${o}`], p3=Wf2&&Wf2[o]&&Wf2[o].points.find(q=>q.hops===p.hops);
     if(c)CK.el('line',{x1:x(p.hops),x2:x(p.hops),y1:y(c.hi),y2:y(c.lo),stroke:col,'stroke-width':1.5},f.svg);
     if(p3)CK.el('circle',{cx:x(p.hops)+dx,cy:y(p3.pj_per_byte),r:3.5,fill:'none',stroke:col,'stroke-width':1.5},f.svg);
     nodes.push(mark(f,f.svg,'circle',{cx:x(p.hops)-dx/2,cy:y(p.pj_per_byte),r:4,fill:col},9,`${p.hops} hop${p.hops>1?'s':''}, ${o}: <b>${f2(p.pj_per_byte)} ± ${f2(p.se)} pJ/B</b> on ${CARDS[0]}${p3?`, ${f2(p3.pj_per_byte)} ± ${f2(p3.se)} on ${CARDS[1]}`:''}${c?`<br>both cards: ${f2(c.mean)} [${f2(c.lo)}–${f2(c.hi)}], n = ${c.n}`:''}<br>${p.shires} shires reading`));});
    groups.push(nodes);});
   groups.forEach(n=>CK.keynav(f,n));
  }});
  const ro=CK.readout('wire-readout');
  function wread(){const u=st.upto, s=(wf,o)=>wf&&wf[o]?fitOf(wf[o],u):null;
   ro.set(`Fit over 1–${u===8?mxh:6} hops: <b>random ${f2(s(Wf,'random').b)}</b> (${CARDS[0]})${Wf2?` and ${f2(s(Wf2,'random').b)} (${CARDS[1]})`:''} pJ/B per hop, intercept ${f2(s(Wf,'random').a)}${Wf2?` and ${f2(s(Wf2,'random').a)}`:''}; <b>zeros ${f2(s(Wf,'zeros').b)}</b>${Wf2?` and ${f2(s(Wf2,'zeros').b)}`:''} per hop.`);}
  wread();
  $('wirecap').textContent=`1 KB tensor loads from a scratchpad exactly d hops away, all 32 shires reading up to ${Math.max(...full)} hops (${shr(6)} at 6 hops, ${shr(8)} at 8, so the 8-hop point has half the traffic), at most two readers per target; d = 0 is the shire's own scratchpad. Filled: ${CARDS[0]}; whiskers: the range over both cards' passes. Dashed: the straight-line fit over the hops chosen above.`;
  const dz=Wf.zeros.slope_pj_per_byte_per_hop, dr=Wf.random.slope_pj_per_byte_per_hop;
  const dz2=Wf2&&Wf2.zeros?Wf2.zeros.slope_pj_per_byte_per_hop:null, dr2=Wf2&&Wf2.random?Wf2.random.slope_pj_per_byte_per_hop:null;
  const s6=wf=>wf?fitOf(wf,6).b:null, r6=s6(Wf.random), z6=s6(Wf.zeros), r6b=Wf2?s6(Wf2.random):null, z6b=Wf2?s6(Wf2.zeros):null;
  const z8=[dz,dz2].filter(v=>v!=null), z6s=[z6,z6b].filter(v=>v!=null), zall=z8.concat(z6s);
  $('wiretext').innerHTML=`<b>One mesh hop costs about 2 pJ per byte on random data</b> (${f2(dr)} on ${CARDS[0]}${dr2!=null?` and ${f2(dr2)} on ${CARDS[1]}`:''} fitted over 1–${mxh} hops; ${f2(r6)}${r6b!=null?` and ${f2(r6b)}`:''} over 1–6, leaving out d = ${mxh}, which only ${shr(mxh)} shires reach and which sits level with d = 6) `+
   `<b>and ${f1(Math.min(...zall))}–${f1(Math.max(...zall))} on zeros</b> (${f2(Math.min(...z8))}–${f2(Math.max(...z8))} over 1–${mxh} hops, ${f2(Math.min(...z6s))}–${f2(Math.max(...z6s))} over 1–6). `+
   `Leaving the shire costs more than any hop: the intercept of the 1–${mxh}-hop fit is ${f2(Wf.random.intercept_pj_per_byte)} pJ/B on random data against ${f2(Wf.random.local_pj_per_byte||0)} for the shire's own scratchpad. `+
   `For wires, use <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm">Heat per millimetre</a>: 2.17 pJ/B per hop on board power, split into bits that differ between flits and ones carried.`;
 }
 /* ---- lines ---- */
 const fz=S['l1fill/stride32/zeros'],fr=S['l1fill/stride32/random'],gz=S['l1fill/stride64/zeros'],gr=S['l1fill/stride64/random'];
 if(fz&&fr&&gz&&gr){
  $('linetab').innerHTML='<thead><tr><th>32 B loads through the L1 from the shire’s scratchpad</th><th class="num">fills per load</th><th class="num">zeros pJ per load</th><th class="num">random pJ per load</th></tr></thead><tbody>'+
   [['32','0.5','l1fill/stride32'],['64','1','l1fill/stride64'],['128','1','l1fill/stride128']].map(r=>{const z=cb(r[2]+'/zeros',32),x=cb(r[2]+'/random',32);return z&&x?`<tr><td>stride ${r[0]} B</td><td class="num">${r[1]}</td><td class="num">${bt(z,f1)}</td><td class="num">${bt(x,f1)}</td></tr>`:'';}).join('')+
   '<tr><td colspan="4"><b>64 B tensor loads from the scratchpad, by stride</b></td></tr>'+
   ['64','128','256'].map(st=>{const z=cb(`scpline/stride${st}/zeros`,64),r=cb(`scpline/stride${st}/random`,64),rs=S[`scpline/stride${st}/random`]; return z&&r?`<tr><td>stride ${st} B (${st==='64'?'cycles the banks':st==='128'?'alternates two banks':'the same bank every time'})</td><td class="num">—</td><td class="num">${bt(z,f1)} per 64 B</td><td class="num">${bt(r,f1)} per 64 B, ${nf(rs.bytes_per_s.mean/1e9)} GB/s</td></tr>`:'';}).join('')+'</tbody>';
  const c32z=cb('l1fill/stride32/zeros',32),c64z=cb('l1fill/stride64/zeros',32),c32r=cb('l1fill/stride32/random',32),c64r=cb('l1fill/stride64/random',32);
  const fillz=2*(c64z.mean-c32z.mean), fillr=2*(c64r.mean-c32r.mean);
  const per=h=>2*((c64r.per_card[h]||{mean:0}).mean-(c32r.per_card[h]||{mean:0}).mean);
  const tlz=cb('tload/scp/zeros'), tlr=cb('tload/scp/random');
  /* the fill against a tensor load, per byte, per card and operand set: the pooled 75% hides 71-86% and an aifoundry2 interval that reaches 1 */
  const c32zr=[c32z,c32r], c64zr=[c64z,c64r], tlzr=[tlz,tlr];
  const frs=['aifoundry2','aifoundry3'].flatMap(h=>[0,1].filter(i=>c64zr[i].per_card[h]&&c32zr[i].per_card[h]&&tlzr[i].per_card[h]).map(i=>2*(c64zr[i].per_card[h].mean-c32zr[i].per_card[h].mean)/64/tlzr[i].per_card[h].mean));
  const fr5=frs.length?[Math.round(20*Math.min(...frs))*5,Math.round(20*Math.max(...frs))*5]:[75,75];
  const bwOf=st=>S[`scpline/stride${st}/random`]?S[`scpline/stride${st}/random`].bytes_per_s.mean/1e9:null, bw64=bwOf(64), bw256=bwOf(256);
  $('linetext').innerHTML=`Twice the difference between the stride-64 and stride-32 rows is what filling one 64 B line from the scratchpad into the L1 costs: <b>${fillz.toFixed(0)} pJ on zeros, ${fillr.toFixed(0)} pJ on random data</b> (${Object.keys(c64r.per_card).sort().map(h=>'a'+h.slice(-1)+' '+per(h).toFixed(0)).join(', ')} on random data) — ${f1(fillz/64)} and ${f1(fillr/64)} pJ per byte of line, roughly ${fr5[0]}–${fr5[1]}% of the ${f1(tlz.mean)} and ${f1(tlr.mean)} pJ/B a tensor load pays for the same bytes from the same scratchpad on the two cards (on aifoundry2 not separable from equal). What random data adds over zeros is about ${(fillr-fillz).toFixed(0)} pJ for the fill's 512 bits, ${((fillr-fillz)*1000/512).toFixed(0)} fJ per bit on the path from the shire cache into the L1.`+
   (bw64&&bw256?` The 64 B tensor loads by stride show the banks: coming back to the same bank every time halves the bandwidth (${nf(bw256)} against ${nf(bw64)} GB/s, on both cards), but what it does to the energy per byte cannot be told apart from the other strides'.`:'');
 }
 /* ---- DRAM rows ---- */
 const rz2=n=>S[`dramrow2/${n}/zeros`], rr2=n=>S[`dramrow2/${n}/random`];
 if(rz2('seq')&&rz2('rowmiss')){
  const PAT=[['seq','sequential: next bank, 32 columns per row visit'],['rowhit','same bank and row, next column, every access'],['rowmiss','a new row on every visit to a bank']];
  $('rowtab').innerHTML='<thead><tr><th>1 KB tensor loads from DRAM, 32 harts with 64 MB each</th><th class="num">zeros pJ/B</th><th class="num">random pJ/B</th><th class="num">GB/s</th></tr></thead><tbody>'+
   PAT.map(r=>{const z=rz2(r[0]),x=rr2(r[0]),cz=cb(`dramrow2/${r[0]}/zeros`),cx=cb(`dramrow2/${r[0]}/random`);return z&&x?`<tr><td>${r[1]}</td><td class="num">${cz?bt(cz,f1):z.pj_per_byte.mean.toFixed(1)+' ± '+z.pj_per_byte.se.toFixed(1)}</td><td class="num">${cx?bt(cx,f1):x.pj_per_byte.mean.toFixed(1)+' ± '+x.pj_per_byte.se.toFixed(1)}</td><td class="num">${(x.bytes_per_s.mean/1e9).toFixed(1)}</td></tr>`:'';}).join('')+
   `<tr><td colspan="4" class="small">${cb('dramrow2/seq/random')&&cb('dramrow2/seq/random').n>3?'Mean and range over three passes on each of two cards.':'Mean and range over three passes on aifoundry2.'}</td></tr></tbody>`;
  /* how often each of the 32 harts comes back to its row: one 1 KB access per visit, at the aggregate rate / 32, 600 MHz */
  const gbs=PAT.flatMap(r=>['zeros','random'].map(o=>S[`dramrow2/${r[0]}/${o}`].bytes_per_s.mean)), cyc=gbs.map(v=>1024*32/v*600e6);
  const prem=o=>PAT.map(r=>100*(cb(`dramrow2/${r[0]}/${o}`).mean/cb(`tload/dram/${o}`).mean-1)), pr=prem('random'), pz=prem('zeros');
  const dlg=S['tload/dram/random'].bytes_per_s.mean/1e9, r100=v=>nf(Math.round(v/100)*100);
  const l3=S['dramrow/stride8K/random'], l3z=S['dramrow/stride8K/zeros'], l3b=SB['dramrow/stride8K/random'], l3bz=SB['dramrow/stride8K/zeros'];
  /* 3.87 µs and 2,325 cycles: the refresh interval the memory-anatomy page reads from the controller (PLAN2 D21) */
  $('rowtext').innerHTML=`<b>The row pattern does not change the energy per byte</b>: row hits, row misses and the streaming case agree within their pass-to-pass error on both operand sets. `+
   `On aifoundry2 the controller runs an open-page policy: a row stays open until a refresh (every 3.87 µs) or an access to another row of its bank closes it (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#how-long-a-row-stays-open">Anatomy of a memory access</a>). `+
   `Each hart here comes back to its row only every ${r100(Math.min(...cyc))}–${r100(Math.max(...cyc))} cycles or so (32 harts at ${f0(Math.min(...gbs)/1e9)}–${f0(Math.max(...gbs)/1e9)} GB/s), with 31 other streams in between, and a refresh falls every 2,325 cycles. `+
   `So either every pattern paid an activation, or an activation is small next to the transfer (one of about 30 pJ/B on zeros, or 50 on random data, would have shown); for a programmer it makes no difference. `+
   `These 32-hart loads cost ${f0(Math.min(...pr))}–${f0(Math.max(...pr))}% more per byte than section 4.1's tensor loads at ${f0(dlg)} GB/s (${f0(Math.min(...pz))}–${f0(Math.max(...pz))}% more on zeros): use them to compare patterns, and section 4.1 to price DRAM.`+
   (l3&&l3z?` An earlier version of this experiment with all 1,024 minions and only 32 KB touched per hart fitted in the L3 and measured that instead: <b>${l3z.pj_per_byte.mean.toFixed(1)} pJ/B on zeros and ${l3.pj_per_byte.mean.toFixed(1)} on random data on ${CARDS[0]}</b>${l3b&&l3bz?`, <b>${l3bz.pj_per_byte.mean.toFixed(1)} and ${l3b.pj_per_byte.mean.toFixed(1)} on ${CARDS[1]}</b>, at ${nf(l3.bytes_per_s.mean/1e9)} GB/s on both`:` at ${nf(l3.bytes_per_s.mean/1e9)} GB/s`}, the L3 read by tensor loads through the mesh.`:'');
 }
 const nb=[0,1,2,3].map(k=>S[`neigh/${k}/random`]); if(nb.every(v=>v)){
  $('neightab').innerHTML='<thead><tr><th>Neighbourhood reading the shire’s own scratchpad (random data)</th><th class="num">pJ/B, both cards</th><th class="num">per card</th><th class="num">GB/s</th></tr></thead><tbody>'+
   nb.map((v,k)=>{const c=cb(`neigh/${k}/random`);return `<tr><td>${k}: minions ${8*k}–${8*k+7}</td><td class="num">${c?bt(c,f2):v.pj_per_byte.mean.toFixed(2)}</td><td class="num small">${c?pcs(c,f2):v.pj_per_byte.se.toFixed(2)}</td><td class="num">${nf(v.bytes_per_s.mean/1e9)}</td></tr>`;}).join('')+'</tbody>';
 }
})();

/* ---------- 4.4 where the current flows, by meter ---------- */
(function(){
 const S=SA;
 const groups=[['scalar integer',['add','sub','and','or','xor','sll','srl','sra','slt','sltu','addi','andi','ori','xori','slli','srli'].map(n=>`${n}/random/h2`)],
  ['scalar multiply',['mul','mulh','mulhu','mulhsu'].map(n=>`${n}/random/h2`)],['scalar float',['fadd.s','fsub.s','fmul.s','fmadd.s','fmsub.s'].map(n=>`${n}/random/h2`)],
  ['vector float',['fadd.ps','fsub.ps','fmul.ps','fmadd.ps','fmsub.ps'].map(n=>`${n}/random/h2`)],['vector integer',['fadd.pi','fsub.pi','fmul.pi','fand.pi','fxor.pi'].map(n=>`${n}/random/h2`)],
  ['transcendental',['fexp.ps','flog.ps','frcp.ps'].map(n=>`${n}/random/h2`)],['L1 hits',['lw','ld','sw','sd','flw.ps','fsw.ps'].map(n=>`${n}/random/h2`)],
  ['L1-bypass to the L2',['flwl.ps','fswl.ps'].map(n=>`${n}/random/h2`)],['atomics, local L2',['amoaddl.w/random/h2','amoaddl.d/random/h2']],['atomics, home L3',['amoaddg.w/random/h2','amoaddg.d/random/h2']],
  ['own scratchpad, tensor load',['tload/scp/random']],['own scratchpad, tensor store',['tstore/scp/random']],['scratchpad 1 hop away',['wire/hop1/random']],['scratchpad 3 hops away',['wire/hop3/random']],['scratchpad 6 hops away',['wire/hop6/random']],
  ['L3, tensor load',['dramrow/stride8K/random']],['DRAM, tensor load',['tload/dram/random']],['DRAM, tensor store',['tstore/dram/random']],['DRAM, stores through the L1',['st_stream/dram/random']]];
 const PARTS=[['minions','var(--c1)'],['SRAM','var(--c3)'],['mesh','var(--c2)'],['no sensor (regulators, PHYs)','var(--ref)']];
 const rows=[]; groups.forEach(gp=>{const rs=gp[1].map(k=>S[k]).filter(Boolean); if(!rs.length)return;
  const av=fn=>rs.reduce((a,r)=>a+fn(r),0)/rs.length, o=av(r=>r.over_idle_w.mean), m=av(r=>r.rails_over_w.minion_w.mean), sr=av(r=>r.rails_over_w.sram_w.mean), n=av(r=>r.rails_over_w.noc_w.mean);
  rows.push({label:gp[0],o,parts:[m,sr,n,o-m-sr-n]});});
 if(!rows.length)return;
 CK.legend('rails-legend',PARTS.map((p,i)=>({key:'p'+i,label:p[0],mark:'box',color:p[1]})));
 CK.frame('railsplit',{height:W=>(W<480?rows.length*42:rows.length*26)+30,label:'Each class of operation split across the metered rails',draw:f=>{
  const stack=f.W<480, L=stack?0:Math.min(220,Math.round(0.34*f.W)), Rr=8, pitch=stack?42:26, bh=stack?18:20, T=4;
  const x=CK.lin(0,1,L,f.W-Rr), nodes=[];
  rows.forEach((r,i)=>{const y0=T+i*pitch, by=stack?y0+18:y0+2; let acc=0;
   CK.txt(f.svg,stack?0:L-8,stack?y0+13:y0+16,r.label,'lab',stack?'start':'end');
   const pos=r.parts.reduce((a,v)=>a+Math.max(0,v),0);
   r.parts.forEach((v,j)=>{const fr=Math.max(0,v)/pos, w=Math.max(0,x(acc+fr)-x(acc)-(j<3?2:0));
    if(w>0.5)nodes.push(mark(f,f.svg,'rect',{x:x(acc),y:by,width:w,height:bh,fill:PARTS[j][1],rx:1},0,`<b>${r.label}</b>: ${f2(r.o)} W over idle<br>${PARTS[j][0]}: ${f2(v)} W (${Math.round(100*v/r.o)}%)`)); acc+=fr;});});
  const yb=T+rows.length*pitch+8; [0,0.25,0.5,0.75,1].forEach(t=>{CK.el('line',{x1:x(t),x2:x(t),y1:yb-6,y2:yb-2,class:'ck-axis'},f.svg); CK.txt(f.svg,x(t),yb+10,Math.round(100*t)+'%','tick',t===0?'start':t===1?'end':'middle');});
  CK.keynav(f,nodes);
 }});
 const RF=D.catalogue.rail_filter, taus=RF?Object.values(RF).map(v=>v.tau_s):[];
 $('railscap').textContent=`Random data, aifoundry2, mean of three passes. The split of each burst's power over idle across the three rails the PMIC meters, read from the end of the burst and corrected for the lag of the PMIC's own running average (a time constant of ${RF&&RF.aifoundry2&&RF.aifoundry3?f2(RF.aifoundry2.tau_s)+' s on aifoundry2 and '+f2(RF.aifoundry3.tau_s)+' s on aifoundry3':taus.length?f1(Math.min(...taus))+'–'+f1(Math.max(...taus))+' s on the two cards':'about a second'}); the remainder has no sensor.`;
 const wire6=rows.find(r=>r.label==='scratchpad 6 hops away'), si=rows.find(r=>r.label==='scalar integer'), dr=rows.find(r=>r.label==='DRAM, tensor load');
 const U=D.unmetered, dd=U&&U.ddr_droop, dl=cb('tload/dram/random'), mn=['aifoundry2','aifoundry3'].filter(h=>U&&U[h]).map(h=>100*U[h].coef.minion);
 if(wire6&&si) $('railstext').innerHTML=`<p><b>An instruction’s energy is the core’s</b>: ${Math.round(100*si.parts[0]/si.o)}% of a scalar integer burst is on the minion rail, almost nothing on the SRAM or the mesh, and the rest is consistent with what the regulators lose delivering it. <b>A byte fetched across the mesh is mostly wire</b>: six hops away, ${Math.round(100*wire6.parts[2]/wire6.o)}% of the energy is on the mesh rail and ${Math.round(100*wire6.parts[1]/wire6.o)}% on the SRAM that holds it, with the minions that asked for it at most about a sixth (${Math.round(100*wire6.parts[0]/wire6.o)}% measured, not resolved from zero).`+
  (dr?` <b>A DRAM byte is mostly off-chip</b>: ${Math.round(100*dr.parts[3]/dr.o)}% of its energy is on no metered rail.`+(U&&U.aifoundry2&&dl?` Fitted over this whole catalogue in <a href="${HUB}#the-unmetered-remainder-attributed">Limits of observability, §4.2–4.3</a>, ${U.aifoundry3?`${f0(Math.min(U.aifoundry2.coef.dram_pj_per_byte,U.aifoundry3.coef.dram_pj_per_byte))}–${f0(Math.max(U.aifoundry2.coef.dram_pj_per_byte,U.aifoundry3.coef.dram_pj_per_byte))}`:f0(U.aifoundry2.coef.dram_pj_per_byte)} of its ${f0(dl.mean)} pJ/B sit in the DDR PHY, the I/O rail and the DRAM chips (the fitted coefficient on the two cards), and the rest of the unmetered share is consistent with the regulators' delivery loss (${mn.length>1?`${f0(mn[0])}% of the minion rail's watts on aifoundry2 and ${f0(mn[1])}% on aifoundry3`:`${f0(mn[0])}% of the minion rail's watts`}, as far as the rails' meters can be trusted) plus the fit's residual${dd?`; the same page reads DRAM power from the DDR rail's voltage droop, 1 mV for about ${f1(1/dd.mv_per_dram_offrail_w)} W`:''}.`:''):'')+'</p>';
})();

/* ---------- 5. comm ---------- */
(function(){
 const rg=RR.rings_pj_per_byte||{}, rr=RR.relay_pj_per_byte||{};
 const val=(r)=>rg[r.ring]?bt(rg[r.ring],f2):`<b>${f2(r.pj_per_byte)}</b> ± ${f2(r.pj_spread)}`;
 const hopk=k=>{const m=MH[k]; return !m?'—':m.mean?`${f1(m.mean)} <span class="small">(${m.min}–${m.max})</span>`:'0';};
 const name=k=>{const x=k.match(/^xshire(\d+)(-c4)?$/); if(x)return `Shires ${x[1]} ID${x[1]==='1'?'':'s'} apart${x[2]?', 128 B':''}`;
   return {pair:'Pair',neigh:'Neighbourhood',shire:'Shire','shire-c4':'Shire, 128 B'}[k]||k;};
 const esc=s=>String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
 /* in-shire rings first, then the 1 KB rings between shires by mean mesh distance, then the 128 B rows */
 const small=k=>k.endsWith('c4'), dist=k=>(MH[k]||{mean:0}).mean;
 const rows=[...D.comm.rows].sort((a,b)=>(small(a.ring)-small(b.ring))||(dist(a.ring)-dist(b.ring)));
 $('comm').innerHTML='<thead><tr><th>Ring, 1 KB messages unless said</th><th class="what">What moves</th><th class="num">Mesh hops, mean (range)</th><th class="num">pJ/B</th><th class="num">per card</th><th class="num">GB/s aggregate</th></tr></thead><tbody>'+
  rows.map(r=>`<tr><td title="${esc(r.what)}">${name(r.ring)} <span class="small">(${r.ring})</span></td><td class="small what">${r.what}</td><td class="num">${hopk(r.ring)}</td><td class="num">${val(r)}</td><td class="num small">${rg[r.ring]?pcs(rg[r.ring],f2):'a2, 2 runs'}</td><td class="num">${nf(r.gb_s)}</td></tr>`).join('')+
  '<tr><td colspan="6"><b>Handing a slab to the next shire</b> <span class="small">(the relay: a stage reads a slab, adds 1 and writes it where the next stage reads it)</span></td></tr>'+
  [['hop','in the next shire’s scratchpad','write where the next shire reads, read there; the next shire by ID',MH.xshire1?hopk('xshire1'):'—'],['dram','through DRAM','write to DRAM, read back','—'],['scp','kept in this shire’s scratchpad','write and read in place','0']].map(m=>
   `<tr><td title="${esc(m[2])}">${m[1]}</td><td class="small what">${m[2]}</td><td class="num">${m[3]}</td><td class="num">${rr[m[0]]?bt(rr[m[0]],f1):'<b>'+f1(rp[m[0]].pj_per_byte)+'</b>'}</td><td class="num small">${rr[m[0]]?pcs(rr[m[0]],f1):'a2 only'}</td><td class="num">${nf(rp[m[0]].bytes_per_s/1e9)}</td></tr>`).join('')+
  '</tbody>';
 $('commnote').innerHTML=(rg.shire?(()=>{
    /* the 18 September runs were on aifoundry2, so they are set against aifoundry2's own new passes */
    const d=D.comm.rows.filter(r=>rg[r.ring]&&rg[r.ring].per_card.aifoundry2&&r.pj_per_byte_local).map(r=>100*(r.pj_per_byte_local/rg[r.ring].per_card.aifoundry2.mean-1)).sort((a,b)=>a-b);
    const pm=v=>(v<0?'−':'+')+f0(Math.abs(v));
    const dr=(RR.dropped||[]).map(x=>x.sampler_median_ms).filter(v=>v!=null);
    const pc=(rr.dram||{}).per_card||{}, n2=(pc.aifoundry2||{}).n, n3=(pc.aifoundry3||{}).n;
    return `<p class="small">Rings: re-measured on 23 September with the manual's own sampler, ${WORD[RR.passes.rings/2]||RR.passes.rings/2} passes on each card (n = ${rg.shire.n}). The 18 September pair of runs on aifoundry2, sampled without the die temperature and so without a leakage correction, is not pooled; against aifoundry2's own new passes the values <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a> publishes from it read ${pm(d[0])}% to ${pm(d[d.length-1])}% (median ${pm(d[d.length>>1])}%). `+
      `On aifoundry2 the s ↔ s+16 ring starves the service processor's own management path — the sampler's latency rises from 22 ms to ${dr.length?f0(Math.min(...dr))+'–'+f0(Math.max(...dr)):'over 60'} ms and the board reading takes a new value about twice a second instead of six times — so its aifoundry2 passes were dropped and that row is aifoundry3 only; aifoundry3's sampler stays at 22 ms in it. `+
      `Relay: 22 September (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay">Hand it to the next shire</a>) and ${WORD[n2-1]||n2-1} warm passes on aifoundry2, ${WORD[n3]||n3} passes on aifoundry3 (n = ${rr.dram?rr.dram.n:'—'}). `+
      `Mesh hops: the Manhattan distance between shire s and shire s + k (or s − 1 for the relay), averaged over all 32 compute shires.</p>`;})():'');
 const mesh=D.comm.rows.filter(r=>r.ring.startsWith('xshire')&&!r.ring.includes('c4'));
 const xs=mesh.map(r=>rg[r.ring]?rg[r.ring].mean:r.pj_per_byte);
 const fit=MH.xshire1?lfit(mesh.map(r=>[MH[r.ring].mean,rg[r.ring]?rg[r.ring].mean:r.pj_per_byte])):null, hx=mesh.map(r=>(MH[r.ring]||{}).mean||0);
 const nb=rg.neigh?rg.neigh.mean:D.comm.rows.find(r=>r.ring==='neigh').pj_per_byte, sh=rg.shire?rg.shire.mean:D.comm.rows.find(r=>r.ring==='shire').pj_per_byte;
 const pr=rg.pair?rg.pair.mean:D.comm.rows.find(r=>r.ring==='pair').pj_per_byte;
 const hop=rr.hop?rr.hop.mean:rp.hop.pj_per_byte, dram=rr.dram?rr.dram.mean:rp.dram.pj_per_byte;
 const hw=['dram','hop','scp'].filter(k=>rr[k]).map(k=>100*(rr[k].hi-rr[k].lo)/2/rr[k].mean), ow=['dram','hop','scp'].map(k=>rp[k].over_idle_w);
 /* the line through the rings between shires, per card, on the rings both cards measured (the pooled line mixes
    cards that disagree, and aifoundry3's s <-> s+16 ring) */
 const both=mesh.filter(r=>rg[r.ring]&&rg[r.ring].per_card.aifoundry2&&rg[r.ring].per_card.aifoundry3&&MH[r.ring]);
 const pcFit=MH.xshire1&&both.length>=3?['aifoundry2','aifoundry3'].map(h=>lfit(both.map(r=>[MH[r.ring].mean,rg[r.ring].per_card[h].mean]))):null, hb=both.map(r=>MH[r.ring].mean);
 const rpc=['aifoundry2','aifoundry3'].filter(h=>rr.dram&&rr.hop&&rr.dram.per_card[h]&&rr.hop.per_card[h]);
 $('commtext').innerHTML=`Between the two minions of a pair a byte costs under a picojoule (${f2(pr)} pJ); around a neighbourhood or a shire about ${f1((nb+sh)/2)} pJ; across the mesh ${f0(Math.min(...xs))}–${f0(Math.max(...xs))} pJ. `+
  (pcFit?`A straight line through the 1 KB rings between shires against their mean distances (the ${WORD[both.length]||both.length} both cards measured, ${f1(Math.min(...hb))}–${f1(Math.max(...hb))} hops) gives ${f1(pcFit[0].a)} pJ to leave the shire plus ${f1(pcFit[0].b)} pJ per mesh hop on aifoundry2, and ${f1(pcFit[1].a)} plus ${f1(pcFit[1].b)} on aifoundry3. <b>Leaving the shire is the biggest single step (section 4.3's wire fit shows it on both cards), but the hops after it are not free.</b> `:'')+
  `Small messages cost more per byte in the 128 B rows, a difference resolved so far only on aifoundry2's shire ring; the per-message overhead is 40–224 cycles of the sending and receiving harts (<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>, one session on aifoundry2). `+
  (rpc.length===2?`Handing a slab to the next shire through its scratchpad is ${f1(rr.dram.per_card.aifoundry2.mean/rr.hop.per_card.aifoundry2.mean)}× cheaper than the DRAM round trip on aifoundry2 and ${f1(rr.dram.per_card.aifoundry3.mean/rr.hop.per_card.aifoundry3.mean)}× on aifoundry3; the hand-off itself costs ${f1(rr.hop.per_card.aifoundry2.mean)} pJ/B on aifoundry2 and ${f1(rr.hop.per_card.aifoundry3.mean)} on aifoundry3. The three relay bars are ±${f0(Math.min(...hw))}–${f0(Math.max(...hw))}%: the hop relay's is mostly that difference between the cards, and the others are a ${f0(Math.min(...ow))}–${f0(Math.max(...ow))} W signal over a board idle that drifts, the DRAM relay's power also riding on a path with no rail sensor.`:
   `Handing a slab to the next shire through its scratchpad is ${f0(dram/hop)}× cheaper than the DRAM round trip. The three relay bars are ±${f0(Math.min(...hw))}–${f0(Math.max(...hw))}% because each is a ${f0(Math.min(...ow))}–${f0(Math.max(...ow))} W signal over a board idle that drifts; the DRAM relay's power also rides on a path with no rail sensor.`);
})();

/* ---------- 6. sync ---------- */
(function(){
 const hn=RR.hotline_nj_per_op||{};
 /* the chip barrier's waiting energy: 1,024 minions stalled for its length at the pooled stalled power (section 2) */
 const stallW=HOT?HOT.mean:at.contended.over_idle_w, bar=stallW*D.sync.barrier_cycles_chip/0.6e9*1e6;
 const conm=hn.contended?hn.contended.mean:at.contended.nj_per_op, sprm=hn.spread?hn.spread.mean:at.spread.nj_per_op;
 $('sync').innerHTML='<thead><tr><th>Event</th><th class="num">Energy</th><th class="num">per card</th><th class="num">Time</th><th>Note</th></tr></thead><tbody>'+
  `<tr><td>Global atomic, one line, 1,024 requesters</td><td class="num">${hn.contended?bt(hn.contended,f1)+' nJ':'<b>'+f1(at.contended.nj_per_op)+' nJ</b>'}</td><td class="num small">${hn.contended?pcs(hn.contended,f1):'a2 only'}</td><td class="num">${f0(at.contended.cycles_per_op)} cycles each at the bank</td><td class="small">the bank serialises and every requester waits its turn; the host shire's own loads stop</td></tr>`+
  `<tr><td>Global atomic, 32 lines, one per shire</td><td class="num">${hn.spread?bt(hn.spread,f2)+' nJ':f1(at.spread.nj_per_op)+' nJ'}</td><td class="num small">${hn.spread?pcs(hn.spread,f2):'a2 only'}</td><td class="num">${f2(at.spread.cycles_per_op)} cycles each, aggregate</td><td class="small">the same instruction, ${f0(conm/sprm)}× cheaper</td></tr>`+
  `<tr><td>Uncontended remote atomic round trip</td><td class="num">—</td><td></td><td class="num">${f0(D.sync.remote_atomic_latency_cycles)} cycles</td><td class="small">the same on both cards</td></tr>`+
  `<tr><td>Chip-wide barrier, ${nf(D.sync.barrier_participants||1024)} minions</td><td class="num">≈ ${f0(bar)} µJ of waiting</td><td></td><td class="num">${nf(D.sync.barrier_cycles_chip)} cycles</td><td class="small">derived: 1,024 minions stalled at ${f1(stallW/1024*1e3)} mW (section 2) for its length; the length is one run on aifoundry2 (18 September)</td></tr>`+
  `<tr><td>FLB (fast local barrier) + credit barrier, one shire</td><td class="num">—</td><td></td><td class="num">237 cycles</td><td class="small"><a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>, aifoundry2, 18 September</td></tr>`+
  `<tr><td>TensorReduce (the hardware reduction tree) + broadcast, 32 minions</td><td class="num">—</td><td></td><td class="num">432 cycles</td><td class="small"><a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">On-chip communication</a>, aifoundry2, 18 September</td></tr>`+
  '</tbody>';
 $('syncnote').innerHTML=(hn.contended?`Hot line: 22 September and ${WORD[(hn.contended.per_card.aifoundry2||{n:1}).n-1]} warm passes on aifoundry2, ${WORD[(hn.contended.per_card.aifoundry3||{n:0}).n]} passes on aifoundry3 (n = ${hn.contended.n}). The first session alone (aifoundry2, 22 September, one run) gave ${f1(at.contended.nj_per_op)} and ${f2(at.spread.nj_per_op)} nJ. The contended row’s bar is wide mostly because of that session: the whole chip stalled drew ${f1(at.contended.over_idle_w)} W over idle in it, against ${HOT&&HOT.n>1?f2((HOT.n*HOT.mean-at.contended.over_idle_w)/(HOT.n-1)):f1(conm*at.contended.ops_per_s*1e-9)} W in the mean of the passes since, and the per-operation figure divides that small number by a rate the bank fixes at one per 10 cycles.`:'');
})();

/* ---------- 7.1 build a workload's energy (em-v1) ---------- */
(function(){
 const rg=RR.rings_pj_per_byte||{}, rr=RR.relay_pj_per_byte||{};
 /* ENT: every event the calculator can price. e(o) is {mean,lo,hi} per event, rate(o) what the card reached per second
    running it alone (aifoundry2), unit MAC | instr | byte; issue rows share the harts' issue slots. */
 const ENT={}, GROUPS=[], put=(grp,id,o)=>{ENT[id]=Object.assign({id},o); let gp=GROUPS.find(g=>g[0]===grp); if(!gp)GROUPS.push(gp=[grp,[]]); gp[1].push(id);};
 const tcfg=(ty,o)=>`${ty}_${o==='zeros'?'zeros':'randn'}`;
 ['fp32','fp16','int8'].forEach(ty=>{if(!TB[tcfg(ty,'random')])return; put('Tensor unit, per multiply-add','t:'+ty,{label:`TensorFMA ${ty}, all 1,024 minions`,short:`TensorFMA ${ty}`,unit:'MAC',issue:true,
   e:o=>TB[tcfg(ty,o)], rate:o=>D.tensor.rows.find(r=>r.config===tcfg(ty,o)).per_s});});
 const catE=(grp,k,sfx,label,short,issue,unit)=>{if(!CB[`${k}/random${sfx}`])return; const ok=o=>CB[`${k}/${o}${sfx}`]?o:'random';
  put(grp,'c:'+k+sfx,{label,short:short||label,unit,issue,e:o=>cb(`${k}/${ok(o)}${sfx}`),rate:o=>{const s=SA[`${k}/${ok(o)}${sfx}`]; return unit==='byte'?s.bytes_per_s.mean:s.ops_per_s.mean;},only:CB[`${k}/zeros${sfx}`]?null:'random'});};
 CLASSES.forEach(c=>c[1].forEach(n=>catE(c[0]+' (both harts, per instruction)',n,'/h2',n,n,true,'instr')));
 [['tload/scp','own scratchpad, tensor load'],['tstore/scp','own scratchpad, tensor store'],['l1fill/stride32','own scratchpad, 32 B loads through the L1'],['tload/dram','DRAM, tensor load'],['tstore/dram','DRAM, tensor store'],['st_stream/dram','DRAM, stores through the L1'],['dramrow/stride8K','L3, tensor load through the mesh']]
  .forEach(([k,l])=>catE('Bytes through the memory hierarchy (per byte)',k,'',l,l,false,'byte'));
 [1,2,3,4,5,6,8].forEach(d=>catE('Bytes from a scratchpad d hops away (tensor loads, per byte)',`wire/hop${d}`,'',`a scratchpad ${d} hop${d>1?'s':''} away`,null,false,'byte'));
 if(wireAt(HH,'random'))put('Bytes from a scratchpad d hops away (tensor loads, per byte)','w:hh',{label:`a scratchpad ${f1(HH)} hops away (interpolated; the relay's next shire)`,short:`a scratchpad ${f1(HH)} hops away`,unit:'byte',issue:false,e:o=>wireAt(HH,o),
   rate:o=>{const lo=Math.floor(HH),hi=Math.ceil(HH),a=SA[`wire/hop${lo}/${o}`].bytes_per_s.mean,b=SA[`wire/hop${hi}/${o}`].bytes_per_s.mean; return a+(b-a)*(hi>lo?(HH-lo)/(hi-lo):0);}});
 D.comm.rows.filter(r=>!r.ring.endsWith('c4')&&rg[r.ring]).forEach(r=>put('Between cores: rings, 1 KB messages (per byte)','r:'+r.ring,{label:`ring ${r.ring}`,short:`ring ${r.ring}`,unit:'byte',issue:false,e:()=>rg[r.ring],rate:()=>r.gb_s*1e9,only:'own'}));
 const tRow=(ty,o)=>D.tensor.rows.find(r=>r.config===tcfg(ty,o));
 const relayP=(m,rd,wr,label)=>({label,rows:[[rd,rp[m].bytes_per_s/2],[wr,rp[m].bytes_per_s/2]],relay:m});
 const PRE=[['fp32','fp32 matmul',{rows:[['t:fp32',1]],tensor:'fp32'}],['fp16','fp16 matmul',{rows:[['t:fp16',1]],tensor:'fp16'}],['int8','int8 matmul',{rows:[['t:int8',1]],tensor:'int8'}],
  ['dram','stream from DRAM (tensor loads)',{rows:[['c:tload/dram',1]]}],
  ['rhop','relay: next shire',relayP('hop','w:hh','c:tstore/scp')],['rscp','relay: own scratchpad',relayP('scp','c:l1fill/stride32','c:tstore/scp')],['rdram','relay: through DRAM',relayP('dram','c:tload/dram','c:tstore/dram')]]
  .filter(p=>p[2].rows.every(r=>ENT[r[0]]));
 const st={T:80,o:'random',dur:7,rows:[{id:'',p:0},{id:'',p:0},{id:'',p:0}],preset:'fp32',capped:false};
 const COL=['var(--c1)','var(--c2)','var(--c3)'];
 /* a preset gives each row a fraction of its measured rate (a number ≤ 1) or an absolute rate per second (a number > 1) */
 function load(id){const p=PRE.find(q=>q[0]===id)[2]; st.preset=id;
  st.rows=[0,1,2].map(i=>{const r=p.rows[i]; if(!r)return {id:'',p:0}; const e=ENT[r[0]], v=r[1]>1?r[1]/e.rate(st.o):r[1]; return {id:r[0],p:Math.min(1,v)};});
  sync(); upd();}
 const pbox=$('calc-presets'), pbtn={};
 PRE.forEach(([id,label])=>{const b=document.createElement('button'); b.type='button'; b.textContent=label; b.setAttribute('aria-pressed','false'); b.addEventListener('click',()=>load(id)); pbox.appendChild(b); pbtn[id]=b;});
 const tr=CK.range('calc-temp',{label:'die temperature',min:45,max:95,step:1,value:80,fmt:v=>v+' °C',onInput:v=>{st.T=v; upd();}});
 const ds=CK.seg('calc-data',{label:'data',options:[['random','random'],['zeros','zeros']],value:'random',onChange:v=>{st.o=v; sync(); upd();}});
 const dur=$('calc-dur'); dur.addEventListener('input',()=>{const v=+dur.value; if(v>0){st.dur=v; upd();}});
 /* the three event rows: a select, a rate slider, and the absolute rate */
 const rowsBox=$('calc-rows'), UI=[];
 const opts='<option value="">(none)</option>'+GROUPS.map(([gname,ids])=>`<optgroup label="${gname}">`+ids.map(id=>`<option value="${id}">${ENT[id].label}</option>`).join('')+'</optgroup>').join('');
 const unitTxt={MAC:'MAC/s',instr:'instructions/s',byte:'B/s'};
 const rateTxt=(e,v)=>!(v>0)?'0 '+unitTxt[e.unit]:e.unit==='byte'?(v>=1e12?f2(v/1e12)+' TB/s':nf(v/1e9)+' GB/s'):sci(v)+' '+unitTxt[e.unit];
 [0,1,2].forEach(i=>{const d=document.createElement('div'); d.className='ck-controls calc-row';
  d.innerHTML=`<span class="ck-range"><label for="calc-e${i}">row ${i+1}</label><select id="calc-e${i}" aria-label="row ${i+1}: what the workload does">${opts}</select></span>`+
   `<span class="ck-range"><label for="calc-p${i}">rate, % of what the card reached</label><input type="range" id="calc-p${i}" min="0" max="100" step="1" aria-label="row ${i+1} rate, percent of what the card reached"><output for="calc-p${i}" id="calc-o${i}"></output></span>`;
  rowsBox.appendChild(d); const sel=d.querySelector('select'), rng=d.querySelector('input'), out=d.querySelector('output');
  sel.addEventListener('change',()=>{const e=sel.value?ENT[sel.value]:null, room=Math.max(0,Math.min(1,1-issueSum(i))); st.capped=!!(e&&e.issue&&room<1); st.rows[i]={id:sel.value,p:e?(e.issue?room:1):0}; st.preset=null; sync(); upd();});
  rng.addEventListener('input',()=>{const r=st.rows[i]; if(!r.id)return; let v=+rng.value/100; st.capped=false;
   if(ENT[r.id].issue){const room=1-issueSum(i); if(v>room+1e-9){v=Math.max(0,room); st.capped=true;}} r.p=v; st.preset=null; sync(st.capped?undefined:i); upd();});   /* a capped slider snaps back to the cap */
  UI.push({sel,rng,out});});
 const issueSum=skip=>st.rows.reduce((s,r,k)=>s+(k!==skip&&r.id&&ENT[r.id].issue?r.p:0),0);
 function sync(skipRange){st.rows.forEach((r,i)=>{const u=UI[i], e=r.id?ENT[r.id]:null; u.sel.value=r.id; u.rng.disabled=!e;
   if(skipRange!==i)u.rng.value=Math.round(100*r.p);
   const s=e?`${f0(100*r.p)}% · ${rateTxt(e,r.p*e.rate(st.o))}`:'—'; u.out.textContent=s; u.rng.setAttribute('aria-valuetext',s);});
  for(const id in pbtn)pbtn[id].setAttribute('aria-pressed',String(id===st.preset));}
 /* price the current state */
 function price(o,T){const fix=R.P_fix_w, leak=lawAt(T)-R.P_fix_w, rows=[];
  st.rows.forEach((r,i)=>{if(!r.id||r.p<=0)return; const e=ENT[r.id], c=e.e(o), rate=r.p*e.rate(o); if(!c)return;
   rows.push({i,e,rate,w:c.mean*rate*1e-12,lo:c.lo*rate*1e-12,hi:c.hi*rate*1e-12,c,op:e.only==='own'?'its own data':e.only&&o!=='random'?'random only':o});});
  const dyn=rows.reduce((s,r)=>s+r.w,0), lo=rows.reduce((s,r)=>s+r.lo,0), hi=rows.reduce((s,r)=>s+r.hi,0);
  return {fix,leak,rows,dyn,lo,hi,tot:fix+leak+dyn};}
 /* the measurement the preset reproduces: the ablation's board power at its 80 °C launch, or the relay's measured
    energy per byte times its rate, over idle (comparable at any temperature, like every priced row) */
 function measured(){const p=st.preset&&PRE.find(q=>q[0]===st.preset); if(!p)return null; const q=p[2];
  if(q.tensor){const t=tRow(q.tensor,st.o); if(!t||t.idle_w==null)return null; return {tot:t.idle_w+t.over_idle_w,T:80,label:`measured ${f1(t.idle_w+t.over_idle_w)} W`,src:'the 21 September ablation on aifoundry2, launched at 80 °C, one of the runs behind the price'};}
  if(q.relay&&rr[q.relay]){const m=rr[q.relay], w=m.mean*rp[q.relay].bytes_per_s*1e-12; return {over:w,label:`measured ${f1(w)} W over idle`,src:`the relay, ${f1(m.mean)} pJ/B [${f1(m.lo)}–${f1(m.hi)}] × ${nf(rp[q.relay].bytes_per_s/1e9)} GB/s, both cards (n = ${m.n})`,relay:q.relay};}
  return null;}
 const ro=CK.readout('calc-readout');
 const fc=CK.frame('calc',{height:W=>W<600?128:118,label:"Board power priced from the tables",draw:f=>{
  const pz=price(st.o,st.T), M=measured(), mx=Math.max(80,Math.ceil((pz.fix+pz.leak+pz.hi+1)/20)*20);
  const L=8,Rr=16,T=34,bh=34, x=CK.lin(0,mx,L,f.W-Rr), y0=T;
  const ax=CK.el('g',{'aria-hidden':'true'},f.svg);
  x.ticks(f.narrow?4:8).forEach(t=>{CK.el('line',{x1:x(t),x2:x(t),y1:T-6,y2:T+bh+6,class:'grid-line'},ax); CK.txt(ax,x(t),T+bh+22,CK.fmt.num(t),'tick','middle');});
  CK.txt(ax,f.W-Rr,f.H-4,'board power, W','lab','end');
  const segs=[['fixed',pz.fix,'var(--ref)',`<b>fixed</b>: ${f1(pz.fix)} W, the idle law's constant at its best fit (section 1)`],['leakage',pz.leak,'var(--c4)',`<b>leakage at ${st.T} °C</b>: ${f1(pz.leak)} W (section 1)`]]
   .concat(pz.rows.map(r=>[r.e.short,r.w,COL[r.i],`<b>${r.e.label}</b>, ${r.op}<br>${fs(r.c.mean)} ${r.e.unit==='byte'?'pJ/B':r.e.unit==='MAC'?'pJ per MAC':'pJ per instruction'} [${fs(r.c.lo)}–${fs(r.c.hi)}] × ${rateTxt(r.e,r.rate)} = <b>${f1(r.w)} W</b> [${f1(r.lo)}–${f1(r.hi)}]`]));
  let acc=0; const nodes=[];
  segs.forEach(s=>{const w=Math.max(0,x(acc+s[1])-x(acc)-2); if(w>0.3)nodes.push(mark(f,f.svg,'rect',{x:x(acc),y:y0,width:w,height:bh,fill:s[2],rx:2},0,s[3])); acc+=s[1];});
  if(pz.rows.length){const a=x(pz.fix+pz.leak+pz.lo), b=x(pz.fix+pz.leak+pz.hi), cy=y0+bh/2;
   CK.el('line',{x1:a,x2:b,y1:cy,y2:cy,stroke:'var(--ink)','stroke-width':1.5},f.svg); [a,b].forEach(v=>CK.el('line',{x1:v,x2:v,y1:cy-6,y2:cy+6,stroke:'var(--ink)','stroke-width':1.5},f.svg));}
  if(M){const v=M.tot!=null?M.tot:pz.fix+pz.leak+M.over, live=M.T==null||Math.abs(st.T-M.T)<=2, xm=x(v);
   CK.el('line',{x1:xm,x2:xm,y1:y0-8,y2:y0+bh+8,stroke:live?'var(--ink)':'var(--muted)','stroke-width':2,'stroke-dasharray':live?null:'3 3'},f.svg);
   const lab=live?M.label:`measured at ${M.T} °C`, right=xm>f.W*0.6;
   const t=CK.txt(f.svg,right?xm+4:xm+4,y0-12,lab,live?'lab-strong':'tick',right&&xm>f.W-150?'end':'start'); if(right&&xm>f.W-150)t.setAttribute('x',xm-4);}
  CK.keynav(f,nodes);
 }});
 function upd(){fc.redraw(); const pz=price(st.o,st.T), M=measured(), J=pz.tot*st.dur, first=pz.rows[0];
  CK.legend('calc-legend',[{key:'f',label:`fixed ${f1(pz.fix)} W`,mark:'box',color:'var(--ref)'},{key:'l',label:`leakage at ${st.T} °C ${f1(pz.leak)} W`,mark:'box',color:'var(--c4)'}]
   .concat(pz.rows.map(r=>({key:'r'+r.i,label:`${r.e.short} ${f1(r.w)} W`,mark:'box',color:COL[r.i]}))).concat(M?[{key:'m',label:'measurement',mark:'line',color:'var(--ink)'}]:[]));
  /* per useful operation: every row in the first row's unit counts (a relay's read row and write row are its bytes moved) */
  const same=first?pz.rows.filter(r=>r.e.unit===first.e.unit):[], k=first&&first.e.unit==='MAC'?2:1, ops=same.reduce((a,r)=>a+k*r.rate,0), dw=same.reduce((a,r)=>a+r.w,0);
  const per=first&&ops>0?[pz.tot/ops*1e12,{MAC:first.e.id==='t:int8'?'pJ per int8 op':'pJ per FLOP',byte:'pJ per byte',instr:'pJ per instruction'}[first.e.unit],dw/ops*1e12]:null;   /* two ops per multiply-add */
  let s=`<b>${f1(pz.tot)} W</b>${pz.rows.length?` [${f1(pz.fix+pz.leak+pz.lo)}–${f1(pz.fix+pz.leak+pz.hi)}]`:''} at ${st.T} °C: idle ${f1(pz.fix+pz.leak)} W (${f1(pz.fix)} fixed + ${f1(pz.leak)} leakage at the law's best fit)`+pz.rows.map(r=>` + ${f1(r.w)} W ${r.e.short}`).join('')+
   `. Over ${CK.fmt.num(st.dur)} s: <b>${nf(J)} J</b>, ${f0(100*(pz.fix+pz.leak)/pz.tot)}% of it static.`;
  if(per)s+=` That is ${CK.fmt.num(per[0])} ${per[1]} with the card's idle, ${CK.fmt.num(per[2])} of it the ${per[1].replace('pJ per ','')}s themselves.`;
  if(M){if(M.tot!=null)s+=Math.abs(st.T-M.T)<=2?` The measurement: ${f1(M.tot)} W (${M.src}).`:` The measurement (${f1(M.tot)} W) was at ${M.T} °C; move the temperature there to compare.`;
   else{const pzz=price('zeros',st.T), pzr=price('random',st.T), inb=M.over<pzz.dyn?'below the bracket':M.over>pzr.dyn?'above the bracket':'inside the bracket';
    s+=` Priced ${f1(pzz.dyn)} W on zeros … ${f1(pzr.dyn)} W on random data over idle; measured ${f1(M.over)} W (${M.src}): ${inb}.`;}}
  if(st.capped)s+=' <span class="small">Instruction rows share the harts’ issue slots, so together they stop at 100%.</span>';
  ro.set(s);}
 sync(); load('fp32');
 /* text beneath: the default preset against its measurement, and the static share at 80 °C */
 const t=tRow('fp32','random'), tz=tRow('fp32','zeros'), tb=TB.fp32_randn;
 const dyns=[...CARDS.flatMap(h=>Object.values(D.catalogue.cards[h].summary).map(e=>e.over_idle_w.mean)),...D.tensor.rows.map(r=>r.over_idle_w)];
 const mxd=Math.max(...dyns), sw=tb.mean*t.per_s*1e-12;
 /* what cooling from 80 to 60 C saves, over the fits in R.profile (each its own T_L) */
 const sv=R.profile?R.profile.fits.map(q=>q.A_leak_80_w*(1-Math.exp(-20/q.T_L_c))):null, cool=sv?[Math.min(...sv),Math.max(...sv)]:null;
 const PF=R.profile;
 $('compcap').innerHTML=`How it is priced: aifoundry2's idle law of section 1 at the chosen die temperature, plus, for each row, its energy per event from sections 3–5 (the mean over both cards; the whisker spans the rows' ranges) times its rate. A rate is a fraction of what the card reached running that row alone. Instruction rows share the harts' issue slots, so together they stop at 100%; byte streams are assumed to add, which no measurement of concurrent streams has tested beyond the relay's reads and writes (section 7.2). Per-instruction costs include the awake core (section 2), so two instruction rows count it twice. The static part carries the idle law's own bar: ±0.2 W on aifoundry2, ${D.cards.leakage?(D.cards.leakage.mean_offset_W>=0?'+':'')+f1(D.cards.leakage.mean_offset_W):'+0.7'} W on aifoundry3 (the mean of its four temperature bins). `+
  (PF?`Its split into fixed and leakage is the best fit's: the e-foldings that fit the idle bins as well put the leakage at 80 °C anywhere from ${f0(PF.A_leak_80_w[0])} to ${f0(PF.A_leak_80_w[1])} W, but move the idle total by at most ${f1(PF.idle_spread_w_45_95)} W between 45 and 95 °C. `:'')+
  `The default is the dense fp32 matmul on random data: ${f1(P80)} W of idle at 80 °C and ${f1(sw)} W of multiply-adds (section 3.2's ${f2(tb.mean)} pJ per MAC at ${sci(t.per_s)} MAC/s), ${f1(P80+sw)} W, against ${f1(t.idle_w+t.over_idle_w)} W measured on aifoundry2 — one of the runs the ${f2(tb.mean)} pJ is built from, so this checks the arithmetic rather than the price; the flip model of section 3.2, fitted on aifoundry2, prices the same tile at ${f1((D.cards.patterns||[]).find(p=>p.values==='randn').model)} W instead of ${f1(sw)}.`;
 $('comptext').innerHTML=`<b>At 80 °C the static ${f0(P80)} W exceeds the dynamic power of every kernel measured here</b>, ${mxd===t.over_idle_w?"the dense random matmul's":'the largest,'} ${f1(mxd)} W included. The same matmul on zeros draws ${f1(tz.over_idle_w)} W over idle instead of ${f1(t.over_idle_w)}, and its measured loaded cost per flop on aifoundry2 falls from ${f1(1e12*(t.idle_w+t.over_idle_w)/(2*t.per_s))} to ${f1(1e12*(tz.idle_w+tz.over_idle_w)/(2*tz.per_s))} pJ, almost all of it static. Cooling the die from 80 to 60 °C saves about ${f0(P80-lawAt(60))} W of aifoundry2's idle power${cool?` (${f1(cool[0])}–${f1(cool[1])} W over the e-foldings that fit)`:''}, and presumably as much under load. <b>On aifoundry2, where the temperature law was measured, the data decides the dynamic energy and the temperature decides the rest.</b>`;
})();

/* ---------- 7.2 the relay, priced from section 4 ---------- */
(function(){
 /* The relay reads with 32 B vector loads through the L1 and writes with tensor stores; its "next shire" is shire
    s - 1 by ID. Each byte is read once and written once, so each bracket is the mean of a read row and a write row,
    zeros ... random (its data is one constant per slab). */
 const rr2=RR.relay_pj_per_byte||{};
 const zr=k=>{const z=cb(k+'/zeros'),r=cb(k+'/random'); return z&&r?[z.mean,r.mean]:null;};
 const mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2];
 const wl=wireAt(HH,'zeros'), wh=wireAt(HH,'random'), wire=wl&&wh?[wl.mean,wh.mean]:null;
 const ts=zr('tstore/scp'), pd=mid(zr('tload/dram'),zr('tstore/dram')), l1f=zr('l1fill/stride32'), ps=l1f&&ts?mid(l1f,ts):null, ph=wire&&ts?mid(wire,ts):null;
 /* within 10% below a bracket is its low edge: the own scratchpad's 8% is within the noise on both cards (version 3) */
 const edge=(v,b)=>v<b[0]&&v>=0.9*b[0];
 const inb=(v,b)=>edge(v,b)?'at its low edge':v<b[0]?'below':v>b[1]?'above':'inside';
 const M=k=>rr2[k]?rr2[k].mean:rp[k].pj_per_byte;
 $('relaycheck').innerHTML='<thead><tr><th>Where the relay keeps its intermediate</th><th class="num">priced pJ/B, zeros … random</th><th class="num">measured</th></tr></thead><tbody>'+
  `<tr><td>intermediate in DRAM</td><td class="num">${f0(pd[0])} … ${f0(pd[1])}</td><td class="num">${rr2.dram?bt(rr2.dram,f1):'<b>'+f1(rp.dram.pj_per_byte)+'</b>'} <span class="small">(${inb(M('dram'),pd)})</span></td></tr>`+
  (ps?`<tr><td>in the shire's own scratchpad</td><td class="num">${f1(ps[0])} … ${f1(ps[1])}</td><td class="num">${rr2.scp?bt(rr2.scp,f2):'<b>'+f2(rp.scp.pj_per_byte)+'</b>'} <span class="small">(${inb(M('scp'),ps)})</span></td></tr>`:'')+
  (ph?`<tr><td>in the next shire's scratchpad</td><td class="num">${f1(ph[0])} … ${f1(ph[1])}</td><td class="num">${rr2.hop?bt(rr2.hop,f2):'<b>'+f2(rp.hop.pj_per_byte)+'</b>'} <span class="small">(${inb(M('hop'),ph)})</span></td></tr>`:'')+'</tbody>';
 const V=[['DRAM',M('dram'),pd],['the next shire',M('hop'),ph],['the own scratchpad',M('scp'),ps]].filter(x=>x[2]);
 const inside=V.filter(x=>x[1]>=x[2][0]&&x[1]<=x[2][1]).map(x=>x[0]), out=V.filter(x=>!(x[1]>=x[2][0]&&x[1]<=x[2][1]));
 /* DRAM priced with the constant-operand rows instead, per card: closer to the relay's data than the zeros ... random bracket */
 const cst=['aifoundry2','aifoundry3'].map(h=>{const a=cb('tload/dram/const'),b=cb('tstore/dram/const'),m=rr2.dram&&rr2.dram.per_card[h];
   return a&&b&&a.per_card[h]&&b.per_card[h]&&m?{h,p:(a.per_card[h].mean+b.per_card[h].mean)/2,m:m.mean}:null;}).filter(Boolean);
 $('relaytext').innerHTML=`No row of section 4 was derived from the relay, but the rows that price it were chosen after it was measured, so this is a consistency check with wide brackets, not a prediction. Each byte is read once and written once, so each bracket is the mean of a read row and a write row of section 4, from zeros to random data (the relay's data is one constant per slab). The relay reads with 32 B loads through the L1 and writes with tensor stores. It is priced with the 32 B L1 row of section 4.3 for its own scratchpad, the wire read of section 4.3 at ${f1(HH)} hops for the next shire, and, for DRAM, section 4.1's tensor-load row, the nearest the catalogue has. `+
  (inside.length?`${inside.join(' and ').replace(/^./,c=>c.toUpperCase())} fall${inside.length>1?'':'s'} inside ${inside.length>1?'their brackets':'its bracket'}`:'')+
  out.map(x=>`${inside.length?' and ':''}${x[0]} ${edge(x[1],x[2])?`sits at the low edge of its bracket (${f0(100*(1-x[1]/x[2][0]))}% below it, within the noise on both cards)`:`reads ${f0(100*Math.abs(1-x[1]/(x[1]<x[2][0]?x[2][0]:x[2][1])))}% ${x[1]<x[2][0]?'below':'above'}`}`).join('')+
  `; the adds and barriers the relay also runs are in no table.`+
  (cst.length===2?` The brackets are wide: priced instead with the constant-operand rows, DRAM comes to ${f1(cst[0].p)} pJ/B on aifoundry2 against ${f1(cst[0].m)} measured, but ${f1(cst[1].p)} on aifoundry3 against ${f1(cst[1].m)}, ${f0(100*(cst[1].m/cst[1].p-1))}% more.`:'')+
  ` Section 7.1 prices the three relays with the same rows.`;
})();

/* ---------- 8. two cards: the ratio against the value (em-l2) ---------- */
(function(){
 const S2c=D.catalogue.cards.aifoundry2&&D.catalogue.cards.aifoundry2.summary, S3c=D.catalogue.cards.aifoundry3&&D.catalogue.cards.aifoundry3.summary; if(!S2c||!S3c)return;
 const pts=[]; for(const k in S2c){const r2=S2c[k],r3=S3c[k]; if(!r3)continue; const byte=r2.bytes_per_s.mean>0, fld=byte?'pj_per_byte':'pj_per_op';
  if(r2[fld].mean>0&&r3[fld].mean>0)pts.push({k,byte,v2:r2[fld].mean,v3:r3[fld].mean,s2:r2[fld].se,s3:r3[fld].se,r:r3[fld].mean/r2[fld].mean});}
 const SEC={relay_pj_per_byte:['relay (section 5)','pJ/B'],hotline_nj_per_op:['hot line (section 6)','nJ'],rings_pj_per_byte:['ring (section 5)','pJ/B'],levels_pj_per_byte:['level (section 4.2)','pJ/B']};
 const rer=[]; Object.keys(SEC).forEach(sec=>{const o=RR[sec]||{}; for(const k in o){const v=o[k]; if(v&&v.per_card.aifoundry2&&v.per_card.aifoundry3)rer.push({k,sec,v2:v.per_card.aifoundry2.mean,v3:v.per_card.aifoundry3.mean,r:v.per_card.aifoundry3.mean/v.per_card.aifoundry2.mean});}});
 const cc=D.catalogue.cross_card, scale=D.cards&&D.cards.scale;
 CK.legend('cards-legend',[{key:'i',label:'per instruction',mark:'dot',color:'var(--c1)'},{key:'b',label:'per byte',mark:'dot',color:'var(--c2)'},{key:'r',label:'reruns (right strip)',mark:'ring',color:'var(--c7)'},
  {key:'m',label:`median ${f3(cc.median)}, shaded 10–90%`,mark:'line',color:'var(--ink-2)'}].concat(scale?[{key:'s',label:`tensor-unit transfer ${f3(scale)}`,mark:'dash',color:'var(--ref)'}]:[]));
 const tipP=p=>`<b>${p.k}</b><br>${CARDS[0]} ${fs(p.v2)} ± ${fs(p.s2)}, ${CARDS[1]} ${fs(p.v3)} ± ${fs(p.s3)} ${p.byte?'pJ/B':'pJ'}<br>ratio <b>${f3(p.r)}</b>`;
 const tipR=p=>`<b>${SEC[p.sec][0]}: ${p.k}</b><br>${CARDS[0]} ${fs(p.v2)}, ${CARDS[1]} ${fs(p.v3)} ${SEC[p.sec][1]}<br>ratio <b>${f3(p.r)}</b>`;
 const byKey={};
 CK.frame('cards',{height:W=>W<600?300:340,label:'Every catalogue entry: aifoundry3 as a fraction of aifoundry2',draw:f=>{
  const SW=f.narrow?58:84, L=40,Rr=10,T=24,B=40, xR=f.W-Rr-SW-10, x=CK.log(1,2000,L,xR), y=CK.lin(0.70,1.20,f.H-B,T);
  CK.axes(f,{x,y,L,R:Rr+SW+10,T,B,yt:[0.7,0.8,0.9,1,1.1,1.2],yfmt:v=>f1(v),xl:`${CARDS[0]}, pJ per instruction or per byte (log)`,yl:`${CARDS[1]} / ${CARDS[0]}`});
  CK.el('rect',{x:L,y:y(cc.p90),width:xR-L,height:y(cc.p10)-y(cc.p90),fill:'var(--grid)',opacity:0.7},f.svg);
  CK.el('line',{x1:L,x2:f.W-Rr,y1:y(cc.median),y2:y(cc.median),stroke:'var(--ink-2)','stroke-width':1.5},f.svg);
  CK.el('line',{x1:L,x2:f.W-Rr,y1:y(1),y2:y(1),stroke:'var(--axis)','stroke-width':1},f.svg);
  if(scale)CK.el('line',{x1:L,x2:f.W-Rr,y1:y(scale),y2:y(scale),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'2 3'},f.svg);
  const nodes=pts.slice().sort((a,b)=>a.v2-b.v2).map(p=>{const m=mark(f,f.svg,'circle',{cx:x(Math.max(1,p.v2)),cy:y(Math.max(0.7,Math.min(1.2,p.r))),r:3,fill:p.byte?'var(--c2)':'var(--c1)','fill-opacity':0.8},6,tipP(p)); byKey[p.k]=m; return m;});
  /* the reruns: their x (pJ/B, nJ) is not comparable, so they get a strip of their own on the same ratio axis */
  const x0=f.W-Rr-SW, cx=x0+SW/2, placed=[];
  CK.el('line',{x1:x0,x2:x0,y1:T,y2:f.H-B,stroke:'var(--axis)'},f.svg);
  CK.txt(f.svg,cx,f.H-B+16,'reruns','tick','middle');
  const rn=rer.slice().sort((a,b)=>a.r-b.r).map(p=>{const cy=y(Math.max(0.7,Math.min(1.2,p.r))); let o=0; for(let k=0;k<40;k++){o=(k%2?1:-1)*Math.ceil(k/2)*7; if(placed.every(q=>(q.o-o)**2+(q.cy-cy)**2>=49))break;} placed.push({o,cy});
   const m=mark(f,f.svg,'circle',{cx:cx+Math.max(-SW/2+5,Math.min(SW/2-5,o)),cy,r:3.2,fill:'none',stroke:'var(--c7)','stroke-width':1.6},6,tipR(p)); byKey['rerun:'+p.sec+':'+p.k]=m; return m;});
  CK.keynav(f,nodes); CK.keynav(f,rn);
 }});
 const rat=pts.map(p=>p.r).sort((a,b)=>a-b), rr=rer.map(p=>p.r).sort((a,b)=>a-b);
 const med=v=>v.length%2?v[v.length>>1]:(v[v.length/2-1]+v[v.length/2])/2;   /* the median of an even count is the mean of the middle two */
 const DB=D.catalogue.die_c_busy_median, LN=D.cards&&D.cards.launch, rl=(sec,k)=>{const x=rer.find(p=>p.sec===sec&&p.k===k); return x?x.r:null;};
 const l1r=rl('levels_pj_per_byte','l1'), scr=rl('levels_pj_per_byte','scp-local');
 /* The lowest and highest ratios are not listed: none of the entries differs from the common scale beyond the noise of
    three passes once the 386 comparisons are allowed for (version 3, energy-manual-158). */
 $('cardscap').textContent=`${pts.length} entries, each the mean of three passes on each card${DB?`, ${CARDS[0]}'s bursts at a median die temperature of ${f0(DB[CARDS[0]])} °C and ${CARDS[1]}'s at ${f0(DB[CARDS[1]])} °C`:''}: ratio ${f3(rat[0])} to ${f3(rat[rat.length-1])}, 10th–90th percentile ${f3(rat[Math.floor(rat.length/10)])}–${f3(rat[Math.floor(rat.length*0.9)])}, median ${f3(rat[rat.length>>1])}; the shaded band and the solid line are the catalogue's own 10–90% and median over its ${cc.n} configurations. The line at 1 is equality. No single entry differs from the common scale beyond the noise of three passes once the ${cc.n} comparisons are allowed for.`+
  (rr.length?` The ${rr.length} rerun entries of sections 4.2, 5 and 6 (right, their energies in their own units) give ${f3(med(rr))} in the median (${f2(rr[0])}–${f2(rr[rr.length-1])}), but they do not share one scale${l1r&&scr?`: some differ from it beyond their noise, the L1 level at ${f2(l1r)} and the own-scratchpad level at ${f2(scr)}`:''}.`:'')+
  ` The tensor-unit transfer of 22 September found ${f3(scale||0.924)} for the same pair of cards${LN&&LN.aifoundry2&&LN.aifoundry3?`, launched at ${f0(LN.aifoundry2.T)} °C on aifoundry2 and ${f0(LN.aifoundry3.T)} °C on aifoundry3`:''}. aifoundry3 runs 5 mV higher, which would make it about 2% dearer, so the voltage does not explain the scale; its die, 20–25 °C cooler in every comparison, has not been ruled out.`;
})();

/* ---------- contents: every h2 and h3, with its section number; runs before the template adds its # links ---------- */
(function(){const ol=$('toclist'); if(!ol)return;
 ol.style.listStyle='none'; ol.style.paddingLeft='0'; ol.style.margin='6px 0 0';
 document.querySelectorAll('main h2, main h3').forEach(hd=>{if(!hd.id)return;
  const li=document.createElement('li'), a=document.createElement('a'); a.href='#'+hd.id; a.textContent=hd.textContent.replace(/\s+/g,' ').trim();
  if(hd.tagName==='H3'){li.style.marginLeft='1.4em'; li.className='small';} li.appendChild(a); ol.appendChild(li);});})();
/* tables become stacked cards under 600 px (template CSS table.stack): each value keeps its column's name */
['awake','instrtab','tensor','memtab','memold','linetab','rowtab','neightab','comm','sync','relaycheck'].forEach(id=>{const t=$(id); if(!t||!t.tHead)return; CK.stackTable(t);
 /* the first header cell often names the table; stacked, the header row is hidden, so it becomes a caption there */
 const th=t.tHead.rows[0].cells[0], tx=th?th.textContent.replace(/\s+/g,' ').trim():''; if(tx.length>12){const c=t.createCaption(); c.className='stack-cap'; c.textContent=tx;}});
/* the Terms box opens when the page is opened at #terms */
(function(){const t=$('terms'); const op=()=>{if(location.hash==='#terms'&&t)t.open=true;}; op(); window.addEventListener('hashchange',op);})();
