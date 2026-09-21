const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
function hover(g,tip,h,html){const s=ev=>{tip.innerHTML=html();tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.max(0,Math.min(ev.clientX-b.left+12,b.width-290))+'px';tip.style.top=(ev.clientY-b.top+12)+'px';};g.addEventListener('mousemove',s);g.addEventListener('mouseleave',()=>tip.style.display='none');}
function path(pts,x,y){return pts.map((p,i)=>`${i?'L':'M'}${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join(' ');}
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const C=D.ablation.configs,PW=D.model.power,V=0.517,F=600e6;

/* ---------- where the watts go: the model's decomposition of five states ---------- */
(function(){const leak=t=>PW.A_leak_at_80*Math.exp((t-80)/PW.T_L);const e=PW.e_fJ,ops=1024*F/546/1e15;const fl=D.flips;
 const dyn=p=>({clk:e.ffclk*fl[p].ffclk*ops,data:(e.mult*fl[p].mult+e.rest*fl[p].rest+e.bus*fl[p].bus)*ops});
 const rows=[['idle, 62 °C',62,null],['idle, 80 °C',80,null],['zeros, 80 °C',80,'zeros'],['ones, 80 °C',80,'ones'],['random fp32, 80 °C',80,'randn']];
 const PART=[['fixed: DDR, PCIe, always-on clocks, regulators','var(--ref)'],['leakage','var(--c2)'],['tensor state machines','var(--c3)'],['clocking the multiply-add registers','var(--c4)'],['data toggles','var(--bad)']];
 document.getElementById('stack-leg').innerHTML=PART.map(p=>`<span><i style="background:${p[1]}"></i>${p[0]}</span>`).join('');
 const W=900,rh=34,L=170,R=70,T=8,H=T+rows.length*rh+34;const {svg,tip,h}=host('stack',W,H);const x=v=>L+v/70*(W-L-R);
 for(let t=0;t<=70;t+=10){el('line',{x1:x(t),x2:x(t),y1:T,y2:H-30,class:'grid-line'},svg);txt(svg,x(t),H-12,t+' W','tick','middle');}
 rows.forEach((r,i)=>{const d=r[2]?dyn(r[2]):{clk:0,data:0};const parts=[PW.P_fix,leak(r[1]),r[2]?PW.p_sm_full_chip:0,d.clk,d.data];let acc=0;const yy=T+i*rh+5;const g=el('g',{},svg);txt(g,L-10,yy+16,r[0],'lab','end');
  parts.forEach((w,k)=>{if(w>0.05)el('rect',{x:x(acc),y:yy,width:Math.max(0.5,x(acc+w)-x(acc)-1),height:22,rx:2,fill:PART[k][1]},g);acc+=w;});txt(g,x(acc)+6,yy+16,f1(acc)+' W','lab-strong');
  hover(g,tip,h,()=>`<b>${r[0]}</b>: ${f1(acc)} W by the model`+parts.map((w,k)=>w>0.05?`<br>${PART[k][0]}: ${f1(w)} W`:'').join(''));});})();

/* ---------- power against active cores ---------- */
(function(){const pts=[['fp32_randn_8',256],['fp32_randn_16',512],['fp32_randn_24',768],['fp32_randn',1024]].filter(q=>C[q[0]]).map(q=>[q[1],C[q[0]].dyn,q[0]]);
 const W=440,H=360,L=50,R=16,T=16,B=40;const {svg,tip,h}=host('cores',W,H);const x=v=>L+v/1100*(W-L-R),y=v=>H-B-v/32*(H-B-T);
 for(const t of [0,10,20,30]){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,t,'tick','end');}
 for(const t of [0,256,512,768,1024])txt(svg,x(t),H-B+16,t,'tick','middle');txt(svg,(L+W-R)/2,H-4,'active minions (random fp32 matmul)','lab','middle');txt(svg,4,T-6,'W over idle','lab');
 const k=pts.reduce((a,p)=>a+p[0]*p[1],0)/pts.reduce((a,p)=>a+p[0]*p[0],0);el('line',{x1:x(0),y1:y(0),x2:x(1100),y2:y(1100*k),stroke:'var(--axis)','stroke-dasharray':'4 4'},svg);
 for(const p of pts){const g=el('g',{},svg);el('circle',{cx:x(p[0]),cy:y(p[1]),r:6,fill:'var(--bad)',stroke:'var(--surface)','stroke-width':1.5},g);hover(g,tip,h,()=>`${p[0]} minions: +${f1(p[1])} W, ${f1(1000*p[1]/p[0])} mW each`);}
 txt(svg,x(560),y(1100*k*0.45),`${f1(1000*k)} mW per active minion`,'lab');})();

/* ---------- energy per multiply-add by precision and data ---------- */
(function(){const rows=[];for(const t of ['int8','fp16','fp32'])for(const v of ['zeros','ones','randn']){const c=C[`${t}_${v}`];if(c)rows.push({t,v,c});}
 const W=440,H=360,L=50,R=16,T=16,B=58;const {svg,tip,h}=host('prec',W,H);const bw=(W-L-R)/rows.length;const ymax=7;const y=v=>H-B-v/ymax*(H-B-T);
 for(const t of [0,1,2,3,4,5,6,7]){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,t,'tick','end');}txt(svg,4,T-6,'pJ per multiply-add, over idle','lab');
 const COLV={zeros:'var(--c1)',ones:'var(--c4)',randn:'var(--bad)'};
 rows.forEach((r,i)=>{const g=el('g',{},svg);const v=r.c.pj_per_unit_dyn;el('rect',{x:L+i*bw+4,y:y(v),width:bw-8,height:Math.max(1,y(0)-y(v)),rx:2,fill:COLV[r.v]},g);
  txt(g,L+i*bw+bw/2,y(v)-5,v.toFixed(v<1?2:1),'lab-strong','middle');txt(g,L+i*bw+bw/2,H-B+15,{zeros:'zeros',ones:'ones',randn:'random'}[r.v],'tick','middle');
  if(r.v==='ones')txt(g,L+i*bw+bw/2,H-B+34,r.t,'lab-strong','middle');
  hover(g,tip,h,()=>`<b>${r.t}, ${r.v}</b><br>${f1(r.c.p80)} W board, +${f1(r.c.dyn)} W over idle<br>${(r.c.per_s/1e12).toFixed(2)}×10¹² multiply-adds per second (${r.c.cycles_per_op.toFixed(0)} cycles per op)<br>${v.toFixed(3)} pJ each over idle, ${r.c.pj_per_unit_board.toFixed(2)} pJ at the board`);});})();

/* ---------- leakage ---------- */
(function(){const pts=PW.idle_curve.filter(p=>p.n>=30);const W=440,H=360,L=50,R=16,T=16,B=40;const {svg,tip,h}=host('leak',W,H);
 const x=v=>L+(v-40)/(95-40)*(W-L-R),y=v=>H-B-(v-10)/(48-10)*(H-B-T);
 for(const t of [10,20,30,40]){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,t,'tick','end');}for(const t of [40,50,60,70,80,90])txt(svg,x(t),H-B+16,t,'tick','middle');
 txt(svg,(L+W-R)/2,H-4,'die temperature, °C','lab','middle');txt(svg,4,T-6,'idle board power, W','lab');
 const curve=[];for(let t=40;t<=95;t+=0.5)curve.push([t,PW.P_fix+PW.A_leak_at_80*Math.exp((t-80)/PW.T_L)]);
 el('path',{d:path(curve,x,y),fill:'none',stroke:'var(--c2)','stroke-width':2},svg);el('line',{x1:L,x2:W-R,y1:y(PW.P_fix),y2:y(PW.P_fix),stroke:'var(--axis)','stroke-dasharray':'4 4'},svg);txt(svg,W-R-4,y(PW.P_fix)-5,`not leakage: ${f1(PW.P_fix)} W`,'lab','end');
 for(const p of pts){const g=el('g',{},svg);el('circle',{cx:x(p.T),cy:y(p.P),r:4.5,fill:'var(--c1)'},g);hover(g,tip,h,()=>`${p.T} °C: ${f2(p.P)} W idle`);}})();

/* ---------- Esperanto's published voltage curve and this card ---------- */
(function(){const pub=[[0.3,8.5],[0.4,20],[0.67,118],[0.75,164],[0.9,275]];const W=440,H=360,L=50,R=16,T=16,B=40;const {svg,tip,h}=host('volt',W,H);
 const x=v=>L+(v-0.25)/(0.95-0.25)*(W-L-R),y=v=>H-B-Math.log10(v/5)/Math.log10(400/5)*(H-B-T);
 for(const t of [5,10,20,50,100,200,400]){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,t,'tick','end');}for(const t of [0.3,0.4,0.5,0.6,0.7,0.8,0.9])txt(svg,x(t),H-B+16,t.toFixed(1),'tick','middle');
 txt(svg,(L+W-R)/2,H-4,'minion core voltage, V','lab','middle');txt(svg,4,T-6,'chip or board power, W (log scale)','lab');
 el('path',{d:path(pub,x,y),fill:'none',stroke:'var(--ref)','stroke-width':2,'stroke-dasharray':'5 4'},svg);
 for(const p of pub){const g=el('g',{},svg);el('circle',{cx:x(p[0]),cy:y(p[1]),r:5,fill:'var(--ref)'},g);hover(g,tip,h,()=>`Esperanto's model, Hot Chips 33: ${p[1]} W per chip at ${p[0]} V${p[0]===0.9?' (the "highest voltage"; the slide gives no number, 0.9 V read off its axis)':''}`);}
 const ours=[[0.517,C.fp32_zeros.p80,'zeros, 600 MHz','var(--c1)'],[0.517,C.fp32_ones.p80,'ones, 600 MHz','var(--c4)'],[0.517,C.fp32_randn.p80,'random fp32, 600 MHz','var(--bad)']].concat(D.vf?D.vf.points:[]);
 for(const p of ours){const g=el('g',{},svg);el('circle',{cx:x(p[0]),cy:y(p[1]),r:6,fill:p[3],stroke:'var(--surface)','stroke-width':1.5},g);hover(g,tip,h,()=>`this card, board power: ${f1(p[1])} W at ${p[0].toFixed(2)} V (${p[2]})`);}
 txt(svg,x(0.31),y(11),'Esperanto’s model of one chip','lab');txt(svg,x(0.64),y(30),'this card, measured','lab');})();

