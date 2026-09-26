/* Every chart is drawn with the shared toolkit (global CK, docs/reports/sources/chartkit.js): sized to its column,
   tooltips on hover, keyboard focus and tap, arrow keys between marks. */
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const C=D.ablation.configs,PW=D.model.power,V=0.517,F=600e6;

/* ---------- power against active cores ---------- */
(function(){const pts=[['fp32_randn_8',256],['fp32_randn_16',512],['fp32_randn_24',768],['fp32_randn',1024]].filter(q=>C[q[0]]).map(q=>[q[1],C[q[0]].dyn,q[0]]);
 const k=pts.reduce((a,p)=>a+p[0]*p[1],0)/pts.reduce((a,p)=>a+p[0]*p[0],0);   /* least squares through the origin: W per active minion */
 CK.frame('cores',{height:W=>W<600?300:360,minW:300,maxW:460,label:'Power over idle against the number of active minions',draw:ff=>{
  const W=ff.W,H=ff.H,L=44,R=14,T=26,B=40;const x=CK.lin(0,1100,L,W-R),y=CK.lin(0,32,H-B,T);
  CK.axes(ff,{x,y,L,R,T,B,xt:[0,256,512,768,1024],yt:[0,10,20,30],xfmt:v=>CK.fmt.num(v,0),yfmt:String,xl:'active minions (random fp32 matmul)',yl:'W over idle'});
  CK.el('line',{x1:x(0),y1:y(0),x2:x(1100),y2:y(1100*k),style:'stroke:var(--axis)','stroke-dasharray':'4 4'},ff.svg);
  CK.inside(ff,[CK.txt(ff.svg,W-R,y(1100*k*0.3),`${f1(1000*k)} mW per active minion`,'lab','end')]);   /* under the line, right-aligned */
  const nodes=pts.map(p=>{const c=CK.el('circle',{cx:x(p[0]),cy:y(p[1]),r:6,style:'fill:var(--bad);stroke:var(--surface)','stroke-width':1.5},ff.svg);
   CK.tip(ff,c,`${CK.fmt.num(p[0],0)} minions: +${f1(p[1])} W, ${f1(1000*p[1]/p[0])} mW each`);return c;});
  CK.keynav(ff,nodes);}});})();

/* ---------- energy per multiply-add by precision and data ---------- */
(function(){const rows=[];for(const t of ['int8','fp16','fp32'])for(const v of ['zeros','ones','randn']){const c=C[`${t}_${v}`];if(c)rows.push({t,v,c});}
 const COLV={zeros:'var(--c1)',ones:'var(--c4)',randn:'var(--bad)'},VN={zeros:'zeros',ones:'ones',randn:'random'},TT=['int8','fp16','fp32'];
 /* where the bars are too narrow for a word under each, a legend above names the colours */
 const lg=document.createElement('div');document.getElementById('prec').before(lg);
 CK.legend(lg,['zeros','ones','randn'].map(v=>({key:v,label:VN[v],mark:'box',color:COLV[v]})));
 CK.frame('prec',{height:W=>W<600?300:360,minW:300,maxW:460,label:'Energy per multiply-add by precision and data',draw:ff=>{
  const W=ff.W,H=ff.H,L=44,R=14,T=26,gap=10,ymax=7,bw=(W-L-R-2*gap)/rows.length,per=bw>=38,B=per?58:40;
  lg.style.display=per?'none':'';
  const y=CK.lin(0,ymax,H-B,T);
  CK.axes(ff,{x:CK.lin(0,1,L,W-R),y,L,R,T,B,xt:[],yt:[0,1,2,3,4,5,6,7],yfmt:String,yl:'pJ per multiply-add, over idle'});
  const nodes=[];
  rows.forEach((r,i)=>{const g=CK.el('g',{},ff.svg),v=r.c.pj_per_unit_dyn,x0=L+i*bw+TT.indexOf(r.t)*gap,cx=x0+bw/2;
   CK.el('rect',{x:x0+4,y:y(v),width:bw-8,height:Math.max(1,y(0)-y(v)),rx:2,style:'fill:'+COLV[r.v]},g);
   CK.txt(g,cx,y(v)-5,v.toFixed(v<1?2:1),'lab-strong','middle');
   if(per)CK.txt(g,cx,H-B+15,VN[r.v],'tick','middle');
   if(r.v==='ones')CK.txt(g,cx,H-B+(per?34:18),r.t,'lab-strong','middle');
   CK.tip(ff,g,()=>`<b>${r.t}, ${r.v}</b><br>${f1(r.c.p80)} W board, +${f1(r.c.dyn)} W over idle<br>${(r.c.per_s/1e12).toFixed(2)}×10¹² multiply-adds per second (${r.c.cycles_per_op.toFixed(0)} cycles per op)<br>${v.toFixed(3)} pJ each over idle, ${r.c.pj_per_unit_board.toFixed(2)} pJ at the board`);nodes.push(g);});
  CK.keynav(ff,nodes);}});})();

