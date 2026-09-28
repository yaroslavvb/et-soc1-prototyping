/* Over the PCIe link. Every number comes from D (pcie.json, written by workloads/pciebench/reduce_pcie.py from the
   raw runs in docs/reports/data/2026-09-27-pcie/raw). Charts use the shared toolkit CK (docs/reports/sources/chartkit.js). */
const $=id=>document.getElementById(id);
const num=CK.fmt.num;
const CS=CK.cardsIn(D.cards), lab=c=>CK.card(c).label;
const LINK=D.meta.link_gbs, BIG=256*1048576;
const andL=a=>a.length<2?a.join(''):a.slice(0,-1).join(', ')+' and '+a[a.length-1];
const rng=(vals,f)=>{const a=f(Math.min(...vals)),b=f(Math.max(...vals));return a===b?a:a+'–'+b;};
const g1=v=>num(v,1), g2=v=>num(v,2);
const us=v=>num(v,Math.abs(v)<10?1:0);                         // microseconds: 2.6, 113, 568
const ms2=v=>num(v/1000,2);                                     // microseconds shown as ms: 0.57
const sz=b=>b>=1048576?num(b/1048576,0)+' MB':num(b/1024,0)+' KB';
const ci=(s,f)=>s?(s.lo==null?f(s.mean):`${f(s.mean)} [${f(s.lo)}–${f(s.hi)}]`):'—';
const bwAt=(c,dir,path,b)=>(D.bw[c][dir][path].find(e=>e.bytes===b)||{}).gbs;
const DIRS={h2d:'host to card (H2D)',d2h:'card to host (D2H)'};
const VERD={PASS:'var(--ok)',FAIL:'var(--bad)',INCONCLUSIVE:'var(--warn)'};

/* ---------- lede and KPIs ---------- */
(function(){
 const h=CS.map(c=>bwAt(c,'h2d','dma',BIG).mean), d=CS.map(c=>bwAt(c,'d2h','dma',BIG).mean);
 const st=CS.map(c=>bwAt(c,'h2d','staged',BIG).mean), sd=CS.map(c=>bwAt(c,'d2h','staged',BIG).mean);
 $('l-spec').textContent=`${g2(LINK)} GB/s`;
 $('l-h2d').textContent=`${rng(h,g1)} GB/s (${rng(h.map(v=>100*v/LINK),v=>num(v,0))}% of that figure)`;
 $('l-d2h').textContent=`${rng(d,g1)} GB/s`;
 const p13=D.predictions.find(p=>p.id==='P13').across_cards;
 const dev=Math.max(...['h2d','d2h'].map(k=>Math.max(...Object.values(p13[k].rel_dev).map(Math.abs))));
 $('l-agree').textContent=`${num(100*dev,1)}% of their mean`;
 $('l-staged').textContent=`${rng(st,g1)} GB/s from host to card and ${rng(sd,g1)} GB/s back, by host`;
 const tally={PASS:0,FAIL:0,INCONCLUSIVE:0};
 D.predictions.forEach(p=>{if(p.per_card)CS.forEach(c=>tally[p.per_card[c].verdict]=(tally[p.per_card[c].verdict]||0)+1);
  else ['h2d','d2h'].forEach(k=>tally[p.across_cards[k].verdict]++);});
 const fails=D.predictions.filter(p=>p.per_card?CS.some(c=>p.per_card[c].verdict==='FAIL'):['h2d','d2h'].some(k=>p.across_cards[k].verdict==='FAIL')).map(p=>p.id);
 $('l-verdicts').textContent=`${tally.PASS} verdicts passed, ${tally.FAIL} failed and ${tally.INCONCLUSIVE} were inconclusive over the three cards`+
  (fails.length?` (failed: ${andL(fails)}; section 6)`:'');
 $('k1').textContent=`${rng(h,g1)} GB/s`; $('k1s').textContent=`${rng(h.map(v=>100*v/LINK),v=>num(v,0))}% of the ${g2(LINK)} GB/s link figure; three cards`;
 $('k2').textContent=`${rng(d,g1)} GB/s`; $('k2s').textContent=`${rng(d.map(v=>100*v/LINK),v=>num(v,0))}% of the link figure`;
 $('k3').textContent=`${rng(st,g1)} GB/s`;
 const one=CS.map(c=>D.launch[c].single_us['32'].mean), b2b=CS.map(c=>D.launch[c].b2b_us['32'].mean);
 const spm=CS.map(c=>{const v=Object.values(D.lat[c].sporadic).map(x=>x.mean_us.mean);return v.reduce((a,b)=>a+b)/v.length;});
 $('l-rt').textContent=`${rng(spm,ms2)} ms`; $('l-launch').textContent=`${rng(one,ms2)} ms`;
 $('k4').textContent=`${rng(one,ms2)} ms`; $('k4s').textContent=`32 shires; ${rng(b2b,ms2)} ms each when 100 are queued`;
})();

