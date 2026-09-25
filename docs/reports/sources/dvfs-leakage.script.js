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
const sgn=v=>(v>0?'+':v<0?'−':'')+Math.abs(v);   // a real minus sign, and no sign on zero
const TH=D.thresholds;

/* ---------- the hunting run: clock, die temperature and board power ---------- */
(function(){const tr=D.traces.find(t=>t.values==='ones')||D.traces[0];
 const W=900,H=420,L=58,R=58,T=18,B=36;const {svg,tip,h}=host('cycle',W,H);
 const ph=H-B-T,tmax=Math.max(...tr.t);const x=v=>L+(v+0.5)/(tmax+0.5)*(W-L-R);
 const band=(lo,hi,top,bot)=>v=>T+bot*ph-(v-lo)/(hi-lo)*(bot-top)*ph;
 const yf=band(560,840,0,0.30);           // clock, top band
 const yT=band(62.5,67.5,0.37,0.64);      // die temperature, middle band
 const yp=band(20,95,0.72,1);             // board power, bottom band
 for(const v of [600,700,800]){el('line',{x1:L,x2:W-R,y1:yf(v),y2:yf(v),class:'grid-line'},svg);txt(svg,L-6,yf(v)+4,v,'tick','end');}
 for(const v of [63,64,65,66,67]){el('line',{x1:L,x2:W-R,y1:yT(v),y2:yT(v),class:'grid-line'},svg);if(v%2)txt(svg,L-6,yT(v)+4,v+' °C','tick','end');}
 for(const v of [30,50,70,90]){el('line',{x1:L,x2:W-R,y1:yp(v),y2:yp(v),class:'grid-line'},svg);txt(svg,W-R+6,yp(v)+4,v+' W','tick');}
 for(let s=0;s<=Math.floor(tmax);s++)txt(svg,x(s),H-B+16,s,'tick','middle');
 txt(svg,(L+W-R)/2,H-4,'seconds since the kernel launched','lab','middle');
 txt(svg,4,T-4,'minion clock, MHz','lab');txt(svg,4,yT(67.5)-4,'die temperature (whole degrees)','lab');
 txt(svg,W-R+6,yp(95)-4,'board W','lab');
 el('line',{x1:L,x2:W-R,y1:yT(TH.temp_c),y2:yT(TH.temp_c),stroke:'var(--bad)','stroke-width':1.2,'stroke-dasharray':'5 4'},svg);
 txt(svg,W-R-4,yT(TH.temp_c)+14,'steps down above '+TH.temp_c+' °C','lab','end');
 el('line',{x1:L,x2:W-R,y1:yp(TH.tdp_w),y2:yp(TH.tdp_w),stroke:'var(--bad)','stroke-width':1.2,'stroke-dasharray':'5 4'},svg);
 txt(svg,W-R-4,yp(TH.tdp_w)-5,'TDP '+TH.tdp_w+' W','lab','end');
 const stairs=a=>{const st=[];for(let i=0;i<tr.t.length;i++){if(i&&a[i]!==a[i-1])st.push([tr.t[i],a[i-1]]);st.push([tr.t[i],a[i]]);}return st;};
 el('path',{d:path(stairs(tr.mhz),x,yf),fill:'none',stroke:'var(--c1)','stroke-width':2.6},svg);
 el('path',{d:path(stairs(tr.T),x,yT),fill:'none',stroke:'var(--c7)','stroke-width':2.2},svg);
 el('path',{d:path(tr.t.map((v,i)=>[v,tr.P[i]]),x,yp),fill:'none',stroke:'var(--c2)','stroke-width':1.8},svg);
 el('line',{x1:x(0),x2:x(0),y1:T,y2:H-B,stroke:'var(--axis)','stroke-width':1},svg);
 txt(svg,x(0)+4,H-B-4,'launch','tick');
 const cur=el('line',{x1:0,x2:0,y1:T,y2:H-B,stroke:'var(--ink-2)','stroke-width':1,opacity:0},svg);
 el('rect',{x:L,y:T,width:W-L-R,height:H-B-T,fill:'transparent'},svg);
 const show=ev=>{const b=svg.getBoundingClientRect(),xv=(ev.clientX-b.left)/b.width*W;
  let i=0,best=1e9;tr.t.forEach((v,k)=>{const d=Math.abs(x(v)-xv);if(d<best){best=d;i=k;}});
  cur.setAttribute('x1',x(tr.t[i]));cur.setAttribute('x2',x(tr.t[i]));cur.setAttribute('opacity',0.5);
  tip.innerHTML=`<b>${tr.t[i].toFixed(2)} s</b> after launch (ones, 1,024 minions)<br>clock ${tr.mhz[i]} MHz · die ${tr.T[i]} °C · board ${tr.P[i].toFixed(1)} W`;
  tip.style.display='block';const hb=h.getBoundingClientRect();
  tip.style.left=Math.max(0,Math.min(ev.clientX-hb.left+12,hb.width-290))+'px';tip.style.top=(ev.clientY-hb.top+12)+'px';};
 svg.addEventListener('mousemove',show);
 svg.addEventListener('mouseleave',()=>{tip.style.display='none';cur.setAttribute('opacity',0);});})();