/* ---------- tables ---------- */
(function(){const A=D.facts.a100,E=D.facts.et;const row=(n,a,e,note)=>`<tr><td>${n}</td><td class="num">${a}</td><td class="num">${e}</td><td class="small">${note||''}</td></tr>`;
 const S2=D.second_card,r2=S2&&S2.patterns.randn;   /* aifoundry3's fp32 random matmul, at its own launch temperature */
 const h16=C.fp16_randn,tf16=2*h16.per_s/1e12;                       /* fp16 random: FLOPs are 2 per multiply-add */
 const pjA=A.watts/A.tflops,pj32=E.watts/E.tflops,pj16=h16.p80/tf16;  /* pJ per FLOP at the board */
 const mhzLo=Math.round(A.tflops/312*A.mhz/10)*10;                    /* 257 of the 312 bf16 peak TFLOPS needs at least this clock */
 const v2f=m=>((A.volts/E.volts)**2*m/E.mhz).toFixed(1);
 const mhz=m=>m.toLocaleString('en-US');
 document.getElementById('cmp').innerHTML='<thead><tr><th></th><th class="num">A100 (SXM4)</th><th class="num">ET-SoC-1 card</th><th>Note</th></tr></thead><tbody>'+
  row('Process, transistors, die',`TSMC 7 nm · ${A.transistors_b} B · ${A.die_mm2} mm²`,`TSMC 7 nm · &gt;${E.transistors_b} B · ${E.die_mm2} mm²`,'same process generation; Esperanto gives "over 24 billion" transistors')+
  row('Dense matmul, measured',`${A.tflops} TFLOPS bf16 at ${A.watts} W`,`${f2(E.tflops)} TFLOPS fp32 at ${f1(E.watts)} W<br>${f1(tf16)} TFLOPS fp16 at ${f1(h16.p80)} W`,'A100: Horace He’s 8192³ bf16 run on random data at a 330 W limit. ET: aifoundry2, TensorFMA on random data, board power at 80 °C; fp16 and bf16 are different formats'+
   (r2?`. aifoundry3, launched at ${f1(S2.launch_T)} °C: fp32 at ${f1(r2.p80)} W; fp16 was measured on aifoundry2 only`:''))+
  row('Energy per FLOP, board',`${pjA.toFixed(2)} pJ (bf16)`,`${pj32.toFixed(1)} pJ fp32<br>${pj16.toFixed(1)} pJ fp16`,'A100 bf16 tensor cores against fp32 and fp16 here'+(r2?` (aifoundry3: ${(r2.p80/r2.tflops).toFixed(1)} pJ fp32)`:'')+'; the fp32 CUDA-core comparison follows the table')+
  row('Idle',`${A.idle} W`,`${f1(E.idle62)} W at 62 °C<br>${f1(E.idle80)} W at 80 °C`,'ET: die temperature; the 62 °C figure is one reading after a night idle'+(r2?`. aifoundry3: ${f1(r2.idle)} W at ${f1(S2.launch_T)} °C`:''))+
  row('Power per transistor under load',`${(A.watts/A.transistors_b).toFixed(1)} nW`,`${(E.watts/E.transistors_b).toFixed(1)} nW`,'the ET figure counts 24 billion transistors')+
  row('Power density under load',`${(A.watts/A.die_mm2).toFixed(2)} W/mm²`,`${(E.watts/E.die_mm2).toFixed(2)} W/mm²`,'board power over die area; both include memory and regulators')+
  row('Core voltage and clock',`about ${A.volts} V · ${mhz(mhzLo)}–${mhz(A.mhz)} MHz`,`${E.volts} V · ${E.mhz} MHz`,`Neither is published. ${mhz(A.mhz)} MHz is the maximum boost. Under He’s 330 W cap on random data the clock is lower: 257 of the 312 peak TFLOPS needs at least ${mhz(mhzLo)} MHz, and if his zero-data run (295 TFLOPS) held ${mhz(A.mhz)} MHz, the random run was near 1,230. 0.75 V is nominal for 7 nm.`)+
  row('V² × f relative to the ET card',`${v2f(mhzLo)}–${v2f(A.mhz)}×`,'1×','the switching power of the same capacitance')+
  row('Memory',`HBM2 ${mhz(A.mem_gbs)} GB/s (40 GB)<br>HBM2e 2,039 GB/s (80 GB)`,`LPDDR4x, ${E.mem_gbs} GB/s`,'ET: the datasheet maximum; these cards’ 933 MHz DDR clock allows 119 GB/s')+'</tbody>';
 const e=PW.e_fJ;const cd=(w)=>(w/1024/(V*V*F)*1e9);
 const rate=c=>!c.per_s?'':c.unit==='byte'?(c.per_s>=1e12?(c.per_s/1e12).toFixed(2)+' TB':(c.per_s/1e9).toFixed(1)+' GB'):(c.per_s/1e12).toFixed(c.per_s<1e12?2:1)+'×10¹² '+c.unit+'s';
 const LIST=[['spin','integer loop on every minion (4 adds and a branch)'],['fp32_zeros','fp32 TensorFMA, zeros: every multiply-add gated'],['fp32_ones','fp32 TensorFMA, ones: registers clocked, no data toggles'],['fp32_randn','fp32 TensorFMA, random data'],['fp16_randn','fp16 TensorFMA, random data'],['int8_randn','int8 TensorFMA, random data'],['tload_l2','TensorLoad streaming from the shire’s L2 cache'],['tload_dram','TensorLoad streaming from LPDDR4x (DRAM)']].filter(q=>C[q[0]]);
 document.getElementById('cdyn').innerHTML='<thead><tr><th>Workload on all 1,024 minions</th><th class="num">board W at 80 °C</th><th class="num">over idle</th><th class="num">mW per minion, over idle</th><th class="num">C<sub>dynamic</sub> per minion, nF</th><th class="num">work per second</th><th class="num">pJ per unit of work, over idle</th></tr></thead><tbody>'+
  LIST.map(q=>{const c=C[q[0]];return `<tr><td>${q[1]}</td><td class="num">${f1(c.p80)}</td><td class="num">+${f1(c.dyn)}</td><td class="num">${f1(c.mw_per_minion)}</td><td class="num">${cd(c.dyn).toFixed(3)}</td><td class="num">${rate(c)}</td><td class="num">${c.unit==='byte'?'–':c.pj_per_unit_dyn?c.pj_per_unit_dyn.toFixed(c.pj_per_unit_dyn<1?2:c.pj_per_unit_dyn<100?1:0):''}</td></tr>`;}).join('')+
  `<tr><td><i>Esperanto’s design target (Hot Chips 33)</i></td><td></td><td></td><td class="num"><i>10 (total)</i></td><td class="num"><i>0.040</i></td><td class="num"><i>at 1 GHz, 0.425 V</i></td><td></td></tr></tbody>`;
 /* the note under the table: which card, aifoundry3's fp32 rows beside these, and where the per-byte energies live */
 const n3=document.getElementById('cdyn-a3');
 if(n3){const P3=S2&&S2.patterns,one=p=>{const q=P3[p],V3=q.mv/1000;return {mw:1000*q.dyn/1024,nf:q.dyn/1024/(V3*V3*F)*1e9,pj:q.dyn/(q.tflops*1e12/2)*1e12};};
  const t=P3?['zeros','ones','randn'].map(one):null,and=a=>a.slice(0,-1).join(', ')+' and '+a[a.length-1];
  n3.textContent='These rows are aifoundry2’s. '+(t?`On aifoundry3 (three runs each, launched at ${f1(S2.launch_T)} °C) the fp32 matmul on zeros, ones and random data switches `+
   `${and(t.map(q=>f1(q.mw)))} mW per minion over idle (${and(t.map(q=>q.nf.toFixed(3)))} nF; ${and(t.map(q=>q.pj.toFixed(2)))} pJ per multiply-add). `:'')+
   'The TensorLoad rows leave out an energy per byte: use the energy manual’s two-card values (Memory, in section 4).';}
})();

/* ---------- §1 as a ratio chart: A100 ÷ ET-SoC-1 for every metric the facts give on both chips ----------
   Each bar's length is the factor between the two chips on a log scale: to the right where the A100's value is the
   larger, to the left where it is the smaller. Colour gives the kind of metric (size, power, throughput, energy per
   FLOP); no bar claims a winner, because lower power is the card's premise, not a virtue on its own. A metric with two ET values (idle at 62 and 80 °C, fp32 and fp16, the A100's
   clock range) is a solid bar to the smaller factor and a light one on to the larger. Every ratio is computed here from
   D.facts (and, for fp16, the same ablation row the table uses), and each tooltip shows its inputs. */