/* ---------- section 1: bandwidth against size ---------- */
(function(){
 const nh=CS.map(c=>D.n_half_log2[c].h2d_dma.mean);
 $('nhalf').textContent=`${rng(nh.map(v=>Math.pow(2,v)/1048576),v=>num(v,1))} MB (host to card)`;
 const n90=CS.map(c=>{const cur=D.bw[c].h2d.dma, top=bwAt(c,'h2d','dma',BIG).mean;   // the smallest size from which every size is >= 90%
  let i=cur.length-1; while(i>0&&cur[i-1].gbs.mean>=0.9*top)i--; return cur[i].bytes;});
 $('n90').textContent=rng(n90,sz);
 let dir='h2d', path='dma';
 CK.seg('bwdir',{label:'Direction',options:[['h2d','Host to card'],['d2h','Card to host']],value:dir,onChange:v=>{dir=v;f.redraw();}});
 CK.seg('bwpath',{label:'Path',options:[['dma','DMA-only'],['staged','Staged'],['both','Both']],value:path,onChange:v=>{path=v;f.redraw();}});
 CK.legend('bwlegend',CK.cardLegend(CS).concat([{key:'dma',label:'DMA-only',mark:'line',color:'var(--ink-2)'},
  {key:'staged',label:'staged',mark:'dash',color:'var(--ink-2)'}]));
 const sizes=D.bw[CS[0]].h2d.dma.map(e=>e.bytes);
 const f=CK.frame('bwchart',{label:'Copy bandwidth against transfer size',height:W=>W<600?300:360,draw:f=>{
  const L=f.narrow?40:48,R=f.narrow?10:16,T=26,B=40;
  const x=CK.log(sizes[0],sizes[sizes.length-1],L,f.W-R), y=CK.lin(0,17,f.H-B,T);
  const xt=sizes.filter((s,i)=>i%(f.narrow?4:2)===0);
  CK.axes(f,{x,y,L,R,T,B,xt,yt:[0,2,4,6,8,10,12,14,16],xfmt:sz,xl:'transfer size (binary MB)',yl:'GB/s'});
  const g=CK.el('g',{},f.svg);
  CK.el('line',{x1:L,x2:f.W-R,y1:y(LINK),y2:y(LINK),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'6 4'},g);
  CK.inside(f,[CK.txt(g,L+6,y(LINK)-6,`link figure, Gen4 x8: ${g2(LINK)} GB/s per direction`,'lab')]);
  const paths=path==='both'?['dma','staged']:[path], nodes=[];
  for(const p of paths) for(const c of CS){
   const pts=D.bw[c][dir][p].map(e=>[e.bytes,e.gbs.mean]);
   const ln=CK.el('path',{d:CK.path(pts,x,y),fill:'none','stroke-width':2,'stroke-linejoin':'round'},g);
   ln.style.stroke=CK.card(c).color; if(p==='staged')ln.setAttribute('stroke-dasharray','5 4');
   ln.setAttribute('data-series',c);
   D.bw[c][dir][p].forEach(e=>{
    const m=CK.cardMark(g,c,x(e.bytes),y(e.gbs.mean),f.narrow?3:3.5); m.setAttribute('data-series',c);
    CK.tip(f,m,`<b>${lab(c)}</b>, ${DIRS[dir]}, ${p==='dma'?'DMA-only':'staged'}, ${sz(e.bytes)}<br>`+
     `${ci(e.gbs,g2)} GB/s (mean of ${e.gbs.n} runs [99% interval])<br>fastest tenth of copies: ${g2(e.floor_gbs.mean)} GB/s`);
    nodes.push(m);});
  }
  CK.keynav(f,nodes);
 }});
 const d2hPk=CS.map(c=>D.derived[c].peak_dma_gbs.d2h);
 $('bwnote').textContent=`Hover or tab to a point for its 99% interval over the five runs and the rate of the fastest tenth of copies at that size. `+
  `Below the half-bandwidth size a copy's time is mostly fixed overhead (section 3), and the medians there switch between the runtime's two polling modes from run to run, so the small-size points scatter.`;
 // the card-to-host curve: its peak, its lowest point above the peak's size, and 256 MB
 const dip=CS.map(c=>{const cur=D.bw[c].d2h.dma, pk=cur.reduce((a,e)=>e.gbs.mean>a.gbs.mean?e:a), after=cur.filter(e=>e.bytes>pk.bytes&&e.bytes<BIG);
  const lo=after.length?after.reduce((a,e)=>e.gbs.mean<a.gbs.mean?e:a):null; return {pk,lo,end:bwAt(c,'d2h','dma',BIG).mean};});
 const recovers=dip.every(o=>o.lo&&o.end>o.lo.gbs.mean&&o.end<o.pk.gbs.mean);
 $('d2hdrop').textContent=`D2H DMA-only is not monotonic in size: it peaks at ${rng(dip.map(o=>o.pk.bytes),sz)}, dips at ${rng(dip.map(o=>o.lo?o.lo.bytes:BIG),sz)}`+
  (recovers?' and partly recovers by 256 MB':'')+` (${CS.map((c,i)=>`${lab(c)} ${g2(dip[i].pk.gbs.mean)}, ${g2(dip[i].lo?dip[i].lo.gbs.mean:dip[i].end)} and ${g2(dip[i].end)} GB/s`).join('; ')}); H2D keeps rising to 256 MB.`;
 const t=$('bwtable');
 t.innerHTML='<thead><tr><th>Size</th>'+CS.map(c=>`<th class="num">${lab(c)} H2D</th><th class="num">${lab(c)} D2H</th>`).join('')+'</tr></thead><tbody>'+
  sizes.map(s=>`<tr><td>${sz(s)}</td>`+CS.map(c=>`<td class="num">${g2(bwAt(c,'h2d','dma',s).mean)}</td><td class="num">${g2(bwAt(c,'d2h','dma',s).mean)}</td>`).join('')+'</tr>').join('')+'</tbody>';
 CK.stackTable(t);
})();