/* ---------- what caused each down-step ---------- */
(function(){const rows=D.transitions.filter(r=>r.dir==='down');
 const W=440,H=380,L=52,R=16,T=16,B=42;const {svg,tip,h}=host('attrib',W,H);
 const x=v=>L+(v-60)/(72-60)*(W-L-R),y=v=>H-B-(v-25)/(95-25)*(H-B-T);
 axes(svg,{W,H,L,R,T,B,x,y,yt:[30,45,60,75,90],xt:[60,63,66,69,72],xl:'die temperature at the step, °C',yl:'board power at the step, W'});
 el('line',{x1:x(TH.temp_c),x2:x(TH.temp_c),y1:T,y2:H-B,stroke:'var(--bad)','stroke-width':1.3,'stroke-dasharray':'5 4'},svg);
 el('line',{x1:L,x2:W-R,y1:y(TH.tdp_w),y2:y(TH.tdp_w),stroke:'var(--bad)','stroke-width':1.3,'stroke-dasharray':'5 4'},svg);
 txt(svg,x(TH.temp_c)+4,T+12,TH.temp_c+' °C',' lab');txt(svg,L+4,y(TH.tdp_w)-5,TH.tdp_w+' W','lab');
 const UN=Object.keys(D.transition_summary.by_cause).find(k=>k.startsWith('unattributed'))||'unattributed';
 const COL={'thermal':'var(--c2)','thermal+power':'var(--bad)','power':'var(--c4)',[UN]:'var(--c1)'};
 for(const r of rows){const g=el('g',{},svg);
  el('circle',{cx:x(r.T),cy:y(r.P),r:6,fill:COL[r.why]||'var(--ref)',opacity:0.85,stroke:'var(--surface)','stroke-width':1.4},g);
  hover(g,tip,h,()=>`<b>${r.values}</b> ${r.f0}→${r.f1} MHz, ${r.mv0}→${r.mv1} mV at ${r.t.toFixed(2)} s<br>die ${r.T} °C, board ${r.P} W<br><b>${r.why}</b>`);}
 document.getElementById('attrib-leg').innerHTML=Object.entries(COL).filter(([k])=>rows.some(r=>r.why===k))
   .map(([k,v])=>`<span><i style="background:${v}"></i>${k}</span>`).join('');})();

/* ---------- wake-up probe ---------- */
(function(){const w=D.wakeup;const W=440,H=380,L=56,R=16,T=30,B=42;const {svg,tip,h}=host('wake',W,H);
 const Z=0.0003;                                   // where "no idle" sits on the log axis
 const lx=v=>Math.log10(Math.max(v,Z));
 const x=v=>L+(lx(v)-lx(Z))/(lx(30)-lx(Z))*(W-L-R),y=v=>H-B-(v+25)/(60)*(H-B-T);
 axes(svg,{W,H,L,R,T,B,x,y,yt:[-20,-10,0,10,20,30],xt:[Z,0.001,0.01,0.1,1,10],xf:v=>v===Z?'0':v<1?(v*1000)+' µs':v+' ms',
   xl:'how long the line sat untouched',yl:'latency minus the same line with no idle, cycles'});
 txt(svg,(x(Z)+x(0.001))/2,H-B+4,'//','tick','middle');
 el('line',{x1:L,x2:W-R,y1:y(0),y2:y(0),stroke:'var(--axis)'},svg);
 const COL=['var(--c1)','var(--c3)','var(--c4)','var(--c7)','var(--bad)'];
 w.levels.forEach((lev,k)=>{const d=lev.paired_median_by_idle||lev.median_cycles.map(c=>c-lev.median_cycles[0]);
  const pts=w.idle_ms.map((ms,i)=>[Math.max(ms,Z),d[i]]);
  el('path',{d:path(pts,x,y),fill:'none',stroke:COL[k%5],'stroke-width':2.2,'stroke-dasharray':k===0?'5 4':'none'},svg);
  const g=el('g',{},svg);pts.forEach(q=>el('circle',{cx:x(q[0]),cy:y(q[1]),r:3.5,fill:COL[k%5]},g));
  const lx0=L+10+(k%2)*170,ly0=T+10+Math.floor(k/2)*18;          // legend, in the empty top of the plot
  el('line',{x1:lx0,x2:lx0+16,y1:ly0-4,y2:ly0-4,stroke:COL[k%5],'stroke-width':2.4,'stroke-dasharray':k===0?'5 4':'none'},svg);
  txt(svg,lx0+22,ly0,lev.level,'lab').setAttribute('style','fill:'+COL[k%5]);
  hover(g,tip,h,()=>`<b>${lev.level}</b><br>longest idle minus no idle, same line: <b>${sgn(lev.paired_delta_cycles)} cycles</b> (median of ${lev.paired_n} repeats, IQR ${lev.paired_iqr})`);});})();