(function(){const A=D.facts.a100,E=D.facts.et,num=CK.fmt.num,h16=C.fp16_randn;
 const has=(...v)=>v.every(x=>x!=null&&isFinite(x)&&x>0);
 const fx=v=>num(v,v>=10?0:1)+'×',rng=(a,b)=>b==null||fx(a)===fx(b)?fx(a):num(a,a>=10?0:1)+'–'+fx(b);
 const ET='ET-SoC-1 card',COL={size:'var(--ref)',power:'var(--c1)',thru:'var(--c4)',eff:'var(--c3)'};
 const tf16=h16?2*h16.per_s/1e12:null,mhzLo=has(A.tflops,A.mhz)?Math.round(A.tflops/312*A.mhz/10)*10:null;
 /* each metric: name, ratio(s) A100 ÷ ET (one value or [lo, hi]), and its kind: size, power, throughput (thru) or energy per FLOP (eff) */
 const M=[];
 const add=(o,ok)=>{if(ok)M.push(o);};
 add({name:'Transistors',r:[A.transistors_b/E.transistors_b],kind:'size',
  tip:`A100 ${num(A.transistors_b)} billion; ${ET} over ${num(E.transistors_b)} billion (Esperanto: “over 24 billion”), so the A100 has at most ${fx(A.transistors_b/E.transistors_b)} as many`},has(A.transistors_b,E.transistors_b));
 add({name:'Die area',r:[A.die_mm2/E.die_mm2],kind:'size',
  tip:`A100 ${num(A.die_mm2,0)} mm²; ${ET} ${num(E.die_mm2,0)} mm²: ratio ${num(A.die_mm2/E.die_mm2,2)}`},has(A.die_mm2,E.die_mm2));
 add({name:'Board power, matmul',low:'board power under a matmul',r:[A.watts/E.watts],kind:'power',
  tip:`A100 ${num(A.watts,0)} W (bf16, Horace He’s run at a 330 W limit); ${ET} ${num(E.watts,1)} W (fp32 random data, aifoundry2, 80 °C): ratio ${num(A.watts/E.watts,2)}`},has(A.watts,E.watts));
 const idl=[E.idle80,E.idle62].filter(v=>has(v));
 add({name:'Idle power',r:idl.map(v=>A.idle/v).sort((a,b)=>a-b),kind:'power',
  tip:`A100 ${num(A.idle,0)} W; ${ET} `+[[E.idle80,80],[E.idle62,62]].filter(q=>has(q[0])).map(q=>`${num(q[0],1)} W at ${q[1]} °C`).join(', ')+
   `: ratio ${idl.map(v=>A.idle/v).sort((a,b)=>a-b).map(v=>num(v,2)).join(' to ')}`},has(A.idle)&&idl.length>0);
 add({name:'Power per transistor',r:[(A.watts/A.transistors_b)/(E.watts/E.transistors_b)],kind:'power',
  tip:`A100 ${num(A.watts,0)} W ÷ ${num(A.transistors_b)} billion = ${num(A.watts/A.transistors_b,1)} nW; ${ET} ${num(E.watts,1)} W ÷ ${num(E.transistors_b)} billion = ${num(E.watts/E.transistors_b,1)} nW`},has(A.watts,A.transistors_b,E.watts,E.transistors_b));
 add({name:'Power per mm² (W/mm²)',low:'power per mm²',r:[(A.watts/A.die_mm2)/(E.watts/E.die_mm2)],kind:'power',
  tip:`A100 ${num(A.watts,0)} W ÷ ${num(A.die_mm2,0)} mm² = ${num(A.watts/A.die_mm2,2)} W/mm²; ${ET} ${num(E.watts,1)} W ÷ ${num(E.die_mm2,0)} mm² = ${num(E.watts/E.die_mm2,2)} W/mm²`},has(A.watts,A.die_mm2,E.watts,E.die_mm2));
 const v2f=m=>(A.volts/E.volts)**2*m/E.mhz;
 add({name:'V² × f',low:'V² × f',r:[v2f(mhzLo),v2f(A.mhz)],kind:'power',
  tip:`(${num(A.volts,2)} V ÷ ${num(E.volts,2)} V)² × (${num(mhzLo,0)} to ${num(A.mhz,0)} MHz ÷ ${num(E.mhz,0)} MHz). Neither the A100’s voltage nor its clock under the cap is published: about ${num(A.volts,2)} V, and ${num(mhzLo,0)} MHz is the least clock that gives ${num(A.tflops,0)} of the 312 peak TFLOPS`},has(A.volts,E.volts,A.mhz,E.mhz,mhzLo));
 const pjA=A.watts/A.tflops,pj32=E.watts/E.tflops,pj16=h16&&tf16?h16.p80/tf16:null;
 add({name:'Energy per FLOP',low:'energy per FLOP',r:[pj32,pj16].filter(v=>has(v)).map(v=>pjA/v).sort((a,b)=>a-b),kind:'eff',
  tip:`A100 ${num(A.watts,0)} W ÷ ${num(A.tflops,0)} TFLOPS = ${num(pjA,2)} pJ (bf16); ${ET} ${num(E.watts,1)} W ÷ ${num(E.tflops,2)} TFLOPS = ${num(pj32,2)} pJ (fp32)`+
   (pj16?`, ${num(h16.p80,1)} W ÷ ${num(tf16,1)} TFLOPS = ${num(pj16,2)} pJ (fp16)`:'')},has(A.watts,A.tflops,E.watts,E.tflops));
 add({name:'Matmul TFLOPS',low:'matmul TFLOPS',r:[A.tflops/E.tflops,tf16?A.tflops/tf16:null].filter(v=>has(v)).sort((a,b)=>a-b),kind:'thru',
  tip:`A100 ${num(A.tflops,0)} TFLOPS (bf16); ${ET} ${num(E.tflops,2)} TFLOPS (fp32)`+(tf16?`, ${num(tf16,1)} TFLOPS (fp16)`:'')},has(A.tflops,E.tflops));
 add({name:'Memory bandwidth',r:[A.mem_gbs/E.mem_gbs],kind:'thru',
  tip:`A100 HBM2 ${num(A.mem_gbs,0)} GB/s (40 GB); ${ET} LPDDR4x ${num(E.mem_gbs,0)} GB/s (the datasheet maximum)`},has(A.mem_gbs,E.mem_gbs));
 /* which chip's value is the larger, and by how much: a factor ≥ 1 and a side (+1: the A100's, −1: the ET card's) */
 for(const m of M){const up=m.r[0]>=1;   /* the A100's value is the larger one */
  m.f=m.r.map(v=>(up?v:1/v)).sort((a,b)=>a-b);
  m.up=up;m.side=up?1:-1;m.col=COL[m.kind];
  const fr=rng(m.f[0],m.f[m.f.length-1]);
  m.say=`the ${up?'A100':ET}’s is ${fr} the ${up?ET+'’s':'A100’s'}`;}
 CK.legend('ratio-leg',[{key:'s',label:'size',mark:'box',color:COL.size},{key:'p',label:'power',mark:'box',color:COL.power},
  {key:'t',label:'throughput',mark:'box',color:COL.thru},{key:'e',label:'energy per FLOP',mark:'box',color:COL.eff}]);
 const lab=m=>rng(m.f[0],m.f[m.f.length-1]);
 CK.frame('ratio',{height:W=>(W<600?44:32)*M.length+70,minW:300,maxW:760,label:'Ratio of the A100 to the ET-SoC-1 card for each metric, on a log scale: right where the A100’s value is larger, left where it is smaller',draw:ff=>{
  const nar=ff.narrow,W=ff.W,H=ff.H,svg=ff.svg,LW=nar?8:178,RP=8,T=34,B=36,rh=nar?44:32,bh=14,nodes=[];
  const cw=s=>7*s.length+10;   /* room for a factor label at a bar's end */
  const Lmax=Math.max(1.5,...M.filter(m=>m.side<0).map(m=>m.f[m.f.length-1])),Rmax=Math.max(1.5,...M.filter(m=>m.side>0).map(m=>m.f[m.f.length-1]));
  const padL=Math.max(20,...M.filter(m=>m.side<0).map(m=>cw(lab(m)))),padR=Math.max(20,...M.filter(m=>m.side>0).map(m=>cw(lab(m))));
  const k=(W-LW-RP-padL-padR)/(Math.log10(Lmax)+Math.log10(Rmax)),cx=LW+padL+k*Math.log10(Lmax);
  const X=(f,side)=>cx+side*k*Math.log10(f);
  /* grid: parity in the middle, then 2×, 5×, 10×, … on each side while they fit */
  const g=CK.el('g',{'aria-hidden':'true'},svg);
  for(const side of [-1,1])for(const t of [2,5,10,20,50,100])if(t<=(side<0?Lmax:Rmax)*1.02){const xx=X(t,side);
   CK.el('line',{x1:xx,x2:xx,y1:T,y2:H-B,class:'grid-line'},g);CK.txt(g,xx,H-B+16,t+'×','tick','middle');}
  CK.el('line',{x1:cx,x2:cx,y1:T-6,y2:H-B,stroke:'var(--axis)','stroke-width':1.5},g);
  CK.txt(g,cx,H-B+16,'1×','tick','middle');
  CK.txt(g,(LW+W-RP)/2,H-6,nar?'factor between the chips (log)':'factor between the two chips (log scale); 1× is parity','lab','middle');
  CK.txt(g,cx-8,T-12,'← A100 smaller','lab-strong','end');CK.txt(g,cx+8,T-12,'A100 larger →','lab-strong','start');
  M.forEach((m,i)=>{const y0=T+i*rh,yc=nar?y0+29:y0+rh/2,gr=CK.el('g',{},svg);
   CK.txt(gr,nar?LW:LW-10,nar?y0+13:yc+4,m.name,'lab',nar?'start':'end');
   const x0=X(1,m.side),x1=X(m.f[0],m.side),x2=X(m.f[m.f.length-1],m.side);
   const rect=(a,b,op)=>CK.el('rect',{x:Math.min(a,b),y:yc-bh/2,width:Math.max(1.5,Math.abs(b-a)),height:bh,rx:2,fill:m.col,opacity:op},gr);
   rect(x0,x1,1);if(m.f.length>1&&x2!==x1)rect(x1,x2,0.4);
   CK.txt(gr,x2+m.side*5,yc+4,lab(m),'lab-strong',m.side>0?'start':'end');
   CK.el('rect',{class:'ck-hit',x:Math.min(x0,x2)-4,y:yc-bh/2-4,width:Math.abs(x2-x0)+8,height:bh+8},gr);
   CK.tip(ff,gr,`<b>${m.name}</b>: ${m.say}<br>${m.tip}`);nodes.push(gr);});
  CK.keynav(ff,nodes);}});
 const lc=m=>m.low||m.name.charAt(0).toLowerCase()+m.name.slice(1),list=ms=>ms.map(m=>`${lc(m)} ${lab(m)}`).join(', ');
 const big=M.filter(m=>m.up),small=M.filter(m=>!m.up),by=k=>M.find(m=>m.kind===k&&m.name!=='Memory bandwidth');
 const pw=M.find(m=>m.name==='Board power, matmul'),tp=M.find(m=>m.name==='Matmul TFLOPS'),ef=M.find(m=>m.kind==='eff');
 document.getElementById('ratio-sum').textContent=`The A100’s value is the larger on ${list(big)}`+(small.length?`, and the smaller on ${list(small)}`:'')+'. '+
  (pw&&tp&&ef&&!ef.up?`It draws ${lab(pw)} the board power under a matmul but does ${lab(tp)} the FLOPS, so each FLOP costs this card ${lab(ef)} the A100’s energy. `:'')+
  'Each bar’s inputs are in its tooltip and in the table below.';
})();