/* ---------- section 2: the staged path against DMA and the host's memcpy ---------- */
(function(){
 const h=D.hosts[CS[0]];
 $('chunk').textContent=`${num(h.dma_max_elem_bytes/1048576,0)} MB (the driver's DMA element; ${num(h.dma_max_elem_count,0)} elements a command, a ${h.cma} bounce buffer)`;
 $('hostcopy').textContent=andL(CS.map(c=>`${g1(D.hostcopy[c].find(e=>e.bytes===BIG).gbs.mean)} GB/s on ${lab(c)}`));
 const t=$('stagetable'), rows=[];
 for(const c of CS) for(const dir of ['h2d','d2h']){
  const dma=bwAt(c,dir,'dma',BIG), stg=bwAt(c,dir,'staged',BIG), mc=D.hostcopy[c].find(e=>e.bytes===BIG).gbs;
  const series=1/(1/dma.mean+1/mc.mean);
  rows.push(`<tr><td>${lab(c)}</td><td>${dir.toUpperCase()}</td><td class="num">${g2(dma.mean)}</td><td class="num">${g1(mc.mean)}</td>`+
   `<td class="num">${g2(series)}</td><td class="num">${ci(stg,g2)}</td><td class="num">${num(100*stg.mean/series,0)}%</td></tr>`);
 }
 t.innerHTML='<thead><tr><th>Card</th><th>Direction</th><th class="num">DMA-only, GB/s</th><th class="num">Host memcpy, GB/s</th>'+
  '<th class="num">The two in series</th><th class="num">Staged, measured [99%]</th><th class="num">Measured / series</th></tr></thead><tbody>'+rows.join('')+'</tbody>';
 CK.stackTable(t);

 /* The same numbers as a picture: one panel per direction, x the host's memcpy of 256 MB, y GB/s. Per card, its staged
    rate (the card's mark, with its 99% interval) at its host's memcpy, and above it the same copy DMA-only (a tick),
    joined by the drop the bounce copy costs. The curve is the series model 1/(1/DMA + 1/memcpy) at the cards' mean
    DMA-only rate (each card's own series value is in its tooltip and the table). */
 const SV={};
 for(const dir of ['h2d','d2h']) SV[dir]=CS.map(c=>{const dma=bwAt(c,dir,'dma',BIG), stg=bwAt(c,dir,'staged',BIG), mc=D.hostcopy[c].find(e=>e.bytes===BIG).gbs;
  return {c,dir,dma,stg,mc,series:1/(1/dma.mean+1/mc.mean)};});
 const ALL=SV.h2d.concat(SV.d2h), mcMax=Math.max(...ALL.map(r=>r.mc.mean)), XMAX=Math.ceil(mcMax*1.15/5)*5;
 CK.legend('serlegend',CK.cardLegend(CS).concat([{key:'dma',label:'the same copy, DMA-only',mark:'line',color:'var(--ink-2)'},
  {key:'curve',label:'the two in series, 1/(1/DMA + 1/memcpy)',mark:'line',color:'var(--c7)'}]));
 CK.frame('serchart',{label:'Staged copy bandwidth against the host memcpy rate, with the series model, both directions, every card',
  height:W=>W<600?620:330,draw:f=>{
  const narrow=f.narrow, gap=narrow?0:36, pw=narrow?f.W:(f.W-gap)/2, ph=narrow?f.H/2:f.H, nodes=[];
  ['h2d','d2h'].forEach((dir,k)=>{
   const ox=narrow?0:k*(pw+gap), oy=narrow?k*ph:0, L=ox+44, R=ox+pw-10, T=oy+30, B=oy+ph-40;
   const x=CK.lin(0,XMAX,L,R), y=CK.lin(0,17,B,T), g=CK.el('g',{},f.svg), ax=CK.el('g',{class:'ck-axes','aria-hidden':'true'},g);
   for(const v of [0,4,8,12,16]){CK.el('line',{x1:L,x2:R,y1:y(v),y2:y(v),class:'grid-line'},ax);CK.txt(ax,L-6,y(v)+4,num(v,0),'tick','end');}
   CK.el('line',{x1:L,x2:R,y1:B,y2:B,class:'ck-axis'},ax);
   for(let v=0;v<=XMAX;v+=5)CK.txt(ax,x(v),B+16,num(v,0),'tick','middle');
   const labs=[CK.txt(ax,(L+R)/2,B+34,'host memcpy of 256 MB, GB/s','lab','middle'),
    CK.txt(ax,ox+2,oy+14,dir==='h2d'?'Host to card: GB/s':'Card to host: GB/s','lab-strong')];
   CK.el('line',{x1:L,x2:R,y1:y(LINK),y2:y(LINK),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'6 4'},g);
   labs.push(CK.txt(g,R,y(LINK)-5,`link figure ${g2(LINK)}`,'lab','end'));
   const rs=SV[dir], dm=rs.reduce((a,r)=>a+r.dma.mean,0)/rs.length, pts=[];
   for(let v=0.5;v<=XMAX+1e-9;v+=0.25)pts.push([v,1/(1/dm+1/v)]);
   CK.el('path',{d:CK.path(pts,x,y),fill:'none','stroke-width':2,style:'stroke:var(--c7)','aria-hidden':'true'},g);
   const xl=XMAX/2; labs.push(CK.txt(g,x(xl),y(1/(1/dm+1/xl))+20,'in series','lab','middle'));
   rs.forEach(r=>{
    const px=x(r.mc.mean), n=CK.el('g',{},g), col=CK.card(r.c).color;
    CK.el('rect',{x:px-12,y:T,width:24,height:B-T,class:'ck-hit'},n);
    CK.el('line',{x1:px,x2:px,y1:y(r.dma.mean),y2:y(r.stg.mean),'stroke-width':1.5,'stroke-dasharray':'3 3',style:`stroke:${col}`,'aria-hidden':'true'},n);
    CK.el('line',{x1:px-9,x2:px+9,y1:y(r.dma.mean),y2:y(r.dma.mean),'stroke-width':2.5,'stroke-linecap':'round',style:'stroke:var(--ink-2)','aria-hidden':'true'},n);
    if(r.stg.lo!=null)CK.el('line',{x1:px,x2:px,y1:y(r.stg.lo),y2:y(r.stg.hi),'stroke-width':2,style:`stroke:${col}`,'aria-hidden':'true'},n);
    CK.cardMark(n,r.c,px,y(r.stg.mean),5);
    const drop=1-r.stg.mean/r.dma.mean;
    labs.push(CK.txt(n,px+9,(y(r.dma.mean)+y(r.stg.mean))/2+4,`−${num(100*drop,0)}%`,'lab'));
    CK.tip(f,n,`<b>${lab(r.c)}</b>, ${DIRS[dir]}, 256 MB<br>host memcpy ${g1(r.mc.mean)} GB/s · DMA-only ${g2(r.dma.mean)} GB/s<br>`+
     `in series: ${g2(r.series)} GB/s · staged, measured: ${ci(r.stg,g2)} GB/s, ${num(100*r.stg.mean/r.series,0)}% of it<br>`+
     `the bounce copy takes ${num(100*drop,0)}% off the DMA-only rate`);
    nodes.push(n);
   });
   CK.inside(f,labs);
  });
  CK.keynav(f,nodes);
 }});
 const fit=ALL.map(r=>100*r.stg.mean/r.series), drop=ALL.map(r=>100*(1-r.stg.mean/r.dma.mean));
 const slow=ALL.reduce((a,r)=>r.mc.mean<a.mc.mean?r:a), fast=ALL.reduce((a,r)=>r.mc.mean>a.mc.mean?r:a);
 const at=(c,dir)=>SV[dir].find(r=>r.c===c);
 /* the staged rate's 99% interval, drawn as a bar through the mark: say so only if it shows (the mark is 10 px, about
    0.6 GB/s on the 0-17 GB/s axis) */
 const ciMax=Math.max(...ALL.filter(r=>r.stg.lo!=null).map(r=>r.stg.hi-r.stg.lo)), ciHid=ciMax<0.6;
 $('sernote').textContent=`Each mark is a card's staged 256 MB copy (the mean of five runs; `+(ciHid?`its 99% interval, at most ${g2(ciMax)} GB/s wide, is smaller than the mark, and the tooltip gives it`:'the bar its 99% interval')+`), placed at its own host's memcpy of 256 MB; `+
  `the grey tick above it is the same copy DMA-only, and the percentage the drop between the two, ${rng(drop,v=>num(v,0))}% here. `+
  `The curve is the two copies in series at the cards' mean DMA-only rate; each card's staged rate is ${rng(fit,v=>num(v,0))}% of its own series value. `+
  `The host decides: ${lab(slow.c)}'s memcpy, the slowest at ${g1(slow.mc.mean)} GB/s, stages ${g2(at(slow.c,'h2d').stg.mean)} GB/s to the card, `+
  `and ${lab(fast.c)}'s, the fastest at ${g1(fast.mc.mean)} GB/s, ${g2(at(fast.c,'h2d').stg.mean)} GB/s, over the same link. `+
  `Because the two copies take turns, even the fastest memcpy leaves the program ${rng([at(fast.c,'h2d'),at(fast.c,'d2h')].map(r=>100*r.stg.mean/r.dma.mean),v=>num(v,0))}% of the DMA-only rate.`;
})();

