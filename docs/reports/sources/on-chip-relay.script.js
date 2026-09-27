/* Hand it to the next shire. Every number comes from D (onchip.json, built by workloads/onchip/analyze_onchip.py)
   except the pooled rerun energies in POOLED below. Charts use the shared toolkit CK (docs/reports/sources/chartkit.js). */
const $=id=>document.getElementById(id);
const f0=v=>v.toFixed(0),f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const num=CK.fmt.num, n0=v=>num(v,0);
const g1=v=>num(v,1);                                  // GB/s to one decimal, with separators
const gb=v=>v<100?num(v,1):num(v,0);                   // GB/s at chart precision: 47.9, 379, 1,263
const pj=v=>v<5?f2(v):f1(v);                           // pJ per byte: 3.99, 8.6, 105.7
const pjr=q=>{const f=q.mean<5?f2:f1;return `${f(q.mean)} [${f(q.lo)}–${f(q.hi)}]`;};   // mean [range] at the mean's precision
const MED=[['dram','write it to DRAM, read it back next stage','var(--c2)','DRAM'],
           ['hop','write it where the next shire will read it','var(--c1)','next shire'],
           ['scp',"keep it in this shire's own scratchpad",'var(--c3)','own shire']];
const A2=D.cards[0], A3=D.cards[1], H=D.headline[A2], H3=D.headline[A3];
const CS=CK.cardsIn(D.cards), lab=c=>CK.card(c).label;   // every card, in the registry's order (26 Sep: three)
const OFF=D.offsets||D.distance;                          // every ring offset measured (claims-v3: 1..31)
/* a card's registry mark at (x, y) in a colour; a ring is drawn hollow so it never hides the first card's dot under it */
const cmark=(g,c,x,y,col,big)=>{const ring=CK.card(c).mark==='ring',e=CK.cardMark(g,c,x,y,ring?(big?9:7):(big?5.5:4),col);
 if(ring){e.style.fill='none';e.style.strokeWidth='1.5';} e.setAttribute('aria-hidden','true');return e;};
const WORD=['no','one','two','three','four','five','six','seven','eight','nine'];
const word=n=>WORD[n]||n0(n);
const andL=a=>a.length<2?a.join(''):a.slice(0,-1).join(', ')+' and '+a[a.length-1];
const rng=(vals,fmt)=>{const a=fmt(Math.min(...vals)),b=fmt(Math.max(...vals));return a===b?a:a+'–'+b;};
const pear=(xs,ys)=>{const n=xs.length,mx=xs.reduce((a,b)=>a+b)/n,my=ys.reduce((a,b)=>a+b)/n;
 let sxy=0,sxx=0,syy=0;xs.forEach((x,i)=>{sxy+=(x-mx)*(ys[i]-my);sxx+=(x-mx)**2;syy+=(ys[i]-my)**2;});
 return {r:sxy/Math.sqrt(sxx*syy),slope:sxy/sxx,icpt:my-sxy/sxx*mx};};

/* Pooled energies, per byte moved (relay_pj_per_byte) and per byte read (levels_pj_per_byte; the scratchpads by the contents
   each pass prefilled, levels_by_contents_pj_per_byte), from docs/reports/data/2026-09-23-energy-manual/reruns.json, written by
     python3 tools/ettelem/analyze_reruns.py docs/reports/data/2026-09-23-reruns-aifoundry2-warm        docs/reports/data/2026-09-23-reruns-aifoundry3 --v3-rl docs/reports/data/2026-09-25-claims-v3/raw --out reruns.json
   i.e. the version-3 check's V3-RL passes, six on each of three cards (26 September); this page's 22 September session is
   not among them. Copied here (4 decimals, by a script over reruns.json) rather than read as data: the page builds from
   onchip.json alone, and reruns.json once took this page's onchip.json as its first relay pass (PLAN2 DP-6). Update
   both together if the reruns change. */
const POOLED={"relay":{"dram":{"mean":116.2426,"lo":104.5151,"hi":135.3423,"n":18,"per_card":{"aifoundry1-c1":{"mean":129.8818,"n":6},"aifoundry2":{"mean":111.3282,"n":6},"aifoundry3":{"mean":107.5177,"n":6}}},"scp":{"mean":4.3392,"lo":3.7535,"hi":5.0667,"n":18,"per_card":{"aifoundry1-c1":{"mean":4.8567,"n":6},"aifoundry2":{"mean":4.0504,"n":6},"aifoundry3":{"mean":4.1106,"n":6}}},"hop":{"mean":8.9236,"lo":7.627,"hi":10.1811,"n":18,"per_card":{"aifoundry1-c1":{"mean":9.8876,"n":6},"aifoundry2":{"mean":8.6085,"n":6},"aifoundry3":{"mean":8.2746,"n":6}}}},"read":{"dram":{"mean":114.5925,"lo":89.0235,"hi":141.263,"n":18},"scp-local":{"zeros":{"mean":2.2527,"lo":2.0636,"hi":2.6115,"n":9},"random":{"mean":4.4,"lo":3.9415,"hi":5.0774,"n":9}},"scp-remote":{"zeros":{"mean":5.0971,"lo":4.4008,"hi":6.4511,"n":9},"random":{"mean":11.8338,"lo":9.5305,"hi":14.4254,"n":9}}}};

/* The three-card check of the own scratchpad's read energy (V3-RL, 26 September), copied from
   docs/reports/data/2026-09-25-claims-v3/results/rl.json: RL-h's per-card means by contents, pJ per byte (RL-g finds no
   difference between aifoundry2 and aifoundry3; RL-h, that the old per-card split was the data read). */
const RL3={h:{zeros:{aifoundry2:2.1124,aifoundry3:2.1003,'aifoundry1-c1':2.5454},random:{aifoundry2:4.1258,aifoundry3:4.042,'aifoundry1-c1':5.0323}}};