/* ---------- Esperanto's published voltage curve and this card: 600 MHz points filled, 800 MHz points as rings ---------- */
(function(){const pub=[[0.3,8.5],[0.4,20],[0.67,118],[0.75,164],[0.9,275]];   /* Hot Chips 33 slide, W per chip (0.9 V read off its axis) */
 const vf=D.vf,COLV={zeros:'var(--c1)',ones:'var(--c4)',randn:'var(--bad)'},NM={zeros:'zeros',ones:'ones',randn:'random fp32'};
 const ours=[['zeros','fp32_zeros'],['ones','fp32_ones'],['randn','fp32_randn']].map(([k,c])=>({k,v:V,w:C[c].p80,ring:false,lab:`${NM[k]}: ${f1(C[c].p80)} W at 0.52 V, 600 MHz, 80 °C (strict start, seconds 1–3)`}));
 let dieR='';
 if(vf){const pk=vf.peaks_at||{},ts=Object.values(pk).map(q=>q.die_c);dieR=ts.length?`${Math.min(...ts)}–${Math.max(...ts)} °C`:'';
  for(const [k,key] of [['zeros','zeros800'],['ones','ones800'],['randn','randn800_peak']])if(vf[key]!=null)ours.push({k,v:vf.points[0][0],w:vf[key],ring:true,peak:k==='randn',
   lab:`${NM[k]}: ${f1(vf[key])} W at ${vf.points[0][0].toFixed(2)} V, 800 MHz`+(pk[k]?`, ${pk[k].die_c} °C (${pk[k].session} run ${pk[k].run}, ${pk[k].t_s.toFixed(1)} s after launch)`:'')+': the highest board reading before the governor stepped down'});}
 CK.legend('volt-leg',[{key:'z',label:'zeros',mark:'dot',color:COLV.zeros},{key:'o',label:'ones',mark:'dot',color:COLV.ones},{key:'r',label:'random fp32',mark:'dot',color:COLV.randn},
  {key:'f',label:'filled: 0.52 V, 600 MHz, 80 °C',mark:'dot',color:'var(--ink-2)'},{key:'g',label:`ring: 0.62 V, 800 MHz, ${dieR}, highest reading before the governor stepped down`,mark:'ring',color:'var(--ink-2)'},
  {key:'e',label:'Esperanto’s model of one chip (Hot Chips 33)',mark:'dash',color:'var(--ref)'}]);
 CK.frame('volt',{height:W=>W<600?320:340,label:'Chip power against core voltage: Esperanto’s model and this card’s board power',draw:ff=>{
  const W=ff.W,H=ff.H,L=44,R=14,T=26,B=40,x=CK.lin(0.25,0.95,L,W-R),y=CK.log(5,400,H-B,T);
  CK.axes(ff,{x,y,L,R,T,B,yt:[5,10,20,50,100,200,400],xt:ff.narrow?[0.3,0.5,0.7,0.9]:[0.3,0.4,0.5,0.6,0.7,0.8,0.9],xfmt:v=>v.toFixed(1),xl:'minion core voltage, V',yl:'chip or board power, W (log scale)'});
  CK.el('path',{d:CK.path(pub,x,y),style:'fill:none;stroke:var(--ref)','stroke-width':2,'stroke-dasharray':'5 4'},ff.svg);
  const pn=pub.map(p=>{const c=CK.el('circle',{cx:x(p[0]),cy:y(p[1]),r:4.5,style:'fill:var(--ref)'},ff.svg);
   CK.tip(ff,c,`Esperanto’s model, Hot Chips 33: ${p[1]} W per chip at ${p[0]} V${p[0]===0.9?' (the “highest voltage”; the slide gives no number, 0.9 V read off its axis)':''}`);return c;});
  const on=ours.map(o=>{const c=CK.el('circle',{cx:x(o.v),cy:y(o.w),r:6,style:o.ring?`fill:var(--surface);stroke:${COLV[o.k]}`:`fill:${COLV[o.k]};stroke:var(--surface)`,'stroke-width':o.ring?2.5:1.5},ff.svg);
   CK.tip(ff,c,`this card, board power: ${o.lab}`);
   if(o.peak)CK.txt(ff.svg,x(o.v)+10,y(o.w)+4,'peak, ≤ 0.3 s','lab');return c;});
  CK.keynav(ff,pn);CK.keynav(ff,on);}});
})();