/* ---------- section 3: small copies ---------- */
(function(){
 let card=CS[0], kind='sporadic_4k';
 CK.cardSeg('hcard',{cards:CS,value:card,onChange:v=>{card=v;f.redraw();note();}});
 CK.seg('hkind',{label:'Issued',options:[['sporadic_4k','after a random gap'],['round_trip_4k','back to back']],value:kind,onChange:v=>{kind=v;f.redraw();note();}});
 const f=CK.frame('hist',{label:'Histogram of 4 KB copy times',height:W=>W<600?240:280,draw:f=>{
  const H=D.hist[card], bins=H[kind], bw=H.bin_us, L=f.narrow?40:48, R=12, T=24, B=40;
  const x=CK.lin(0,bins.length*bw,L,f.W-R), y=CK.lin(0,Math.max(...bins)*1.08,f.H-B,T);
  CK.axes(f,{x,y,L,R,T,B,xt:[0,100,200,300,400,500,600,700,800],xfmt:v=>v===800?'800+':num(v,0),xl:'issue to completion, µs',yl:'copies'});
  const g=CK.el('g',{},f.svg), nodes=[], tot=bins.reduce((a,b)=>a+b,0);
  bins.forEach((n,i)=>{ if(!n)return;
   const x0=x(i*bw)+1, w=Math.max(1,x((i+1)*bw)-x(i*bw)-2);
   const r=CK.el('rect',{x:x0,y:y(n),width:w,height:Math.max(0.5,y(0)-y(n)),rx:Math.min(2,w/2)},g); r.style.fill=CK.card(card).color;
   CK.tip(f,r,`<b>${num(i*bw,0)}–${i===bins.length-1?'':num((i+1)*bw,0)} µs</b><br>${num(n,0)} of ${num(tot,0)} copies (${num(100*n/tot,1)}%), ${lab(card)}`);
   nodes.push(r);});
  CK.keynav(f,nodes);
 }});
 (function(){const bins=CS.map(c=>D.hist[c].sporadic_4k).reduce((a,b)=>a.map((v,i)=>v+b[i])), tot=bins.reduce((a,b)=>a+b,0), w=D.hist[CS[0]].bin_us;
  let acc=0,p1=null,p99=null; bins.forEach((n,i)=>{acc+=n; if(p1==null&&acc>=0.01*tot)p1=i*w; if(p99==null&&acc>=0.99*tot)p99=(i+1)*w;});
  $('rtspan').textContent=`${num(p1,0)} to ${num(p99,0)} µs`;})();
 function note(){
  const L=D.lat[card], sp=Object.values(L.sporadic), rt=L.round_trip;
  const share=kind==='sporadic_4k'?sp.map(v=>v.fast_share.mean):['h2d_staged_4096','h2d_dma_4096','d2h_staged_4096','d2h_dma_4096'].map(k=>rt[k].fast_share.mean);
  $('histnote').textContent=`${lab(card)}: ${rng(share.map(v=>100*v),v=>num(v,0))}% of the copies finished within 300 µs, depending on the variant (direction and path); `+
   `the rest waited for part or all of the runtime's 500 µs idle sleep. `+(kind==='round_trip_4k'?`Back to back, whether the next copy is issued before the response thread checks for work in flight is a race, so a variant can sit in either mode for a whole run.`:
   `After a random gap the issue lands anywhere in the response thread's cycle.`);
 }
 note();
 const t=$('lattable'), rows=[];
 const row=(label,get,f)=>rows.push(`<tr><td>${label}</td>`+CS.map(c=>`<td class="num">${ci(get(c),f)}</td>`).join('')+'</tr>');
 row('Waiting on an idle stream',c=>D.lat[c].idle_wait_us,us);
 [['h2d_staged_4096','4 KB, H2D, staged, back to back'],['d2h_staged_4096','4 KB, D2H, staged, back to back'],
  ['h2d_dma_4096','4 KB, H2D, DMA-only, back to back'],['d2h_dma_4096','4 KB, D2H, DMA-only, back to back'],
  ['h2d_staged_64','64 B, H2D, staged, back to back']].forEach(([k,l])=>row(l,c=>D.lat[c].round_trip[k].median_us,us));
 const spMean=c=>{const v=Object.values(D.lat[c].sporadic).map(x=>x.mean_us.mean);return {mean:v.reduce((a,b)=>a+b)/v.length,lo:null};};
 row('4 KB after a random 0–1 ms gap: each run\'s mean, averaged over the four variants and five runs',spMean,us);
 row('4 KB after a random gap, H2D staged',c=>D.lat[c].sporadic.h2d_staged.median_us,us);
 row('200 queued 4 KB copies, H2D staged: per copy',c=>D.lat[c].pipelined_us_per_copy.h2d_staged,us);
 row('200 queued 4 KB copies, D2H staged: per copy',c=>D.lat[c].pipelined_us_per_copy.d2h_staged,us);
 t.innerHTML='<thead><tr><th>Microseconds: each run\'s median, mean over five runs [99%]</th>'+CS.map(c=>`<th class="num">${lab(c)}</th>`).join('')+'</tr></thead><tbody>'+rows.join('')+'</tbody>';
 CK.stackTable(t);
 const pipe=CS.map(c=>D.lat[c].pipelined_us_per_copy.h2d_staged.mean);
 const idle=CS.map(c=>D.lat[c].idle_wait_us.mean);
 $('latnote').textContent=`The back-to-back rows ran the four variants in a fixed order (host to card staged, then DMA-only, then card to host staged and DMA-only, every repeat): `+
  `each variant's time reflects its place in that order, which of the runtime's two polling modes it lands in, not a property of its path. The random-gap rows shuffle the order. `+
  `Queued without waiting, 4 KB copies (H2D, staged) complete one every ${andL(CS.map((c,i)=>`${us(pipe[i])} µs on ${lab(c)}`))}: `+
  `the per-command cost with the polling overlapped. It differs by host as the runtime builds do (so does the idle-stream wait, ${andL(CS.map((c,i)=>`${us(idle[i])} µs on ${lab(c)}`))}), `+
  `while the link and the card are the same. A single copy costs that plus the wait for the response thread.`;
})();