/* ---------- KPIs, the lede's computed spans and the two-card line of section 7 ---------- */
(function(){
 $('k1').textContent=(H.hop.gb_s/H.dram.gb_s).toFixed(1)+'× faster';
 $('k2').textContent=(H.scp.gb_s/H.dram.gb_s).toFixed(1)+'× faster';
 $('k3').textContent=(POOLED.relay.dram.mean/POOLED.relay.hop.mean).toFixed(0)+'× less';   // the three-card check's passes (section 2)
 $('k4').textContent='>32 MB';
 const stg=m=>CS.map(c=>D.headline[c][m].cycles_max/D.headline[c][m].stages), k0=v=>n0(Math.round(v/1000)*1000);
 $('stagecyc').textContent=`${rng(stg('dram'),k0)} cycles (${andL(CS.map((c,i)=>k0(stg('dram')[i])))} on ${andL(CS.map(lab))}), a hand-off stage ${rng(stg('hop'),k0)} and an `+
  `own-scratchpad stage ${rng(stg('scp'),k0)}`;
 const gbs=[].concat(...OFF.map(r=>CS.filter(c=>r.by_card&&r.by_card[c]).map(c=>r.by_card[c].gb_s)));
 $('l-gbr').textContent=`${n0(Math.min(...gbs))}–${n0(Math.max(...gbs))} GB/s`;
 const hx=c=>(D.headline[c].hop.gb_s/D.headline[c].dram.gb_s).toFixed(1), sx=c=>(D.headline[c].scp.gb_s/D.headline[c].dram.gb_s).toFixed(1);
 $('l-a3').textContent=`${andL(CS.map(hx))}× for the hand-off and ${andL(CS.map(sx))}× for the own scratchpad, on ${andL(CS.map(lab))}`;
 const rep=[].concat(...CS.map(c=>D.repeats[c]));
 const hopR=rng(rep.map(r=>r.hop_over_dram),v=>v.toFixed(1)), scpR=rng(rep.map(r=>r.scp_over_dram),v=>v.toFixed(1));
 const nRep=CS.map(c=>D.repeats[c].length);
 $('l-rep').textContent=`${hopR}× and ${scpR}× over ${rng(nRep,n0)} runs per card`;
 const groups=[...new Set(D.repeats[A2].map(r=>r.group))], cov=D.coverage||{};
 const lost=CS.filter(c=>cov[c]&&cov[c].short.length);
 $('cards').textContent=CS.map(c=>`${lab(c)} ${hx(c)}×`).join(', ')+' for the hand-off, '+andL(CS.map(sx).map(v=>v+'×'))+
   ` for the shire-local case. The same configuration ran in the ${groups.slice(0,-1).join(', ')} and ${groups[groups.length-1]} sweeps of every pass, `+
   `${andL(CS.map((c,i)=>`${nRep[i]} times on ${lab(c)}`))}, and the two ratios run ${hopR}× and ${scpR}×; the scatter is almost all DRAM (${rng(rep.map(r=>r.dram),f1)} GB/s), `+
   `and the hand-off ran at ${rng(rep.map(r=>r.hop),f0)} GB/s every time`+
   (lost.length?`. ${andL(lost.map(c=>`${lab(c)} lacks ${word(cov[c].short.length)} of its ${n0(cov[c].configs*cov[c].passes.length)} launches`))}, whose host process crashed (aifoundry3's known host crash, about one launch in a hundred, since traced to the runtime's logging and fixed: E49); those configurations are the mean of two passes`:'');
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
   lab:(v,m)=>pjr(POOLED.relay[m])}];
 const tip=(key,m,label)=>{const x=med(m),q=POOLED.relay[m],pc=q.per_card;
  if(key==='w')return `<b>${label}</b> · ${f2(x.over_idle_w)} W over idle (board power, ${A2}; idle ${f2(p.idle.board_w)} W)<br>${x.n} readings over ${f1(x.wall_s)} s; the kernel ran ${f0(100*x.duty)}% of the burst`;
  if(key==='gb')return `<b>${label}</b> · ${g1(x.bytes_per_s/1e9)} GB/s while the kernel runs (cycle counter), over ${x.runs} launches in the power burst<br>the headline run of the table above: ${g1(H[m].gb_s)} GB/s`;
  return `<b>${label}</b> · ${pj(q.mean)} pJ per byte moved, mean of ${q.n} passes [${pjr(q).split('[')[1]}<br>`+
   `${CS.filter(c=>pc[c]).map(c=>`${lab(c)} ${pj(pc[c].mean)} (n = ${pc[c].n})`).join(', ')}; this session (${A2}, not pooled) ${pj(x.pj_per_byte)}`;};
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
      CS.filter(c=>pc[c]).forEach((c,i)=>{const e=CK.cardMark(g,c,x(pc[c].mean),yc+[-9,9,0][i%3],CK.card(c).mark==='diamond'?4:3,'var(--ink)');
       e.setAttribute('aria-hidden','true'); if(CK.card(c).mark==='ring'){e.style.fill='none';e.style.strokeWidth='1.2';}});
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
  `Watts and GB/s are from one power session on ${A2}: board power over an idle of ${f2(p.idle.board_w)} W, and the rate while the kernel runs, `+
  `from the cycle counter, during those bursts (the headline runs in the table above ran at ${MED.map(m=>g1(H[m[0]].gb_s)).join(', ')} GB/s). `+
  `Energy per byte pools the three-card check's ${q.dram.n} passes, ${word(q.dram.per_card[A2].n)} per card (26 September): the bar is the mean, the whisker the range, `+
  `the marks each card's mean (${andL(CS.filter(c=>q.dram.per_card[c]).map(c=>({dot:'dot',ring:'ring',diamond:'diamond'}[CK.card(c).mark]||'mark')+' '+lab(c)))}), the tick this session, which is not pooled. The power moves by ${f1(Math.max(...w)-Math.min(...w))} W while the work grows `+
  `${f0(med('hop').bytes_per_s/dr.bytes_per_s)}× and ${f0(med('scp').bytes_per_s/dr.bytes_per_s)}×.`;
})();