/* ---------- the factors: from the A100's switching watts to this card's (both ends measured, the middle assumed) ---------- */
(function(){const A=D.facts.a100,SW=A.watts-A.idle;
 const MHZ_LO=Math.round(A.tflops/312*A.mhz/10)*10;     /* 257 of the A100's 312 bf16 peak TFLOPS needs at least this clock (NVIDIA datasheet) */
 const MHZ_LIKELY=Math.round(A.tflops/295*A.mhz/10)*10; /* if He's zero-data run (295 TFLOPS) held the 1,410 MHz boost */
 const st={va:A.volts,fa:MHZ_LIKELY,prec:'fp32'};
 const ctl=document.getElementById('fx-ctl');
 const mk=o=>CK.range(ctl.appendChild(document.createElement('div')),o);
 const rV=mk({label:'A100 core voltage',min:0.75,max:0.95,step:0.01,value:st.va,fmt:v=>v.toFixed(2)+' V',onInput:v=>{st.va=v;upd();}});
 const rF=mk({label:'A100 clock under the 330 W cap',min:MHZ_LO,max:A.mhz,step:10,value:st.fa,fmt:v=>v.toLocaleString('en-GB')+' MHz',onInput:v=>{st.fa=v;upd();}});
 const bx=ctl.appendChild(document.createElement('div'));bx.className='controls';bx.setAttribute('role','group');bx.setAttribute('aria-label','A100 clock');
 for(const [m,t] of [[MHZ_LO,'257/312 of peak'],[MHZ_LIKELY,'257/295: likely'],[A.mhz,'max boost']]){const b=bx.appendChild(document.createElement('button'));b.type='button';
  b.textContent=`${m.toLocaleString('en-GB')} MHz (${t})`;b.addEventListener('click',()=>rF.set(m));}
 CK.seg(ctl.appendChild(document.createElement('div')),{label:'this card',options:[['fp32','fp32'],['fp16','fp16']],value:'fp32',onChange:v=>{st.prec=v;upd();}});
 CK.legend('fx-leg',[{key:'e',label:'measured switching power (under load − idle)',mark:'box',color:'var(--ink-2)'},{key:'v',label:'÷ V²',mark:'box',color:'var(--c1)'},
  {key:'f',label:'÷ clock',mark:'box',color:'var(--c2)'},{key:'c',label:'÷ capacitance: the remainder',mark:'box',color:'var(--c3)'}]);
 const out=CK.readout('fx-out');let Z=null;
 function calc(){const c=C[st.prec+'_randn'],dyn=c.dyn,v2=(st.va/V)**2,fr=st.fa*1e6/F,tot=SW/dyn,cap=tot/(v2*fr);
  const tfE=2*c.per_s/1e12;   /* FLOPs are 2 per multiply-add */
  return {dyn,v2,fr,tot,cap,CA:SW/(st.va**2*st.fa*1e6)*1e9,CE:dyn/(V*V*F)*1e9,pjA:SW/A.tflops,pjAb:A.watts/A.tflops,pjE:dyn/tfE,pjEb:c.p80/tfE};}
 const fr=CK.frame('fx',{height:W=>W<600?440:330,label:'Waterfall from the A100’s switching power to this card’s, and energy per FLOP',draw:ff=>{if(!Z)return;
  const nar=ff.narrow,W=ff.W,H=ff.H,L=nar?22:250,R=nar?20:16,T=8,rh=nar?46:32,bh=16,x=CK.log(10,400,L,W-R),nodes=[];
  const lev=[SW,SW/Z.v2,SW/Z.v2/Z.fr,Z.dyn];
  const rows=[[`A100 switching: ${A.watts} − ${A.idle} W idle`,null,SW,'var(--ink-2)',`${CK.fmt.num(SW,0)} W`,'measured by Horace He and the datasheet'],
   [`÷ V²: (${st.va.toFixed(2)} ÷ ${V} V)²`,lev[1],lev[0],'var(--c1)',`÷ ${Z.v2.toFixed(2)}`,'the A100’s voltage is assumed'],
   [`÷ clock: ${st.fa.toLocaleString('en-GB')} ÷ 600 MHz`,lev[2],lev[1],'var(--c2)',`÷ ${Z.fr.toFixed(2)}`,'the A100’s clock under its cap is inferred'],
   ['÷ capacitance (the remainder)',lev[3],lev[2],'var(--c3)',`÷ ${Z.cap.toFixed(2)}`,'whatever voltage and clock do not explain'],
   [`this card, ${st.prec} random data`,null,Z.dyn,'var(--ink-2)',`${CK.fmt.num(Z.dyn,1)} W`,'measured: power under load − idle, 80 °C']];
  const g0=CK.el('g',{'aria-hidden':'true'},ff.svg),yAx=T+rows.length*rh+4;
  for(const t of [10,20,50,100,200,400]){CK.el('line',{x1:x(t),x2:x(t),y1:T,y2:yAx,class:'grid-line'},g0);CK.txt(g0,x(t),yAx+14,CK.fmt.num(t,0)+' W','tick','middle');}
  CK.txt(g0,W-R,yAx+30,'switching power, W (log scale)','lab','end');
  rows.forEach(([lab,a,b,c,val,why],i)=>{const y0=T+i*rh,by=nar?y0+20:y0+(rh-bh)/2,g=CK.el('g',{},ff.svg),x0=a==null?L:x(a);
   CK.el('rect',{x:0,y:y0,width:W,height:rh,class:'ck-hit'},g);
   CK.txt(g,nar?8:L-10,nar?y0+14:by+12,lab,'lab',nar?'start':'end');
   CK.el('rect',{x:x0,y:by,width:Math.max(2,x(b)-x0),height:bh,rx:2,style:'fill:'+c},g);
   if(a!=null)CK.el('line',{x1:x(b),x2:x(b),y1:by-rh+bh,y2:by+bh,style:'stroke:var(--axis)','stroke-dasharray':'2 2'},g);
   CK.txt(g,a==null?x(b)+6:x0-6,by+12,val,'lab-strong',a==null?'start':'end');
   CK.tip(ff,g,a==null?`<b>${lab}</b>: ${CK.fmt.num(b)} W, ${why}`:`<b>${lab}</b> = ${val.slice(2)}: ${CK.fmt.num(b)} W → ${CK.fmt.num(a)} W (${why})`);nodes.push(g);});
  /* per FLOP: switching (ring) and board (dot) energy, each chip */
  const y1=yAx+46,x2=CK.log(0.5,10,L,W-R),g1=CK.el('g',{'aria-hidden':'true'},ff.svg),rr=nar?40:26;
  CK.txt(g1,8,y1,nar?'energy per FLOP, pJ (log scale)':'energy per FLOP, pJ (log scale): ring switching, dot at the board, idle floor included','lab');
  if(nar)CK.txt(g1,8,y1+15,'ring switching, dot at the board','tick');
  const yb0=y1+(nar?40:22);
  for(const t of [0.5,1,2,5,10]){CK.el('line',{x1:x2(t),x2:x2(t),y1:yb0-12,y2:H-20,class:'grid-line'},g1);CK.txt(g1,x2(t),H-6,CK.fmt.num(t,t<1?1:0),'tick','middle');}
  [['A100, bf16 tensor cores',Z.pjA,Z.pjAb],[`this card, ${st.prec}`,Z.pjE,Z.pjEb]].forEach(([lab,a,b],i)=>{const yy=yb0+i*rr,g=CK.el('g',{},ff.svg);
   const vt=`${a.toFixed(a<2?2:1)} → ${b.toFixed(b<2?2:1)} pJ`;   /* the precision of the readout below */if(nar)CK.txt(g,8,yy-8,`${lab}: ${vt}`,'lab');else CK.txt(g,L-10,yy+4,lab,'lab','end');const ym=nar?yy+6:yy;
   CK.el('line',{x1:x2(a),x2:x2(b),y1:ym,y2:ym,style:'stroke:var(--ink-2)','stroke-width':2},g);
   CK.el('circle',{cx:x2(a),cy:ym,r:5,style:'fill:var(--surface);stroke:var(--ink)','stroke-width':2},g);CK.el('circle',{cx:x2(b),cy:ym,r:5,style:'fill:var(--ink)'},g);
   if(!nar)CK.txt(g,x2(b)+9,ym+4,vt,'tick');
   CK.tip(ff,g,`<b>${lab}</b>: switching ${a.toFixed(2)} pJ per FLOP; at the board ${b.toFixed(2)} pJ`);nodes.push(g);});
  CK.keynav(ff,nodes);}});
 function upd(){Z=calc();fr.redraw();
  out.set(`V² <b>${Z.v2.toFixed(2)}×</b> · clock <b>${Z.fr.toFixed(2)}×</b> · capacitance <b>${Z.cap.toFixed(2)}×</b> (the remainder) = ${Z.tot.toFixed(2)}×, with `+
   `${CK.fmt.num(Z.CA,0)} nF switched on the A100 against ${CK.fmt.num(Z.CE,0)} nF here. The operating point alone is ${(Z.v2*Z.fr).toFixed(1)}×. `+
   `Per FLOP, switching ${Z.pjA.toFixed(2)} against ${Z.pjE.toFixed(Z.pjE<2?2:1)} pJ, at the board ${Z.pjAb.toFixed(2)} against ${Z.pjEb.toFixed(1)} pJ.`);}
 upd();
})();