/* ---------- section 4: launches ---------- */
(function(){
 const t=$('launchtable'), rows=[];
 const row=(label,get)=>rows.push(`<tr><td>${label}</td>`+CS.map(c=>`<td class="num">${ci(get(c),us)}</td>`).join('')+'</tr>');
 row('One launch, waited for: 32 shires',c=>D.launch[c].single_us['32']);
 row('One launch, waited for: 1 shire',c=>D.launch[c].single_us['1']);
 row('100 launches queued: per launch, 32 shires',c=>D.launch[c].b2b_us['32']);
 row('100 launches queued: per launch, 1 shire',c=>D.launch[c].b2b_us['1']);
 row('The first launch after loading the kernel',c=>D.launch[c].first_us);
 row('Loading the kernel (a 5 KB ELF)',c=>D.launch[c].load_us);
 t.innerHTML='<thead><tr><th>Microseconds: each run\'s median, mean over five runs [99%]</th>'+CS.map(c=>`<th class="num">${lab(c)}</th>`).join('')+'</tr></thead><tbody>'+rows.join('')+'</tbody>';
 CK.stackTable(t);
 const b32=CS.map(c=>D.launch[c].b2b_us['32'].mean), b1=CS.map(c=>D.launch[c].b2b_us['1'].mean), one=CS.map(c=>D.launch[c].single_us['32'].mean);
 $('launchnote').textContent=`Queued, an empty kernel on all 32 shires takes ${rng(b32,us)} µs of the card's time and on one shire ${rng(b1,us)} µs: `+
  `about ${rng(CS.map((c,i)=>b32[i]-b1[i]),us)} µs for the other 31 shires, the rest fixed. Waited for one at a time, a launch takes ${rng(one,us)} µs: `+
  `the queued cost plus most of a 500 µs sleep of the response thread, which a single launch meets nearly every time (within a run, the middle 80% of single launches lie within ${rng(CS.map(c=>D.launch[c].single_p10_p90_spread_us['32'].mean),us)} µs of each other).`;

 /* Where the time of one operation goes. Two operations, each card a bar: an empty kernel on 32 shires launched and
    waited for (single_us['32']) and a 4 KB copy after a random 0-1 ms gap (the mean of the four variants' mean_us).
    The first segment is the operation's cost when many are queued, so that the response thread's polling overlaps the
    work: 100 queued launches (b2b_us['32']) and 200 queued copies (pipelined_us_per_copy, the same four variants
    averaged); the second is the rest, the wait for the response thread. The dashed line is its 500 us idle sleep
    (kResponsePollingIntervalNoEventsOnFly, ResponseReceiver.cpp, cited in section 3). */
 const V4=['d2h_dma','d2h_staged','h2d_dma','h2d_staged'], avg=a=>a.reduce((s,v)=>s+v,0)/a.length, SLEEP=500;
 const OPS=[{key:'launch',label:'An empty kernel on 32 shires, launched and waited for',labelN:'An empty kernel, 32 shires',short:'empty kernel',
   rows:CS.map(c=>({c,total:D.launch[c].single_us['32'],work:D.launch[c].b2b_us['32'].mean,
    how:'100 launches queued, per launch'}))},
  {key:'copy',label:'A 4 KB copy after a random 0–1 ms gap (the four variants averaged)',labelN:'A 4 KB copy after a random gap',short:'4 KB copy',
   rows:CS.map(c=>({c,total:{mean:avg(V4.map(v=>D.lat[c].sporadic[v].mean_us.mean)),lo:null},work:avg(V4.map(v=>D.lat[c].pipelined_us_per_copy[v].mean)),
    how:'200 copies queued, per copy'}))}];
 CK.legend('waitlegend',[{key:'work',label:'its cost when queued, polling overlapped',mark:'box',color:'var(--c7)'},
  {key:'wait',label:'the rest: waiting for the response thread',mark:'box',color:'var(--ref)'}]);
 const tmax=Math.max(...OPS.map(o=>Math.max(...o.rows.map(r=>r.total.mean))));
 CK.frame('waitchart',{label:'Time of one operation split into its queued cost and the wait for the response thread, per card',
  height:W=>(W<600?58:44)*CS.length*OPS.length+(W<600?40:34)*OPS.length+56,draw:f=>{
  const narrow=f.narrow, L=narrow?12:176, R=narrow?56:64, T=26, B=40, head=narrow?40:34, rowH=narrow?58:44, bh=narrow?16:18;
  const x=CK.lin(0,Math.max(SLEEP,Math.ceil(tmax/100)*100),L,f.W-R), g=CK.el('g',{},f.svg), nodes=[], labs=[];
  CK.axes(f,{x,y:CK.lin(0,1,f.H-B,T),L,R,T,B,yt:[],yfmt:()=>'',xt:[0,100,200,300,400,500,600].filter(v=>v<=x.domain[1]),xl:'microseconds'});
  CK.el('line',{x1:x(SLEEP),x2:x(SLEEP),y1:T-4,y2:f.H-B,stroke:'var(--ink-2)','stroke-width':1.5,'stroke-dasharray':'5 4','aria-hidden':'true'},g);
  labs.push(CK.txt(g,x(SLEEP),T-10,narrow?`idle sleep, ${num(SLEEP,0)} µs`:`the response thread's idle sleep, ${num(SLEEP,0)} µs`,'lab','middle'));
  let yy=T;
  OPS.forEach(o=>{
   labs.push(CK.txt(g,narrow?L:4,yy+22,narrow?o.labelN:o.label,'lab-strong'));
   yy+=head;
   o.rows.forEach(r=>{
    const cy=yy+(narrow?34:rowH/2), y0=cy-bh/2, t=r.total.mean, wait=t-r.work, n=CK.el('g',{},g);
    CK.el('rect',{x:L,y:yy+2,width:f.W-L-R,height:rowH-4,class:'ck-hit'},n);
    if(narrow)labs.push(CK.txt(n,L+14,yy+14,lab(r.c),'lab')); else labs.push(CK.txt(n,L-22,cy+4,lab(r.c),'lab','end'));
    CK.cardMark(n,r.c,narrow?L+5:L-12,narrow?yy+10:cy,4);
    const a=CK.el('rect',{x:x(0),y:y0,width:Math.max(1,x(r.work)-x(0)),height:bh,rx:2,'aria-hidden':'true'},n); a.style.fill='var(--c7)';
    const b=CK.el('rect',{x:x(r.work)+2,y:y0,width:Math.max(1,x(t)-x(r.work)-2),height:bh,rx:2,'aria-hidden':'true'},n); b.style.fill='var(--ref)';
    const tl=CK.txt(n,x(t)+6,cy+4,`${num(t,0)} µs`,'tick'); tl.setAttribute('style','paint-order:stroke;stroke:var(--page);stroke-width:4px;stroke-linejoin:round'); labs.push(tl);
    /* a value that would reach the dashed sleep line moves to its far side, clear of it */
    {let w=0; try{w=tl.getComputedTextLength();}catch(_){} if(!(w>0))w=7*tl.textContent.length; const xs=x(SLEEP);
     if(x(t)+6<xs+4&&x(t)+6+w>xs-4)tl.setAttribute('x',(Math.max(x(t),xs)+6).toFixed(1));}
    CK.tip(f,n,`<b>${lab(r.c)}</b> · ${o.short}<br>one at a time: ${ci(r.total,v=>num(v,0))} µs<br>`+
     `its cost when queued (${r.how}): ${us(r.work)} µs, ${num(100*r.work/t,0)}%<br>the rest, waiting for the response thread: ${num(wait,0)} µs, ${num(100*wait/t,0)}%`);
    nodes.push(n);
    yy+=rowH;
   });
  });
  CK.inside(f,labs);
  CK.keynav(f,nodes);
 }});
 const share=o=>o.rows.map(r=>100*(1-r.work/r.total.mean)), L_=OPS[0], C_=OPS[1];
 $('waitnote').textContent=`Each bar is one operation at a time (the mean of five runs); its first segment is what the same operation costs when many are queued, `+
  `so that the runtime's polling overlaps the work (per launch with 100 queued; per copy with 200 queued, from section 3's table), and the rest is the wait. `+
  `Waiting takes ${rng(share(L_),v=>num(v,0))}% of an empty kernel's ${rng(L_.rows.map(r=>r.total.mean),v=>num(v,0))} µs `+
  `and ${rng(share(C_),v=>num(v,0))}% of a 4 KB copy's ${rng(C_.rows.map(r=>r.total.mean),v=>num(v,0))} µs. `+
  `Against the response thread's ${num(SLEEP,0)} µs idle sleep, a launch waits ${rng(L_.rows.map(r=>(r.total.mean-r.work)/SLEEP),v=>num(v,2))} of one `+
  `and a copy issued after a random gap, which lands anywhere in the sleep, ${rng(C_.rows.map(r=>(r.total.mean-r.work)/SLEEP),v=>num(v,2))} on average. `+
  `Queued, a launch costs ${rng(L_.rows.map(r=>r.work),us)} µs on every card, and a copy ${andL(C_.rows.map(r=>`${us(r.work)} µs on ${lab(r.c)}`))}: `+
  `the copies differ by host as the runtime builds do (section 3).`;
})();