/* ---------- tables ---------- */
(function(){const A=D.facts.a100,E=D.facts.et;const row=(n,a,e,note)=>`<tr><td>${n}</td><td class="num">${a}</td><td class="num">${e}</td><td class="small">${note||''}</td></tr>`;
 document.getElementById('cmp').innerHTML='<thead><tr><th></th><th class="num">A100 (SXM4)</th><th class="num">ET-SoC-1 card</th><th>Note</th></tr></thead><tbody>'+
  row('Process, transistors, die',`TSMC 7 nm · ${A.transistors_b} B · ${A.die_mm2} mm²`,`TSMC 7 nm · ${E.transistors_b} B · ${E.die_mm2} mm²`,'same process generation')+
  row('Dense matmul, measured',`${A.tflops} TFLOPS at ${A.watts} W`,`${f2(E.tflops)} TFLOPS at ${f1(E.watts)} W`,'A100: Horace He’s 8192³ bf16 run on random data at a 330 W limit. ET: fp32 TensorFMA on random data, board power at 80 °C')+
  row('Energy per FLOP, board',`${(A.watts/A.tflops).toFixed(2)} pJ`,`${(E.watts/E.tflops).toFixed(1)} pJ`,'the A100 is about five times better at dense matmul')+
  row('Idle',`${A.idle} W`,`${f1(E.idle62)} W at 62 °C, ${f1(E.idle80)} W at 80 °C`,'')+
  row('Power per transistor under load',`${(A.watts/A.transistors_b).toFixed(1)} nW`,`${(E.watts/E.transistors_b).toFixed(1)} nW`,'')+
  row('Power density under load',`${(A.watts/A.die_mm2).toFixed(2)} W/mm²`,`${(E.watts/E.die_mm2).toFixed(2)} W/mm²`,'board power over die area; the ET figure includes DRAM and regulators')+
  row('Core voltage and clock',`about ${A.volts} V · ${A.mhz} MHz max`,`${E.volts} V · ${E.mhz} MHz`,'A100 core voltage is not published: 0.75 V is nominal for 7 nm, GPUs run above it at full clock')+
  row('V² × f relative to the ET card',`${((A.volts/E.volts)**2*A.mhz/E.mhz).toFixed(1)}×`,'1×','the switching power of the same capacitance')+
  row('Memory',`HBM2e, ${A.mem_gbs} GB/s`,`LPDDR4x, ${E.mem_gbs} GB/s`,'')+'</tbody>';
 const e=PW.e_fJ;const cd=(w)=>(w/1024/(V*V*F)*1e9);
 const LIST=[['spin','integer loop on every minion (4 adds and a branch)'],['fp32_zeros','fp32 TensorFMA, zeros: every multiply-add gated'],['fp32_ones','fp32 TensorFMA, ones: registers clocked, no data toggles'],['fp32_randn','fp32 TensorFMA, random data'],['fp16_randn','fp16 TensorFMA, random data'],['int8_randn','int8 TensorFMA, random data'],['tload_l2','TensorLoad streaming from the shire’s L2 SRAM'],['tload_dram','TensorLoad streaming from LPDDR4x']].filter(q=>C[q[0]]);
 document.getElementById('cdyn').innerHTML='<thead><tr><th>Workload on all 1,024 minions</th><th class="num">board W at 80 °C</th><th class="num">over idle</th><th class="num">mW per minion</th><th class="num">C<sub>dynamic</sub> per minion, nF</th><th class="num">work per second</th><th class="num">pJ per unit of work, over idle</th></tr></thead><tbody>'+
  LIST.map(q=>{const c=C[q[0]];return `<tr><td>${q[1]}</td><td class="num">${f1(c.p80)}</td><td class="num">+${f1(c.dyn)}</td><td class="num">${f1(c.mw_per_minion)}</td><td class="num">${cd(c.dyn).toFixed(3)}</td><td class="num">${c.per_s?(c.per_s/1e12).toFixed(c.per_s<1e12?2:1)+'×10¹² '+c.unit+'s':''}</td><td class="num">${c.pj_per_unit_dyn?c.pj_per_unit_dyn.toFixed(c.pj_per_unit_dyn<1?2:1):''}</td></tr>`;}).join('')+
  `<tr><td><i>Esperanto’s design target (Hot Chips 33)</i></td><td></td><td></td><td class="num"><i>10</i></td><td class="num"><i>0.040</i></td><td class="num"><i>at 1 GHz, 0.425 V</i></td><td></td></tr></tbody>`;
})();