/* ---------- Esperanto's equation on this card: fixed + leakage(T) + extra idle at voltage + C·V²·f, per workload ---------- */
(function(){const vf=D.vf,law=t=>PW.P_fix+PW.A_leak_at_80*Math.exp((t-80)/PW.T_L),leak=t=>PW.A_leak_at_80*Math.exp((t-80)/PW.T_L);
 /* the extra idle measured at 0.62 V over the 0.52 V law, at the mid temperature of those readings */
 const V8=vf?vf.points[0][0]:0.618,T8=vf?(vf.die_c.idle800[0]+vf.die_c.idle800[1])/2:65,EXTRA=vf?vf.idle800-law(T8):0;
 const ops=1024*F/546/1e15,e=PW.e_fJ,fl=D.flips;
 const WL=[['idle','idle',null],['spin','integer loop','spin'],['fp32_zeros','fp32 zeros','fp32_zeros'],['fp32_ones','fp32 ones','fp32_ones'],['fp32_randn','fp32 random','fp32_randn'],
  ['fp16_randn','fp16 random','fp16_randn'],['int8_randn','int8 random','int8_randn']].filter(q=>!q[2]||C[q[2]]);
 const SPLIT={fp32_zeros:'zeros',fp32_ones:'ones',fp32_randn:'randn'};
 const PART=[['fix','fixed: the idle law’s constant (a fit, not a block split)','var(--ref)'],['leak','leakage (the idle law’s best-fit split)','var(--c2)'],['xtra','extra idle at this voltage','var(--c5)'],
  ['sm','tensor state machines','var(--c3)'],['clk','clocking the multiply-add registers','var(--c4)'],['data','data toggles','var(--bad)'],['sw','switching (not split)','var(--c7)']];
 const st={w:'fp32_randn',v:V,f:600,t:80,act:1024,xtra:true};
 function calc(){const c=st.w==='idle'?null:C[st.w],k=(st.v/V)**2*(st.f*1e6/F)*(c?st.act/c.minions:0),inR=st.v>=V-1e-6&&st.v<=V8+1e-6;
  const w={fix:PW.P_fix,leak:leak(st.t),xtra:st.xtra&&inR?EXTRA*(st.v-V)/(V8-V):0,sm:0,clk:0,data:0,sw:0};
  if(c){const q=SPLIT[st.w];
   if(q&&fl[q]){const m={sm:PW.p_sm_full_chip,clk:e.ffclk*fl[q].ffclk*ops,data:(e.mult*fl[q].mult+e.rest*fl[q].rest+e.bus*fl[q].bus)*ops},sm=m.sm+m.clk+m.data;
    for(const kk of ['sm','clk','data'])w[kk]=m[kk]/sm*c.dyn*k;}   /* the measured switching, split in the flip model's proportions */
   else w.sw=c.dyn*k;}
  const swt=w.sm+w.clk+w.data+w.sw;return {c,w,swt,inR,board:w.fix+w.leak+w.xtra+swt};}
 /* controls */
 const ctl=document.getElementById('eq-ctl');
 CK.seg(ctl.appendChild(document.createElement('div')),{label:'workload',options:WL.map(q=>[q[0],q[1]]),value:st.w,onChange:v=>{st.w=v;upd();}});
 const mk=o=>CK.range(ctl.appendChild(document.createElement('div')),o);
 const rV=mk({label:'core voltage',min:0.40,max:0.90,step:0.001,value:st.v,fmt:v=>v.toFixed(3)+' V',onInput:v=>{st.v=v;upd();}});
 const rF=mk({label:'clock',min:400,max:1410,step:10,value:st.f,fmt:v=>v.toLocaleString('en-GB')+' MHz',onInput:v=>{st.f=v;upd();}});
 const rT=mk({label:'die temperature',min:50,max:90,step:0.5,value:st.t,fmt:v=>v.toFixed(1)+' °C',onInput:v=>{st.t=v;upd();}});
 const rA=mk({label:'active minions',min:0,max:1024,step:32,value:st.act,fmt:v=>v.toLocaleString('en-GB'),onInput:v=>{st.act=v;upd();}});
 const bx=ctl.appendChild(document.createElement('div'));bx.className='controls';bx.setAttribute('role','group');bx.setAttribute('aria-label','operating points');
 const pre=(t,v,f,T)=>{const b=bx.appendChild(document.createElement('button'));b.type='button';b.textContent=t;b.addEventListener('click',()=>{rV.set(v);rF.set(f);if(T!=null)rT.set(T);});};
 pre(`this card at 80 °C (${V} V, 600 MHz)`,V,600,80);pre(`800 MHz point (${V8} V, ${T8} °C)`,V8,800,T8);
 pre('Esperanto’s target (0.425 V, 1 GHz)',0.425,1000,null);pre('a GPU’s point (0.85 V, 1,410 MHz)',0.85,1410,null);
 const xb=bx.appendChild(document.createElement('button'));xb.type='button';xb.setAttribute('aria-pressed','true');
 xb.textContent=vf?`add the extra idle measured at ${V8} V (${f1(vf.idle800)} W at ${vf.die_c.idle800.join('–')} °C)`:'extra idle';
 xb.addEventListener('click',()=>{st.xtra=!st.xtra;xb.setAttribute('aria-pressed',String(st.xtra));upd();});
 CK.legend('eq-leg',PART.map(([k,l,c])=>({key:k,label:l,mark:'box',color:c})).concat([{key:'m',label:'measured (faint: at another operating point)',mark:'line',color:'var(--ink)'}]));
 const out=CK.readout('eq-out');let Z=null;
 /* measured board power for the chosen workload: [V, MHz, °C, W, what] */
 function measured(){const c=st.w==='idle'?null:C[st.w],m=[];
  if(st.w==='idle'){m.push([V,600,80,C.fp32_randn.idle,'idle before the strict runs, 80 °C']);
   if(vf){m.push([V,600,null,vf.idle600,`idle at 600 MHz, ${vf.die_c.idle600.join('–')} °C`]);m.push([V8,800,T8,vf.idle800,`idle at 800 MHz, ${vf.die_c.idle800.join('–')} °C`]);}}
  else{m.push([V,600,80,c.p80,'strict start, 80 °C, seconds 1–3']);const q=SPLIT[st.w];
   const key={zeros:'zeros800',ones:'ones800',randn:'randn800_peak'}[q];
   if(vf&&key&&vf[key]!=null)m.push([V8,800,vf.peaks_at&&vf.peaks_at[q]?vf.peaks_at[q].die_c:null,vf[key],'800 MHz from a cool die: the highest reading before the governor stepped down']);}
  return m;}
 const fb=CK.frame('stack',{height:W=>W<600?150:140,label:'Board power by term for the chosen workload and operating point',draw:ff=>{if(!Z)return;
  const W=ff.W,H=ff.H,L=12,R=16,y0=40,bh=34,m=measured(),mx=Math.max(100,Z.board*1.08,...m.map(q=>q[3]*1.08)),x=CK.lin(0,Math.ceil(mx/20)*20,L,W-R),nodes=[];
  const defs=CK.el('defs',{},ff.svg),pat=CK.el('pattern',{id:'eq-hatch',width:7,height:7,patternUnits:'userSpaceOnUse',patternTransform:'rotate(45)'},defs);
  CK.el('line',{x1:0,y1:0,x2:0,y2:7,style:'stroke:var(--ref)','stroke-width':2},pat);
  for(const t of x.ticks(Math.max(3,Math.round(W/90)))){CK.el('line',{x1:x(t),x2:x(t),y1:y0-10,y2:y0+bh+10,class:'grid-line'},ff.svg);CK.txt(ff.svg,x(t),y0+bh+26,CK.fmt.num(t,0)+' W','tick','middle');}
  const order=Z.inR?['fix','leak','xtra','sm','clk','data','sw']:['sm','clk','data','sw'];let acc=0;
  for(const k of order){const v=Z.w[k];if(v<0.02)continue;const pp=PART.find(q=>q[0]===k);
   const r=CK.el('rect',{x:x(acc),y:y0,width:Math.max(1,x(acc+v)-x(acc)-2),height:bh,rx:2,style:'fill:'+pp[2]},ff.svg);
   CK.tip(ff,r,`<b>${pp[1]}</b>: ${v.toFixed(1)} W`);nodes.push(r);acc+=v;}
  if(!Z.inR){const r=CK.el('rect',{x:x(acc),y:y0,width:Math.max(0,W-R-x(acc)),height:bh,style:'fill:url(#eq-hatch);stroke:var(--ref)','stroke-dasharray':'4 3'},ff.svg);
   CK.txt(ff.svg,W-R,y0-10,'+ fixed and leakage: not measured at this voltage','lab','end');
   CK.tip(ff,r,'Leakage and the idle floor were measured only at 0.517 and 0.618 V; outside that range only switching is priced');nodes.push(r);}
  else CK.txt(ff.svg,Math.min(x(acc)+6,W-R),y0-10,`${Z.board.toFixed(1)} W at the board`,'lab-strong',x(acc)+6>W-R-130?'end':'start');
  for(const [v,f,t,w,what] of m){const g=CK.el('g',{},ff.svg),here=Math.abs(v-st.v)<0.002&&Math.abs(f-st.f)<5&&st.act===1024;
   CK.el('line',{x1:x(w),x2:x(w),y1:y0-4,y2:y0+bh+4,style:'stroke:var(--ink)','stroke-width':2.5,opacity:here?1:0.35},g);
   CK.el('rect',{x:x(w)-6,y:y0-6,width:12,height:bh+12,class:'ck-hit'},g);
   CK.tip(ff,g,`<b>measured ${f1(w)} W</b> at ${v} V, ${f} MHz: ${what}${here?'':' (a different operating point from the one set above)'}`);nodes.push(g);}
  CK.keynav(ff,nodes);}});
 const fl2=CK.frame('leak',{height:W=>W<600?240:220,maxW:520,label:'Idle board power against die temperature with the idle law',draw:ff=>{
  const W=ff.W,H=ff.H,L=40,R=12,T=24,B=38,x=CK.lin(48,92,L,W-R),y=CK.lin(10,46,H-B,T),nodes=[];
  CK.axes(ff,{x,y,L,R,T,B,xt:[50,60,70,80,90],yt:[10,20,30,40],xl:'die temperature, °C',yl:'idle board power, W'});
  const cv=[];for(let t=48;t<=92;t+=0.5)cv.push([t,law(t)]);
  CK.el('path',{d:CK.path(cv,x,y),style:'fill:none;stroke:var(--c2)','stroke-width':2},ff.svg);
  CK.el('line',{x1:L,x2:W-R,y1:y(PW.P_fix),y2:y(PW.P_fix),style:'stroke:var(--axis)','stroke-dasharray':'4 4'},ff.svg);CK.txt(ff.svg,L+4,y(PW.P_fix)-5,`fixed part, best fit: ${f1(PW.P_fix)} W`,'lab');
  for(const p of PW.idle_curve.filter(p=>p.n>=30)){const c=CK.el('circle',{cx:x(p.T),cy:y(p.P),r:4,style:'fill:var(--c1)'},ff.svg);
   CK.tip(ff,c,`${p.T} °C: ${f2(p.P)} W idle (${p.n.toLocaleString('en-GB')} samples at 0.52 V, 600 MHz)`);nodes.push(c);}
  if(vf){const c=CK.el('circle',{cx:x(T8),cy:y(vf.idle800),r:5,style:'fill:var(--surface);stroke:var(--c5)','stroke-width':2.5},ff.svg);
   CK.tip(ff,c,`idle at ${V8} V, 800 MHz: ${f1(vf.idle800)} W at ${vf.die_c.idle800.join('–')} °C, ${f1(EXTRA)} W above the 0.52 V law`);nodes.push(c);}
  CK.el('line',{x1:x(st.t),x2:x(st.t),y1:T,y2:H-B,style:'stroke:var(--ink)','stroke-dasharray':'3 3'},ff.svg);
  const d=CK.el('circle',{cx:x(st.t),cy:y(law(st.t)),r:5.5,style:'fill:var(--c2);stroke:var(--surface)','stroke-width':1.5},ff.svg);
  CK.tip(ff,d,`the law at ${st.t.toFixed(1)} °C: ${f1(law(st.t))} W idle, ${f1(leak(st.t))} W of it leakage in the best-fit split`);nodes.push(d);
  nodes.sort((a,b)=>+a.getAttribute('cx')-+b.getAttribute('cx'));CK.keynav(ff,nodes);}});
 function upd(){Z=calc();fb.redraw();fl2.redraw();const c=Z.c,sw=Z.swt,k=(st.v/V)**2*st.f*1e6/F;
  const permin=st.act&&c?`${f1(1000*sw/st.act)} mW per active minion (Esperanto’s budget: 10 mW per minion, leakage included)`:'';
  const pj=c&&c.per_s&&st.act?sw/(c.per_s*(st.f*1e6/F)*(st.act/c.minions))*1e12:null;
  const unit=pj!=null?`${pj.toFixed(pj<1?2:1)} pJ per ${c.unit==='MAC'?'multiply-add':c.unit} over idle`:'';
  const head=Z.inR?`<b>${Z.board.toFixed(1)} W</b> at the board: ${f1(Z.w.fix)} fixed + ${f1(Z.w.leak)} leakage (the idle law’s best-fit split)`+(Z.w.xtra>0.05?` + ${f1(Z.w.xtra)} extra idle at this voltage`:'')+` + ${f1(sw)} switching`
   :`<b>${f1(sw)} W</b> switching (leakage not measured here)`;
  out.set(`${head}. Switching scales by ${k.toFixed(3)}× from 0.517 V and 600 MHz`+[permin,unit].filter(Boolean).map(t=>'; '+t).join('')+'.');}
 upd();
})();