/* ---------- section 5: several transfers at once ---------- */
(function(){
 const CFG=[['h2d/ser','H2D, one at a time'],['h2d','H2D, two in flight'],['2xh2d','H2D, two streams (four in flight)'],
  ['d2h/ser','D2H, one at a time'],['d2h','D2H, two in flight'],['2xd2h','D2H, two streams (four in flight)'],
  ['h2d+d2h/ser','Both ways, one at a time each'],['h2d+d2h','Both ways, two in flight each']];
 CK.legend('cclegend',CK.cardLegend(CS));
 const vmax=Math.max(...CS.map(c=>Math.max(...CFG.map(([k])=>D.conc[c].dma[k].agg_gbs.mean))));
 const f=CK.frame('ccchart',{label:'Aggregate bandwidth by configuration',height:W=>(W<600?56:40)*CFG.length+60,draw:f=>{
  const narrow=f.narrow, L=narrow?12:228, R=16, T=24, B=40, rowH=(f.H-T-B)/CFG.length;
  const x=CK.lin(0,Math.max(20,Math.ceil(vmax/2)*2+2),L,f.W-R);
  const yr=i=>T+rowH*(narrow?i+0.66:i+0.5);   // narrow: the label sits at the top of its row, the marks below it
  CK.axes(f,{x,y:CK.lin(0,1,f.H-B,T),L,R,T,B,yt:[],yfmt:()=>'',xl:'aggregate GB/s (both directions counted)'});
  const g=CK.el('g',{},f.svg), nodes=[];
  CK.el('line',{x1:x(LINK),x2:x(LINK),y1:T,y2:f.H-B,stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'6 4'},g);
  CK.inside(f,[CK.txt(g,x(LINK)+4,T-6,`one direction's link figure, ${g2(LINK)} GB/s`,'lab')]);
  CFG.forEach(([k,label],i)=>{
   CK.el('line',{x1:L,x2:f.W-R,y1:yr(i),y2:yr(i),class:'grid-line'},g);
   if(narrow)CK.txt(g,L,T+rowH*i+12,label,'lab'); else CK.txt(g,L-8,yr(i)+4,label,'lab','end');
   CS.forEach((c,j)=>{
    const s=D.conc[c].dma[k].agg_gbs, off=(j-1)*(narrow?5:6);
    const m=CK.cardMark(g,c,x(s.mean),yr(i)+off,4.5);
    const legs=D.conc[c].dma[k].legs_gbs.map(l=>g2(l.mean)).join(' + ');
    CK.tip(f,m,`<b>${label}</b> · ${lab(c)}<br>${ci(s,g2)} GB/s aggregate (median of three trials, mean of ${s.n} runs [99%])<br>each leg alone: ${legs} GB/s`);
    nodes.push(m);});
  });
  CK.keynav(f,nodes);
 }});
 const r=k=>CS.map(c=>D.derived[c][k].mean);
 const one=CS.map(c=>D.conc[c].dma['h2d/ser'].agg_gbs.mean), two=CS.map(c=>D.conc[c].dma['h2d'].agg_gbs.mean);
 const stg=CS.map(c=>D.conc[c].staged['h2d'].agg_gbs.mean/D.conc[c].staged['h2d/ser'].agg_gbs.mean);
 $('ccnote').textContent=`One H2D command at a time moves ${rng(one,g1)} GB/s; two in flight move ${rng(two,g1)} GB/s together, `+
  `${rng(r('h2d_two_in_flight_over_one'),g2)} times as much, and four in flight on two streams no more. D2H gains a little from a second command (${rng(r('d2h_two_in_flight_over_one'),g2)} times). `+
  `The link is full duplex: one command each way at a time gives ${rng(r('duplex_ser_over_faster_ser'),g2)} times the faster direction alone. `+
  `DMA-only, two host-to-card copies at once halve the rate; a program's staged copies, queued two at a time as the runtime's asynchronous API invites, keep ${rng(stg,g2)} of their one-at-a-time rate (staged, not shown in the chart), because the host copy between the DMAs hides part of the loss. `+
  `Why concurrent DMA reads collapse (the engine, the IOMMU or the host's read completions) is not established; the hub lists what would settle it.`;
})();