/* ---------- section 2: power ---------- */
(function(){
 const p=D.power; if(!p){return;}
 const name={dram:'DRAM',scp:"own shire's scratchpad",hop:"next shire's scratchpad"}, q=POOLED.relay;
 $('power').innerHTML=`<thead><tr><th>Where the intermediate goes</th><th class="num">GB/s on the card</th><th class="num">Watts over idle</th><th class="num">pJ, this session</th><th class="num">pJ per byte moved, all passes: mean [range], n = ${q.dram.n}</th></tr></thead><tbody>`+
  ['dram','hop','scp'].map(m=>{const r=p.media.find(x=>x.medium===m);
   return `<tr><td>${name[m]}</td><td class="num">${g1(r.bytes_per_s/1e9)}</td><td class="num">${f2(r.over_idle_w)}</td><td class="num">${pj(r.pj_per_byte)}</td><td class="num">${pjr(q[m])}</td></tr>`;}).join('')+
  `</tbody>`;
 CK.stackTable('power');
 const duty=p.media.map(m=>m.duty);
 $('powernote').textContent=
  `One session on ${A2}, board power, reduced against one idle for the whole session with no leakage correction (the 26 September `+
  `passes in the last column were reduced against the idle just before and after each burst and corrected for leakage). `+
  `Idle was ${f2(p.idle.board_w)} W at a die temperature of ${f0(p.idle.die_c)} °C, and the `+
  `minion clock stayed at 600 MHz throughout. The GB/s column is the rate while the kernel runs, from the cycle counter, and the kernel ran only `+
  `${f0(100*Math.min(...duty))}–${f0(100*Math.max(...duty))}% of each burst; `+
  `the watts are averaged over the whole burst, launch gaps included, so pJ per byte is watts over idle ÷ `+
  `(GB/s × ${Math.min(...duty).toFixed(2)}–${Math.max(...duty).toFixed(2)}).`;
 const pc=q.dram.per_card, r=POOLED.read, pcs=CS.filter(c=>pc[c]), nper=[...new Set(pcs.map(c=>pc[c].n))];
 const rd=m=>`${f2(m.mean)} [${f2(m.lo)}–${f2(m.hi)}]`, hi1=pcs.reduce((a,c)=>pc[c].mean>pc[a].mean?c:a,pcs[0]);
 $('remeasured').innerHTML=
  `<b>Re-measured.</b> The last column is the energy manual's pool of the three-card check (n = ${q.dram.n}, `+
  `${nper.length===1?word(nper[0])+' passes on each of '+word(pcs.length)+' cards':pcs.map(c=>word(pc[c].n)+' on '+lab(c)).join(', ')}, 26 September; `+
  `this session is not among them; <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-between-cores-and-shires">§5</a>): `+
  `${f0(q.dram.mean/q.hop.mean)}× and ${f0(q.dram.mean/q.scp.mean)}× less than DRAM. The hand-off's advantage is the same on every card `+
  `(${andL(pcs.map(c=>f1(pc[c].mean/q.hop.per_card[c].mean)))}× on ${andL(pcs.map(lab))}), although the DRAM relay itself costs more on ${lab(hi1)} `+
  `(${f0(pc[hi1].mean)} pJ per byte against ${andL(pcs.filter(c=>c!==hi1).map(c=>f0(pc[c].mean)))}, beyond the 99% interval). Reading a byte costs ${f0(r.dram.mean)} `+
  `[${f0(r.dram.lo)}–${f0(r.dram.hi)}] pJ from DRAM; from the shire's own scratchpad ${rd(r['scp-local'].zeros)} when it holds zeros and ${rd(r['scp-local'].random)} `+
  `when it holds random data, and from another shire's ${f2(r['scp-remote'].zeros.mean)} and ${f1(r['scp-remote'].random.mean)} `+
  `(<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual#bytes-through-the-memory-hierarchy">the energy manual, §4</a>; the check filled the scratchpads `+
  `with zeros or random data before reading them). `+
  `The own scratchpad's figure is not split by card: in the three-card check the difference between ${A2} and ${A3} was the data `+
  `read, not the card; at equal contents they agree (${f2(RL3.h.zeros[A2])} and ${f2(RL3.h.zeros[A3])} pJ per byte for zeros, `+
  `${f2(RL3.h.random[A2])} and ${f2(RL3.h.random[A3])} for random data), while ${lab('aifoundry1-c1')} read more `+
  `(${f2(RL3.h.zeros['aifoundry1-c1'])} and ${f2(RL3.h.random['aifoundry1-c1'])}).`;
})();