/* ---------- leakage fraction against temperature ---------- */
(function(){const m=D.leak_model;const W=440,H=380,L=52,R=16,T=36,B=42;const {svg,tip,h}=host('leakfrac',W,H);
 const x=v=>L+(v-55)/(95-55)*(W-L-R),y=v=>H-B-v/0.8*(H-B-T);
 axes(svg,{W,H,L,R,T,B,x,y,yt:[0,0.2,0.4,0.6,0.8],yf:v=>Math.round(v*100)+'%',xt:[55,65,75,85,95],
   xl:'die temperature, °C'});
 txt(svg,4,T-18,'leakage as a share of board power','lab');   // clear of the top tick
 const band=D.leak_fraction.kanter_range;
 el('rect',{x:L,y:y(band[1]),width:W-L-R,height:y(band[0])-y(band[1]),fill:'var(--c3)',opacity:0.16},svg);
 txt(svg,W-R-6,y(band[0])-6,'Kanter: typically 5–30%','lab','end');   // inside the band, clear of both curves
 const leak=t=>m.A_at_80*Math.exp((t-80)/m.T_L);
 const idle=[],busy=[];
 for(let t=55;t<=95;t+=0.5){idle.push([t,leak(t)/(m.P_fix+leak(t))]);busy.push([t,leak(t)/(m.P_fix+leak(t)+(D.busy_randn_80c-D.idle_80c))]);}
 el('path',{d:path(idle,x,y),fill:'none',stroke:'var(--c1)','stroke-width':2.4},svg);
 el('path',{d:path(busy,x,y),fill:'none',stroke:'var(--bad)','stroke-width':2.4},svg);
 txt(svg,x(58),y(idle[8][1])+16,'idle card','lab').setAttribute('style','fill:var(--c1)');
 txt(svg,x(58),y(busy[8][1])+16,'random-data matmul','lab').setAttribute('style','fill:var(--bad)');
 const ic=D.idle_check;const g=el('g',{},svg);
 el('circle',{cx:x(ic.die_c),cy:y(ic.temp_dependent_frac),r:6,fill:'var(--c1)',stroke:'var(--surface)','stroke-width':1.5},g);
 hover(g,tip,h,()=>`measured on 22 September after about ${ic.hours_idle} h with no workload:<br>${f2(ic.board_w)} W at ${f1(ic.die_c)} °C, ${Math.round(100*ic.temp_dependent_frac)}% temperature-dependent`);})();

/* ---------- tables ---------- */
// number the seven cool-start runs in order (every one of them has transitions), so the table can name a run
{let run=0,key=null;for(const r of D.transitions){const k=r.session+'/'+r.values;if(k!==key){run++;key=k;}r.run=run;}}
document.getElementById('trans').innerHTML='<thead><tr><th>Run</th><th class="num">t</th><th class="num">MHz</th><th class="num">mV</th><th class="num">die °C</th><th class="num">board W</th><th>Cause</th></tr></thead><tbody>'+
 D.transitions.filter(r=>r.dir==='down').map(r=>`<tr><td>${r.run} · ${r.values}</td><td class="num">${f2(r.t)} s</td><td class="num">${r.f0}→${r.f1}</td><td class="num">${r.mv0}→${r.mv1}</td><td class="num">${r.T}</td><td class="num">${f1(r.P)}</td><td>${r.why}</td></tr>`).join('')+'</tbody>';