/* ---------- section 6: predictions ---------- */
(function(){
 const fv=(s,id)=>{if(!s)return '—';
  if(id==='P5'){const m=v=>num(Math.pow(2,v)/1048576,2)+' MB';return s.lo==null?m(s.mean):`${m(s.mean)} [${m(s.lo)}–${m(s.hi)}]`;}
  const mx=Math.max(Math.abs(s.mean),Math.abs(s.lo||0),Math.abs(s.hi||0)), f=mx>=100?v=>num(v,0):mx>=10?v=>num(v,1):v=>num(v,2);
  return s.lo==null?f(s.mean):`${f(s.mean)} [${f(s.lo)}, ${f(s.hi)}]`;};
 const chip=v=>`<b style="color:${VERD[v]||'var(--muted)'}">${v==='INCONCLUSIVE'?'inconclusive':v.toLowerCase()}</b>`;
 const t=$('predtable');
 t.innerHTML='<thead><tr><th>ID</th><th>Quantity</th><th>Predicted</th>'+CS.map(c=>`<th>${lab(c)}</th>`).join('')+'</tr></thead><tbody>'+
  D.predictions.map(p=>{
   if(p.per_card)return `<tr><td>${p.id}</td><td>${p.text}</td><td>${p.prediction}</td>`+CS.map(c=>`<td>${chip(p.per_card[c].verdict)} ${fv(p.per_card[c].value,p.id)}</td>`).join('')+'</tr>';
   const a=p.across_cards;
   return `<tr><td>${p.id}</td><td>${p.text}</td><td>${p.prediction}</td>`+CS.map(c=>`<td>H2D ${num(100*a.h2d.rel_dev[c],1)}%, D2H ${num(100*a.d2h.rel_dev[c],1)}% (${chip(a.h2d.verdict)}, ${chip(a.d2h.verdict)} for all three)</td>`).join('')+'</tr>';
  }).join('')+'</tbody>';
 CK.stackTable(t);
 // why the predictions that did not pass did not: one sentence per such prediction, from the data
 const P=id=>D.predictions.find(p=>p.id===id), not=(id,v)=>CS.filter(c=>P(id).per_card[c].verdict===v);
 const why=[];
 if(not('P3','FAIL').length){const d=CS.map(c=>-P('P3').per_card[c].value.mean);
  why.push(`<b>P3 had the direction backwards:</b> host to card is the faster direction, by ${rng(d,g2)} GB/s at 256 MB (on ${andL(not('P3','FAIL').map(lab))}).`);}
 const p4=[...new Set(not('P4a','FAIL').concat(not('P4b','FAIL')))];
 if(p4.length)why.push(`<b>P4 failed on ${andL(p4.map(lab))}:</b> its host's memcpy (${andL(p4.map(c=>g1(D.hostcopy[c].find(e=>e.bytes===BIG).gbs.mean)+' GB/s'))}) is slower than the link. The prediction assumed the bounce copy overlaps the DMA; the runtime runs them one after the other (section 2).`);
 if(not('P11','FAIL').length){const ser=CS.map(c=>D.derived[c].duplex_ser_over_faster_ser.mean);
  why.push(`<b>P11 failed on ${andL(not('P11','FAIL').map(lab))}</b> (${rng(CS.map(c=>P('P11').per_card[c].value.mean),g2)} times): the registered configuration kept two H2D commands in flight, which halves host to card (section 5). With one command each way at a time the link carries ${rng(ser,g2)} times the faster direction: duplex works, but short of the predicted 1.5.`);}
 const inc=['P5','P6','P7'].filter(id=>not(id,'INCONCLUSIVE').length);
 const RANGE={P5:[17,22],P6:[60,700],P7:[-25,25]};   // as registered (PREREG.md)
 // per prediction: every run inside the range but a wide interval (one slow run widens the t-interval), or runs outside it
 inc.forEach(id=>{
  const cards=not(id,'INCONCLUSIVE'), runs=[].concat(...CS.map(c=>P(id).per_card[c].value.runs)), [lo,hi]=RANGE[id], out=runs.filter(v=>v<lo||v>hi).length;
  const f=id==='P5'?(v=>num(Math.pow(2,v)/1048576,2)+' MB'):(v=>num(v,0)+' µs'), band=id==='P5'?`${f(lo)} to ${f(hi)}`:id==='P7'?`±${num(hi,0)} µs`:`${num(lo,0)}–${num(hi,0)} µs`;
  if(!out)why.push(`<b>${id} is inconclusive</b> on ${andL(cards.map(lab))}: every run lies inside the predicted ${band}, but one slower run per card (up to ${f(Math.max(...cards.map(c=>Math.max(...P(id).per_card[c].value.runs))))}) widens the 99% t-interval of five runs past the range's edge.`);
  else why.push(`<b>${id} is inconclusive</b> on ${andL(cards.map(lab))}: the runs spread wider than the predicted ${band} (${num(out,0)} of ${num(runs.length,0)} runs outside it), so the intervals straddle its edge.`);
 });
 const other=D.predictions.filter(p=>p.per_card&&!['P3','P4a','P4b','P11','P5','P6','P7'].includes(p.id)&&CS.some(c=>p.per_card[c].verdict!=='PASS'));
 other.forEach(p=>why.push(`<b>${p.id}</b> is ${andL(CS.filter(c=>p.per_card[c].verdict!=='PASS').map(c=>`${p.per_card[c].verdict.toLowerCase()} on ${lab(c)}`))}`+
  (p.id==='P10'?`: see the clock note in section 7.`:'.')));
 $('predwhy').innerHTML=why.join(' ');
 $('prednote').innerHTML=`Values: mean over five runs [99% interval]. P5 is shown in MB and judged on log2 of the size. `+
  `P6 and P7 were judged on the back-to-back round trips, which kept a fixed order of the four copy variants (section 3), so their values carry that order's polling mode. `+
  `P3, P9b, P10, P11 and P12 are judged on each run's own difference or ratio. P11 and P12 used the configurations as registered (two commands in flight per stream), `+
  `which the pilot run showed to be the slow case for H2D; section 5 adds the one-at-a-time configurations. The PREREG file's sha256 is <code>${D.meta.prereg_sha256}</code>.`;
})();