/* ---------- section 3: working-set size, to 256 MB ---------- */
(function(){
 const rows=D.size, mb=r=>r.stage_bytes*32/1048576, top=Math.max(...rows.map(mb));
 const big=D.bigsize.filter(r=>mb(r)>top);                    // DRAM-only continuation past the on-chip limit
 /* Colour is the medium, as everywhere on this page; the mark's shape is the card (CK's registry: filled, ring,
    diamond), one line per card (the first solid, the others dashed), for every card the rows' by_card carries: each
    point the mean of that card's passes (analyze_onchip.py). bigsize's by_card is {card: GB/s}. Data without by_card
    draws the first card from the row itself. */
 const cards=CK.cardsIn([...new Set(rows.flatMap(r=>Object.keys(r.by_card||{[A2]:1})))]), OTH=cards.filter(c=>c!==A2);
 const rowOf=(r,c)=>r.by_card?r.by_card[c]||null:(c===A2?r:null);
 const bigOf=(r,c)=>r.by_card?(r.by_card[c]!=null?r.by_card[c]:null):(c===A2?r.gb_s:null);
 const mark=(g,c,x,y,col)=>{const k=CK.card(c).mark,e=CK.cardMark(g,c,x,y,k==='ring'?6.5:k==='dot'?3.5:4,col);
  if(k==='ring'){e.style.fill='none';e.style.strokeWidth='1.5';}   // a ring round a dot: both cards stay visible
  e.setAttribute('aria-hidden','true');return e;};
 const lg=CK.legend('sizelegend',MED.map(m=>({key:m[0],label:m[3],mark:'dot',color:m[2]})));
 if(cards.length>1) for(const c of cards){  // the card key: the mark's shape, in ink
  const s=document.createElement('span'); s.className='ck-li';
  const v=CK.el('svg',{viewBox:'0 0 18 12',width:18,height:12,'aria-hidden':'true'}); mark(v,c,9,6,'var(--ink-2)');
  s.append(v,document.createTextNode(lab(c))); lg.el.appendChild(s);
 }
 CK.frame('size',{label:'Relay bandwidth against working-set size for the three media, to 256 MB per buffer, every card',height:W=>W<600?320:340,
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
   MED.forEach(m=>cards.forEach((c,ci)=>{
    const pts=rows.map(r=>[mb(r),rowOf(r,c)]).filter(p=>p[1]).map(p=>[p[0],p[1][m[0]].gb_s])
     .concat(m[0]==='dram'?big.map(r=>[mb(r),bigOf(r,c)]).filter(p=>p[1]!=null):[]);
    const ln=CK.el('path',{d:CK.path(pts,x,y),fill:'none'},svg); ln.style.stroke=m[2]; ln.style.strokeWidth=ci?'1.25':'2';
    if(ci) ln.style.strokeDasharray='4 3';
    for(const [a,b] of pts) mark(CK.el('g',{},svg),c,x(a),y(b),m[2]);
   }));
   /* one focusable column per size: the crosshair lists every medium on every card at that size */
   const cols=rows.map(r=>({mb:mb(r),r})).concat(big.map(r=>({mb:mb(r),big:r}))), nodes=[];
   for(const c of cols){
    const g=CK.el('g',{},svg), xc=x(c.mb);
    CK.el('rect',{x:xc-14,y:T,width:28,height:Hh-B-T,class:'ck-hit'},g);
    const ln=CK.el('line',{x1:xc,x2:xc,y1:T,y2:Hh-B,class:'xh'},g); ln.style.stroke='var(--ink-2)'; ln.style.strokeWidth='1'; ln.style.opacity='0';
    g.addEventListener('pointerenter',()=>{ln.style.opacity='0.6';}); g.addEventListener('pointerleave',()=>{ln.style.opacity='0';});
    g.addEventListener('focus',()=>{ln.style.opacity='0.6';}); g.addEventListener('blur',()=>{ln.style.opacity='0';});
    const html=`<b>${c.mb} MB per buffer</b> (footprint ${2*c.mb} MB)<br>`+cards.map(cd=>{
     if(c.big){const v=bigOf(c.big,cd);return v==null?null:`${lab(cd)}: DRAM ${gb(v)} GB/s; the on-chip routes have no room`;}
     const q=rowOf(c.r,cd); if(!q)return null;
     return `${lab(cd)}: DRAM ${gb(q.dram.gb_s)}, next shire ${gb(q.hop.gb_s)} (${f2(q.hop_over_dram)}×), own ${gb(q.scp.gb_s)} (${f2(q.scp_over_dram)}×) GB/s`;
    }).filter(Boolean).join('<br>');
    CK.tip(f,g,html); nodes.push(g);
   }
   CK.keynav(f,nodes);
  }});
 const small=rows[0], last=rows[rows.length-1];
 const and=a=>a.slice(0,-1).join(', ')+' and '+a[a.length-1];
 const fit=rows.filter(r=>2*mb(r)<=32), lastfit=fit[fit.length-1];
 const hopMax=Math.max(...fit.map(r=>r.hop_over_dram));
 const devs=[0];   // every other card's relative distance from the first card, every medium and size
 for(const r of rows) for(const c of OTH) if(r.by_card&&r.by_card[c]) for(const m of MED) devs.push(Math.abs(r.by_card[c][m[0]].gb_s/r[m[0]].gb_s-1));
 for(const r of big) for(const c of OTH) if(r.by_card&&r.by_card[c]) devs.push(Math.abs(r.by_card[c]/r.gb_s-1));
 $('sizecap').textContent=
  `Log axes. Colour is where a stage's output goes; the mark is the card`+
  (cards.length>1?` (${cards.map(c=>`${lab(c)} ${CK.card(c).mark==='dot'?'filled':CK.card(c).mark==='ring'?'ring':CK.card(c).mark}`).join(', ')}; each point the mean of that card's passes, and every card within ${f0(Math.ceil(100*Math.max(...devs)))}% of ${lab(A2)} at every size)`:` (${lab(A2)})`)+
  `. Two buffers are live at once, so the chip footprint is twice the figure on the x axis; the dashed line `+
  `marks where that footprint equals the 32 MB L3. Past ${top} MB per buffer only the DRAM route can run: the buffers start 256 KB into `+
  `each shire's 2.5 MB scratchpad, and two of them no longer fit in what is left. The numbers below are ${lab(A2)}'s unless the text names a card.`;
 $('sizetext').innerHTML=
  `At ${mb(small)} MB per buffer the DRAM route runs at <b>${g1(small.dram.gb_s)} GB/s</b>, because it is not `+
  `going to DRAM at all: the 32 MB L3 holds the whole thing. Handing the data to the next shire then buys `+
  `${small.hop_over_dram.toFixed(2)}×, which is nothing, and keeping it in the shire's own scratchpad `+
  `${small.scp_over_dram.toFixed(1)}×. Up to ${mb(lastfit)} MB per buffer, while both buffers fit in the L3, the hand-off `+
  `wins at most `+(OTH.length?andL(CS.map(c=>`${Math.max(...fit.filter(r=>r.by_card&&r.by_card[c]).map(r=>r.by_card[c].hop_over_dram)).toFixed(1)}× on ${lab(c)}`)):`${hopMax.toFixed(1)}×`)+
  `. At ${mb(last)} MB per buffer, a ${2*mb(last)} MB footprint, the DRAM route falls to `+
  `<b>${g1(last.dram.gb_s)} GB/s</b> and stays below ${f0(Math.ceil(Math.max(...big.map(r=>r.gb_s))))} GB/s: ${and(big.map(r=>g1(r.gb_s)))} GB/s at `+
  `${and(big.map(r=>String(mb(r))))} MB per buffer`+
  (OTH.length&&big[0].by_card?`, rising ${rng(CS.filter(c=>big[0].by_card[c]&&big[big.length-1].by_card[c]).map(c=>100*(big[big.length-1].by_card[c]/big[0].by_card[c]-1)),f0)}% from ${mb(big[0])} to ${mb(big[big.length-1])} MB on every card`:'')+`. `+
  `<b>The advantage is not a property of the computation. It is the L3 capacity.</b> Below it the cache is already doing most of the job; `+
  `above it, nothing is, unless you place the data yourself.`;
})();

/* ---------- section 3: stages and shires, one setting changed at a time from the headline run ----------
   Two panels on one y scale. Colour is the medium, as everywhere on this page; the mark's shape is the card
   (CK's registry: filled, ring, diamond), for every card in the rows' by_card (analyze_onchip.py, 26 Sep). Data
   without by_card draws the first card from the row itself. The headline setting is in both sweeps: hovering or
   focusing it in one panel marks it in the other too. */