/* ---------- numbers in the prose, from the data ---------- */
(function(){const put=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v;},vf=D.vf,M=D.model;
 if(vf){const V8=vf.points[0][0],pred=(V8/V)**2*800/600,pairs={z:[vf.zeros800-vf.idle800,vf.zeros600_dyn],o:[vf.ones800-vf.idle800,vf.ones600-vf.idle600],r:[vf.randn800_peak-vf.idle800,vf.randn600-vf.idle600]};
  const ts=[...vf.die_c.idle600,...vf.die_c.idle800,...Object.values(vf.peaks_at||{}).map(q=>q.die_c)];
  put('vf-T',`${Math.min(...ts)} to ${Math.max(...ts)}`);put('vf-z6',f1(pairs.z[1]));put('vf-o8',f1(pairs.o[0]));put('vf-o6',f1(pairs.o[1]));
  put('vf-r8',f1(pairs.r[0]));put('vf-r6',f1(pairs.r[1]));
  /* the V²f check rests on random data; zeros (two runs 0.5 W apart on about 4 W over idle) do not test it */
  const ro=pairs.o[0]/pairs.o[1],rr=pairs.r[0]/pairs.r[1],pct=v=>`${Math.round(100*(v/pred-1))}%`;
  put('vf-rr',f2(rr));put('vf-ro',f1(ro));put('vf-pred',f2(pred));put('vf-devr',pct(rr));put('vf-devo',pct(ro));
  put('vf-dev2',`${Math.round(100*Math.max(Math.abs(ro/pred-1),Math.abs(rr/pred-1)))}%`);
  const ep=[ro,rr].map(v=>v/(800/600));put('vf-epo',`${f1(Math.min(...ep))}–${f1(Math.max(...ep))}`);put('vf-epo2',`${f1(Math.min(...ep))}–${f1(Math.max(...ep))}`);put('vf-v2',f2((V8/V)**2));
  const ic=M.power.idle_curve,a=ic.find(q=>q.T===64),b=ic.find(q=>q.T===66);if(a&&b)put('vf-slope',f1((b.P-a.P)/2));
  const it=[...vf.die_c.idle600,...vf.die_c.idle800];
  put('vf-i8',f1(vf.idle800));put('vf-i6',f1(vf.idle600));put('vf-iT',`${Math.min(...it)}–${Math.max(...it)}`);}
 if(M.step_open){put('lg-lam',f2(M.power.lambda_at_80));put('lg-R',f2(M.R_total));put('lg-10m',f1(M.step_open[600]));put('lg-gain',`${f2(M.power.lambda_at_80)} × ${f2(M.R_total)} = ${f2(M.loop_gain_at_80)}`);}
 const d=C.tload_dram,l=C.tload_l2;
 /* this session's own pJ per byte is left out (one aifoundry2 session); the prose quotes the energy manual's two-card values */
 if(d){put('mem-dg',f1(d.per_s/1e9));put('mem-dpct',Math.round(100*d.per_s/119e9)+'%');put('mem-dw',f1(d.dyn));}   /* 119 GB/s: these cards' 933 MHz DDR clock */
 if(l){put('mem-lt',f2(l.per_s/1e12));put('mem-lw',f1(l.dyn));}
 put('m-rn',f1(C.fp32_randn.p80));
})();