/* ---------- caveat and method spans ---------- */
(function(){
 const links=[...new Set(CS.map(c=>`${D.hosts[c].link_speed} x${D.hosts[c].link_width}`))];
 $('hostlist').textContent=andL(CS.map(c=>`${lab(c)} (${D.hosts[c].host_threads} host threads)`))+`; every card's link negotiated ${andL(links)}`;
 $('elapsed').textContent=`${num(Math.max(...CS.map(c=>D.hosts[c].elapsed_s_max)),1)} s`;
 const held=[].concat(...CS.map(c=>D.hosts[c].run_times_ms.map(r=>(r[1]-r[0])/1000)));   // each run's start to end, the lock held throughout
 $('lockheld').textContent=`${num(Math.max(...held),1)} s (${rng(held,v=>num(v,1))} s per run)`;
 const die=[].concat(...CS.map(c=>D.hosts[c].die_c)), mhz=[...new Set([].concat(...CS.map(c=>D.hosts[c].minion_mhz)))];
 $('dierange').textContent=`the minion clock at ${andL(mhz.map(v=>num(v,0)+' MHz'))} and the dies at ${rng(die,v=>num(v,0))} °C (the minion-shire mean)`;
 const t=[].concat(...CS.map(c=>D.hosts[c].run_times_ms.flat())), d0=new Date(Math.min(...t)), d1=new Date(Math.max(...t));
 const hm=d=>new Date(d.getTime()-7*3600e3).toISOString().slice(11,16);   // the lab's clock, PDT (UTC-7)
 $('window').textContent=`${hm(d0)}–${hm(d1)} PDT`;
 // a run whose queued one-shire launches ran well below the card's other runs (the governor lifting the clock between samples?)
 const odd=[];
 CS.forEach(c=>{const r=D.launch[c].b2b_us['1'].runs, runs=D.hosts[c].runs;
  r.forEach((v,i)=>{const rest=r.filter((_,j)=>j!==i), m=rest.reduce((a,b)=>a+b,0)/rest.length;
   if(v<0.95*m)odd.push({c,run:runs[i],v,m,die:(D.hosts[c].die_c_by_run||{})[runs[i]]});});});
 $('clocknote').textContent=odd.length?odd.map(o=>`On ${lab(o.c)}, run ${o.run}${o.die&&o.die[0]!=null?` (which began at ${num(o.die[0],0)} °C)`:''} queued one-shire launches at ${us(o.v)} µs against ${us(o.m)} µs in its other runs, `+
  `with 600 MHz in both of its samples: probably the clock moving between them`+(o.c==='aifoundry2'?`, as aifoundry2's governor does below about 68 °C (docs/findings/14-card-behaviour.md)`:'')+`; it moves that card's one-shire launch figures, not its transfers.`).join(' '):'';
 const v=[].concat(...CS.map(c=>D.hosts[c].verify));
 $('verify').textContent=`${v.filter(Boolean).length} of ${v.length} runs`;
})();