(function(){
 const HC=H.dram, MB=HC.stage_bytes/1048576;                 // the headline run: 1 MB per shire per stage, 8 stages, 32 shires
 const rowOf=(r,c)=>r.by_card?r.by_card[c]||null:(c===A2?r:null);
 const PAN=[{key:'stages',rows:D.stages,head:HC.stages,xt:[1,2,4,8,16,32],
             title:`against pipeline stages (${HC.shires} shires)`,at:n=>`${n} stage${n>1?'s':''} on ${HC.shires} shires`},
            {key:'shires',rows:D.shires,head:HC.shires,xt:[2,4,8,16,32],
             title:`against shires taking part (${HC.stages} stages)`,at:n=>`${n} shires, ${HC.stages} stages, ${n*MB} MB per buffer`}];
 const cards=CK.cardsIn([...new Set([].concat(...PAN.map(P=>[].concat(...P.rows.map(r=>r.by_card?Object.keys(r.by_card):[A2])))))]);
 const L3=32, fitMax=L3/(2*MB);                              // shires at which both buffers exactly fill the 32 MB L3
 /* the card's mark (shape from the registry) in the medium's colour */
 const mark=(g,c,x,y,col)=>{const k=CK.card(c).mark,e=CK.cardMark(g,c,x,y,k==='ring'?6.5:k==='dot'?3.5:4,col);
  if(k==='ring'){e.style.fill='none';e.style.strokeWidth='1.5';}   // a ring round a dot: both cards stay visible
  e.setAttribute('aria-hidden','true');return e;};
 const lg=CK.legend('stshlegend',MED.map(m=>({key:m[0],label:m[3],mark:'line',color:m[2]})),{toggle:true,onChange:keys=>CK.showSeries(f,keys)});
 for(const c of cards){  // the card key: the mark's shape, in ink
  const s=document.createElement('span'); s.className='ck-li';
  const v=CK.el('svg',{viewBox:'0 0 18 12',width:18,height:12,'aria-hidden':'true'}); mark(v,c,9,6,'var(--ink-2)');
  s.append(v,document.createTextNode(CK.card(c).label)); lg.el.appendChild(s);
 }
 const tipHtml=(P,r)=>`<b>${P.at(r[P.key])}</b>${r[P.key]===P.head?' · the headline setting':''}<br>`+
  cards.map(c=>{const q=rowOf(r,c);if(!q)return `${CK.card(c).label}: not run`;
   return `${CK.card(c).label}: DRAM ${gb(q.dram.gb_s)}, next shire ${gb(q.hop.gb_s)} (${f2(q.hop_over_dram)}×), own ${gb(q.scp.gb_s)} (${f1(q.scp_over_dram)}×) GB/s`;}).join('<br>');
 const f=CK.frame('stsh',{label:'Relay bandwidth of DRAM, the next shire and the own scratchpad against pipeline stages and against shires taking part',
  height:W=>W<600?2*262+18:292,
  draw(f){
   const svg=f.svg,W=f.W,narrow=f.narrow,GAP=24,ph=narrow?262:f.H, pw=narrow?W:(W-GAP)/2;
   const heads=[];
   PAN.forEach((P,pi)=>{
    const ox=narrow?0:pi*(pw+GAP), oy=narrow?pi*(ph+18):0, L=ox+46, R=10, T=oy+40, B=44, x1=ox+pw-R, y1=oy+ph-B;
    const x=CK.log(P.xt[0],P.xt[P.xt.length-1],L+8,x1-8), y=CK.log(20,2000,y1,T);
    CK.txt(svg,ox+4,oy+14,P.title,'lab-strong');
    CK.txt(svg,ox+4,T-10,'GB/s','lab');
    if(P.key==='shires'){  // where both buffers fit in the L3, the DRAM route is not reaching DRAM
     const xf=x(fitMax), sh=CK.el('rect',{x:L,y:T,width:xf-L,height:y1-T,'aria-hidden':'true'},svg); sh.style.fill='var(--grid)'; sh.style.opacity='0.6';
     CK.el('line',{x1:xf,x2:xf,y1:T,y2:y1,'aria-hidden':'true',style:'stroke:var(--ref);stroke-width:1.5;stroke-dasharray:5 4'},svg);
     CK.txt(svg,L+4,y(1500),'both buffers fit in the L3','lab');
    }
    CK.axes({svg,W:ox+pw,H:oy+ph},{x,y,L,R,T,B,xt:P.xt,yt:[20,100,500,2000],yfmt:n0,xfmt:String,
     xl:P.key==='stages'?'stages in the relay':'shires taking part'});
    for(const [m,,col] of MED) cards.forEach((c,ci)=>{
     const pts=P.rows.map(r=>[r[P.key],rowOf(r,c)]).filter(p=>p[1]).map(p=>[p[0],p[1][m].gb_s]);
     const g=CK.el('g',{'data-series':m,'aria-hidden':'true'},svg);
     const ln=CK.el('path',{d:CK.path(pts,x,y),fill:'none'},g); ln.style.stroke=col; ln.style.strokeWidth=ci?'1.25':'2';
     if(ci) ln.style.strokeDasharray='4 3';
     for(const [a,b] of pts) mark(g,c,x(a),y(b),col);
    });
    /* one focusable column per setting; its tooltip lists every medium on every card */
    const nodes=[];
    for(const r of P.rows){
     const g=CK.el('g',{},svg), xc=x(r[P.key]);
     CK.el('rect',{x:xc-13,y:T,width:26,height:y1-T,class:'ck-hit'},g);
     const xh=CK.el('line',{x1:xc,x2:xc,y1:T,y2:y1,'aria-hidden':'true'},g); xh.style.stroke='var(--ink-2)'; xh.style.opacity='0';
     if(r[P.key]===P.head){  // a capsule round the headline setting's column, from its highest point to its lowest
      const qs=cards.map(c=>rowOf(r,c)).filter(Boolean), top=y(Math.max(...qs.map(q=>q.scp.gb_s)))-12, bot=y(Math.min(...qs.map(q=>q.dram.gb_s)))+12;
      const rr=CK.el('rect',{x:xc-9,y:top,width:18,height:bot-top,rx:9,fill:'none','aria-hidden':'true'},g);
      rr.style.stroke='var(--ink)'; rr.style.strokeWidth='1.25';
      heads.push(xh);
     }
     const on=()=>{xh.style.opacity='0.6'; if(r[P.key]===P.head) heads.forEach(h=>{h.style.opacity='0.6';});};
     const off=()=>{xh.style.opacity='0'; if(r[P.key]===P.head) heads.forEach(h=>{h.style.opacity='0';});};
     g.addEventListener('pointerenter',on); g.addEventListener('pointerleave',off); g.addEventListener('focus',on); g.addEventListener('blur',off);
     CK.tip(f,g,tipHtml(P,r)); nodes.push(g);
    }
    CK.keynav(f,nodes);
   });
  }});
 /* the lead-in and the caption, every number from the rows */
 const ratio=(rows,sel,k)=>[].concat(...rows.filter(sel).map(r=>cards.map(c=>rowOf(r,c)).filter(Boolean).map(q=>q[k])));
 const st=D.stages, sh=D.shires, few=r=>r.shires<=fitMax, all=r=>r.shires===HC.shires;
 const deep=r=>r.stages>=4, shallow=r=>r.stages<4;
 const dr32=ratio(sh,all,'dram').map(q=>q.gb_s);
 $('stshlead').textContent=`Two more sweeps change one setting at a time from the headline run (${num(MB)} MB per shire per stage, `+
  `${word(HC.stages)} stages, ${HC.shires} shires): the number of stages in the chain, and the number of shires taking part.`;
 $('stshcap').textContent=
  `Log axes, one y scale for both panels. Colour is where a stage's output goes; the mark is the card (${cards.map(c=>`${CK.card(c).label} ${CK.card(c).mark==='dot'?'filled':CK.card(c).mark==='ring'?'ring':CK.card(c).mark}`).join(', ')}). `+
  `Left: from ${word(Math.min(...st.map(r=>r.stages)))} stage to ${Math.max(...st.map(r=>r.stages))}, the next shire runs ${rng(ratio(st,deep,'hop_over_dram'),f1)}× DRAM at four stages or more `+
  `and ${rng(ratio(st,shallow,'hop_over_dram'),f1)}× with one or two, where the DRAM route reaches only ${rng(ratio(st,shallow,'dram').map(q=>q.gb_s),f0)} GB/s. `+
  `Right: every shire keeps ${num(MB)} MB per stage, so fewer shires also means less data. Up to ${fitMax} shires both buffers fit in the ${L3} MB L3 (shaded), `+
  `and the hand-off runs at ${rng(ratio(sh,few,'hop_over_dram'),f2)}× the DRAM route's rate; at ${HC.shires} the DRAM route falls to ${rng(dr32,f1)} GB/s and the hand-off is `+
  `${rng(ratio(sh,all,'hop_over_dram'),f1)}×. The ringed column is the headline setting, the same configuration in both panels, measured in different sweeps.`;
})();