(function(){const s=D.transition_summary,w=D.wakeup,ic=D.idle_check;
 const el_=document.getElementById('idlehours');if(el_)el_.textContent=ic.hours_idle;
 const V=[['Any mature design runs a DVFS loop that steps voltage and frequency to stay inside a power and thermal envelope.','confirmed',
   `Three operating points, ${D.operating_points.map(o=>o.mhz+' MHz at '+f2(o.volts)+' V').join(', ')}. Voltage moved with frequency in all ${s.total} observed transitions.`],
  ['The chip counts bus bits and execution-unit activity factors and computes its own power estimate on millisecond timescales.','not on this chip',
   'The loop reads the PMIC’s measured board power over I2C and the on-die PVT temperature. There is no activity counter anywhere in it, in the 353f20e source or in the older governor. He hedged that Esperanto might not have one; that hedge was right.'],
  ['Thermal sensors are part of the same loop, because leakage depends on temperature.','confirmed, and thermal has priority',
   `The temperature branch is tested before the power branch, and ${s.by_cause['thermal']||0} of ${s.down} down-steps were thermal-only.`],
  ['Cache data arrays sit behind leakage-suppression transistors; a lookup un-suppresses only the part it needs, at a small wake-up latency.','tied off in the open RTL',
   `The open RTL (Erbium, a later configuration of the same core, not the ET-SoC-1 chip) has per-minion sleep and isolation ports, tied off; no firmware line drives any power gating; and after 27 ms of idle no cache level shows a wake-up. Paired shifts: ${w.levels.map(l=>l.level+' '+sgn(l.paired_delta_cycles)).join(', ')} cycles. The L2 shift comes from a slow no-idle baseline, and the DRAM one is a row closing.`],
  ['Leakage is typically 5–30% of a design’s power, about 20% common.','this card is worse',
   `${Math.round(100*D.leak_fraction.busy_randn_80c)}% of a ${Math.round(D.busy_randn_80c)} W random-data matmul and ${Math.round(100*D.leak_model.A_at_80/(D.leak_model.P_fix+D.leak_model.A_at_80))}% of an idle card at 80 °C (the idle law, <a href="#what-that-costs">§4</a>).`],
  ['Leakage costs power, not correctness.','consistent, weakly tested',
   `Every result checked in this work was correct: the matmul benchmark checks its outputs bit-exact against a host reference, and the relay checks every element. The power sessions’ launches were not compared with a reference (none raised the tensor unit’s error flag). The idle of about ${ic.hours_idle} hours cannot show errors either way: nothing computed, DRAM ECC is compiled off and the SRAM ECC interrupt sources are never enabled.`]];
 document.getElementById('verdict').innerHTML='<thead><tr><th>What David Kanter said (paraphrased)</th><th>Verdict on the ET-SoC-1</th><th>Evidence</th></tr></thead><tbody>'+
  V.map(v=>`<tr><td>${v[0]}</td><td class="lvl">${v[1]}</td><td class="small">${v[2]}</td></tr>`).join('')+'</tbody>';})();