/* ---------- section 4: arithmetic intensity ---------- */
(function(){
 const rows=D.intensity;
 const S=[['scp_over_dram',"own shire",'var(--c3)','scp'],['hop_over_dram',"next shire",'var(--c1)','hop']];
 /* Colour is which route is compared with DRAM; the mark's shape is the card, as in section 3. */
 const cards=CK.cardsIn([...new Set(rows.flatMap(r=>Object.keys(r.by_card||{[A2]:1})))]);
 const rowOf=(r,c)=>r.by_card?r.by_card[c]||null:(c===A2?r:null);
 const mark=(g,c,x,y,col)=>{const k=CK.card(c).mark,e=CK.cardMark(g,c,x,y,k==='ring'?6.5:k==='dot'?3.5:4,col);
  if(k==='ring'){e.style.fill='none';e.style.strokeWidth='1.5';}
  e.setAttribute('aria-hidden','true');return e;};
 const lg=CK.legend('intlegend',S.map(s=>({key:s[0],label:s[1],mark:'dot',color:s[2]})));
 if(cards.length>1) for(const c of cards){
  const s=document.createElement('span'); s.className='ck-li';
  const v=CK.el('svg',{viewBox:'0 0 18 12',width:18,height:12,'aria-hidden':'true'}); mark(v,c,9,6,'var(--ink-2)');
  s.append(v,document.createTextNode(lab(c))); lg.el.appendChild(s);
 }
 CK.frame('intensity',{label:'Advantage over the DRAM route against vector adds per element, every card',height:W=>W<600?320:340,
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
   S.forEach(s=>cards.forEach((c,ci)=>{
    const pts=rows.map(r=>[r.work,rowOf(r,c)]).filter(p=>p[1]).map(p=>[p[0],p[1][s[0]]]);
    const ln=CK.el('path',{d:CK.path(pts,x,y),fill:'none'},svg); ln.style.stroke=s[2]; ln.style.strokeWidth=ci?'1.25':'2';
    if(ci) ln.style.strokeDasharray='4 3';
    for(const [a,b] of pts) mark(CK.el('g',{},svg),c,x(a),y(b),s[2]);
   }));
   const nodes=[];
   for(const r of rows){
    const g=CK.el('g',{},svg), xc=x(r.work);
    CK.el('rect',{x:xc-14,y:T,width:28,height:Hh-B-T,class:'ck-hit'},g);
    CK.tip(f,g,`<b>${r.work} add${r.work>1?'s':''} per element</b> (${num(r.work/8)} flop per byte moved, ${num(r.work/4)} per byte read)<br>`+
     cards.map(c=>{const q=rowOf(r,c);if(!q)return null;
      return `${lab(c)}: `+S.map(s=>`${s[1]} ${q[s[0]].toFixed(1)}× DRAM (${g1(q[s[3]].gb_s)} GB/s)`).join(', ');}).filter(Boolean).join('<br>'));
    nodes.push(g);
   }
   CK.keynav(f,nodes);
  }});
 /* a value per setting over every card: one number when the cards agree to the printed digit, else the range */
 const last=rows[rows.length-1], at=w=>{const r=rows.find(q=>q.work===w);
  return rng(cards.map(c=>rowOf(r,c)).filter(Boolean).map(q=>q.hop_over_dram),v=>v.toFixed(1));};
 $('intcap').textContent=`Log axes. The mark is the card`+
  (cards.length>1?` (${cards.map(c=>`${lab(c)} ${CK.card(c).mark==='dot'?'filled':CK.card(c).mark==='ring'?'ring':CK.card(c).mark}`).join(', ')}; each point the mean of that card\u2019s passes); the text gives the range over the cards`:` (${lab(A2)})`)+
  `. The dashed line is parity with DRAM. Each element is 4 bytes read `+
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

/* ---------- section 5: distance ----------
   Since 26 September the ring offsets are the three-card passes' 'offsets' sweep, every offset d = 1..31 on every card
   (D.offsets, pass means), and the fits over the 16 ring geometries (offset g with its mirror 32 - g) are
   analyze_onchip.py's D.offset_fit. Without D.offsets (the 22 September data) the five offsets of D.distance are drawn. */
(function(){
 const d=OFF, k=n=>d.find(r=>r.hop_distance===n).mesh_hops, mh=d.map(r=>r.mesh_hops.mean);
 const cs=CS.filter(c=>d.every(r=>r.by_card&&r.by_card[c]));   // the cards with every offset, registry order
 const gbOf=c=>d.map(r=>r.by_card[c].gb_s), Ls=d.map(r=>r.longest.hops), FIT=D.offset_fit||{};
 const fitted=cs.filter(c=>FIT[c]);
 const byL=[...new Set(Ls)].sort((a,b)=>b-a);
 const rngOf=Lh=>rng([].concat(...cs.map(c=>d.filter(r=>r.longest.hops===Lh).map(r=>r.by_card[c].gb_s))),n0);
 const and=a=>a.slice(0,-1).join(', ')+' and '+a[a.length-1];
 const rngH=m=>`${m.min} to ${m.max}`;
 const allG=[].concat(...cs.map(gbOf));
 const R={longest:{},mean:{}};
 for(const c of cs){const g=gbOf(c);R.longest[c]=pear(Ls,g);R.mean[c]=pear(mh,g);}
 const rr=o=>rng(cs.map(c=>R[o][c].r),v=>num(v,2));
 /* how far apart the cards are: the largest spread of one offset over the cards, relative to its mean */
 const spread=Math.max(...d.map(r=>{const v=cs.map(c=>r.by_card[c].gb_s);return (Math.max(...v)-Math.min(...v))/(v.reduce((a,b)=>a+b)/v.length);}));
 const ci=(c,key)=>`${num(FIT[c][key][0],1)} to ${num(FIT[c][key][1],1)}`;
 const mk=c=>{const m=CK.card(c).mark;return m==='dot'?'dots':m==='ring'?'rings':m==='diamond'?'diamonds':'squares';};
 $('distintro').innerHTML=
  `The obvious worry about handing data to another shire is the network in between. Shire numbers do not follow `+
  `the mesh: on the shire map of the <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication">on-chip `+
  `communication report</a>, the next shire in the ring is on average ${f1(k(1).mean)} mesh hops away `+
  `(${rngH(k(1))}), two places on ${f1(k(2).mean)}, and sixteen places on only ${f1(k(16).mean)} (${rngH(k(16))}). `+
  `Across all ${d.length} offsets the bandwidth runs from ${n0(Math.min(...allG))} to ${n0(Math.max(...allG))} GB/s, `+
  (cs.length>1?`and the ${word(cs.length)} cards agree within ${f1(100*spread)}% at every offset. `:'')+
  `It does not follow the mean distance (${f1(Math.min(...mh))} to ${f1(Math.max(...mh))} hops): r = ${rr('mean')} against it. `+
  `It falls with the longest hand-off in the ring: ${and(byL.map(String))} hops give ${and(byL.map(rngOf))} GB/s, `+
  `r = ${rr('longest')}. `+
  (fitted.length?`That was a prediction. A line fitted on 22 September to five offsets (1, 2, 4, 8 and 16) put the eleven ring geometries `+
   `not tried then within 0.7% of where they landed, on every card, where the registered test allowed 5%; and with the longest hand-off `+
   `in the fit, the mean hop count adds ${and(fitted.map(c=>`${num(FIT[c].mean_hops_coef,1)} GB/s per hop (99% interval ${ci(c,'mean_hops_coef_ci99')}) on ${lab(c)}`))}: `+
   `nothing measurable. `:'')+
  `That is what one would expect when every stage waits at a barrier for its slowest shire, though it is an observation across `+
  `ring geometries, not a test of one link.`;
 const W_='style="white-space:normal"';
 $('dist').innerHTML=`<thead><tr><th class="num" ${W_}>Shire IDs back round the ring</th>`+
  `<th class="num" ${W_}>Mesh hops, mean</th><th class="num" ${W_}>Longest hand-off, hops</th>`+
  cs.map(c=>`<th class="num" ${W_}>GB/s, ${lab(c)}</th>`).join('')+
  `<th class="num" ${W_}>Against the next shire in ID order, ${cs.map(c=>CK.card(c).short).join(' / ')}</th></tr></thead><tbody>`+
  d.map(r=>`<tr><td class="num">${r.hop_distance}</td><td class="num">${f1(r.mesh_hops.mean)}</td><td class="num">${r.longest.hops}</td>`+
   cs.map(c=>`<td class="num">${g1(r.by_card[c].gb_s)}</td>`).join('')+
   `<td class="num">${cs.map(c=>(r.by_card[c].gb_s/d[0].by_card[c].gb_s).toFixed(2)+'×').join(' / ')}</td></tr>`).join('')+'</tbody>';
 CK.stackTable('dist');
 CK.sortTable('dist');
 const slope=fitted.length?fitted.map(c=>FIT[c].stage_cycles_per_hop):cs.map(c=>pear(Ls,d.map(r=>r.by_card[c].stage_cycles)).slope);
 const r10=v=>n0(Math.round(v/10)*10);
 const cost=cs.map(c=>{const g=gbOf(c);return 1-d[0].by_card[c].gb_s/Math.max(...g);});
 const bestOff=cs.map(c=>FIT[c]?FIT[c].best.offset:d[gbOf(c).indexOf(Math.max(...gbOf(c)))].hop_distance);
 const mir=fitted.map(c=>Math.abs(FIT[c].worst_mirror.rel)), W0=fitted.length&&FIT[fitted[0]].worst_mirror;
 $('distafter').innerHTML=
  `The headline in section 1 uses offset ${d[0].hop_distance}, the slowest geometry together with its mirror image, offset ${d[d.length-1].hop_distance}. `+
  `Transfers here are 32 KB per minion and pipelined, yet the mesh distance still shows: the stage time grows about `+
  `${rng(slope,r10)} cycles for each hop of the longest hand-off`+
  (fitted.length?` (99% interval ${r10(Math.min(...fitted.map(c=>FIT[c].stage_cycles_per_hop_ci99[0])))}–${r10(Math.max(...fitted.map(c=>FIT[c].stage_cycles_per_hop_ci99[1])))} `+
   `on every card; a least-squares line over the ${FIT[fitted[0]].geometries} ring geometries, each offset averaged with its mirror, one per card)`
   :` (a least-squares line over the ${word(d.length)} offsets, one per card)`)+
  `. The practical consequence is to keep the longest hand-off short: the ID ring's ${d[0].longest.hops}-hop pair costs `+
  `${rng(cost.map(v=>100*v),f0)}% of the bandwidth of the best offset (${[...new Set(bestOff)].join(', ')}), on every card. `+
  (fitted.length?`An offset and its mirror hand the same pairs of shires the slab in opposite directions; they agree within `+
   `${rng(mir.map(v=>100*v),f1)}% (offsets ${W0.offset} and ${W0.mirror} differ most), a little more than the 2% the registered test allowed. `:'')+
  `Placement is not free in energy either. On a loaded mesh each hop costs 1.6–2.3 pJ per byte of random data `+
  `(<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm#meaning">Heat per millimetre, §8</a>), about half of the `+
  `${f1(POOLED.read['scp-local'].random.mean)} pJ a tensor load of a random byte from the shire's own scratchpad costs (section 2). The hand-off's bytes cross ${f1(k(1).mean)} hops on average, so a physical `+
  `neighbour should cost less (untested; section 7). This relay's slabs each hold a single value repeated, and such data costs less to `+
  `carry than random data.`;

 /* ---- the map and the scatter ---- */
 const LAY=D.layout, ring=D.ring, n=ring.length;
 const hops=(a,b)=>Math.abs(LAY[a][0]-LAY[b][0])+Math.abs(LAY[a][1]-LAY[b][1]);
 const src=(s,o)=>ring[(ring.indexOf(s)-o+n)%n];
 let off=d[0].hop_distance, xm='longest', f=null;
 const offCtl=CK.range('ringoff',{label:'Ring offset (shire IDs back)',stops:d.map(r=>r.hop_distance),value:off,fmt:v=>String(v),onInput:v=>{off=v;upd();}});
 CK.seg('ringx',{label:'Scatter against',options:[['longest','longest hand-off'],['mean','mean hops']],value:xm,onChange:v=>{xm=v;upd();}});
 const out=CK.readout('ringout');
 function upd(){
  const r=d.find(q=>q.hop_distance===off);
  out.set(`<b>Offset ${off}:</b> mean ${f1(r.mesh_hops.mean)} hops, longest ${r.longest.hops} → `+
   cs.map(c=>`${f1(r.by_card[c].gb_s)} GB/s (${lab(c)})`).join(', ')+'. '+
   `Bandwidth against the ${xm==='longest'?'longest hand-off':'mean hops'}, ${d.length} offsets: r = `+
   cs.map(c=>`${num(R[xm][c].r,2)} (${lab(c)})`).join(', ')+'.');
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
   /* scatter: every offset, each card's registry mark */
   const sx0=narrow?48:mx+mapW+70, sx1=W-14, sy0=narrow?ky+78:28, sy1=f.H-44;
   const x=xm==='longest'?CK.lin(5.5,10.5,sx0,sx1):CK.lin(1,5,sx0,sx1), y=CK.lin(575,750,sy1,sy0);
   CK.axes({svg,W:sx1+14,H:sy1+44},{x,y,L:sx0,R:14,T:sy0,B:44,xt:xm==='longest'?[6,7,8,9,10]:[1,2,3,4,5],yt:[600,650,700,750],
     yfmt:n0,xl:xm==='longest'?'longest hand-off in the ring, mesh hops':'mean hand-off, mesh hops'});
   CK.txt(svg,sx0-44,sy0-10,'GB/s, whole relay','lab');
   const xv=q=>xm==='longest'?q.longest.hops:q.mesh_hops.mean;
   const F=R[xm][A2];
   /* the least-squares line of the first card, clipped to the plot (it would run past the axes at the ends) */
   const fy=v=>F.icpt+F.slope*v, cl=[y.domain[0],y.domain[1]].map(g=>(g-F.icpt)/F.slope).sort((p,q)=>p-q);
   const lx0=Math.max(x.domain[0],cl[0]), lx1=Math.min(x.domain[1],cl[1]);
   CK.el('line',{x1:x(lx0),x2:x(lx1),y1:y(fy(lx0)),y2:y(fy(lx1)),'aria-hidden':'true',
     style:'stroke:var(--ref);stroke-width:1.5;stroke-dasharray:5 4'},svg);
   /* r is in the readout above the chart, which follows the toggle */
   const pts=[];
   for(const q of d.slice().sort((a,b)=>xv(a)-xv(b)||a.hop_distance-b.hop_distance)){
    const g=CK.el('g',{},svg), sel=q.hop_distance===off, X=x(xv(q));
    cs.forEach((cc,ci)=>cmark(g,cc,X+(ci-(cs.length-1)/2)*7,y(q.by_card[cc].gb_s),CK.card(cc).color,sel));   // side by side: the cards agree within 1%
    const y0=y(q.by_card[A2].gb_s);
    if(sel){
     const rr_=CK.el('circle',{cx:X,cy:y0,r:14,fill:'none','aria-hidden':'true'},g);rr_.style.stroke='var(--ink)';rr_.style.strokeWidth='2';
     const edge=X>sx1-70;
     CK.txt(g,edge?X-18:X+18,y0+(edge?-14:4),`offset ${q.hop_distance}`,'tick',edge?'end':'start');
    }
    CK.tip(f,g,`<b>offset ${q.hop_distance}</b> · longest hand-off ${q.longest.hops} hops, mean ${f1(q.mesh_hops.mean)}<br>`+
     cs.map(cc=>`${f1(q.by_card[cc].gb_s)} GB/s (${lab(cc)})`).join(', ')+`<br>Enter shows this offset on the map`);
    g.dataset.o=q.hop_distance; g.addEventListener('click',()=>{off=q.hop_distance;segSet();});
    pts.push(g);
   }
   CK.keynav(f,pts,{onEnter:n=>{off=+n.dataset.o;segSet();}});
  }});
 function segSet(){offCtl.set(off);}
 upd();
 $('ringcap').textContent=
  `The map colours each shire by how many mesh hops the slab it reads at this offset has to travel (the stronger the blue, the farther); the arrows mark `+
  `the longest hand-offs, drawn straight because the route on the mesh was not measured. `+
  `The scatter puts the bandwidth at every offset against the longest hand-off or, toggled, the mean`+
  (cs.length>1?`: ${andL(cs.map(c=>`${mk(c)} ${lab(c)}`))}, side by side at each offset, each the mean of that card's passes; the dashed line is ${lab(A2)}'s least-squares line.`:'.');
})();