/* ---------- section 6-7: the three machines ---------- */
(function(){const C=D.cards,cf=C.config,sp=C.sptrace_aifoundry3;
 const R=[['Firmware release / PMIC','1.3.1 / 1.5.0','1.3.1 / 1.5.0','not readable'],
  ['TDP the <i>driver</i> reports','65 W','65 W','65 W'],
  ['TDP the <i>service processor</i> reports',cf.aifoundry2.tdp_w+' W','<b>'+cf.aifoundry3.tdp_w+' W</b>','—'],
  ['Software temperature threshold',cf.aifoundry2.temp_threshold_c+' °C',cf.aifoundry3.temp_threshold_c+' °C','—'],
  ['Power state the firmware reports',cf.aifoundry2.power_state_name,'<b>'+cf.aifoundry3.power_state_name+'</b>','—'],
  ['Minion clock ever observed above 600 MHz','yes, 700 and 800','<b>no</b>','—'],
  ['Usable for these measurements','yes','yes','<b>no</b>']];
 document.getElementById('cardcfg').innerHTML='<thead><tr><th>&nbsp;</th><th>aifoundry2</th><th>aifoundry3</th><th>aifoundry1 (2 cards)</th></tr></thead><tbody>'+
  R.map(r=>`<tr><td class="small">${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join('')+'</tbody>';
 const ev=D.sptrace_events;
 if(sp) document.getElementById('spcount').innerHTML=`That 8 KB window of the card's trace buffer holds <b>${sp.down_events} throttle-down events</b>`+
  (ev?` alternating with <b>${ev.idle} idle events</b>`+(ev.consecutive_idle_pairs?` (one idle event follows another ${ev.consecutive_idle_pairs===1?'once':ev.consecutive_idle_pairs+' times'})`:''):'')+
  `, and <b>${sp.up_events} throttle-up events</b>, every one of them printing a TDP level of ${sp.tdp_levels.join(', ')}. `+
  `One throttle-down per busy period is how the older governor logs, once per change of state (<a href="#method-and-what-is-not-established">§8</a>); `+
  `the 353f20e source would log on every pass or, at the lowest operating point, not at all.`;

 const P=C.patterns,W=700,H=348,L=52,R2=150,T=26,B=52;
 const {svg,tip,h}=host('cardsw',W,H);
 const mx=Math.max(...P.map(p=>Math.max(p.a2,p.a3,p.model)))*1.08;
 const bw=(W-L-R2)/P.length, y=v=>H-B-(H-B-T)*v/mx, x=i=>L+bw*i;
 axes(svg,{W,H,L,R:R2,T,B,x:i=>x(i),y,yt:[0,5,10,15,20,25],xt:[],yl:'switching power over idle, W'});
 P.forEach((p,i)=>{const g=el('g',{},svg),w=bw*0.26;
  el('rect',{x:x(i)+bw*0.10,y:y(p.a2),width:w,height:H-B-y(p.a2),fill:'var(--c1)'},g);
  el('rect',{x:x(i)+bw*0.38,y:y(p.a3),width:w,height:H-B-y(p.a3),fill:'var(--c2)'},g);
  el('line',{x1:x(i)+bw*0.06,x2:x(i)+bw*0.70,y1:y(p.model),y2:y(p.model),stroke:'var(--ink)','stroke-width':2,'stroke-dasharray':'4 3'},g);
  txt(g,x(i)+bw*0.38,H-B+16,p.values,'tick','middle');
  hover(g,tip,h,()=>`<b>${p.values}</b><br>aifoundry2 ${f2(p.a2)} W<br>aifoundry3 ${f2(p.a3)} W<br>model fitted on aifoundry2 ${f2(p.model)} W<br>ratio ${f2(p.a3/p.a2)}`);});
 [['aifoundry2 at 81 °C','var(--c1)'],['aifoundry3 at 56 °C','var(--c2)'],['model (aifoundry2 fit)','var(--ink)']]
  .forEach((l,i)=>{el('rect',{x:W-R2+8,y:T+6+i*20,width:11,height:11,fill:l[1]},svg);txt(svg,W-R2+25,T+16+i*20,l[0],'lab');});
 document.getElementById('cardswcap').textContent=
  `Each card at its own launch temperature, ${f2(C.launch.aifoundry2.T)} °C and ${f2(C.launch.aifoundry3.T)} °C, both at 600 MHz. `+
  `Idle power under those runs was ${f1(C.idle.aifoundry2)} W and ${f1(C.idle.aifoundry3)} W, and is subtracted.`;
 document.getElementById('scaletext').innerHTML=
  `The ordering is identical and so are the ratios between patterns. Applied to aifoundry3 with no change at all, `+
  `the aifoundry2 model is off by <b>${f2(C.rms_raw)} W rms</b>, worst case ${f2(C.max_raw)} W — and the error is not scatter, `+
  `it is a consistent ${Math.round(100*(1-C.scale))}% overestimate. Multiply every flip energy by one number, `+
  `<b>${f2(C.scale)}</b>, and the residual falls to <b>${f2(C.rms_scaled)} W rms</b> across a 1.9 to 25 W range, `+
  `which is as good as the model's own in-sample fit on the card it came from. Calibrating that one number on a single `+
  `operand pattern and predicting the other seven gives ${f2(C.loo.median_rms)} W rms in the median and `+
  `${f2(C.loo.worst)} W at worst; calibrate on a random-data run and it is ${f2(C.loo.per_pattern.randn)} W.`;

 const lk=C.leakage;
 document.getElementById('leaktab').innerHTML='<thead><tr><th class="num">aifoundry3 die °C</th><th class="num">measured idle W</th><th class="num">aifoundry2 law W</th><th class="num">difference</th><th class="num">samples</th></tr></thead><tbody>'+
  lk.idle_curve.map(r=>`<tr><td class="num">${r.T}</td><td class="num">${f2(r.W)}</td><td class="num">${f2(r.card2_law_W)}</td><td class="num">${(r.W-r.card2_law_W>=0?'+':'')}${f2(r.W-r.card2_law_W)}</td><td class="num">${r.n.toLocaleString('en-US')}</td></tr>`).join('')+
  `<tr><td class="num"><b>mean</b></td><td class="num"></td><td class="num"></td><td class="num"><b>${(lk.mean_offset_W>=0?'+':'')}${f2(lk.mean_offset_W)}</b></td><td class="num"></td></tr></tbody>`;
})();
